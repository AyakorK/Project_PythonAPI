from fastapi import FastAPI
import json

app = FastAPI()

data = json.load(open("Project/db.json"))

@app.get("/")
async def root():
    return data

@app.get("/users")
async def get_users():
    if data["users"]:
        return data["users"]
    return {"message": "No users found"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in data["users"]:
        if user["id"] == user_id:
            return user
    return {"error": "User not found"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
