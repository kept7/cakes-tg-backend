import asyncio
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends

from settings.config import settings

from models import OrderSchema

import uvicorn

from db_init import DBInit, OrderInfoModel, OrderDataModel
from db_operations import DBInfoOperations, DBDataOperations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.middleware.cors import CORSMiddleware

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

db_order_info = DBInit(settings.BD_ORDER_INFO_NAME)
db_order_data = DBInit(settings.BD_ORDER_DATA_NAME)

db_order_info_session = db_order_info.get_session()
db_order_data_session = db_order_data.get_session()

db_order_info_operator = DBInfoOperations(db_order_info_session)
db_order_data_operator = DBDataOperations(db_order_data_session)

SessionDepOrderInfo = Annotated[AsyncSession, Depends(db_order_info.get_session)]
SessionDepOrderData = Annotated[AsyncSession, Depends(db_order_data.get_session)]


@app.get(
    "/orders/info",
    tags=["Заказы"],
    summary="Получить ифнормацию о всех заказах",
)
async def get_all_orders(
    db_order_info_operator: SessionDepOrderInfo,
    db_order_data_operator: SessionDepOrderData,
):
    query = select(OrderInfoModel)
    result_1 = await db_order_info_operator.execute(query)

    query_2 = select(OrderDataModel)
    result_2 = await db_order_data_operator.execute(query_2)

    result = []
    result_1 = result_1.scalars().all()
    result_2 = result_2.scalars().all()

    for item1, item2 in zip(result_1, result_2):
        combined_item = {**vars(item1), **vars(item2)}
        result.append(combined_item)

    return result


@app.post("/orders/info", tags=["Заказы"], summary="Добавить заказ")
async def add_order(
    order: OrderSchema,
    db_order_info_operator: SessionDepOrderInfo,
    db_order_data_operator: SessionDepOrderData,
):
    if await DBInfoOperations(db_order_info_operator).add_order_info(
        order
    ) and await DBDataOperations(db_order_data_operator).add_order_data(order):
        return {"ok": True, "msg": "Order was created"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create order")


@app.get(
    "/orders/info/user/{user_tg_id}",
    tags=["Заказы"],
    summary="Получить информацию о всех заказах конкретного пользователя",
)
async def get_user_orders(
    user_tg_id: int,
    db_order_info_operator: SessionDepOrderInfo,
    db_order_data_operator: SessionDepOrderData,
):
    orders_info_list, orders_data_list = await DBDataOperations(
        db_order_data_operator
    ).get_orders_data_info(user_tg_id, db_order_info_operator)

    all_orders = []

    for item1, item2 in zip(orders_info_list, orders_data_list):
        combined_item = {**vars(item1), **vars(item2)}
        all_orders.append(combined_item)

    return all_orders


@app.get(
    "/orders/info/order/{order_id}",
    tags=["Заказы"],
    summary="Получить информацию о всех заказах конкретного пользователя",
)
async def get_order(
    order_id: int,
    db_order_info_operator: SessionDepOrderInfo,
    db_order_data_operator: SessionDepOrderData,
):
    order_info = await DBInfoOperations(db_order_info_operator).get_order_info(order_id)
    order_data = await DBDataOperations(db_order_data_operator).get_order_data(order_id)

    return {**vars(order_info), **vars(order_data)}


async def main():
    # await db_order_info.drop_database()
    await db_order_info.setup_database()

    # await db_order_data.drop_database()
    await db_order_data.setup_database()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("main:app", reload=True)
