from fastapi import FastAPI
import json

app = FastAPI()
data = json.load(open("Project/db.json"))

@app.get("/")
async def root():
    return data

@app.get("/{products}")
async def root():
    return data["products"]

@app.get("/product/{products_id}")
async def get_products_by_id(products_id:int):
    for products in data["products"]:
        if products["id"] == products_id:
            return products


