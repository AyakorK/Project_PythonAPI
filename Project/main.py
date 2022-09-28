from fastapi import FastAPI
import json
from pydantic import BaseModel
import random
import string

app = FastAPI()
data = json.load(open("Project/db.json"))

"""
Definition of every classes used in the API
- User
- Edited User
- Products
- Orders
- Categories
"""


class User(BaseModel):
    password: str
    email: str
    id: int = None
    token: str = None
    money: int = None
    admin: int = None


class CategoriesItem(BaseModel):
    id: int = None
    title: str


class EditedUser(BaseModel):
    password: str = None
    email: str = None


class EditedProduct(BaseModel):
    name: str = None
    price: int = None
    quantity: int = None
    category: int = None


class Order(BaseModel):
    user_id: int
    total_price: int
    id: int
    products: list


class EditCategory(BaseModel):
    title: str = None


@app.get("/")
async def root():
    return data


"""
All functions that will concern the user:
- List all users
- Get details from a user (by ID)
- Get every orders made by a user (by ID)
- Create a user
- Update a user
- Delete a user
"""


@app.get("/users")
async def get_users(token: str = None):
    if token is not None:
        for user in data["users"]:
            if user["token"] == token:
                return user
        return {"error": "Invalid token"}

    return data["users"]
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in data["users"]:
        if user["id"] == user_id:
            return user
    return {"error": "User not found"}

@app.put("/users/{user_id}")
async def update_user(user_id: int, edited_user: EditedUser):
    if any(user["email"] == edited_user.email for user in data["users"]):
        return {"error": "Email already used"}
    for user in data["users"]:
        if user["id"] == user_id:
            user["password"] = edited_user.password or user["password"]
            user["email"] = edited_user.email or user["email"]
            return data["users"]
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


@app.post("/users")
async def create_user(new_user: User):
    new_user.id = data["users"][-1]["id"] + 1
    new_user.token = "".join(random.choices(string.ascii_lowercase + string.digits, k=22))
    new_user.admin = 0  # default to 0
    new_user.money = 3000
    if any(user["email"] == new_user.email for user in data["users"]):
        return {"error": "User already exists"}
    data["users"].append(new_user.dict())
    return data["users"]


@app.get("/users/{user_id}/orders/{order_id}")
async def get_user_order(user_id: int, order_id: int):
    # If the user does not exist
    if not any(user["id"] == user_id for user in data["users"]):
        return {"error": "User not found"}
    # If the order does not exist
    if not any(order["id"] == order_id for order in data["orders"]):
        return {"error": "Order not found"}
    for order in data["orders"]:
        if order["user_id"] == user_id and order["id"] == order_id:
            return order
    return {"error": "This order does not belong to this user"}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    for user in data["users"]:
        if user["id"] == user_id:
            data["users"].remove(user)
            return {"message": "User deleted"}
    return {"error": "User not found"}


"""
All functions that will concern the products:
- List all products
- Get details from a product (by ID)
- Create a product
- Update a product
- Delete a product
"""


@app.get("/products")
async def root():
    if data["products"]:
        return data["products"]
    return {"message": "No products found"}


@app.get("/products/{products_id}")
async def get_products_by_id(products_id: int):
    for products in data["products"]:
        if products["id"] == products_id:
            return products
    return {"error": "Product not found"}


@app.put("/products/{products_id}")
async def update_products(products_id: int, edited_products: EditedProduct):
    for products in data["products"]:
        if products["id"] == products_id:
            products["name"] = edited_products.name or products["name"]
            products["price"] = edited_products.price or products["price"]
            products["quantity"] = edited_products.quantity or products["quantity"]
            products["category"] = edited_products.category or products["category"]
            return products
    return {"error": "Product not found"}


"""
All functions that will concern the orders:
- List all orders
- Get details from an order (by ID)
- Create an order
- Update an order
- Delete an order
"""


@app.get("/orders")
async def get_order():
    return data["orders"]


@app.get("/orders/{order_id}")
async def get_order_by_id(order_id: int):
    for order in data["orders"]:
        if order["id"] == order_id:
            return order


@app.post("/orders")
async def create_order(new_order: Order):
    data["orders"].append(new_order)
    return data["orders"]


"""
All functions that will concern the categories:
- List all categories
- Get details from a category (by ID)
- Create a category
- Update a category
- Delete a category
"""


# List all categories
@app.get("/categories")
async def get_all_categories():
    if data["categories"]:
        return data["categories"]
    return {"message": "No categories found"}


# Get details from a category (by ID)
@app.get("/categories/{category_id}")
async def get_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            return category
    return {"error": str(category_id) + " isn't a valid category id"}


# Create a category
@app.post("/categories")
async def create_categories(item: CategoriesItem):
    item.id = data["categories"][-1]["id"] + 1
    if any(category["title"] == item.title for category in data["categories"]):
        return {"error": "Category already exists"}
    data["categories"].append(item.dict())
    return data["categories"]


# Get products by the category
@app.get("/categories/{category_id}/products")
async def get_products_by_category(category_id: int):
    products = []
    for product in data["products"]:
        if product["category"] == category_id:
            products.append(product)
    return products


# Update a category
@app.put("/categories/{category_id}")
async def update_categories(category_id: int, item: EditCategory):
    if any(category["title"] == item.title for category in data["categories"]):
        return {"error": "Category already exists"}
    for category in data["categories"]:
        if category["id"] == category_id:
            category["title"] = item.title or category["title"]
            return category
    return {"error": "Category not found"}


# Delete a category
@app.delete("/categories/{category_id}")
async def delete_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            data["categories"].remove(category)
            return {"message": "Category deleted"}
    return {"error": "Category not found"}

@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    for product in data["products"]:
        if product["id"] == product_id:
            data["products"].remove(product)
            return {"message": "Product deleted"}
    return {"error": "Product not found"}
