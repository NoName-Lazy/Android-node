from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from auth import auth_router
from auth.db import create_db_and_tables
from sql_app import models
from sql_app import user_router,item_router
from sql_app.database import SessionLocal, engine


# https://fastapi.tiangolo.com/learn/

# https://fastapi-users.github.io/fastapi-users/latest/

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield

models.Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)

# 允许跨域操作
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，也可以指定具体源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

app.include_router(auth_router.app)
app.include_router(user_router.app)
app.include_router(item_router.app)




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info",port=80,reload=True)