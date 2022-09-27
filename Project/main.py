from fastapi import FastAPI
import json

app = FastAPI()

data = json.load(open("Project/db.json"))

@app.get("/")
async def root():
    return data


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
