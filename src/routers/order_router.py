from fastapi import APIRouter, HTTPException

from src.sessions.db_sessions import db_order, db_user
from src.models.schemes import UserSchema, UserOrderSchema


router = APIRouter(prefix="/order")


@router.post("", tags=["Заказы"], summary="Добавить заказ")
async def add_order(
    order: UserOrderSchema,
):
    if await db_user.get_or_create(order) and await db_order.create(order):
        return {"ok": True, "msg": "Order was created"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create order")


@router.get(
    "/{order_id}",
    tags=["Заказы"],
    summary="Получить ифнормацию о заказе",
)
async def get_order(
    order_id: int,
):
    res = await db_order.get(order_id)
    if res is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    else:
        return res


@router.get(
    "/user/{user_id}",
    tags=["Заказы"],
    summary="Получить заказы по id пользователя",
)
async def get_order_by_user_id(
    user_id: int,
):
    res = await db_order.get_by_user_id(user_id)
    if res:
        return res
    raise HTTPException(status_code=404, detail=f"User {user_id} has no orders yet")


@router.get(
    "",
    tags=["Заказы"],
    summary="Получить ифнормацию о всех заказах",
)
async def get_orders():
    res = await db_order.get_all()
    if res:
        return res
    raise HTTPException(status_code=404, detail=f"No orders have been placed yet")


@router.put(
    "/{order_id}",
    tags=["Заказы"],
    summary="Изменить статус заказа",
)
async def put_order_status(
    order_id: int,
    order_status: str,
):
    try:
        await db_order.update(order_id, order_status)
        return {"ok": True, "msg": "Order status was changed"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to change order status: {e}"
        )


@router.delete(
    "/{order_id}",
    tags=["Заказы"],
    summary="Удалить заказ",
)
async def delete_order(
    order_id: int,
):
    try:
        await db_order.delete(order_id)
        return {"ok": True, "msg": "Order was deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete order: {e}")
