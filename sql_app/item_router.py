import mimetypes
import os
import time
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, HTTPException, Response, File
from sqlalchemy.orm import Session

from auth.db import User
from auth.users import current_active_user
from sql_app import schemas, crud, models
from sql_app.crud import get_db




app=APIRouter(tags=["items"])

@app.post("/items/", response_model=schemas.Item)
def create_item_for_user(
     item: schemas.ItemCreate,
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
        ):
    uuid=str(auth_user.id)
    print("uuid for post item:",uuid)
    return crud.create_user_item(db=db, item=item, uuid=uuid)


@app.post("/items/put/{item_id}", response_model=schemas.ItemDetail)
def modify_item_for_user(
        item_id: int,
        item: schemas.ItemModify,
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
):
    uuid = str(auth_user.id)
    db_item = crud.get_items_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != uuid:
        raise HTTPException(status_code=404, detail="The Item owner is not you")
    return crud.modify_user_item(db=db, item=item, item_id=item_id)



@app.post("/items/put/addstar/{item_id}", response_model=schemas.Item)
def add_item_star(
        item_id: int,
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
):
    uuid = str(auth_user.id)
    db_item= crud.get_items_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return crud.modify_item_star(db, item_id, 1)


@app.post("/items/put/decreasestar/{item_id}", response_model=schemas.Item)
def decrease_item_star(
        item_id: int,
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
):
    uuid = str(auth_user.id)
    db_item= crud.get_items_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return crud.modify_item_star(db, item_id, -1)





@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, keyword:str='', db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit, keyword=keyword)
    return items

@app.get("/items/auto-refresh/{time_tag}", response_model=list[schemas.Item])
# refresh by time_tag
def read_items_tag(time_tag:str,skip: int = 0, limit: int = 100, keyword:str='', db: Session = Depends(get_db)):
    print(f'Tag:{time_tag}')
    items = crud.get_items(db, skip=skip, limit=limit, keyword=keyword)
    return items

@app.get("/items/{item_id}", response_model=schemas.ItemDetail)
def read_item_detail( item_id:int,db: Session = Depends(get_db)):
    item = crud.get_items_by_id(db, id=item_id)
    return item

@app.get("/items/users/star")
def find_items_users_star(
    item_id: int,
    uuid: str,
    db: Session = Depends(get_db)
):
    star_record = db.query(models.Star).filter(
        models.Star.item_id == item_id,
        models.Star.uuid == uuid
    ).first()

    return bool(star_record)

@app.get("/stars/uuid")
def find_stars_uuid(uuid: str, db: Session = Depends(get_db)):
    # 查询所有匹配的 Star 记录
    star_records = db.query(models.Star).filter(
        models.Star.uuid == uuid
    ).all()  # 使用 .all() 返回所有记录

    if not star_records:
        raise HTTPException(status_code=404, detail="未找到相关记录")

    return star_records


@app.get("/items/users/{user_uuid}", response_model=list[schemas.Item])
def read_items(user_uuid:str, keyword:str='', db: Session = Depends(get_db)):
    # print("user_uuid:",user_uuid)
    items = crud.get_items_by_uuid(db, uuid=user_uuid,keyword=keyword)
    if not items:
        raise HTTPException(status_code=404,detail="Items not found")
    return items


@app.post("/uploadimage/",dependencies=[Depends(current_active_user)], response_model=schemas.ImageUploadAck)
async def upload_simple_image(file: UploadFile = File(...)):
    try:
        src=await uploadImageFile(file)
        return {"src":src,"name":file.filename}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))




