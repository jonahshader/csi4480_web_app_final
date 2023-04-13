import random

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from dataclasses import dataclass
import time

from starlette.requests import Request

from common import users

app = FastAPI()

EXPIRATION_TIME = 5 * 60
MAX_FAILED_ATTEMPTS = 5
BLACKLIST_COOLDOWN = 5

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], # having issues with origins, allowing all for now
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@dataclass
class Session:
    user_token: int
    creation_time: float
    max_duration: float
    ip: str

    def is_expired(self):
        return time.time() - self.creation_time > self.max_duration

    def is_same_ip(self, ip):
        return self.ip == ip

    @staticmethod
    def create_token(ip, max_duration=EXPIRATION_TIME):
        # create random 32 bit token
        user_token = 0
        for i in range(32):
            user_token = (user_token << 1) | (random.randint(0, 1))
        return Session(user_token, time.time(), max_duration, ip)


user_token_to_session = {}
user_token_to_user_id = {}

ip_fail_cooldown = {}
ip_fail_count = {}

def user_token_to_user(user_token):
    if user_token not in user_token_to_user_id:
        return None
    user_id = user_token_to_user_id[user_token]
    return users[user_id]

def user_email_to_user(email):
    for user in users.values():
        if user['email'] == email:
            return user
    return None


def is_request_allowed(user_token, ip):
    if is_ip_on_cooldown(ip):
        return False

    # check if user token is valid
    if user_token not in user_token_to_session:
        increment_ip_fail_count(ip)
        return False

    # grab session, check if it's expired
    session = user_token_to_session[user_token]
    if session.is_expired():
        del user_token_to_session[user_token]
        del user_token_to_user_id[user_token]
        increment_ip_fail_count(ip)
        return False
    # check if ip is the same
    elif not session.is_same_ip(ip):
        increment_ip_fail_count(ip)
        return False
    # success: reset fail count
    reset_ip_fail_count(ip)
    return True


def cooldown_ip(ip):
    ip_fail_cooldown[ip] = time.time()


def increment_ip_fail_count(ip):
    if ip not in ip_fail_count:
        ip_fail_count[ip] = 0
    ip_fail_count[ip] += 1

    if ip_fail_count[ip] >= MAX_FAILED_ATTEMPTS:
        cooldown_ip(ip)
        reset_ip_fail_count(ip)


def reset_ip_fail_count(ip):
    ip_fail_count[ip] = 0


def is_ip_on_cooldown(ip):
    # check if ip is on cooldown
    if ip in ip_fail_cooldown:
        if time.time() - ip_fail_cooldown[ip] < BLACKLIST_COOLDOWN:
            print(f'IP {ip} is on cooldown')
            return True
        else:
            del ip_fail_cooldown[ip]
            del ip_fail_count[ip]
    return False


#curl "localhost:8000/authenticate?email=john@gmail.com&password=bing"
@app.get('/authenticate', tags=['authentication'])
async def get_user_token(email: str, password: str, request: Request, duration:float=EXPIRATION_TIME, ip=None):
    if is_ip_on_cooldown(request.client.host):
        return {'success': False}
    for user in users.values():
        if user['email'] == email and user['password'] == password:
            if ip:
                session = Session.create_token(ip, duration)
            else:
                session = Session.create_token(request.client.host, duration)
            print(f'Created session: {session}')
            user_token_to_session[session.user_token] = session
            user_token_to_user_id[session.user_token] = user['id']
            return {'user_token': session.user_token, 'success': True}
    increment_ip_fail_count(request.client.host)
    return {'success': False}

#curl localhost:8000/data?user_token=1
@app.get('/data', tags=['main data'])
async def read_data(user_token: int, request: Request):
    if not is_request_allowed(user_token, request.client.host):
        return {'token_expired': True}
    for user in users.values():
        if user['id'] == user_token_to_user_id[user_token]:
            return {'user': user, 'success': True}
    return {'success': False}

#curl -X PUT "localhost:8000/add_balance?user_token=1&amount=10"
@app.put('/add_balance', tags=['add balance'])
async def add_balance(user_token: int, amount: int, request: Request):
    if not is_request_allowed(user_token, request.client.host):
        return {'token_expired': True}
    for user in users.values():
        if user['id'] == user_token_to_user_id[user_token]:
            user['balance'] += amount
            return {'success': True}
    return {'success': False}


@app.put('/transfer', tags=['transfer money'])
async def transfer(user_token: int, dest_email: str, amount: int, request: Request):
    if not is_request_allowed(user_token, request.client.host):
        return {'token_expired': True}
    if amount < 0:
        print('Amount must be positive')
        return {"success": False}
    sender = user_token_to_user(user_token)
    receiver = user_email_to_user(dest_email)
    if sender is None or receiver is None:
        print('Sender or receiver not found')
        return {"success": False}
    if sender['balance'] < amount:
        print('Sender does not have enough money')
        return {"success": False}
    sender['balance'] -= amount
    receiver['balance'] += amount
    return {'success': True}

#curl -X POST "localhost:8000/create_account?email=cool@gmail.com&password=cool&fname=cool&lname=cool&p_number=1234567890&ssn=123456789"
@app.post('/create_account', tags=['create account'])
async def create_account(email: str, password: str, fname: str, lname: str, p_number: str, ssn: str):
    max_id = 0
    for user in users.values():
        if user['id'] > max_id:
            max_id = user['id']
    new_user = {
        'id': max_id + 1,
        'email': email,
        'password': password,
        'fname': fname,
        'lname': lname,
        'p_number': p_number,
        'ssn': ssn,
        'balance': 0
    }
    users[max_id + 1] = new_user
    print(users)
    return {"success": True}

#curl -X PUT localhost:8000/logout?user_token=1
@app.put('/logout', tags=['logout'])
async def logout(user_token: int):
    if user_token in user_token_to_session:
        del user_token_to_session[user_token]
    if user_token in user_token_to_user_id:
        del user_token_to_user_id[user_token]
    return {"success": True}

if __name__ == '__main__':
    #uvicorn.run('backend.v2:app', host='0.0.0.0', port=8000, reload=True)
    uvicorn.run('v2:app', host='0.0.0.0', port=8000, reload=True)