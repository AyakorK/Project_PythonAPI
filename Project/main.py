from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel
import random
import string
import pymysql

pymysql.install_as_MySQLdb()

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

app = FastAPI()

DATABASE_URL = "mysql+pymysql://root:root@10.10.20.100/LaCroste"

engine = create_engine(DATABASE_URL)


app = FastAPI()

# Create seeds for the database
@app.on_event("startup")
def create_seeds():
    # If db is empty, create some seeds
    session = Session(engine)
    # If db is empty, create some tables (orders and products and users and categories)
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            money VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        );
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        );
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            price FLOAT NOT NULL,
            category_id INT NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
        """
    )
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INT NOT NULL AUTO_INCREMENT,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        """
    )
    session.commit()
    if session.execute("SELECT * FROM orders").fetchone() is None:
        session.execute(
            "INSERT INTO orders (id, products, total_price, user_id) VALUES ('1', '[{\"id\": \"1\", \"name\": \"Pizza\", \"price\": 10}, {\"id\": \"2\", \"name\": \"Pasta\", \"price\": 8}]', '300', 1)",
            "INSERT INTO orders (id, products, total_price, user_id) VALUES ('2', '[{\"id\": \"3\", \"name\": \"Salad\", \"price\": 5}, {\"id\": \"4\", \"name\": \"Cake\", \"price\": 7}]', '300', 1)",
            "INSERT INTO orders (id, products, total_price, user_id) VALUES ('3', '[{\"id\": \"5\", \"name\": \"Ice cream\", \"price\": 4}, {\"id\": \"6\", \"name\": \"Coke\", \"price\": 2}]', '300', 1)",
            "INSERT INTO orders (id, products, total_price, user_id) VALUES ('4', '[{\"id\": \"7\", \"name\": \"Burger\", \"price\": 9}, {\"id\": \"8\", \"name\": \"Fries\", \"price\": 3}]', '300', 1)",
        )
        session.commit()
    if session.execute("SELECT * FROM products").fetchone() is None:
        session.execute(
            "INSERT INTO products (id, name, category, price) VALUES ('1', 'Pizza', 1, 10)",
            "INSERT INTO products (id, name, category, price) VALUES ('2', 'Pasta', 1, 8)",
            "INSERT INTO products (id, name, category, price) VALUES ('3', 'Salad', 1, 5)",
            "INSERT INTO products (id, name, category, price) VALUES ('4', 'Cake', 2, 7)",
            "INSERT INTO products (id, name, category, price) VALUES ('5', 'Ice cream', 2, 4)",
            "INSERT INTO products (id, name, category, price) VALUES ('6', 'Coke', 3, 2)",
            "INSERT INTO products (id, name, category, price) VALUES ('7', 'Burger', 1, 9)",
            "INSERT INTO products (id, name, category, price) VALUES ('8', 'Fries', 1, 3)",
        )
        session.commit()
    if session.execute("SELECT * FROM users").fetchone() is None:
        session.execute(
            "INSERT INTO users (id, email, password, admin, money) VALUES ('1', 'coucou@coucou.fr', 'Password1', 0, 30000')",
            "INSERT INTO users (id, email, password, admin, money) VALUES ('2', 'admin@admin.fr')", 'PasswordAdmin', '1', '3000000')",
        )
        session.commit()
    if session.execute("SELECT * FROM categories").fetchone() is None:
        session.execute(
            "INSERT INTO categories (id, name) VALUES ('1', 'Salted')",
            "INSERT INTO categories (id, name) VALUES ('2', 'Sweet')",
            "INSERT INTO categories (id, name) VALUES ('3', 'Drinks')",
        )
        session.commit()



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
    return {"message": "Welcome to the API of Lacroste"}


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


