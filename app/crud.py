"""Shared list/create/update/delete helpers for the ordered content collections."""

from typing import Any

from fastapi import HTTPException
from pymongo import ReturnDocument

from . import db

SORT = [("sortOrder", 1), ("createdAt", 1)]


async def list_docs(coll, only_published: bool = False) -> list[dict[str, Any]]:
    query = {"status": "published"} if only_published else {}
    return [db.serialize(doc) async for doc in coll.find(query).sort(SORT)]


async def next_sort_order(coll) -> int:
    top = await coll.find_one(sort=[("sortOrder", -1)])
    return int(top.get("sortOrder", 0)) + 1 if top else 1


async def create_doc(coll, data: dict[str, Any]) -> dict[str, Any]:
    if not data.get("sortOrder"):
        data["sortOrder"] = await next_sort_order(coll)
    data["createdAt"] = db.now()
    data["updatedAt"] = db.now()
    result = await coll.insert_one(data)
    return db.serialize(await coll.find_one({"_id": result.inserted_id}))


async def update_doc(coll, item_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    patch = {k: v for k, v in patch.items() if v is not None}
    patch["updatedAt"] = db.now()
    doc = await coll.find_one_and_update(
        {"_id": db.oid(item_id)}, {"$set": patch}, return_document=ReturnDocument.AFTER
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Not found")
    return db.serialize(doc)


async def delete_doc(coll, item_id: str) -> dict[str, Any]:
    doc = await coll.find_one_and_delete({"_id": db.oid(item_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="Not found")
    return doc
