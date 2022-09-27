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


@app.get("/categories")
async def get_allCategories():
    return data["categories"]


@app.get("/categories/{category_id}")
async def get_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            return category
    return {"error": "ID not found"}