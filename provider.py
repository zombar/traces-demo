import json, uuid

from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

import utils as u

name = "traces-demo-provider"
db_name = "provider"
tags_metadata = [
    {
        "name": "provider",
        "description": "Manage item providers",
    },
    {
        "name": "item",
        "description": "Manage provider item lists",
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

u.init_db("provider", "redis", 6379)


@app.get("/health")
async def health():
    log.debug("health check probed")
    return {"health": "OK"}


@app.get("/provider", tags=["provider", "get"])
async def get(
    uid: Optional[str] = Form(None),
):
    return u.get(db_name, "provider", uid)


@app.delete("/provider", tags=["provider", "remove"])
async def rm(
    uid: str = Form(...),
):
    u.rm(db_name, "provider", uid)


@app.post("/provider", tags=["provider", "add"])
async def add(
    name: str = Form(...),
):
    uid = str(uuid.uuid4())
    data = {
        "uid": uid,
        "name": name,
    }
    u.add(db_name, "provider", uid, json.dumps(data))
    return uid


@app.post("/provider/items", tags=["provider", "item", "add"])
async def add_item(
    provider_uid: str = Form(...),
    item_uid: str = Form(...),
):
    if not u.get(db_name, "provider", provider_uid):
        raise HTTPException(status_code=400, detail="provider uid not found in db")

    u.add_to_list(db_name, "items.%s" % provider_uid, item_uid)


@app.delete("/provider/items", tags=["provider", "item", "remove"])
async def rm_item(
    provider_uid: str = Form(...),
    item_uid: str = Form(...),
):
    if not u.get(db_name, "provider", provider_uid):
        raise HTTPException(status_code=400, detail="provider uid not found in db")

    u.rm_from_list(db_name, "items.%s" % provider_uid, item_uid)


@app.get("/provider/items", tags=["provider", "item", "get"])
async def get_item(
    provider_uid: str = Form(...),
):
    if not u.get(db_name, "provider", provider_uid):
        raise HTTPException(status_code=400, detail="provider uid not found in db")

    return u.get_list(db_name, "items.%s" % provider_uid)
