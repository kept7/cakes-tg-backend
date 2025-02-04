from datetime import datetime
from typing import List, Optional, AsyncGenerator

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db_init import OrderInfoModel, OrderDataModel
from models import OrderSchema


# class DBOperationsInit:
#     def __init__(self, session: AsyncSession):
#         self.session = session


class DBInfoOperations:
    def __init__(self, session: AsyncGenerator[AsyncSession, None]):
        self.session = session

    async def add_order_info(self, order: OrderSchema) -> bool:
        current_time = datetime.now().strftime("%d, %B %Y %H:%M")
        new_order_info = OrderInfoModel(
            tg_id=order.tg_id,
            tg_username=order.tg_username,
            date=current_time,
            status=order.status,
        )
        self.session.add(new_order_info)
        await self.session.commit()
        return True

    async def get_orders_info(self, user_tg_id: int) -> List[OrderInfoModel]:
        query = select(OrderInfoModel).filter(OrderInfoModel.tg_id == user_tg_id)
        result = await self.session.execute(query)
        orders_info_list = result.scalars().all()

        if not orders_info_list:
            raise HTTPException(status_code=404, detail="Orders not found")
        return orders_info_list

    async def get_order_info(self, order_id: int) -> Optional[OrderInfoModel]:
        query = select(OrderInfoModel).filter(OrderInfoModel.order_id == order_id)
        result = await self.session.execute(query)
        order_info = result.scalars().first()

        if order_info is None:
            raise HTTPException(status_code=404, detail="Order doesn't exist")
        return order_info


class DBDataOperations:
    def __init__(self, session: AsyncGenerator[AsyncSession, None]):
        self.session = session

    async def add_order_data(self, order: OrderSchema) -> bool:
        new_order_data = OrderDataModel(
            type=order.type,
            shape=order.shape,
            filling=order.filling,
            confi=order.confi,
            design=order.design,
        )
        self.session.add(new_order_data)
        await self.session.commit()
        return True

    async def get_orders_data_info(
        self, user_tg_id: int, db_order_info_operator
    ) -> List[OrderDataModel]:
        orders_info_list = await DBInfoOperations(
            db_order_info_operator
        ).get_orders_info(user_tg_id)

        query = select(OrderDataModel)
        result = await self.session.execute(query)

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
        query = select(OrderDataModel).filter(OrderDataModel.order_id == order_id)
        result = await self.session.execute(query)
        order_data = result.scalars().first()

        if order_data is None:
            raise HTTPException(status_code=404, detail="Order data doesn't exist")
        return order_data
