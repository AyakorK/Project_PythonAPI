from fastapi import FastAPI
from typing import List, Set, Tuple, Dict, Union
from typing import Optional

app = FastAPI()





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

def process_items(items: List[str], items_t: Tuple[int, int, str], items_s: Set[bytes], items_d: Dict[str, str], item_u: Union[int, str]):
    return {"items": items, "items_t": items_t, "items_s": items_s, "items_d": items_d, "item_u": item_u}
print(process_items(["a", "b", "c"], (1, 2, "3"), {b"1", b"2", b"3"}, {"a": "b", "c": "d"}, 1))




