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
    params: password, email, money, admin, token, id
- Edited User
    params: password, email
- Products
    params: name, price, category, quantity, id
- Edited Products
    params: name, price, category, quantity
- Orders
    params: products, total_price, id, user_id
- Edited Orders
    params: products, total_price
- Categories
    params: name, id
- Edited Categories
    params: name
"""

# Create a class for the user
class User(BaseModel):
    password: str
    email: str
    id: int = None
    token: str = None
    money: int = None
    admin: int = None

# Create a class to edit the user
class EditedUser(BaseModel):
    password: str = None
    email: str = None

# Create a class for the products
class Product(BaseModel):
    name: str
    price: int
    id: int = None
    category: int
    quantity: int

# Create a class to edit the products
class EditedProduct(BaseModel):
    name: str = None
    price: int = None
    quantity: int = None
    category: int = None

# Create a class for the orders
class Order(BaseModel):
    user_id: int
    total_price: int
    id: int = None
    products: list

# Create a class to edit the orders
class EditedOrder(BaseModel):
    user_id: int = None
    total_price: int = None
    products: list = None

# Create a class for the categories of the products
class Category(BaseModel):
    id: int = None
    title: str

# Create a class to edit the categories
class EditCategory(BaseModel):
    title: str = None

# This is the base route of the api that return all the data
@app.get("/")
async def root():
    return data


"""
All functions that will concern the user:
- List all users and permit it to be sorted
    root: /products (GET)
    params: sort (str), token (str)
- Get details from a user (by ID)
    root: /products/{id} (GET)
- Get every orders made by a user (by ID)
    root: /products/{id}/orders (GET)
- Get one order made by a user (by ID)
    root: /products/{id}/orders/{order_id} (GET)
- Create a user
    root: /products (POST)
- Update a user
    root: /products/{id} (PATCH)
- Delete a user
    root: /products/{id} (DELETE)
"""

# list all users and permit it to be sorted by ID, email or money
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
    elif data["users"]:
        return data["users"]
    raise HTTPException(status_code=404, detail="Error: No users found")


# get details from a user by ID
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in data["users"]:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Error: User not found")


# get every order made by a specific user
@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    # If the user does not exist
    if not any(user["id"] == user_id for user in data["users"]):
        raise HTTPException(status_code=404, detail="Error: User not found")
    for order in data["orders"]:
        if order["user_id"] == user_id:
            return order
    raise HTTPException(status_code=404, detail="Error: This user has no active orders")


# get a specific order made by a specific user
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


# create a user, add and ID and randomly generate a token
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


# update a user
@app.patch("/users/{user_id}")
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


# delete a user
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
    root: /products (GET)
- Get details from a product (by ID)
    root: /products/{product_id} (GET)
    params: token (str)
- Create a product
    root: /products (POST)
- Update a product
    root: /products/{product_id} (PATCH)
- Delete a product
    root: /products/{product_id} (DELETE)
"""


