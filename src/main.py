from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field, ConfigDict


app = FastAPI()

class OrderInfo(BaseModel):
    tg_id: int
    tg_username: str
    creation_date: str
    order_status: str


class OrderData(BaseModel):
    type: str
    shape: str
    flavour: str
    confi: str
    design: str = Field(max_length=1000)


class OrderSchema(OrderData, OrderInfo):
    model_config = ConfigDict(extra="forbid")


orders_info = [
    {
        "order_id": 1001,
        "tg_id": 1657854937958,
        "tg_username": "@kept7",
        "date": "12, January 2023",
        "status": "Completed",
    },
    {
        "order_id": 1002,
        "tg_id": 4698678923409230,
        "tg_username": "@hadron",
        "date": "24, January 2024",
        "status": "Delivery",
    },
    {
        "order_id": 1003,
        "tg_id": 1657854937958,
        "tg_username": "@kept7",
        "date": "8, February 2024",
        "status": "Created",
    },
]

orders_data = [
    {
        "order_id": 1001,
        "type": "bento",
        "shape": "round",
        "flavour": "salty-caramel",
        "confi": "",
        "design": "Green color, nothing else",
    },
    {
        "order_id": 1002,
        "type": "cake > 1 kg",
        "shape": "",
        "flavour": "red-velvet",
        "confi": "strawberry",
        "design": "fjdsfsdhfjsdhfsj",
    },
    {
        "order_id": 1003,
        "type": "cake to go",
        "shape": "heart",
        "flavour": "red-velvet",
        "confi": "cherry",
        "design": "my name is my name is slimshady",
    },
]

"""
TODO:
    complete read_orders_info func
    change create_order func
"""


@app.get(
    "/orders",
    tags=["Заказы"],
    summary="Получить информацию о всех заказах конкретного пользователя",
)
def read_orders_info(user_id: int):
    orders_list = []

    for order in orders_info:
        if order["tg_id"] == user_id:
            orders_list.append(order)

    if orders_list:
        return orders_list
    else:
        raise HTTPException(
            status_code=404, detail="This user has not placed an order yet"
        )


@app.get(
    "/orders/info",
    tags=["Заказы"],
    summary="Получить детали всех заказов конкретного пользователя",
)
def read_orders_data(user_id: int):
    orders_list = read_orders_info(user_id)

    user_orders_list = []
    for order in orders_list:
        for ord_info in orders_data:
            if ord_info["order_id"] == order["order_id"]:
                user_orders_list.append(ord_info)

    return user_orders_list


@app.get(
    "/orders/{order_id}",
    tags=["Заказы"],
    summary="Получить конкретный заказ",
)
def get_order_info(order_id: int):
    for ord_info in orders_data:
        if ord_info["order_id"] == order_id:
            return ord_info
    raise HTTPException(status_code=404, detail="Order not found")


@app.post("/orders", tags=["Заказы"], summary="Добавить заказ")
def create_order(new_order: OrderSchema):
    new_order_id = orders_info[-1]["order_id"] + 1

    orders_info.append({
        "order_id": new_order_id,
        "tg_id": new_order.tg_id,
        "tg_username": new_order.tg_username,
        "date": new_order.creation_date,
        "status": new_order.order_status,
    })

    orders_data.append(
        {
            "order_id": new_order_id,
            "type": new_order.type,
            "shape": new_order.shape,
            "flavour": new_order.flavour,
            "confi": new_order.confi,
            "design": new_order.design,
        }
    )
    return {"ok": True, "msg": "Order was created"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
