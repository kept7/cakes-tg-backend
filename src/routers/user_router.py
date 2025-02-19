from fastapi import APIRouter, HTTPException

from src.sessions.db_sessions import db_user
from src.models.schemes import UserOrderSchema


router = APIRouter(prefix="/user")


@router.post(
    "",
    tags=["Пользователи"],
    summary="Добавить пользователя",
)
async def add_user(order: UserOrderSchema):
    if await db_user.create(order):
        return {"ok": True, "msg": "User was created"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create user")


@router.get(
    "/{user_id}",
    tags=["Пользователи"],
    summary="Получить ифнормацию о пользователе",
)
async def get_user(
    user_id: int,
):
    res = await db_user.get(user_id)
    if res is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    else:
        return res


@router.get(
    "",
    tags=["Пользователи"],
    summary="Получить ифнормацию о пользователях",
)
async def get_users():
    return await db_user.get_all()


@router.put(
    "/{user_id}",
    tags=["Пользователи"],
    summary="Изменить никнейм пользователя",
)
async def update_username(
    user_id: int,
    username: str,
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
async def delete_user(user_id: int):
    try:
        await db_user.delete(user_id)
        return {"ok": True, "msg": "User was deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to delete user: {e}")
