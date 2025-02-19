import datetime
from functools import wraps

from typing import Callable, Coroutine, Any, TypeVar, Sequence, Generic

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.models.models import UserModel, OrderModel, ComponentModel
from src.models.schemes import UserOrderSchema, ComponentSchema, UserSchema


R = TypeVar("R")
M = TypeVar("M")


class DBUserRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(method)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    async def create(
        self, order: UserOrderSchema, session: AsyncSession = None
    ) -> UserModel:
        @self.connection
        async def inner_create(inner_order: UserOrderSchema, session: AsyncSession):
            new_user = UserModel(
                id=inner_order.tg_id,
                username=inner_order.tg_username,
            )
            session.add(new_user)
            await session.commit()
            return new_user

        return await inner_create(order)

    async def get(self, user_id: int, session: AsyncSession = None) -> UserModel | None:
        @self.connection
        async def inner_get(inner_user_id: int, session: AsyncSession):
            query = select(UserModel).filter_by(id=inner_user_id)
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get(user_id)

    async def update(
        self,
        user_id: int,
        username: str,
        session: AsyncSession = None,
    ) -> None:
        @self.connection
        async def inner_update(
            inner_user_id: int, inner_username: str, session: AsyncSession
        ):
            stmt = (
                update(UserModel)
                .values(username=inner_username)
                .filter_by(id=inner_user_id)
            )
            await session.execute(stmt)
            await session.commit()

        return await inner_update(user_id, username)

    async def delete(self, user_id: int, session: AsyncSession = None) -> None:
        @self.connection
        async def inner_delete(inner_user_id: int, session: AsyncSession):
            stmt = delete(UserModel).filter_by(id=inner_user_id)
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(user_id)

    async def get_or_create(
        self, order: UserOrderSchema, session: AsyncSession = None
    ) -> UserModel:
        @self.connection
        async def inner_get_or_create(
            inner_order: UserOrderSchema, session: AsyncSession
        ):
            user = await self.get(inner_order.tg_id, session)
            if user is None:
                user = await self.create(inner_order, session)
            return user

        return await inner_get_or_create(order)

    async def get_all(self, session: AsyncSession = None) -> Sequence[UserModel]:
        @self.connection
        async def inner_get_all(session: AsyncSession):
            query = select(UserModel)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_all()


class DBOrderRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(method)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    async def create(
        self, order: UserOrderSchema, session: AsyncSession = None
    ) -> OrderModel:
        @self.connection
        async def inner_create(inner_order: UserOrderSchema, session: AsyncSession):
            new_order = OrderModel(
                user_id=inner_order.tg_id,
                type_id=inner_order.data.type_id,
                shape_id=inner_order.data.shape_id,
                flavour_id=inner_order.data.flavour_id,
                confit_id=inner_order.data.confit_id,
                comment=inner_order.data.comment,
                delivery=inner_order.data.delivery,
                status="created",
                created=datetime.datetime.now(),
            )
            session.add(new_order)
            await session.commit()
            return new_order

        return await inner_create(order)

    async def get(
        self, order_id: OrderModel.id, session: AsyncSession = None
    ) -> OrderModel | None:
        @self.connection
        async def inner_get(inner_order_id: OrderModel.id, session: AsyncSession):
            query = select(OrderModel).filter_by(id=inner_order_id)
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get(order_id)

    async def update(
        self,
        order_id: OrderModel.id,
        order_status: OrderModel.status,
        session: AsyncSession = None,
    ) -> None:
        @self.connection
        async def inner_delete(
            inner_order_id: OrderModel.id,
            inner_order_status: OrderModel.status,
            session: AsyncSession,
        ):
            order = await self.get(inner_order_id, session)
            if order is None and inner_order_status in OrderModel:
                raise Exception
            stmt = (
                update(OrderModel)
                .values(status=inner_order_status)
                .filter_by(id=inner_order_id)
            )
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(order_id, order_status)

    async def delete(
        self, order_id: OrderModel.id, session: AsyncSession = None
    ) -> None:
        @self.connection
        async def inner_delete(inner_order_id: OrderModel.id, session: AsyncSession):
            stmt = delete(OrderModel).filter_by(id=inner_order_id)
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(order_id)

    async def get_by_user_id(
        self, user_id: UserModel.id, session: AsyncSession = None
    ) -> Sequence[OrderModel]:
        @self.connection
        async def inner_get_by_user_id(
            inner_user_id: UserModel.id, session: AsyncSession
        ):
            query = select(OrderModel).filter_by(user_id=inner_user_id)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_by_user_id(user_id)

    async def get_all(self, session: AsyncSession = None) -> Sequence[OrderModel]:
        @self.connection
        async def inner_get_all(session: AsyncSession):
            query = select(OrderModel)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_all()


class DBComponentRepository(Generic[M]):
    def __init__(self, session: async_sessionmaker[AsyncSession], comp_model: type[M]):
        self.session = session
        self.CompModel = comp_model

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(method)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    async def create(self, comp: ComponentSchema, session: AsyncSession = None) -> M:
        @self.connection
        async def inner_create(inner_comp: ComponentSchema, session: AsyncSession):
            new_comp = self.CompModel(
                name=inner_comp.name, desc=inner_comp.desc, available="no"
            )
            session.add(new_comp)
            await session.commit()
            return new_comp

        return await inner_create(comp)

    async def get(self, comp_name: str, session: AsyncSession = None) -> M | None:
        @self.connection
        async def inner_get(inner_comp_name: str, session: AsyncSession):
            query = select(self.CompModel).filter_by(name=inner_comp_name)
            res = await session.execute(query)
            return res.scalars().one_or_none()

        return await inner_get(comp_name)

    async def update(
        self, comp_id: int, comp_avail: str, session: AsyncSession = None
    ) -> None:
        @self.connection
        async def inner_update(
            inner_comp_id: int, inner_comp_avail: str, session: AsyncSession = None
        ):
            stmt = (
                update(self.CompModel)
                .values(available=inner_comp_avail)
                .filter_by(id=inner_comp_id)
            )
            await session.execute(stmt)
            await session.commit()

        return await inner_update(comp_id, comp_avail)

    async def delete(self, comp_id: int, session: AsyncSession = None) -> None:
        @self.connection
        async def inner_delete(inner_comp_id: int, session: AsyncSession):
            stmt = delete(self.CompModel).filter_by(id=inner_comp_id)
            await session.execute(stmt)
            await session.commit()

        return await inner_delete(comp_id)

    async def get_or_create(
        self, comp_info: ComponentSchema, session: AsyncSession = None
    ) -> M:
        @self.connection
        async def inner_get_or_create(
            inner_comp_info: ComponentSchema, session: AsyncSession
        ):
            comp = await self.get(inner_comp_info.name, session)
            if comp is None:
                comp = await self.create(inner_comp_info, session)
            return comp

        return await inner_get_or_create(comp_info)

    async def get_all(self, session: AsyncSession = None) -> Sequence[M]:
        @self.connection
        async def inner_get_all(session: AsyncSession):
            query = select(self.CompModel)
            res = await session.execute(query)
            return res.scalars().all()

        return await inner_get_all()

    async def update_desc(
        self, comp_name: str, comp_desc: str, session: AsyncSession = None
    ) -> None:
        @self.connection
        async def inner_update_desc(
            inner_comp_name: str, inner_comp_desc: str, session: AsyncSession = None
        ):
            stmt = (
                update(self.CompModel)
                .values(desc=inner_comp_desc)
                .filter_by(name=inner_comp_name)
            )
            await session.execute(stmt)
            await session.commit()

        return await inner_update_desc(comp_name, comp_desc)