# List all users and permit it to be sorted by ID, email or money
@app.get("/users")
async def get_users(token: str = None, sort: str = None):
    session = Session(engine)
    users = session.execute("SELECT * FROM users").fetchAll()
    if token is not None:
        for user in users:
            if user["token"] == token:
                return user
        raise HTTPException(status_code=404, detail="Error: Token not found")

    if sort is not None:
        if sort == "email":
            return sorted(users, key=lambda k: k["email"].lower())
        elif sort == "money":
            return sorted(users, key=lambda k: k["money"])
        elif sort == "email_desc":
            return sorted(users, key=lambda k: k["email"].lower(), reverse=True)
        elif sort == "money_desc":
            return sorted(users, key=lambda k: k["money"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif users:
        return users
    raise HTTPException(status_code=404, detail="Error: No users found")


# Get details from a user by ID
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    session = Session(engine)
    users = session.execute("SELECT * FROM users").fetchAll()
    for user in users:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="Error: User not found")


# Get every order made by a specific user
@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    users = session.execute("SELECT * FROM users").fetchAll()
    # If the user does not exist
    if not any(user["id"] == user_id for user in users):
        raise HTTPException(status_code=404, detail="Error: User not found")
    for order in orders:
        if order["user_id"] == user_id:
            return order
    raise HTTPException(status_code=404, detail="Error: This user has no active orders")


# Get a specific order made by a specific user
@app.get("/users/{user_id}/orders/{order_id}")
async def get_user_order(user_id: int, order_id: int):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    users = session.execute("SELECT * FROM users").fetchAll()
    # If the user does not exist
    if not any(user["id"] == user_id for user in users):
        raise HTTPException(status_code=404, detail="Error: User not found")
    # If the order does not exist
    if not any(order["id"] == order_id for order in orders):
        raise HTTPException(status_code=404, detail="Error: Order not found")
    for order in orders:
        if order["user_id"] == user_id and order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Error: This order does not belong to a user")


# Create a user, add and ID and randomly generate a token
@app.post("/users")
async def create_user(new_user: User):
    session = Session(engine)
    users = session.execute("SELECT * FROM users").fetchAll()
    new_user.id = users.last()["id"] + 1
    new_user.token = "".join(random.choices(string.ascii_lowercase + string.digits, k=22))
    new_user.admin = 0  # default to 0
    new_user.money = 3000
    if any(user["email"] == new_user.email for user in users):
        raise HTTPException(status_code=400, detail="Error: Email already used")
    session.execute(
        "INSERT INTO users (id, email, password, token, money, admin) VALUES (:id, :email, :password, :token, :money, :admin)",
        new_user.dict()
    )
    session.commit()
    return new_user


# Update a user
@app.patch("/users/{user_id}")
async def update_user(user_id: int, edited_user: EditedUser):
    session = Session(engine)
    users = session.execute("SELECT * FROM users").fetchAll()
    if any(user["email"] == edited_user.email for user in users):
        return {"error": "Error: Email already used"}
    for user in users:
        if user["id"] == user_id:
            user["password"] = edited_user.password or user["password"]
            user["email"] = edited_user.email or user["email"]

            session.execute(
                "UPDATE users SET email = :email, password = :password WHERE id = :id",
                user
            )
            session.commit()
            return user
    raise HTTPException(status_code=404, detail="Error: User not found")


# Delete an user
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    session = Session(engine)
    users = session.execute("SELECT * FROM users").fetchAll()
    for user in users:
        if user["id"] == user_id:
            session.execute("DELETE FROM users WHERE id = :id", user)
            session.commit()
            return {"message": "User deleted"}
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


# List all products and permit it to be sorted by ID, name, price or quantity
@app.get("/products")
async def root(sort: str = None):
    session = Session(engine)
    products = session.execute("SELECT * FROM products").fetchAll()
    if sort is not None:
        if sort == "name":
            return sorted(products, key=lambda k: k["name"].lower())
        elif sort == "price":
            return sorted(products, key=lambda k: k["price"])
        elif sort == "category":
            return sorted(products, key=lambda k: k["category"])
        elif sort == "quantity":
            return sorted(products, key=lambda k: k["quantity"])
        elif sort == "name_desc":
            return sorted(products, key=lambda k: k["name"].lower(), reverse=True)
        elif sort == "price_desc":
            return sorted(products, key=lambda k: k["price"], reverse=True)
        elif sort == "category_desc":
            return sorted(products, key=lambda k: k["category"], reverse=True)
        elif sort == "quantity_desc":
            return sorted(products, key=lambda k: k["quantity"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif products:
        return products
    raise HTTPException(status_code=404, detail="Error: No products found")


# Get details from a product thanks to his ID
@app.get("/products/{products_id}")
async def get_products_by_id(products_id: int):
    session = Session(engine)
    products = session.execute("SELECT * FROM products").fetchAll()
    for product in products:
        if product["id"] == products_id:
            return product
    # Return code error 404 if the product is not found
    raise HTTPException(status_code=404, detail="Product not found")


# Create a product, add and ID
@app.post("/products")
async def create_product(new_product: Product):
    session = Session(engine)
    products = session.execute("SELECT * FROM products").fetchAll()
    new_product.id = products.last()["id"] + 1
    if any(product["name"] == new_product.name for product in products):
        raise HTTPException(status_code=400, detail="Error: Product already exists")
    session.execute(
        "INSERT INTO products (id, name, price, category, quantity) VALUES (:id, :name, :price, :category, :quantity)",
        new_product.dict()
    )
    session.commit()
    return new_product

# Update a product
@app.patch("/products/{products_id}")
async def update_products(products_id: int, edited_products: EditedProduct):
    session = Session(engine)
    products = session.execute("SELECT * FROM products").fetchAll()
    for product in products:
        if product["id"] == products_id:
            product["name"] = edited_products.name or products["name"]
            product["price"] = edited_products.price or products["price"]
            product["quantity"] = edited_products.quantity or products["quantity"]
            product["category"] = edited_products.category or products["category"]
            session.execute(
                "UPDATE products SET name = :name, price = :price, quantity = :quantity, category = :category WHERE id = :id",
                product
            )
            session.commit()
            return products
    raise HTTPException(status_code=404, detail="Error: Product not found")


# Delete a product
@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    session = Session(engine)
    products = session.execute("SELECT * FROM products").fetchAll()
    for product in products:
        if product["id"] == product_id:
            session.execute("DELETE FROM products WHERE id = :id", product)
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
    root: /orders/{order_id}/products (PATCH)
- Delete only one product of an order
    root: /orders/{order_id}/products/{product_id} (DELETE)
- Delete an order
    root: /orders/{order_id} (DELETE)
"""


# list all orders and permit it to be sorted by ID, user ID, date or total
@app.get("/orders")
async def get_order(sort: str = None):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    if sort is not None:
        if sort == "user":
            return sorted(orders, key=lambda k: k["user_id"])
        elif sort == "total":
            return sorted(orders, key=lambda k: k["total_price"])
        elif sort == "user_desc":
            return sorted(orders, key=lambda k: k["user_id"], reverse=True)
        elif sort == "total_desc":
            return sorted(orders, key=lambda k: k["total_price"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif orders:
        return orders
    raise HTTPException(status_code=404, detail="Error: No orders found")


# Get details from an order thanks to his ID
@app.get("/orders/{order_id}")
async def get_order_by_id(order_id: int):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    for order in orders:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Error: Order not found")


# Get products of an order thanks to his ID
@app.get("/orders/{order_id}/products")
async def get_products_in_order(order_id: int):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    if not any(order["id"] == order_id for order in orders):
        raise HTTPException(status_code=404, detail="Error: Order not found")
    for order in orders:
        if order["id"] == order_id:
            return order["products"]
    raise HTTPException(status_code=404, detail="Error: Products not found")


# Create an order, add and ID
@app.post("/orders")
async def create_order(new_order: Order):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    new_order.id = orders.last()["id"] + 1
    session.execute(
        "INSERT INTO orders (id, user_id, total_price, products) VALUES (:id, :user_id, :total_price, :products)",
        new_order.dict()
    )
    session.commit()
    return new_order



# Update an order thanks to its id
@app.patch("/orders/{order_id}")
async def update_order(order_id: int, edited_order: EditedOrder):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    for order in orders:
        if order["id"] == order_id:
            order["user_id"] = edited_order.user_id or order["user_id"]
            order["total_price"] = edited_order.total_price or order["total_price"]
            order["products"] = edited_order.products or order["products"]
            session.execute(
                "UPDATE orders SET user_id = :user_id, total_price = :total_price, products = :products WHERE id = :id",
                order
            )
            session.commit()
            return order
    raise HTTPException(status_code=404, detail="Error: Order not found")


# Update products of an order
@app.put("/orders/{order_id}/products")
async def add_product_in_order(order_id: int, product: Product):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    for order in orders:
        if any(products["id"] == product.id for products in order["products"]):
            raise HTTPException(status_code=400, detail="Error: Product already exists")
        if order["id"] == order_id:
            order["products"].append(product.dict())
            session.execute(
                "UPDATE orders SET products = :products WHERE id = :id",
                order
            )
            session.commit()
            return order
    raise HTTPException(status_code=404, detail="Error: Order not found")


# Update only one product of an order
@app.delete("/orders/{order_id}/products/{product_id}")
async def delete_product_in_order(order_id: int, product_id: int):
    session = Session(engine)
    orders = session.execute("SELECT * FROM orders").fetchAll()
    for order in orders:
        if order["id"] == order_id:
            select_product_and_delete_it(order, product_id)
            return order["products"]
    raise HTTPException(status_code=404, detail="Error: Order not found")


def select_product_and_delete_it(order, product_id):
    for product in order["products"]:
        if product["id"] == product_id:
            session.execute(
                "UPDATE orders SET products = :products WHERE id = :id",
                order
            )
            session.commit()
            order["products"].remove(product)
            return order
    raise HTTPException(status_code=404, detail="Error: Product not found")


# Delete an order
@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    session = Session(engine)
    for order in orders:
        if order["id"] == order_id:
            session.execute(
                "DELETE FROM orders WHERE id = :id",
                order
            )
            session.commit()
            return order
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
    session = Session(engine)
    categories = session.execute("SELECT * FROM categories").fetchAll()
    if sort is not None:
        if sort == "title":
            return sorted(categories, key=lambda k: k["title"])
        elif sort == "title_desc":
            return sorted(categories, key=lambda k: k["title"], reverse=True)
        raise HTTPException(status_code=400, detail="Error: Invalid sort parameter")
    elif categories:
        return categories
    raise HTTPException(status_code=404, detail="Error: No categories found")


# Get details from a category (by ID)
@app.get("/categories/{category_id}")
async def get_categories(category_id: int):
    session = Session(engine)
    categories = session.execute("SELECT * FROM categories").fetchAll()
    for category in categories:
        if category["id"] == category_id:
            return category
    raise HTTPException(status_code=404, detail="Error: Category not found")


# Get products by the category ID
@app.get("/categories/{category_id}/products")
async def get_products_by_category(category_id: int):
    session = Session(engine)
    categories = session.execute("SELECT * FROM categories").fetchAll()
    products = session.execute("SELECT * FROM products").fetchAll()
    for category in categories:
        if category["id"] == category_id:
            return [product for product in products if product["category_id"] == category_id]
    raise HTTPException(status_code=404, detail="Error: Category not found")


# Create a category
@app.post("/categories")
async def create_categories(item: Category):
    session = Session(engine)
    categories = session.execute("SELECT * FROM categories").fetchAll()
    item.id = categories.last()["id"] + 1
    if any(category["title"] == item.title for category in categories):
        raise HTTPException(status_code=400, detail="Error: Category already exists")
    session.execute(
        "INSERT INTO categories (id, title) VALUES (:id, :title)",
        item.dict()
    )
    session.commit()
    return item


# Update a category
@app.patch("/categories/{category_id}")
async def update_categories(category_id: int, item: EditCategory):
    session = Session(engine)
    categories = session.execute("SELECT * FROM categories").fetchAll()
    if any(category["title"] == item.title for category in categories):
        raise HTTPException(status_code=400, detail="Error: Category already exists")
    for category in categories:
        if category["id"] == category_id:
            category["title"] = item.title or category["title"]
            session.execute(
                "UPDATE categories SET title = :title WHERE id = :id",
                category
            )
            session.commit()
            return category
    raise HTTPException(status_code=404, detail="Error: Category not found")


# Delete a category
@app.delete("/categories/{category_id}")
async def delete_categories(category_id: int):
    for category in categories:
        if category["id"] == category_id:
            session.execute(
                "DELETE FROM categories WHERE id = :id",
                category
            )
            session.commit()
            raise HTTPException(status_code=200, detail="Category deleted")
    raise HTTPException(status_code=404, detail="Error: Category not found")
