from fastapi import FastAPI
from typing import List, Union,Optional
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
        name: str
        price: float
        is_offer: Optional[bool] = None

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
        {"name": "Foo", "price": 50.2},
        {"name": "Bar", "price": 62, "is_offer": False},
        {"name": "Baz", "price": 50.2, "is_offer": True},
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
def get_full_name(first_name: str, last_name: str, age: int):
    full_name = first_name.title() + " " + last_name.title()
    name_age = "Hello " + full_name + " you are " + str(age) + " years old"
    return name_age
print(get_full_name("john", "doe", 30))

def describe_item(item: Item):
    return {"item_name": item.name, "item_price": item.price, "item_offer": item.is_offer}
print(describe_item(Item(name="Foo", price=50.2)))

user = User(**external_data)

@app.get("/user/{user_id}")
def get_user(user_id: int):
    if user_id == user.id:
        return user
    return user



# def process_items(items: List[str], items_t: Tuple[int, int, str], items_s: Set[bytes], items_d: Dict[str, str], item_u: Union[int, str]):
#     return {"items": items, "items_t": items_t, "items_s": items_s, "items_d": items_d, "item_u": item_u}
# print(process_items(["a", "b", "c"], (1, 2, "3"), {b"1", b"2", b"3"}, {"a": "b", "c": "d"}, 1))





