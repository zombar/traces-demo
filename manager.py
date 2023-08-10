import json, uuid

from typing import Optional
from fastapi import FastAPI, Form, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator

import utils as u
import client as c

name = "traces-demo-item"
db_name = "item"
tags_metadata = [
    {
        "name": "manager",
        "description": "Provides an interface for managing items and providers",
    },
    {
        "name": "update",
        "description": "Update item quantity and provider (if doesn't exist) to the database via name, if provider has no more items we remove them from the system",
    },
    {
        "name": "get",
        "description": "Fetch a list of providers item's from the database",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
Instrumentator().instrument(app).expose(app)

log = u.init_logger(name)
log.info("starting app ...")

cache = {}

# Build local lookup table
response = c.get_providers()

for provider in response.json():

    if provider["name"] not in cache:
        cache[provider["name"]] = {}

    cache[provider["name"]]["uid"] = provider["uid"]

    response = c.get_provider_items(provider["uid"])
    # Add providers items to local lookup
    for uid in response.json():
        item_response = c.get_item(uid)
        data = json.loads(item_response.json())

        if "items" not in cache[provider["name"]]:
            cache[provider["name"]]["items"] = {}

        cache[provider["name"]]["items"][data["name"]] = data["uid"]


@app.get("/health")
async def health():
    log.debug("health check probed")
    return {"health": "OK"}


@app.get("/inventory", tags=["manager", "update"])
async def get(
    provider_name: str = Form(...),
):
    
    if provider_name not in cache:
        raise HTTPException(status_code=422, detail="provider %s not found" % provider_name)
    
    data = {
        "uid": cache[provider_name]["uid"],
        "name": provider_name,
        "items": [],
    }

    for item_name in cache[provider_name]["items"]:
        item_uid = cache[provider_name]["items"][item_name]
        item_data = c.get_item(item_uid)
        data.items.append(item_data)

    return json.dumps(data)


@app.post("/inventory", tags=["manager", "add"])
async def post(
    provider_name: str = Form(...),
    item_name: str = Form(...),
    quantity: int = Form(...),
):

    # Fail if we're trying to decrement item for a provider that doesn't exist
    if quantity < 0 and provider_name not in cache[provider_name]:
        raise HTTPException(status_code=422, detail="provider %s not found" % provider_name)

    # Fail if we're trying to decrement item for a provider that doesn't have the item
    if quantity < 0 and item_name not in cache[provider_name]["items"]:
        raise HTTPException(status_code=422, detail="item %s not found" % item_name)

    # Otherwise add the provider if they don't exit
    if provider_name not in cache:
        provider_uid = c.add_provider(provider_name)
        cache[provider_name] = {}
        cache[provider_name]["uid"] = provider_uid

    provider_uid = cache[provider_name]["uid"]

    # Add item to system if it is new
    if item_name not in cache[provider_name]:
        item_uid = c.add_item(
            name=item_name,
            quantity=quantity,
        )
        c.add_provider_item(provider_uid, item_uid)

        # Update local lookup table
        if "items" not in cache[provider_name]:
            cache[provider_name]["items"] = {}

        cache[provider_name]["items"][item_name] = item_uid
        return

    item_uid = cache[provider_name]["items"][item_name]

    response = c.get_item(item_uid)
    item_data = json.loads(response.json())

    # Fail if we don't have adequate stock
    if item_data["quantity"] + quantity < 0:
        raise HTTPException(status_code=422, detail="provider %s has not enough stock of item %s" % (provider_name, item_name))

    # If we have just given out the last of the item, cleanup
    if item_data["quantity"] + quantity == 0:
        c.delete_item(item_uid)
        c.delete_provider_items(provider_uid, item_uid)

        # Update the lookup table
        del(cache[provider_name]["items"][item_name])

        # Delete the provider if they have no more items
        response = c.get_provider_items(provider_uid)
        if len(json.loads(response.json())) == 0:
            c.delete_provider(provider_uid)

            # Update the lookup table
            del(cache[provider_name])

    # Otherwise, just update the item
    c.add_item(
        uid=item_uid,
        quantity=item_data["quantity"] + quantity,
    )
