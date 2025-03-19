import mimetypes
import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException,UploadFile,Response
from sqlalchemy.orm import Session
import time

from . import crud, models, schemas
from .database import SessionLocal, engine
from contextlib import asynccontextmanager
from auth.db import User, create_db_and_tables
from auth.schemas import UserCreate, UserRead, UserUpdate
from auth.users import auth_backend, current_active_user, fastapi_users

# https://fastapi-users.github.io/fastapi-users/latest/

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
    yield

models.Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),auth_user: User = Depends(current_active_user)):
    db_user=crud.get_user_by_name(db,name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="name already registered")
    db_user=crud.get_user_by_uuid(db,uuid=auth_user.id)
    if db_user:
        return crud.update_user(db=db, uuid=auth_user.id,user=user)
    else:
        user.uuid = auth_user.id
        return crud.create_user(db=db, user=user)


@app.get("/users/", dependencies=[current_active_user],response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}",dependencies=[current_active_user], response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/",dependencies=[current_active_user], response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items



@app.post("/uploadimage/{user_id}/{item_id}",dependencies=[current_active_user],response_model=schemas.Image)
async def upload_image(file: UploadFile,user_id:int,item_id:int,db: Session = Depends(get_db)):
    # 上传的时候，使用multipart/form-data格式，file是一个文件对象，可以直接保存，key采用file，即本函数的变量名称，value是文件对象
    try:
        contents = await file.read()
        #给出1970年1月1日到现在的秒数，作为文件名
        current_time=int(time.time()*1000)
        _,file_extension=os.path.splitext(file.filename)#获取文件的扩展名
        new_file_name=f"{current_time}{file_extension}"
        with open(f"images/{new_file_name}", "wb") as f:
            # with as 可以自动处理异常，会调用对象的__enter__和__exit__方法，在__exit__方法里关闭文件，并处理可能存在的异常
            f.write(contents)
        image_url=f"/images/{file.filename}"
        return crud.create_image(db=db, image=schemas.ImageCreate(url=image_url), user_id=user_id, item_id=item_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


#显示images文件夹下的图片
@app.get("/images/{image_path}")
async def get_image(image_path:str):
    try:
        with open(f"images/{image_path}", "rb") as f:
            contents= f.read()
        mime_type,_=mimetypes.guess_type(image_path)
        return Response(content=contents,media_type=mime_type)
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))


if __name__ == "__main__":
    uvicorn.run("auth.app:app", host="0.0.0.0", log_level="info",port=80,reload=True)