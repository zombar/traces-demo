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
tracer = u.init_tracer("provider")

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
    with tracer.start_active_span("get") as scope:
        scope.span.set_tag("uid", uid)
        return u.get(db_name, "provider", uid)


@app.delete("/provider", tags=["provider", "remove"])
async def rm(
    uid: str = Form(...),
):
    with tracer.start_active_span("delete") as scope:
        scope.span.set_tag("uid", uid)
        u.rm(db_name, "provider", uid)


@app.post("/provider", tags=["provider", "add"])
async def add(
    name: str = Form(...),
):
    with tracer.start_active_span("add") as scope:
        uid = str(uuid.uuid4())
        data = {
            "uid": uid,
            "name": name,
        }
        scope.span.set_tag("uid", uid)
        scope.span.set_tag("name", name)
        u.add(db_name, "provider", uid, json.dumps(data))
        return uid


@app.post("/provider/items", tags=["provider", "item", "add"])
async def add_item(
    provider_uid: str = Form(...),
    item_uid: str = Form(...),
):
    with tracer.start_active_span("add_item") as scope:
        scope.span.set_tag("uid", provider_uid)
        scope.span.set_tag("uid", item_uid)

        if not u.get(db_name, "provider", provider_uid):
            raise HTTPException(status_code=400, detail="provider uid not found in db")

        u.add_to_list(db_name, "items.%s" % provider_uid, item_uid)


@app.delete("/provider/items", tags=["provider", "item", "remove"])
async def rm_item(
    provider_uid: str = Form(...),
    item_uid: str = Form(...),
):
    with tracer.start_active_span("remove_item") as scope:
        scope.span.set_tag("uid", provider_uid)
        scope.span.set_tag("uid", item_uid)

        if not u.get(db_name, "provider", provider_uid):
            raise HTTPException(status_code=400, detail="provider uid not found in db")

        u.rm_from_list(db_name, "items.%s" % provider_uid, item_uid)


@app.get("/provider/items", tags=["provider", "item", "get"])
async def get_item(
    provider_uid: str = Form(...),
):
    with tracer.start_active_span("get_item") as scope:
        scope.span.set_tag("uid", provider_uid)
    
        if not u.get(db_name, "provider", provider_uid):
            raise HTTPException(status_code=400, detail="provider uid not found in db")

        return u.get_list(db_name, "items.%s" % provider_uid)
