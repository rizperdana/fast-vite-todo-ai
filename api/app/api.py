from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to todo list API!"}


@app.get("/todo", tags=["todos"])
async def get_todos() -> dict:
    todos = [
        {
            "id": 1,
            "item": "Read a book"
        },
        {
            "id": 2,
            "item": "Code project AZ"
        }
    ]
    return { "data": todos }
