import datetime
import enum

from typing import Literal

from sqlalchemy import DateTime, Integer, String, Enum, JSON
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

OrderStatus = Literal["created", "delivering", "finished", "cancelled"]


class Base(DeclarativeBase): ...


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tg_username: Mapped[str] = mapped_column(String, nullable=True)

class OrderDataModel(Base):
    __tablename__ = "order_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    # 2 table setup
    # user_id ForeignKey

    # 1 table setup
    # tg_id
    # tg_username
    
    # Problem order configs
    # Solution 1 Literal = bad scalability
    # Solution 2 DB entry/JSON
    # Solution 3 store order configuration as is
    #   order_config: Mapped[str] = json.dumps({'type': 'a', ...})
    
    type: Mapped[str]
    shape: Mapped[str]
    filling: Mapped[str]
    confit: Mapped[str]
    
    comment: Mapped[str]

    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            "created", "delivering", "finished", "cancelled",
            name="order_status_enum"
        ),
        nullable=False
    )
    
    created: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class DBInit:
    def __init__(self, bd_name: str):
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{bd_name}.db")
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
