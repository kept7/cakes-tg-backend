from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

app = FastAPI()

class NewOrder(BaseModel):
    tg_username: str
    id: int
    creation_date: str
    order_status: str

class OrderInfo(BaseModel):
    type: str
    shape: str
    flavour: str
    confi: str
    design: str

orders = [
    {
        "tg_username": "@kept7",
        "id": 1,
        "date": "12, January 2023",
        "status": "Completed",
    },
    {
        "tg_username": "@hadrizi",
        "id": 2,
        "date": "24, January 2024",
        "status": "Delivery",
    },
    {
        "tg_username": "@kept7",
        "id": 3,
        "date": "8, February 2024",
        "status": "Created",
    },
]

orders_info = [
    {
        "id": 1,
        "type": "bento",
        "shape": "round",
        "flavour": "salty-caramel",
        "confi": "",
        "design": "Green color, nothing else",
    },
    {
        "id": 2,
        "type": "cake > 1 kg",
        "shape": "",
        "flavour": "red-velvet",
        "confi": "strawberry",
        "design": "fjdsfsdhfjsdhfsj",
    },
    {
        "id": 3,
        "type": "cake to go",
        "shape": "heart",
        "flavour": "red-velvet",
        "confi": "cherry",
        "design": "my name is my name is slimshady",
    },
]


@app.get(
    "/orders",
    tags=["Заказы"],
    summary="Получить информацию о всех заказах конкретного пользователя",
)
def read_orders(username: str):
    orders_list = []

    for order in orders:
        if order["tg_username"] == username:
            orders_list.append(order)

    if len(orders_list):
        return orders_list
    else:
        raise HTTPException(status_code=404, detail="This user has not placed an order yet")


@app.get(
    "/orders_info",
    tags=["Заказы"],
    summary="Получить детали всех заказов конкретного пользователя",
)
def read_orders_info(username: str):
    try:
        orders_list = read_orders(username)
    except HTTPException:
        raise HTTPException(status_code=404, detail="This user has not placed an order yet")

    user_orders_list = []
    for id_order in orders_list:
        for order in orders_info:
            if order["id"] == id_order:
                user_orders_list.append(order)

    return user_orders_list


@app.get(
    "/orders/{order_id}",
    tags=["Заказы"],
    summary="Получить конкретный заказ",
)
def get_order(order_id: int):
    for order in orders_info:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.post(
    "/orders",
    tags=["Заказы"],
    summary="Добавить заказ"
)
def create_order(new_order: OrderInfo):
    orders_info.append(
        {
            "id": len(orders_info) + 1,
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
