from fastapi import FastAPI
import json

app = FastAPI()

data = json.load(open("/Users/coding/Documents/GitHub/Project_PythonAPI/Project/db.json"))

@app.get("/")
async def root():
    return data

@app.get("/orders")
async def get_order():
    return data["orders"]

@app.get("/orders/{order_id}")
async def get_order_by_id(order_id: int):
    for order in data["orders"] :
        if order["id"] == order_id :
            return order

