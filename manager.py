import json

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
        "description": "Add provider (if doesn't exist) and add/update item quantity to the database via name, if provider has no more items we remove them from the system",
    },
    {
        "name": "get",
        "description": "Fetch a list of providers item's from the database",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
Instrumentator().instrument(app).expose(app)

log = u.init_logger(name)
tracer = u.init_tracer("manager")

log.info("starting app ...")

cache = {}

# Build local lookup table
with tracer.start_active_span("build_lookups") as scope:
    response = c.get_providers()

    for provider in response.json():

        if provider["name"] not in cache:
            cache[provider["name"]] = {}

        cache[provider["name"]]["uid"] = provider["uid"]

        response = c.get_provider_items(provider["uid"])
        
        # Add providers items to local lookup
        for uid in response.json():
            item_response = c.get_item(uid)
            data = item_response.json()

            if "items" not in cache[provider["name"]]:
                cache[provider["name"]]["items"] = {}

            cache[provider["name"]]["items"][data["name"]] = data["uid"]


@app.get("/health")
async def health():
    log.debug("health check probed")
    return {"health": "OK"}


@app.get("/inventory", tags=["manager", "get"])
async def get(
    provider_name: str = Form(...),
):
    with tracer.start_active_span("get") as scope:
        
        if provider_name not in cache:
            raise HTTPException(status_code=400, detail="provider %s not found" % provider_name)
        
        provider_uid = cache[provider_name]["uid"]
        scope.span.set_tag("uid", provider_uid)
        scope.span.set_tag("name", provider_name)

        data = {
            "uid": provider_uid,
            "name": provider_name,
            "items": [],
        }

        for item_name in cache[provider_name]["items"]:
            item_uid = cache[provider_name]["items"][item_name]
            response = c.get_item(item_uid)
            data["items"].append(response.json())

        return data


@app.post("/inventory", tags=["manager", "update"])
async def post(
    provider_name: str = Form(...),
    item_name: str = Form(...),
    quantity: int = Form(...),
):

    with tracer.start_active_span("update") as scope:

        # Fail if we're trying to decrement item for a provider that doesn't exist
        if quantity < 0 and provider_name not in cache:
            raise HTTPException(status_code=400, detail="provider %s not found" % provider_name)

        # Fail if we're trying to decrement item for a provider that doesn't have the item
        if quantity < 0 and item_name not in cache[provider_name]["items"]:
            raise HTTPException(status_code=400, detail="item %s not found" % item_name)

        # Otherwise add the provider if they don't exit
        if provider_name not in cache:
            spanB = tracer.start_span("add_provider")
            log.info("adding new provider %s" % provider_name)
            response = c.add_provider(provider_name)
            provider_uid = response.json()
            spanB.set_tag("uid", provider_uid)
            cache[provider_name] = {
                "uid": provider_uid,
                "items": {},
            }
            spanB.finish()

        provider_uid = cache[provider_name]["uid"]

        # Add item to system if it is new
        if item_name not in cache[provider_name]["items"]:
            spanC = tracer.start_span("add_item")
            log.info("adding new item %s" % item_name)
            response = c.add_item(
                name=item_name,
                quantity=quantity,
            )
            item_uid = response.json()
            spanC.set_tag("uid", item_uid)
            spanC.set_tag("name", item_name)
            spanC.set_tag("quantity", quantity)
            c.add_provider_item(provider_uid, item_uid)

            # Update local lookup table
            if "items" not in cache[provider_name]:
                cache[provider_name]["items"] = {}

            cache[provider_name]["items"][item_name] = item_uid
            spanC.finish()
            return

        item_uid = cache[provider_name]["items"][item_name]

        response = c.get_item(item_uid)
        item_data = response.json()

        # Fail if we don't have adequate stock
        if item_data["quantity"] + quantity < 0:
            raise HTTPException(status_code=400, detail="provider %s has not enough stock of item %s" % (provider_name, item_name))

        # If we have just given out the last of the item, cleanup
        if item_data["quantity"] + quantity == 0:
            spanD = tracer.start_span("delete_item")
            log.info("no more stock of item %s, deleting ..." % item_name)
            c.delete_item(item_uid)
            c.delete_provider_items(provider_uid, item_uid)
            spanD.set_tag("provider_uid", provider_uid)
            spanD.set_tag("item_uid", item_uid)

            # Update the lookup table
            del(cache[provider_name]["items"][item_name])
            spanD.finish()

            # Delete the provider if they have no more items
            response = c.get_provider_items(provider_uid)
            if len(response.json()) == 0:
                spanE = tracer.start_span("delete_provider")
                log.info("provider %s has no more items, deleting ..." % provider_name)
                c.delete_provider(provider_uid)
                spanE.set_tag("provider_uid", provider_uid)

                # Update the lookup table
                del(cache[provider_name])
                spanE.finish()

        # Otherwise, just update the item
        spanF = tracer.start_span("update_item")
        new_quantity = item_data["quantity"] + quantity
        spanF.set_tag("uid", provider_uid)
        spanF.set_tag("quantity", new_quantity)
        c.add_item(
            uid=item_uid,
            quantity=new_quantity,
        )
        spanF.finish()
