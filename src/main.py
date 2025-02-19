import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.settings.config import settings
from src.sessions.db_sessions import db

from src.routers.user_router import router as user_router
from src.routers.order_router import router as order_router
from src.routers.comp_router import router as comp_router


app = FastAPI()

origins = [
    settings.BASE_URL_1,
    settings.BASE_URL_2,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(order_router)
app.include_router(comp_router)


async def main():
    # await db.drop_database()
    await db.setup_database()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("main:app", reload=True)

''' 
TODO: 
    1) при изменении статуса заказа на вариант 
не предусмотренный валится дб при попытке  получить 
информацию о заказах. get/order -> 500
    2) продумать более жёсткую валидацию данных
и реализовать её
    3) обработать все ситуации, когда пользователь
пытается достать какой-то объект, но его нет
(попытка удалить компонент торта, которого нет в дб)
'''