from pydantic import BaseModel, Field, ConfigDict


class UserSchema(BaseModel):
    tg_id: int
    tg_username: str


class OrderSchema(BaseModel):
    type_id: int
    shape_id: int | None
    flavour_id: int
    confit_id: int | None
    comment: str | None = Field(max_length=512)


class UserOrderSchema(BaseModel):
    user: UserSchema
    order: OrderSchema

    model_config = ConfigDict(extra="forbid")


class ComponentSchema(BaseModel):
    name: str = Field(max_length=64)
    desc: str = Field(max_length=512)

    model_config = ConfigDict(extra="forbid")
