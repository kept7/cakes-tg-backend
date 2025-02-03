import asyncio
from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends

import uvicorn

from pydantic import BaseModel, Field, ConfigDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Base(DeclarativeBase): ...


class OrderInfoModel(Base):
    __tablename__ = "orders_info"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int]
    tg_username: Mapped[str]
    date: Mapped[str]
    status: Mapped[str]


class OrderDataModel(Base):
    __tablename__ = "orders_data"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    shape: Mapped[str]
    filling: Mapped[str]
    confi: Mapped[str]
    design: Mapped[str]


class OrderInfoAddSchema(BaseModel):
    tg_id: int
    tg_username: str
    status: str


class OrderDataAddSchema(BaseModel):
    type: str
    shape: str
    filling: str
    confi: str
    design: str = Field(max_length=1000)


class OrderSchema(OrderDataAddSchema, OrderInfoAddSchema):
    model_config = ConfigDict(extra="forbid")



# def create_engine(bd_name: str):
#     engine = create_async_engine(f"sqlite+aiosqlite:///{bd_name}.db")
#     new_session = async_sessionmaker(engine, expire_on_commit=False)
#     return engine, new_session

# engine_order_info_db, new_session_order_info_db = create_engine("orders_info")
# engine_order_data_db, new_session_order_data_db = create_engine("orders_data")

# async def get_session_order_info_db():
#     async with new_session_order_info_db() as session_order_info_db:
#         yield session_order_info_db
#
# async def get_session_order_data_db():
#     async with new_session_order_data_db() as session_order_data_db:
#         yield session_order_data_db
#
# SessionDep_order_info_db = Annotated[AsyncSession, Depends(get_session_order_info_db)]
# SessionDep_order_data_db = Annotated[AsyncSession, Depends(get_session_order_data_db)]



engine = create_async_engine("sqlite+aiosqlite:///orders_info.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)



engine_2 = create_async_engine("sqlite+aiosqlite:///orders_data.db")
new_session_2 = async_sessionmaker(engine_2, expire_on_commit=False)

async def get_session_2():
    async with new_session_2() as session_2:
        yield session_2

SessionDep_2 = Annotated[AsyncSession, Depends(get_session_2)]

async def setup_database_2():
    async with engine_2.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_database_2():
    async with engine_2.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def add_order_info(order: OrderSchema, session: SessionDep):
    current_time = datetime.now().strftime("%d, %B %Y %H:%M")
    new_order_info = OrderInfoModel(
        tg_id=order.tg_id,
        tg_username=order.tg_username,
        date=current_time,
        status=order.status,
    )
    session.add(new_order_info)
    await session.commit()
    return True


async def add_order_data(order: OrderSchema, session_2: SessionDep_2):
    new_order_data = OrderDataModel(
        type=order.type,
        shape=order.shape,
        filling=order.filling,
        confi=order.confi,
        design=order.design,
    )
    session_2.add(new_order_data)
    await session_2.commit()
    return True


@app.get(
    "/orders/info",
    tags=["Заказы"],
    summary="Получить ифнормацию о всех заказах",
)
async def get_all_orders(session: SessionDep, session_2: SessionDep_2):
    query = select(OrderInfoModel)
    result = await session.execute(query)

    query_2 = select(OrderDataModel)
    result_2 = await session_2.execute(query_2)

    resultat = []
    result = result.scalars().all()
    result_2 = result_2.scalars().all()

    for item1, item2 in zip(result, result_2):
        combined_item = {**vars(item1), **vars(item2)}
        resultat.append(combined_item)

    return resultat

@app.post("/orders/info", tags=["Заказы"], summary="Добавить заказ")
async def add_order(order: OrderSchema, session: SessionDep, session_2: SessionDep_2):
    if await add_order_info(order, session) and await add_order_data(order, session_2):
        return {"ok": True, "msg": "Order was created"}
    else:
        raise HTTPException(status_code=400, detail="Failed to create order")

'''
Получить информацию о всех заказах пользователя
'''
async def get_orders_info(user_tg_id: int, session: SessionDep):
    query = select(OrderInfoModel).filter(OrderInfoModel.tg_id == user_tg_id)
    result = await session.execute(query)

    orders_info_list = []
    for order_info in result.scalars().all():
        if order_info.tg_id == user_tg_id:
            orders_info_list.append(order_info)

    if orders_info_list:
        return orders_info_list
    else:
        raise HTTPException(status_code=404, detail="Orders not found")


'''
Получить данные о всех заказах пользователя
'''
async def get_orders_data_info(user_tg_id: int, session: SessionDep, session_2: SessionDep_2):
    orders_info_list = await get_orders_info(user_tg_id, session)

    query = select(OrderDataModel)
    result = await session_2.execute(query)

    result_list = result.scalars().all()
    orders_data_list = []

    for order_info in orders_info_list:
        for order_data in result_list:
            if order_info.order_id == order_data.order_id:
                orders_data_list.append(order_data)

    # order_data_dict = {order_data.order_id: order_data for order_data in order_data_list}
    #
    # orders_data_list = [order_data_dict[order_info.order_id] for order_info in orders_info_list if
    #                     order_info.order_id in order_data_dict]

    return orders_info_list, orders_data_list


@app.get(
"/orders/info/user/{user_tg_id}",
    tags=["Заказы"],
    summary="Получить информацию о всех заказах конкретного пользователя",
)
async def get_user_orders(user_tg_id: int, session: SessionDep, session_2: SessionDep_2):
    orders_info_list, orders_data_list = await get_orders_data_info(user_tg_id, session, session_2)

    all_orders = []

    for item1, item2 in zip(orders_info_list, orders_data_list):
        combined_item = {**vars(item1), **vars(item2)}
        all_orders.append(combined_item)

    return all_orders


'''
Получить информацию о конкретном заказе
'''
async def get_order_info(order_id: int, session: SessionDep):
    query = select(OrderInfoModel).filter(OrderInfoModel.order_id == order_id)
    result = await session.execute(query)
    order_info = result.scalars().first()

    if order_info is not None:
        return order_info
    else:
        raise HTTPException(status_code=404, detail="Order doesn't exist")


'''
Получить данные о конкретном заказе
'''
async def get_order_data(order_id: int, session_2: SessionDep_2):
    query = select(OrderDataModel).filter(OrderDataModel.order_id == order_id)
    result = await session_2.execute(query)
    order_data = result.scalars().first()

    if order_data is not None:
        return order_data
    else:
        raise HTTPException(status_code=404, detail="Order doesn't exist")


@app.get(
"/orders/info/order/{order_id}",
    tags=["Заказы"],
    summary="Получить информацию о всех заказах конкретного пользователя",
)
async def get_order(order_id: int, session: SessionDep, session_2: SessionDep_2):
    order_info = await get_order_info(order_id, session)
    order_data = await get_order_data(order_id, session_2)

    return {**vars(order_info), **vars(order_data)}


async def main():
    await drop_database()
    await drop_database_2()
    await setup_database()
    await setup_database_2()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("main:app", reload=True)