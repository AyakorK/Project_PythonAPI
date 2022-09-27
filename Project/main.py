from fastapi import FastAPI
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item( user_id: int, item_id: str, q: str | None = None, short: bool = False ):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("users/me")
async def read_user_me():
    return{"user_id":"the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id:str):
    return {"user_id": user_id}

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

@app.get("/users")
async def read_users2():
    return ["Bean", "Elfo"]

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet :
        return {"model_name":model_name,"message":"Deep Learning FTW!"}
    if model_name.value == "lenet" :
        return {"model_name":model_name,"message":"LeCNN all the images"}
    return{"model_name":model_name,"message":"Have some residuals"}
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

def get_full_name(first_name:str,last_name:str):
    full_name = first_name.title() + " " + last_name.title()
    return full_name
def get_name_with_age(name:str,age:int):
    name_with_age = name + " is this old " + str(age)
    return name_with_age
def process_items1(items : list[str]):
    for item in items:
        print(item)
def process_items2(items_t : tuple[int,int,str], item_s : set[bytes]):
    return items_t, item_s
def process_items3(prices : dict[str,float]):
    for item_name, item_price in prices.items():
        print(item_name)
        print(item_price)
def process_items4(item : int | str):
    print(item)
def say_hi1(name: Optional[str]=None):
    if name is not None :
        print(f"Hey {name}!")
    else :
        print("Hello world!")
def say_hi2(name: str | None) :
    if name is not None :
        print(f"Hey {name}!")
    else :
        print("Hello world")
class Person :
    def __init__(self,name: str):
        self.name=name
def get_person_name(one_person: Person):
    return one_person.name

thomas = Person("Thomas")

class User(BaseModel):
    id:int
    name= "Jane Doe"
    signup_ts: datetime|None
    friends: list[int] = []

external_data ={
    "id":"123",
    "signup_ts": "2017-06-01 12:22",
    "friends": [1,"2",b"3"],
}
user = User(**external_data)
