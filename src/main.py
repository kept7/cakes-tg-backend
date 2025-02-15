import asyncio
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.user_router import router as user_router
from routers.order_router import router as order_router
from routers.comp_router import router as comp_router

from settings.config import settings

from sessions.db_sessions import db

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
    # await db_order_info.drop_database()
    await db.setup_database()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("main:app", reload=True)
