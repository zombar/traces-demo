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
tracer = u.init_tracer("item")

log.info("starting app ...")

u.init_db("item", "redis", 6379)

@app.get("/health")
async def health():
    log.debug("health check probed")
    return {"health": "OK"}


@app.get("/item", tags=["item", "get"])
async def get(
    uid: Optional[str] = Form(None),
):
    with tracer.start_active_span("get") as scope:
        scope.span.set_tag("uid", uid)
        return u.get(db_name, "item", uid)


@app.delete("/item", tags=["item", "remove"])
async def rm(
    uid: str = Form(...),
):
    with tracer.start_active_span("rm") as scope:
        scope.span.set_tag("uid", uid)
        u.rm(db_name, "item", uid)


@app.post("/item", tags=["item", "add"])
async def add(
    name: Optional[str] = Form(None),
    uid: Optional[str] = Form(None),
    quantity: int = Form(...),
):
    with tracer.start_active_span("add") as scope:
    
        if not name and not uid:
            raise HTTPException(status_code=400, detail="either a name or uid must be specified")

        if name:

            spanB = tracer.start_span("new")
            uid = str(uuid.uuid4())
            data = {
                "uid": uid,
                "name": name,
                "quantity": quantity,
            }
            spanB.set_tag("uid", uid)
            spanB.set_tag("name", name)
            spanB.set_tag("quantity", quantity)
            u.add(db_name, "item", uid, json.dumps(data))
            spanB.finish()
            return uid
        
        spanC = tracer.start_span("update")
        spanB.set_tag("uid", uid)
        spanB.set_tag("quantity", quantity)
        data = u.get(db_name, "item", uid)
        data["quantity"] = quantity
        u.rm(db_name, "item", uid)
        u.add(db_name, "item", uid, json.dumps(data))
        spanC.finish()
    
