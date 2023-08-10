import json, uuid, requests

from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

import utils as u

name = "traces-demo-item"
db_name = "item"
tags_metadata = [
    {
        "name": "manager",
        "description": "Provides an interface for managing items and providers",
    },
    {
        "name": "add",
        "description": "Add item quantity and provider (if doesn't exist) to the database via name",
    },
    {
        "name": "remove",
        "description": "Decrement item quantity and remove provider from the database if has no more items",
    },
    {
        "name": "get",
        "description": "Fetch a list of providers items from the database",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
Instrumentator().instrument(app).expose(app)

log = u.init_logger(name)
log.info("starting app ...")



@app.get("/health")
async def health():
    log.debug("health check probed")
    return {"health": "OK"}

