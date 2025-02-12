import datetime

from typing import Literal

from sqlalchemy import DateTime, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


OrderStatus = Literal["created", "finished", "cancelled"]
DataAvailable = Literal["yes", "no", "deleted"]


class Base(DeclarativeBase): ...


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String, nullable=True)


class OrderDataModel(Base):
    __tablename__ = "order_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("UserModel.id"))

    type_id: Mapped[int] = mapped_column(String, ForeignKey("TypeDataModel.id"))
    shape_id: Mapped[int] = mapped_column(
        String, ForeignKey("ShapeDataModel.id"), nullable=True
    )
    flavour_id: Mapped[int] = mapped_column(String, ForeignKey("FlavourDataModel.id"))
    confit_id: Mapped[int] = mapped_column(
        String, ForeignKey("ConfitDataModel.id"), nullable=True
    )

    comment: Mapped[str] = mapped_column(String, nullable=True)

    status: Mapped[OrderStatus] = mapped_column(
        Enum("created", "finished", "cancelled", name="order_status_enum"),
        nullable=False,
    )

    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TypeDataModel(Base):
    __tablename__ = "type_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    type: Mapped[str] = mapped_column(String, nullable=False)
    disc: Mapped[str] = mapped_column(String, nullable=False)

    available: Mapped[DataAvailable] = mapped_column(
        Enum("yes", "no", "deleted", name="data_available_enum"), nullable=False
    )


class ShapeDataModel(Base):
    __tablename__ = "shape_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    shape: Mapped[str] = mapped_column(String, nullable=False)
    disc: Mapped[str] = mapped_column(String, nullable=False)

    available: Mapped[DataAvailable] = mapped_column(
        Enum("yes", "no", "deleted", name="data_available_enum"), nullable=False
    )


class FlavourDataModel(Base):
    __tablename__ = "flavour_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    flavour: Mapped[str] = mapped_column(String, nullable=False)
    disc: Mapped[str] = mapped_column(String, nullable=False)

    available: Mapped[DataAvailable] = mapped_column(
        Enum("yes", "no", "deleted", name="data_available_enum"), nullable=False
    )


class ConfitDataModel(Base):
    __tablename__ = "confit_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    confit: Mapped[str] = mapped_column(String, nullable=False)
    disc: Mapped[str] = mapped_column(String, nullable=False)

    available: Mapped[DataAvailable] = mapped_column(
        Enum("yes", "no", "deleted", name="data_available_enum"), nullable=False
    )


class DBInit:
    def __init__(self, db_name: str):
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_name}.db")
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def setup_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
