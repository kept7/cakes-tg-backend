from fastapi import APIRouter, HTTPException

from ..sessions.db_sessions import db_order, db_user
from ..models.schemes import UserSchema, UserOrderSchema


router = APIRouter(prefix="/order")


@router.get(
    "/{order_id}",
    tags=["Заказы"],
    summary="Получить ифнормацию о заказе",
)
async def get_order(
    order_id: int,
):
    res = db_order.get(order_id)
    if res is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    else:
        return res


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


@router.get(
    "/{user_id}",
    tags=["Заказы"],
    summary="Получить заказы по id пользователя",
)
async def get_order_by_user_id(
    user_id: UserSchema.tg_id,
):
    return db_order.get_by_user_id(user_id)


@router.get(
    "/all",
    tags=["Заказы"],
    summary="Получить ифнормацию о всех заказах",
)
async def get_orders():
    return db_order.get_all()


@router.post("", tags=["Заказы"], summary="Добавить заказ")
async def add_order(
    order: UserOrderSchema,
):
    if await db_user.get_or_create(order) and await db_order.create(order):
        return {"ok": True, "msg": "Order was created"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create order")
