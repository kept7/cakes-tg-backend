from fastapi import APIRouter, HTTPException

from ..sessions.db_sessions import db_user
from ..models.schemes import UserSchema


router = APIRouter(prefix="/user")


@router.get(
    "/{user_id}",
    tags=["Пользователи"],
    summary="Получить ифнормацию о пользователе",
)
async def get_user(
    user_id: UserSchema.tg_id,
):
    res = await db_user.get(user_id)
    if res is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    else:
        return res


@router.put(
    "/{user_id}",
    tags=["Пользователи"],
    summary="Изменить никнейм пользователя",
)
async def update_username(
    user_id: UserSchema.tg_id,
    username: UserSchema.tg_username,
):
    try:
        await db_user.update(user_id, username)
        return {"ok": True, "msg": "Username was changed"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to change username: {e}")


@router.delete(
    "/{user_id}",
    tags=["Пользователи"],
    summary="Удалить пользователя",
)
async def delete_user(user_id: UserSchema.tg_id):
    try:
        await db_user.delete(user_id)
        return {"ok": True, "msg": "User was deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to delete user: {e}")


@router.get(
    "/all",
    tags=["Пользователи"],
    summary="Получить ифнормацию о пользователях",
)
async def get_users():
    return db_user.get_all()
