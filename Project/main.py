from fastapi import FastAPI
from typing import List, Union ,Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

fake_items_db = [{"id": 1, "item_name": "Foo"}, {"id": 2, "item_name": "Bar"}, {"id": 3, "item_name": "Baz"}, {"id": 4, "item_name": "Qux"}, {"id": 5, "item_name": "Quux"}, {"id": 6, "item_name": "Corge"}, {"id": 7, "item_name": "Grault"}, {"id": 8, "item_name": "Garply"}, {"id": 9, "item_name": "Waldo"}, {"id": 10, "item_name": "Fred"}, {"id": 11, "item_name": "Plugh"}, {"id": 12, "item_name": "Xyzzy"}, {"id": 13, "item_name": "Thud"}]


class Item(BaseModel):
        id: int
        name: str
        price: float
        is_offer: Optional[bool] = None

class Cars(str, Enum):
    Audi = "Audi"
    BMW = "BMW"
    Mercedes = "Mercedes"
    Ferrari = "Ferrari"
    Redbull = "Redbull"

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    id: int
    signup_ts: Union[datetime, None] = None
    items: List[Item] = []

external_data = {
    "username": "johndoe",
    "full_name": "John Doe",
    "id": "123",
    "signup_ts": datetime(2017, 6, 19, 11, 4, 5),
    "items": [
        {"id": 1, "name": "Foo", "price": 50.2},
        {"id": 2, "name": "Bar", "price": 62, "is_offer": False},
        {"id": 3, "name": "Baz", "price": 50.2, "is_offer": True},
    ],
}




@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str, q: str = None):
    return {"message": f"Hello {name} - {q}"}


# Get an optional url saying hi
@app.get("/hi")
async def say_hi(name: Optional[str] = None, q: Optional[str] = None):
    if name is not None and q is not None:
        return(f"Hey {name}! You just said -'{q}'")
    elif name is not None:
        return(f"Hey {name}! You didn't say anything!")
    else:
        return("Hello World")


@app.get("/hello/{first_name}/{last_name}/{age}")
async def get_full_name(first_name: str, last_name: str, age: int):
    full_name = first_name.title() + " " + last_name.title()
    name_age = "Hello " + full_name + " you are " + str(age) + " years old"
    return name_age

def describe_item(item: Item):
    return {"item_name": item.name, "item_price": item.price, "item_offer": item.is_offer}


user = User(**external_data)

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id == user.id:
        return user
    return user

@app.get("/users/{user_id}/items")
def get_user_items(user_id: int):
    if user_id == user.id:
        return user.items
    return user.items

@app.get("/database/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


@app.get("/database/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/models/{model_name}")
async def get_model(model_name: Cars):
    if model_name is Cars.Mercedes:
        return {"model_name": model_name, "message": "Mercedes is the best car"}
    elif model_name.value == "Ferrari":
        return {"model_name": model_name, "message": "Ferrari is the worst car"}
    elif model_name.value == "Redbull":
        return {"model_name": model_name, "message": "Redbull is the best drink but not a car"}
    elif model_name.value == "Audi":
        return {"model_name": model_name, "message": "Audi will be there on 2024"}
    return {"model_name": model_name, "message": "This car is not in F1"}


    return {"model_name": model_name, "message": "Have some residuals"}

# def process_items(items: List[str], items_t: Tuple[int, int, str], items_s: Set[bytes], items_d: Dict[str, int], item_u: Union[int, str]):
#     return {"items": items, "items_t": items_t, "items_s": items_s, "items_d": items_d, "item_u": item_u}
# print(process_items(["a", "b", "c"], (1, 2, "3"), {b"1", b"2", b"3"}, {"a": "b", "b": 3}, 1))





