from fastapi import FastAPI

app = FastAPI()





@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str, q: str = None):
    return {"message": f"Hello {name} - {q}"}

@app.get("/hello/{first_name}/{last_name}/{age}")
def get_full_name(first_name: str, last_name: str, age: int):
    full_name = first_name.title() + " " + last_name.title()
    return {"full_name": full_name, "age": age}
print(get_full_name("john", "doe", 30))


