import asyncio
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from settings.config import settings

from models.models import TypeModel, ShapeModel, FlavourModel, ConfitModel, data_avail
from models.schemes import UserOrderSchema, UserSchema, ComponentSchema

from db_init import DB
from db_operations import DBUserRepository, DBOrderRepository, DBComponentRepository


app = FastAPI()

origins = [
    settings.BASE_URL_1,
    settings.BASE_URL_2,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DB(settings.DB_NAME)

db_user = DBUserRepository(db.session)
db_order = DBOrderRepository(db.session)
db_components_type = DBComponentRepository(db.session, TypeModel)
db_components_shape = DBComponentRepository(db.session, ShapeModel)
db_components_flavour = DBComponentRepository(db.session, FlavourModel)
db_components_confit = DBComponentRepository(db.session, ConfitModel)


@app.get(
    "/user/{user_id}",
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


@app.put(
    "/user/{user_id}",
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


@app.delete(
    "/user/{user_id}",
    tags=["Пользователи"],
    summary="Удалить пользователя",
)
async def delete_user(user_id: UserSchema.tg_id):
    try:
        await db_user.delete(user_id)
        return {"ok": True, "msg": "User was deleted"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to delete user: {e}")


@app.get(
    "/user/all",
    tags=["Пользователи"],
    summary="Получить ифнормацию о пользователях",
)
async def get_users():
    return db_user.get_all()


@app.get(
    "/order/{order_id}",
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


@app.put(
    "/order/{order_id}",
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


@app.delete(
    "/order/{order_id}",
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


@app.get(
    "/order/{user_id}",
    tags=["Заказы"],
    summary="Получить заказы по id пользователя",
)
async def get_order_by_user_id(
    user_id: UserSchema.tg_id,
):
    return db_order.get_by_user_id(user_id)


@app.get(
    "/order/all",
    tags=["Заказы"],
    summary="Получить ифнормацию о всех заказах",
)
async def get_orders():
    return db_order.get_all()


@app.post("/order", tags=["Заказы"], summary="Добавить заказ")
async def add_order(
    order: UserOrderSchema,
):
    if await db_user.get_or_create(order) and await db_order.create(order):
        return {"ok": True, "msg": "Order was created"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create order")


@app.get(
    "/components/all",
    tags=["Компоненты"],
    summary="Получить информацию о компонентах",
)
async def get_components():
    res = [
        await db_components_type.get_all(),
        await db_components_shape.get_all(),
        await db_components_flavour.get_all(),
        await db_components_confit.get_all(),
    ]
    return res


# TODO: fix this route
@app.put(
    "/components/{comp}/{comp_id}",
    tags=["Компоненты"],
    summary="Изменить статус компонента",
)
async def update_type_avail(
    comp: ComponentSchema.name,
    comp_id: int,
    comp_avail: data_avail,
):
    try:
        if comp == "type":
            await db_components_type.update(comp_id, comp_avail)
        elif comp == "shape":
            await db_components_shape.update(comp_id, comp_avail)
        elif comp == "flavour":
            await db_components_flavour.update(comp_id, comp_avail)
        elif comp == "confit":
            await db_components_confit.update(comp_id, comp_avail)
        else:
            raise Exception

        return {"ok": True, "msg": "Availability was changed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete order: {e}")


async def main():
    # await db_order_info.drop_database()
    await db.setup_database()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("main:app", reload=True)