# list all products and permit it to be sorted by ID, name, price or quantity
@app.get("/products")
async def root(sort: str = None):
    if sort is not None:
        if sort == "name":
            return sorted(data["products"], key=lambda k: k["name"].lower())
        elif sort == "price":
            return sorted(data["products"], key=lambda k: k["price"])
        elif sort == "category":
            return sorted(data["products"], key=lambda k: k["category"])
        elif sort == "quantity":
            return sorted(data["products"], key=lambda k: k["quantity"])
        elif sort == "name_desc":
            return sorted(data["products"], key=lambda k: k["name"].lower(), reverse=True)
        elif sort == "price_desc":
            return sorted(data["products"], key=lambda k: k["price"], reverse=True)
        elif sort == "category_desc":
            return sorted(data["products"], key=lambda k: k["category"], reverse=True)
        elif sort == "quantity_desc":
            return sorted(data["products"], key=lambda k: k["quantity"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif data["products"]:
        return data["products"]
    raise HTTPException(status_code=404, detail="Error: No products found")


# get details from a product thanks to his ID
@app.get("/products/{products_id}")
async def get_products_by_id(products_id: int):
    for products in data["products"]:
        if products["id"] == products_id:
            return products
    # Return code error 404 if the product is not found
    raise HTTPException(status_code=404, detail="Product not found")


# create a product, add and ID
@app.post("/products")
async def create_product(new_product: Product):
    new_product.id = data["products"][-1]["id"] + 1
    if any(product["name"] == new_product.name for product in data["products"]):
        raise HTTPException(status_code=400, detail="Error: Product already exists")
    data["products"].append(new_product.dict())
    return data["products"]


# update a product
@app.patch("/products/{products_id}")
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


# delete a product
@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    for product in data["products"]:
        if product["id"] == product_id:
            data["products"].remove(product)
            write_db()
            raise HTTPException(status_code=200, detail="Product deleted")
    raise HTTPException(status_code=404, detail="Error: Product not found")


"""
All functions that will concern the orders:
- List all orders
    root: /orders (GET)
    params: sort (str)
- Get details from an order (by ID)
    root: /orders/{order_id} (GET)
- Get products of an order (by ID)
    root: /orders/{order_id}/products (GET)
- Create an order
    root: /orders (POST)
- Update an order
    root: /orders/{order_id} (PATCH)
- Update products of an order
    root: /orders/{order_id}/products (PUT)
- Delete only one product of an order
    root: /orders/{order_id}/products/{product_id} (DELETE)
- Delete an order
    root: /orders/{order_id} (DELETE)
"""


# list all orders and permit it to be sorted by ID, user ID, date or total
@app.get("/orders")
async def get_order(sort: str = None):
    if sort is not None:
        if sort == "user":
            return sorted(data["orders"], key=lambda k: k["user_id"])
        elif sort == "total":
            return sorted(data["orders"], key=lambda k: k["total_price"])
        elif sort == "user_desc":
            return sorted(data["orders"], key=lambda k: k["user_id"], reverse=True)
        elif sort == "total_desc":
            return sorted(data["orders"], key=lambda k: k["total_price"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif data["orders"]:
        return data["orders"]
    raise HTTPException(status_code=404, detail="Error: No orders found")


# get details from an order thanks to his ID
@app.get("/orders/{order_id}")
async def get_order_by_id(order_id: int):
    for order in data["orders"]:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Error: Order not found")


# get products of an order thanks to his ID
@app.get("/orders/{order_id}/products")
async def get_products_in_order(order_id: int):
    if not any(order["id"] == order_id for order in data["orders"]):
        raise HTTPException(status_code=404, detail="Error: Order not found")
    for order in data["orders"]:
        if order["id"] == order_id:
            return order["products"]
    raise HTTPException(status_code=404, detail="Error: Products not found")


# create an order, add and ID
@app.post("/orders")
async def create_order(new_order: Order):
    new_order.id = data["orders"][-1]["id"] + 1
    data["orders"].append(new_order)
    write_db()
    return data["orders"]


# Update an order thanks to its id
@app.patch("/orders/{order_id}")
async def update_order(order_id: int, edited_order: EditedOrder):
    for order in data["orders"]:
        if order["id"] == order_id:
            order["user_id"] = edited_order.user_id or order["user_id"]
            order["total_price"] = edited_order.total_price or order["total_price"]
            order["products"] = edited_order.products or order["products"]
            return data["orders"]
    raise HTTPException(status_code=404, detail="Error: Order not found")


# Update products of an order
@app.put("/orders/{order_id}/products")
async def add_product_in_order(order_id: int, product: Product):
    for order in data["orders"]:
        if any(products["id"] == product.id for products in order["products"]):
            raise HTTPException(status_code=404, detail="Error: Product not found")
        if order["id"] == order_id:
            order["product"] = order["products"].append(product)
            return data["orders"]
    raise HTTPException(status_code=404, detail="Error: Order not found")


# Delete only one product of an order
@app.delete("/orders/{order_id}/products/{product_id}")
async def delete_product_in_order(order_id: int, product_id: int):
    for order in data["orders"]:
        if order["id"] == order_id:
            select_product_and_delete_it(order, product_id)
            return order["products"]
        raise HTTPException(status_code=404, detail="Error: Product not found")
    raise HTTPException(status_code=404, detail="Error: Order not found")
def select_product_and_delete_it(order, product_id):
    for product in order["products"]:
        if product["id"] == product_id:
            order["products"].remove(product)



# Delete an order
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
    root: /categories (GET)
- Get details from a category (by ID)
    root: /categories/{category_id} (GET)
- Get products of a category (by ID)
    root: /categories/{category_id}/products (GET)
- Create a category
    root: /categories (POST)
- Update a category
    root: /categories/{category_id} (PATCH)
- Delete a category
    root: /categories/{category_id} (DELETE)
"""


# List all categories
@app.get("/categories")
async def get_all_categories(sort: str = None):
    if sort is not None:
        if sort == "title":
            return sorted(data["categories"], key=lambda k: k["title"])
        elif sort == "title_desc":
            return sorted(data["categories"], key=lambda k: k["title"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif data["categories"]:
        return data["categories"]
    raise HTTPException(status_code=404, detail="Error: No categories found")


# Get details from a category (by ID)
@app.get("/categories/{category_id}")
async def get_categories(category_id: int):
    for category in data["categories"]:
        if category["id"] == category_id:
            return category
    raise HTTPException(status_code=404, detail="Error: Category not found")


# Get products by the category ID
@app.get("/categories/{category_id}/products")
async def get_products_by_category(category_id: int):
    products = []
    for product in data["products"]:
        if product["category"] == category_id:
            products.append(product)
    return products


# Create a category
@app.post("/categories")
async def create_categories(item: Category):
    item.id = data["categories"][-1]["id"] + 1
    if any(category["title"] == item.title for category in data["categories"]):
        raise HTTPException(status_code=400, detail="Error: Category already exists")
    data["categories"].append(item.dict())
    write_db()
    return data["categories"]


# Update a category
@app.patch("/categories/{category_id}")
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
