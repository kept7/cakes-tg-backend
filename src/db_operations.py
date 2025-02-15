import datetime

from typing import Callable, Coroutine, Any, TypeVar, Sequence, Generic

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from models.models import UserModel, OrderModel, ComponentModel
from models.schemes import UserOrderSchema, ComponentSchema, UserSchema


R = TypeVar("R")
M = TypeVar("M")


class DBUserRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    @connection
    async def create(
        self, user_info: UserSchema, session: AsyncSession = None
    ) -> UserModel:
        new_user = UserModel(
            id=user_info.tg_id,
            username=user_info.tg_username,
        )
        session.add(new_user)
        await session.commit()
        return new_user

    @connection
    async def get(
        self, user_id: UserOrderSchema.tg_id, session: AsyncSession = None
    ) -> UserModel | None:
        query = select(UserModel).filter_by(id=user_id)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @connection
    async def update(
        self,
        user_id: UserOrderSchema.tg_id,
        username: UserOrderSchema.tg_username,
        session: AsyncSession = None,
    ) -> None:
        stmt = update(UserModel).values(username=username).filter_by(id=user_id)
        await session.execute(stmt)
        await session.commit()

    @connection
    async def delete(
        self, user_id: UserOrderSchema.tg_id, session: AsyncSession = None
    ) -> None:
        stmt = delete(UserModel).filter_by(id=user_id)
        await session.execute(stmt)
        await session.commit()

    @connection
    async def get_or_create(
        self, order: UserOrderSchema, session: AsyncSession = None
    ) -> UserModel:
        user = self.get(order.user.tg_id, session)
        if user is None:
            user = await self.create(order.user.tg_id, order.user.tg_username, session)
        return user

    @connection
    async def get_all(self, session: AsyncSession = None) -> Sequence[UserModel]:
        query = select(UserModel)
        res = await session.execute(query)
        return res.scalars().all()


class DBOrderRepository:
    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    @connection
    async def create(
        self, order: UserOrderSchema, session: AsyncSession = None
    ) -> OrderModel:
        new_order = OrderModel(
            user_id=order.tg_id,
            type_id=order.type_id,
            shape_id=order.shape_id,
            flavour_id=order.flavour_id,
            confit_id=order.confit_id,
            comment=order.comment,
            status="created",
            created=datetime.datetime.now(),
        )
        session.add(new_order)
        await session.commit()
        return new_order

    @connection
    async def get(
        self, order_id: OrderModel.id, session: AsyncSession = None
    ) -> OrderModel | None:
        query = select(OrderModel).filter_by(id=order_id)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @connection
    async def update(
        self,
        order_id: OrderModel.id,
        order_status: OrderModel.status,
        session: AsyncSession = None,
    ) -> None:
        stmt = update(OrderModel).values(status=order_status).filter_by(id=order_id)
        await session.execute(stmt)
        await session.commit()

    @connection
    async def delete(
        self, order_id: OrderModel.id, session: AsyncSession = None
    ) -> None:
        stmt = delete(OrderModel).filter_by(id=order_id)
        await session.execute(stmt)
        await session.commit()

    @connection
    async def get_by_user_id(
        self, user_id: UserModel.id, session: AsyncSession = None
    ) -> Sequence[OrderModel]:
        query = select(OrderModel).filter_by(user_id=user_id)
        res = await session.execute(query)
        return res.scalars().all()

    @connection
    async def get_all(self, session: AsyncSession = None) -> Sequence[OrderModel]:
        query = select(OrderModel)
        res = await session.execute(query)
        return res.scalars().all()


class DBComponentRepository(Generic[M]):
    def __init__(self, session: async_sessionmaker[AsyncSession], comp_model: type[M]):
        self.session = session
        self.CompModel = comp_model

    def connection(
        self, method: Callable[..., Coroutine[Any, Any, R]]
    ) -> Callable[..., Coroutine[Any, Any, R]]:
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            async with self.session() as session:
                try:
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e

        return wrapper

    @connection
    async def create(
        self, comp_info: ComponentSchema, session: AsyncSession = None
    ) -> M:
        new_comp = self.CompModel(
            name=comp_info.name, disc=comp_info.disc, available="no"
        )
        session.add(new_comp)
        await session.commit()
        return new_comp

    @connection
    async def get(
        self, comp_name: ComponentModel.name, session: AsyncSession = None
    ) -> M | None:
        query = select().filter_by(name=comp_name)
        res = await session.execute(query)
        return res.scalars().one_or_none()

    @connection
    async def update(
        self,
        comp_id: ComponentModel.id,
        comp_avail: ComponentModel.available,
        session: AsyncSession = None,
    ) -> None:
        stmt = update(self.CompModel).values(available=comp_avail).filter_by(id=comp_id)
        await session.execute(stmt)
        await session.commit()

    @connection
    async def delete(
        self, comp_id: ComponentModel.id, session: AsyncSession = None
    ) -> None:
        stmt = delete(self.CompModel).filter_by(id=comp_id)
        await session.execute(stmt)
        await session.commit()

    @connection
    async def get_or_create(
        self, comp_info: ComponentSchema, session: AsyncSession = None
    ) -> M:
        comp = await self.get(comp_info.name, session)
        if comp is None:
            comp = await self.create(comp_info, session)
        return comp

    @connection
    async def get_all(self, session: AsyncSession = None) -> Sequence[M]:
        query = select(self.CompModel)
        res = await session.execute(query)
        return res.scalars().all()

    @connection
    async def update_disc(
        self,
        comp_name: ComponentModel.name,
        comp_disc: ComponentModel.disc,
        session: AsyncSession = None,
    ) -> None:
        stmt = update(self.CompModel).values(disc=comp_disc).filter_by(name=comp_name)
        await session.execute(stmt)
        await session.commit()
