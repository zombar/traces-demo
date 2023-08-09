import json, uuid

from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

import utils as u

name = "traces-demo-item"
db_name = "item"
tags_metadata = [
    {
        "name": "item",
        "description": "Manage items",
    },
    {
        "name": "add",
        "description": "Add item to the database",
    },
    {
        "name": "get",
        "description": "Fetch item(s) from the database",
    },
    {
        "name": "remove",
        "description": "Delete item from the database",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
Instrumentator().instrument(app).expose(app)

log = u.init_logger(name)
log.info("starting app ...")

u.init_db("item", "redis", 6379)

@app.get("/health")
async def health():
    log.debug("health check probed")
    return {"health": "OK"}


@app.get("/item/get", tags=["item", "get"])
async def get(
    uid: Optional[str] = Form(None),
):
    return u.get(db_name, "item", uid)


@app.delete("/item/remove", tags=["item", "remove"])
async def rm(
    uid: str = Form(...),
):
    u.rm(db_name, "item", uid)


@app.post("/item/add", tags=["item", "add"])
async def add(
    name: Optional[str] = Form(None),
    uid: str = Form(...),
    quantity: Optional[int] = Form(None),
):
    if name:
        uid = str(uuid.uuid4())
        data = {
            "uid": uid,
            "name": name,
            "quantity": quantity,
        }
        u.add(db_name, "item", uid, json.dumps(data))
        return uid
    
    data = u.get(db_name, "item", uid)
    data["quantity"] = quantity
    u.rm(db_name, "item", uid)
    u.add(db_name, "item", uid, json.dumps(data))
    
