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


@app.get('/', tags=['root'])
async def read_root():
    return {"message": "Hello World"}


@app.get('/authenticate', tags=['authentication'])
async def get_user_token(email: str, password: str):
    return {
        'user_token': 0
    }


@app.get('/data', tags=['main data'])
async def read_data(user_token: int):
    return {
        'email': 'jonahshader@oakland.edu',
        'fname': 'Jonah',
        'lname': 'Shader',
        'money': 10000
    }


@app.put('/add-balance', tags=['add balance'])
async def add_balance(amount: int):
    return {"success": True}


@app.put('/transfer', tags=['transfer money'])
async def transfer(user_token: int, other_username: str, amount: int):
    return {"success": True}


@app.post('/create-account', tags=['create account'])
async def create_account(email: str, password: str, fname: str, lname: str, p_number: str):
    return {"success": True}


@app.put('/logout', tags=['logout'])
async def logout(user_token: int):
    return {"success": True}


if __name__ == '__main__':
    uvicorn.run('backend.temp:app', host='0.0.0.0', port=8000, reload=True)