@app.post("/uploadimage/{item_id}",response_model=schemas.Image)
async def upload_image(item_id:int,
                       file: UploadFile,
                       db: Session = Depends(get_db),
                       auth_user=Depends(current_active_user)):
    # 上传的时候，使用multipart/form-data格式，file是一个文件对象，可以直接保存，key采用file，即本函数的变量名称，value是文件对象
    uuid:str=str(auth_user.id)
    item = crud.get_items_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id!=uuid:
        raise HTTPException(status_code=404, detail="The Item owner is not you")
    try:
        image_url = await uploadImageFile(file)
        return crud.create_image(db=db, image=schemas.ImageCreate(name=file.filename,url=image_url), uuid=uuid, item_id=item_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.post("/modifyimage/{image_id}",response_model=schemas.Image)
async def modify_image(image_id:int,image_modify: schemas.ImageModify,
                       db: Session = Depends(get_db),
                       auth_user=Depends(current_active_user)):
    uuid:str=str(auth_user.id)
    item = crud.get_image(db, image_id)
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")
    if item.owner_id!=uuid:
        raise HTTPException(status_code=404, detail="The Image owner is not you")
    try:
        return crud.modify_img_by_id(db=db, image=image_modify, img_id=image_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/modifyimage/{item_id}/{image_id}",response_model=schemas.Image)
async def add_modify_image(item_id:int,image_id:int,image_modify: schemas.ImageModify,
                       db: Session = Depends(get_db),
                       auth_user=Depends(current_active_user)):
    uuid:str=str(auth_user.id)
    item = crud.get_items_by_id(db, id=item_id)
    # item = crud.get_image(db, image_id)
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")
    if item.owner_id!=uuid:
        raise HTTPException(status_code=404, detail="The Image owner is not you")
    try:
        if image_id==0:
            return crud.create_image_detail(db=db,image=image_modify,uuid=uuid, item_id=item_id)
        else:
            image_item = crud.get_image(db, image_id)
            if not image_item:
                return crud.create_image_detail(db=db, image=image_modify, uuid=uuid, item_id=item_id)
            else:
                return crud.modify_img_by_id(db=db, image=image_modify, img_id=image_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.post("/addstar", response_model=schemas.Star)
async def add_modify_star(
    item_id: int,
    uuid: str,
    item_title: str,
    db: Session = Depends(get_db),
):
    print(f"item_id: {item_id}, uuid: {uuid}, item_title: {item_title}")
    star_status = find_items_users_star(item_id, uuid, db)
    if star_status:
        print(star_status)
        raise HTTPException(status_code=400, detail="用户已点赞")


    star_time = datetime.now()
    new_star = models.Star(
        item_id=item_id,
        uuid=uuid,
        item_title=item_title,
        star_time=star_time
    )
    db.add(new_star)
    db.commit()
    db.refresh(new_star)

    return new_star

@app.delete("/deletestar")
async def delete_star(
    item_id: int,
    uuid: str,
    db: Session = Depends(get_db)
):

    star_record = db.query(models.Star).filter(
        models.Star.item_id == item_id,
        models.Star.uuid == uuid
    ).first()


    if not star_record:
        raise HTTPException(status_code=404, detail="记录不存在")


    db.delete(star_record)
    db.commit()

    return {"detail": "记录已删除"}

@app.delete("/deleteimage-byid/{image_id}",response_model=schemas.Image)
async def delete_image(image_id:int,
                       db: Session = Depends(get_db),
                       auth_user=Depends(current_active_user)):
    uuid:str=str(auth_user.id)
    item = crud.get_image(db, image_id)
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")
    if item.owner_id!=uuid:
        raise HTTPException(status_code=404, detail="The Image owner is not you")
    try:
        return crud.delete_img_by_id(db=db, img_id=image_id)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.delete("/deleteimage-bypath/images/{path}",response_model=schemas.DeleteAck)
# 需要改进，任何登录用户都可以删除图片，没有进行权限检查，可以通过建表或者建图片目录来限制，图片目录中应该只有用户自己的图片，这样就不会删除其他用户的图片
# 图片目录可以使用用户的uuid作为目录名，这样就不会有重名的问题
async def delete_image(path:str,
                       auth_user=Depends(current_active_user)):
    uuid: str = str(auth_user.id)
    print(f'delete file for path:{path} by {uuid}')
    try:
        return crud.delete_img_by_path(path)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.delete("/deleteitem-byid/{item_id}", response_model=schemas.DeleteAck)
async def delete_item(item_id:int,
                       db: Session = Depends(get_db),
                       auth_user=Depends(current_active_user)):
    uuid:str=str(auth_user.id)
    item = crud.get_items_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    # 超级用户可以删除item
    if item.owner_id!=uuid and not auth_user.is_superuser:
        raise HTTPException(status_code=404, detail="The Item owner is not you")
    try:
        s= crud.delete_item_by_item(db=db, db_item=item)
        return {'ack':s}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


async def uploadImageFile(file):
    contents = await file.read()
    # 给出1970年1月1日到现在的秒数，作为文件名
    current_time = int(time.time() * 1000)
    _, file_extension = os.path.splitext(file.filename)  # 获取文件的扩展名
    new_file_name = f"{current_time}{file_extension}"
    with open(f"images/{new_file_name}", "wb") as f:
        # with as 可以自动处理异常，会调用对象的__enter__和__exit__方法，在__exit__方法里关闭文件，并处理可能存在的异常
        f.write(contents)
    image_url = f"/images/{new_file_name}"
    return image_url


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


@app.post("/comments/{item_id}", response_model=list[schemas.CommentDetail])
def create_comment_for_item(
        item_id: int,
        comment: schemas.CommentCreate,
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
):
    uuid = str(auth_user.id)
    db_item = crud.get_items_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    crud.create_comment(db,item_id=item_id,uuid=uuid,comment=comment)
    return crud.get_comment_by_itemId(db,item_id)




@app.get("/comments/by-user/{uuid}", response_model=list[schemas.CommentDetail])
def get_comment_by_uuid(
        uuid: str,
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
):
    db_item = crud.get_comment_by_ownerId(db, uuid=uuid)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/comments/by-itemid/{item_id}", response_model=list[schemas.CommentDetail])
def get_comment_by_itemId(
        item_id: int,
        db: Session = Depends(get_db),
):
    db_item = crud.get_comment_by_itemId(db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.get("/comments/auto-refresh/by-itemid/{item_id}/{time_tag}", response_model=list[schemas.CommentDetail])
# refresh by time_tag
def get_comment_by_itemId_tag(
        item_id: int,
        time_tag:str,
        db: Session = Depends(get_db),
):
    db_item = crud.get_comment_by_itemId(db, item_id=item_id)
    print(f'tag:{time_tag}')
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item



@app.get("/comments/mine/", response_model=list[schemas.CommentDetail])
def get_comment_by_mine(
        db: Session = Depends(get_db),
        auth_user: User = Depends(current_active_user)
):
    uuid:str=str(auth_user.id)
    db_item = crud.get_comment_by_ownerId(db, uuid=uuid)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item



@app.delete("/delete-comment/{comment_id}", response_model=schemas.DeleteAck)
async def delete_comment(comment_id:int,
                       db: Session = Depends(get_db),
                       auth_user=Depends(current_active_user)):
    uuid:str=str(auth_user.id)
    item = crud.get_comment_byid(db, comment_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    #超级用户可以删除评论
    if item.owner_id!=uuid and not auth_user.is_superuser:
        raise HTTPException(status_code=404, detail="The Item owner is not you")
    try:
        db.delete(item)
        db.commit()
        return {'ack':f'Comment {comment_id} deleted'}
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/comment-image", response_model=schemas.CommentImage)
async def add_commentimage(file: UploadFile, content: str, db: Session = Depends(get_db)):
    print(f"imageurl: {file}, content: {content}")

    new_commentimage = models.CommentImage(
        imageurl=await uploadImageFile(file),
        content=content
    )
    db.add(new_commentimage)
    db.commit()
    db.refresh(new_commentimage)

    return new_commentimage