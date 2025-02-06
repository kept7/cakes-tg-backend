from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from db_init import OrderInfoModel, OrderDataModel
from models import OrderSchema

# class DBOperationsInit:
#     def __init__(self, session: AsyncSession):
#         self.session = session


# get user orders
# @hadrizi
# user_model = get(id="@hadrizi")
# if not user_model:
#   return {}

# creating
# @hadrizi cake
# user_model = get_or_create(id="@hadrizi")
# order_model = OrderModel(user_id=user_model.id, **cake)

# CRUD
# C - CREATE
# R - READ
# U - UPDATE
# D - DELETE
# https://en.wikipedia.org/wiki/Create,_read,_update_and_delete

# create  = CREATE
# get(id) = READ
# update  = UPDATE
# delete  = DELETE
# exist
# mb you aint gonna need it
# get_or_create(id) -> UserModel, bool
# list/get_all
# bulk_update/bulk_delete(list[id], update_data)
# get_by_user_id(user_id)
class DBUserRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    async def add(self, order: OrderSchema) -> None:
        async with self.session() as session:
            new_order_info = OrderInfoModel(
                tg_id=order.tg_id,
                tg_username=order.tg_username,
                status=order.status,
            )
            session.add(new_order_info)
            await session.commit()

    async def get_orders_info(self, user_tg_id: int) -> List[OrderInfoModel]:
        async with self.session() as session:
            query = select(OrderInfoModel).filter(OrderInfoModel.tg_id == user_tg_id)
            result = await session.execute(query)
            orders_info_list = result.scalars().all()

            # TODO remove HTTPException from repos
            if not orders_info_list:
                raise HTTPException(status_code=404, detail="Orders not found")
            return orders_info_list

    async def get_order_info(self, order_id: int) -> Optional[OrderInfoModel]:
        async with self.session() as session:
            query = select(OrderInfoModel).filter(OrderInfoModel.order_id == order_id)
            result = await session.execute(query)
            order_info = result.scalars().first()

            if not order_info:
                raise HTTPException(status_code=404, detail="Order not found")
            return order_info

    async def change_order_status(self, order_id, order_status) -> None:
        async with self.session() as session:
            order_info: OrderInfoModel = await self.get_order_info(order_id)

            order_info.status = order_status
            await session.commit()
            await session.refresh(order_info)


class DBDataRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    async def add_order_data(self, order: OrderSchema) -> bool:
        async with self.session() as session:
            new_order_data = OrderDataModel(
                type=order.type,
                shape=order.shape,
                filling=order.filling,
                confi=order.confi,
                design=order.design,
            )
            session.add(new_order_data)
            await session.commit()
            return True

    async def get_orders_data_info(
        self, user_tg_id: int, db_order_info_operator
    ) -> Tuple[List[OrderInfoModel], List[OrderDataModel]]:
        async with self.session() as session:
            orders_info_list = await DBInfoRepository(
                db_order_info_operator
            ).get_orders_info(user_tg_id)

            query = select(OrderDataModel)
            result = await session.execute(query)

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

    async def get_order_data(self, order_id: int) -> Optional[OrderDataModel]:
        async with self.session() as session:
            query = select(OrderDataModel).filter(OrderDataModel.order_id == order_id)
            result = await session.execute(query)
            order_data = result.scalars().first()

            if order_data is None:
                raise HTTPException(status_code=404, detail="Order data doesn't exist")
            return order_data
