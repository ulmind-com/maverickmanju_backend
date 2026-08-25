from fastapi import APIRouter, Depends, HTTPException

from .. import db, security
from ..schemas import LoginIn, PasswordChangeIn, TokenOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn):
    user = await db.admin_users().find_one({"email": payload.email.strip().lower()})
    if user is None or not security.verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return TokenOut(
        access_token=security.create_token(user), user=security.public_user(user)
    )


@router.get("/me")
async def me(admin=Depends(security.current_admin)):
    return security.public_user(admin)


@router.post("/change-password")
async def change_password(
    payload: PasswordChangeIn, admin=Depends(security.current_admin)
):
    if not security.verify_password(payload.currentPassword, admin["passwordHash"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    await db.admin_users().update_one(
        {"_id": admin["_id"]},
        {"$set": {"passwordHash": security.hash_password(payload.newPassword)}},
    )
    return {"ok": True}
