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
async def root():
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run('backend.v1:app', host='0.0.0.0', port=8000, reload=True)