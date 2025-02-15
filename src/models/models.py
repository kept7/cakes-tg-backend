import datetime

from typing import Literal, Annotated

from sqlalchemy import DateTime, Integer, String, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


OrderStatus = Literal["created", "finished", "cancelled"]
DataAvailable = Literal["yes", "no", "deleted"]

str_64 = Annotated[str, 64]
str_512 = Annotated[str, 512]
int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
data_avail = Annotated[
    DataAvailable,
    mapped_column(
        Enum("yes", "no", "deleted", name="data_available_enum"), nullable=False
    ),
]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_64: String(64),
        str_512: String(512),
    }


class ComponentModel(Base):
    __abstract__ = True

    id: Mapped[int_pk]

    name: Mapped[str_64]
    disc: Mapped[str_512]

    available: Mapped[data_avail]


class UserModel(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(String, nullable=True)


class OrderModel(Base):
    __tablename__ = "order"

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("UserModel.id"))

    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("TypeDataModel.id"))
    shape_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ShapeDataModel.id"), nullable=True
    )
    flavour_id: Mapped[int] = mapped_column(Integer, ForeignKey("FlavourDataModel.id"))
    confit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ConfitDataModel.id"), nullable=True
    )

    comment: Mapped[str] = mapped_column(String, nullable=True)

    status: Mapped[OrderStatus] = mapped_column(
        Enum("created", "finished", "cancelled", name="order_status_enum"),
        nullable=False,
    )

    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TypeModel(ComponentModel):
    __tablename__ = "type"


class ShapeModel(ComponentModel):
    __tablename__ = "shape"


class FlavourModel(ComponentModel):
    __tablename__ = "flavour"


class ConfitModel(ComponentModel):
    __tablename__ = "confit"
