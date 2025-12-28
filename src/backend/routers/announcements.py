"""
Announcement endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from ..database import announcements_collection
from .auth import get_current_user

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

@router.get("", response_model=List[dict])
def get_announcements():
    """Get all current (non-expired) announcements"""
    now = datetime.utcnow()
    announcements = list(announcements_collection.find({
        "$or": [
            {"start_date": None},
            {"start_date": {"$lte": now}}
        ],
        "expiration_date": {"$gte": now}
    }))
    for a in announcements:
        a["id"] = str(a.pop("_id"))
    return announcements

@router.post("", response_model=dict)
def create_announcement(data: dict, user=Depends(get_current_user)):
    """Create a new announcement (auth required)"""
    if not data.get("message") or not data.get("expiration_date"):
        raise HTTPException(status_code=400, detail="Message and expiration date required.")
    data["start_date"] = data.get("start_date")
    data["created_by"] = user["username"]
    result = announcements_collection.insert_one(data)
    return {"id": str(result.inserted_id)}

@router.put("/{announcement_id}", response_model=dict)
def update_announcement(announcement_id: str, data: dict, user=Depends(get_current_user)):
    """Update an announcement (auth required)"""
    result = announcements_collection.update_one({"_id": announcement_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found.")
    return {"success": True}

@router.delete("/{announcement_id}", response_model=dict)
def delete_announcement(announcement_id: str, user=Depends(get_current_user)):
    """Delete an announcement (auth required)"""
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found.")
    return {"success": True}
