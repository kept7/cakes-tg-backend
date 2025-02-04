from pydantic import BaseModel, Field, ConfigDict


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
