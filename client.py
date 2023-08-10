import utils as u
import os
import requests

PROVIDER_HOST = os.getenv("PROVIDER_API_HOST", "provider")
PROVIDER_PORT = os.getenv("PROVIDER_API_PORT", "80")
ITEM_HOST = os.getenv("ITEM_API_HOST", "item")
ITEM_PORT = os.getenv("ITEM_API_PORT", "80")

s = requests.Session()


def url(path, host, port):
    return "http://%s:%s%s" % (host, port, path)


# INTERNAL API


def get_items():
    return s.get(
        url(
            "/item", ITEM_HOST, ITEM_PORT
        ),
    )


def get_item(uid):
    return s.get(
        url(
            "/item", ITEM_HOST, ITEM_PORT
        ),
        data={
            "uid": uid,
        },
    )


def add_item(uid, name=None, quantity=1):
    return s.post(
        url(
            "/item", ITEM_HOST, ITEM_PORT
        ),
        data={
            "uid": uid,
            "name": name,
            "quantity": quantity,
        },
    )


def remove_item(uid):
    return s.delete(
        url(
            "/item", ITEM_HOST, ITEM_PORT
        ),
        data={
            "uid": uid,
        },
    )


def get_providers():
    return s.get(
        url(
            "/provider", PROVIDER_HOST, PROVIDER_PORT
        ),
    )


def get_provider(uid):
    return s.get(
        url(
            "/provider", PROVIDER_HOST, PROVIDER_PORT
        ),
        data={
            "uid": uid,
        },
    )


def add_provider(uid, name=None, quantity=1):
    return s.post(
        url(
            "/provider", PROVIDER_HOST, PROVIDER_PORT
        ),
        data={
            "uid": uid,
            "name": name,
        },
    )


def remove_provider(uid):
    return s.delete(
        url(
            "/provider", PROVIDER_HOST, PROVIDER_PORT
        ),
        data={
            "uid": uid,
        },
    )


def get_provider_items(provider_uid, item_uid):
    return s.get(
        url(
            "/provider/items", PROVIDER_HOST, PROVIDER_PORT
        ),
        data={
            "provider_uid": provider_uid,
        },
    )

def add_provider_items(provider_uid, item_uid):
    return s.post(
        url(
            "/provider/items", PROVIDER_HOST, PROVIDER_PORT
        ),
        data={
            "provider_uid": provider_uid,
            "item_uid": item_uid,
        },
    )

def delete_provider_items(provider_uid, item_uid):
    return s.delete(
        url(
            "/provider/items", PROVIDER_HOST, PROVIDER_PORT
        ),
        data={
            "provider_uid": provider_uid,
            "item_uid": item_uid,
        },
    )