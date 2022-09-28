from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
import random
import string

app = FastAPI()
data = json.load(open("Project/db.json"))


def write_db():
    with open("Project/db.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True, separators=(",", ": "))


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


class Product(BaseModel):
    name: str
    price: int
    id: int = None
    category: int
    quantity: int


class EditedProduct(BaseModel):
    name: str = None
    price: int = None
    quantity: int = None
    category: int = None


class Order(BaseModel):
    user_id: int
    total_price: int
    id: int = None
    products: list


class EditedOrder(BaseModel):
    user_id: int = None
    total_price: int = None
    products: list = None


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
async def get_users(token: str = None, sort: str = None):
    if token is not None:
        for user in data["users"]:
            if user["token"] == token:
                return user
        raise HTTPException(status_code=404, detail="Error: Token not found")

    if sort is not None:
        if sort == "email":
            return sorted(data["users"], key=lambda k: k["email"].lower())
        elif sort == "money":
            return sorted(data["users"], key=lambda k: k["money"])
        elif sort == "email_desc":
            return sorted(data["users"], key=lambda k: k["email"].lower(), reverse=True)
        elif sort == "money_desc":
            return sorted(data["users"], key=lambda k: k["money"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    return data["users"]


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in data["users"]:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Error: User not found")


@app.put("/users/{user_id}")
async def update_user(user_id: int, edited_user: EditedUser):
    if any(user["email"] == edited_user.email for user in data["users"]):
        return {"error": "Error: Email already used"}
    for user in data["users"]:
        if user["id"] == user_id:
            user["password"] = edited_user.password or user["password"]
            user["email"] = edited_user.email or user["email"]
            write_db()
            return data["users"]
    raise HTTPException(status_code=404, detail="Error: User not found")


@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    # If the user does not exist
    if not any(user["id"] == user_id for user in data["users"]):
        raise HTTPException(status_code=404, detail="Error: User not found")
    for order in data["orders"]:
        if order["user_id"] == user_id:
            return order
    raise HTTPException(status_code=404, detail="Error: This user has no active orders")


@app.post("/users")
async def create_user(new_user: User):
    new_user.id = data["users"][-1]["id"] + 1
    new_user.token = "".join(random.choices(string.ascii_lowercase + string.digits, k=22))
    new_user.admin = 0  # default to 0
    new_user.money = 3000
    if any(user["email"] == new_user.email for user in data["users"]):
        raise HTTPException(status_code=400, detail="Error: Email already used")
    data["users"].append(new_user.dict())
    write_db()
    return data["users"]


@app.get("/users/{user_id}/orders/{order_id}")
async def get_user_order(user_id: int, order_id: int):
    # If the user does not exist
    if not any(user["id"] == user_id for user in data["users"]):
        raise HTTPException(status_code=404, detail="Error: User not found")
    # If the order does not exist
    if not any(order["id"] == order_id for order in data["orders"]):
        raise HTTPException(status_code=404, detail="Error: Order not found")
    for order in data["orders"]:
        if order["user_id"] == user_id and order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Error: This order does not belong to a user")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    for user in data["users"]:
        if user["id"] == user_id:
            data["users"].remove(user)
            write_db()
            raise HTTPException(status_code=200, detail="User deleted")
    raise HTTPException(status_code=404, detail="Error: User not found")


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
    raise HTTPException(status_code=404, detail="Error: No products found")


@app.get("/products/{products_id}")
async def get_products_by_id(products_id: int):
    for products in data["products"]:
        if products["id"] == products_id:
            return products
    # Return code error 404 if the product is not found
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products")
async def create_product(new_product: Product):
    new_product.id = data["products"][-1]["id"] + 1
    if any(product["name"] == new_product.name for product in data["products"]):
        raise HTTPException(status_code=400, detail="Error: Product already exists")
    data["products"].append(new_product.dict())
    return data["products"]


@app.put("/products/{products_id}")
async def update_products(products_id: int, edited_products: EditedProduct):
    for products in data["products"]:
        if products["id"] == products_id:
            products["name"] = edited_products.name or products["name"]
            products["price"] = edited_products.price or products["price"]
            products["quantity"] = edited_products.quantity or products["quantity"]
            products["category"] = edited_products.category or products["category"]
            write_db()
            return products
    raise HTTPException(status_code=404, detail="Error: Product not found")


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
    raise HTTPException(status_code=404, detail="Error: Order not found")


@app.get("/orders/{order_id}/products")
async def get_products_in_order(order_id: int):
    for order in data["orders"]:
        if order["id"] == order_id:
            return order["products"]
    raise HTTPException(status_code=404, detail="Error: Order not found")


@app.post("/orders")
async def create_order(new_order: Order):
    new_order.id = data["orders"][-1]["id"] + 1
    data["orders"].append(new_order)
    write_db()
    return data["orders"]


@app.put("/orders/{order_id}")
async def update_order(order_id: int, edited_order: EditedOrder):
    for order in data["orders"]:
        if order["id"] == order_id:
            order["user_id"] = edited_order.user_id or order["user_id"]
            order["total_price"] = edited_order.total_price or order["total_price"]
            order["products"] = edited_order.products or order["products"]
            return data["orders"]
    raise HTTPException(status_code=404, detail="Error: Order not found")


@app.put("/orders/{order_id}/products")
async def add_product_in_order(order_id: int, product: Product):
    for order in data["orders"]:
        if any(products["id"] == product.id for products in order["products"]):
            raise HTTPException(status_code=400, detail="Error: Product not found")
        if order["id"] == order_id:
            order["product"] = order["products"].append(product)
            return data["orders"]
    raise HTTPException(status_code=404, detail="Error: Order not found")


@app.put("/orders/{order_id}/products/{product_id}")
async def delete_product_in_order(order_id: int, product_id: int):
    for order in data["orders"]:
        if order["id"] == order_id:
            for product in order["products"]:
                if product["id"] == product_id:
                    order["products"].remove(product)
                    return order["products"]
        raise HTTPException(status_code=404, detail="Error: Product not found")
    raise HTTPException(status_code=404, detail="Error: Order not found")


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    for order in data["orders"]:
        if order["id"] == order_id:
            data["orders"].remove(order)
            write_db()
            raise HTTPException(status_code=200, detail="Order deleted")
    raise HTTPException(status_code=404, detail="Error: Order not found")


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
    raise HTTPException(status_code=404, detail="Error: No categories found")


# Get details from a category (by ID)
@app.get("/categories/{category_id}")
async def get_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            return category
    raise HTTPException(status_code=404, detail="Error: Category not found")


# Create a category
@app.post("/categories")
async def create_categories(item: CategoriesItem):
    item.id = data["categories"][-1]["id"] + 1
    if any(category["title"] == item.title for category in data["categories"]):
        raise HTTPException(status_code=400, detail="Error: Category already exists")
    data["categories"].append(item.dict())
    write_db()
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
        raise HTTPException(status_code=400, detail="Error: Category already exists")
    for category in data["categories"]:
        if category["id"] == category_id:
            category["title"] = item.title or category["title"]
            write_db()
            return category
    raise HTTPException(status_code=404, detail="Error: Category not found")


# Delete a category
@app.delete("/categories/{category_id}")
async def delete_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            data["categories"].remove(category)
            write_db()
            raise HTTPException(status_code=200, detail="Category deleted")
    raise HTTPException(status_code=404, detail="Error: Category not found")


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    for product in data["products"]:
        if product["id"] == product_id:
            data["products"].remove(product)
            write_db()
            raise HTTPException(status_code=200, detail="Product deleted")
    raise HTTPException(status_code=404, detail="Error: Product not found")
