from fastapi import FastAPI
import json
from pydantic import BaseModel

app = FastAPI()

data = json.load(open("Project/db.json"))


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
class Order(BaseModel):
    user_id: int
    total_price: int
    id:int
    products: list
@app.post("/orders")
async def create_order(new_order : Order):
    data["orders"].append(new_order)
    return data["orders"]

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

@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    # If the user does not exist
    if not any(user["id"] == user_id for user in data["users"]):
        return {"error": "User not found"}
    for order in data["orders"]:
        if order["user_id"] == user_id:
            return order
    return {"error": "This user has no active orders"}

@app.get("/categories")
async def get_allCategories():
    if data["categories"]:
        return data["categories"]
    return {"message": "No categories found"}


@app.get("/categories/{category_id}")
async def get_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            return category
    return {"error": str(category_id) + " isn't a valid category id"}

