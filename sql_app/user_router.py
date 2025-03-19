import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.db import User
from auth.schemas import UserRead, UserUpdate
from auth.users import fastapi_users, current_active_user
from sql_app import schemas, crud
from sql_app.crud import get_db

app= APIRouter(prefix="/users",tags=["users"])

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate)
)


@app.post("/rename/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),auth_user: User = Depends(current_active_user)):
    db_user=crud.get_user_by_name(db,name=user.name)
    db_email=crud.get_user_by_email(db,email=user.name)# 用户名是其它注册用户的email也不行
    uuid: str = str(auth_user.id)
    if db_email and db_email.uuid != uuid:
        raise HTTPException(status_code=400, detail="name can't be registered to other user's email")

    print('uuid:',uuid)
    if db_user and db_user.uuid!=uuid:
        raise HTTPException(status_code=400, detail="name already registered")
    db_user=crud.get_user_by_uuid(db,uuid=uuid)
    if db_user:
        return crud.update_user(db=db, uuid=uuid,user=user)
    else:
        return crud.create_user(db=db, uuid=uuid,email=auth_user.email,user=user)




@app.get("/", dependencies=[Depends(current_active_user)],response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users




@app.get("/mine/", response_model=schemas.UserProfile)
#最后一个斜杠要给，否则被认定为非法路径，返回未授权
def read_my_profile( db: Session = Depends(get_db),auth_user: User = Depends(current_active_user)):
    uuid:str=str(auth_user.id)
    print('uuid:',uuid)
    # 将auth_user字符串化并打印
    # print('auth_user:',dir(auth_user))
    db_user = crud.get_user_by_uuid(db,uuid=uuid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



@app.get("/items/{user_uuid}",dependencies=[Depends(current_active_user)], response_model=schemas.UserDetail)
def read_user(user_uuid: str, db: Session = Depends(get_db)):
# def read_user(user_uuid: str, db: Session = Depends(get_db)):
    print('user_uuid:',user_uuid)
    # uuid:str=str(auth_user.id)
    # print('uuid:',uuid)
    # if user_uuid!=uuid:
    #     raise HTTPException(status_code=400,detail="You can only get your own information")
    db_user = crud.get_user_by_uuid(db,uuid=user_uuid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

