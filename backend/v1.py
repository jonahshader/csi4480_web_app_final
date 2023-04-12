import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:3000'
    'localhost:3000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

users = {
    0: {
        'id': 0,
        'email': 'foo@gmail.com',
        'password': 'password',
        'fname': 'Foo',
        'lname': 'Bruh',
        'p_number': '1234567890',
        'ssn': '123456789',
        'balance': 69
    },
    1: {
        'id': 1,
        'email': 'john@gmail.com',
        'password': 'bing',
        'fname': 'John',
        'lname': 'Cena',
        'p_number': '5555555555',
        'ssn': '111223333',
        'balance': 200
    }
}

@app.get('/', tags=['root'])
async def root():
    return {"message": "Hello World"}

#curl "localhost:8000/authenticate?email=john@gmail.com&password=bing"
@app.get('/authenticate', tags=['authentication'])
async def get_user_token(email: str, password: str):
    for user in users.values():
        if user['email'] == email and user['password'] == password:
            return { 'user_token': user['id'] }
    return { 'user_token': 0 }

#curl localhost:8000/data?user_token=1
@app.get('/data', tags=['main data'])
async def read_data(user_token: int):
    for user in users.values():
        if user['id'] == user_token:
            return { 'data': user }
    return { 'data': 0 }

#curl -X PUT "localhost:8000/add_balance?user_token=1&amount=10"
@app.put('/add_balance', tags=['add balance'])
async def add_balance(user_token: int, amount: int):
    for user in users.values():
        if user['id'] == user_token:
            print(f'Old: {user["balance"]}')
            user['balance'] += amount
            print(f'New: {user["balance"]}')
    return {"success": True}

#curl -X PUT "localhost:8000/transfer?src=1&dst=0&amount=10"
@app.put('/transfer', tags=['transfer money'])
async def transfer(src: int, dst: int, amount: int):
    for user in users.values():
        if user['id'] == src:
            print(f'Src Old: {user["balance"]}')
            user['balance'] -= amount
            print(f'Src New: {user["balance"]}')
        if user['id'] == dst:
            print(f'Dest Old: {user["balance"]}')
            user['balance'] += amount
            print(f'Dest New: {user["balance"]}')
    return {"success": True}

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
    return {"message": 'You\'ve been \'logged out\''}

if __name__ == '__main__':
    #uvicorn.run('backend.v1:app', host='0.0.0.0', port=8000, reload=True)
    uvicorn.run('v1:app', host='0.0.0.0', port=8000, reload=True)