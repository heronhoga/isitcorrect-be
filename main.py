from fastapi import FastAPI
from config import settings


app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World", "APP_KEY": settings.app_key}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}