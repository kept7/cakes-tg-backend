from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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


class DBInit:
    def __init__(self, bd_name: str):
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{bd_name}.db")
        self.new_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.new_session() as session:
            yield session

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
