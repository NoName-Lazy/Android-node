from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal
import os


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, user_uuid: str):
    return db.query(models.User).filter(models.User.uuid == user_uuid).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name==name).first()

def get_user_by_fuzzy_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name.like('%name%')).all()

def get_user_by_uuid(db: Session, uuid: str):
    return db.query(models.User).filter(models.User.uuid==uuid).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def update_user(db: Session, uuid: str, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.uuid == uuid).first()
    # db_user.name= user.name
    # db_user.avatar= user.avatar
    # print("db_user.to_dict()",db_user.to_dict())
    db_user.updateData(user.model_dump(exclude=("uuid","email","create_time")))
    db_user.modify_time=datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, uuid:str,email:str,user: schemas.UserCreate):
    db_user = models.User(uuid=uuid,email=email,**user.model_dump())
    db_user.create_time=datetime.now()
    db_user.modify_time=datetime.now()
    print("db_user",db_user.to_my_dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # db.refresh()方法是刷新数据库对象，使数据库对象的属性与数据库中的数据保持一致.
    return db_user



def get_items(db: Session, skip: int = 0, limit: int = 100, keyword:str=''):
    # 将返回的结果按id逆序排序，如何写？order_by(models.Item.id.desc())
    if keyword and len(keyword) >= 1:
        q = '%' + keyword + '%'
        return db.query(models.Item).outerjoin(models.Image)\
            .outerjoin(models.User)\
            .filter(or_(models.Item.title.like(q),
                        models.Item.content.like(q),
                        models.Item.description.like(q),
                        models.Image.img_content.like(q),
                        models.User.name.like(q))).order_by(models.Item.modify_time.desc()).all()
    else:
        return db.query(models.Item).order_by(models.Item.modify_time.desc()).offset(skip).limit(limit).all()

def get_items_by_id(db: Session, id:int):
    return db.query(models.Item).filter(models.Item.id==id).first()

def get_items_by_uuid(db: Session, uuid:str, keyword:str=''):
    if keyword and len(keyword) >= 1:
        q = '%' + keyword + '%'
        #使用outerjoin，某些关联为空也没问题，不要使用join，这样关联为空的Item被干掉了
        return db.query(models.Item).outerjoin(models.Image).outerjoin(models.Comment)\
            .filter(models.Item.owner_id == uuid)\
            .filter(or_(models.Item.title.like(q),
                        models.Item.content.like(q),
                        models.Item.description.like(q),
                        models.Image.img_content.like(q),
                        models.Comment.content.like(q))).order_by(models.Item.modify_time.desc()).all()

    else:
        return db.query(models.Item).filter(models.Item.owner_id == uuid).order_by(models.Item.modify_time.desc()).all()



def create_user_item(db: Session, item: schemas.ItemCreate, uuid: str):
    db_item = models.Item(**item.model_dump(), owner_id=uuid)
    db_item.star=0
    db_item.create_time=datetime.now()
    db_item.modify_time=datetime.now()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    print("db_item",db_item.to_my_dict())
    return db_item


def modify_user_item(db: Session, item: schemas.ItemModify, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    # db_item.update(**item.model_dump())# 非字典对象，不能使用字典对象的update方法
    # db_item.title = item.title
    # db_item.description = item.description
    # db_item.src = item.src
    # db_item.content = item.content
    # print("db_item.to_dict()",db_item.to_dict())
    db_item.updateData(item.model_dump(exclude=("owner_id","id","star"),exclude_none=True))
    db_item.modify_time=datetime.now()
    db.commit()
    db.refresh(db_item)
    return db_item


def modify_item_star(db: Session,  item_id: int, star_num:int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    # db_item.update(**item.model_dump())# 非字典对象，不能使用字典对象的update方法
    # db_item.title = item.title
    # db_item.description = item.description
    # db_item.src = item.src
    # db_item.content = item.content
    # print("db_item.to_dict()",db_item.to_dict())
    db_item.star=db_item.star+star_num
    if db_item.star<0:
        db_item.star=0
    db.commit()
    db.refresh(db_item)
    return db_item


def create_image(db: Session, image: schemas.ImageCreate, uuid: str,item_id:int):
    db_image = models.Image(**image.model_dump(), owner_id=uuid, item_id=item_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def create_image_detail(db: Session, image: schemas.ImageModify, uuid: str,item_id:int):
    db_image = models.Image(**image.model_dump(), owner_id=uuid, item_id=item_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def delete_item_by_id(db:Session, item_id:int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    return delete_item_by_item(db,db_item)


def delete_item_by_item(db:Session, db_item:any):
    images=db_item.images
    comments=db_item.comments
    s:str=''
    try:
        for image in images:
            delete_img_by_id(db,image.id)
        for comment in comments:
            delete_comment(db,comment.id)
        if db_item.src:
            url:str=db_item.src
            url=url[1:]
            delete_file(url)
        db.delete(db_item)
        db.commit()
        s=f"Item :{db_item.id} deleted"
    except Exception as e:
        print(e)
        s=''+e
    return s


def modify_img_by_id(db: Session, image: schemas.ImageModify, img_id: int):
    db_item = db.query(models.Image).filter(models.Image.id == img_id).first()
    db_item.updateData(image.model_dump(exclude=("owner_id","id","item_id"),exclude_none=True))
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_img_by_id(db: Session, img_id: int):
    db_item = db.query(models.Image).filter(models.Image.id == img_id).first()
    url:str=db_item.url
    url=url[1:]
    # 注意，url头部有一个斜杠，需要去掉，不去掉，路径不同，删除失败

    delete_file(url)
    db.delete(db_item)
    db.commit()
    return db_item

def delete_img_by_path(filepath: str):
    url="images/"+filepath
    if filepath=='logo.png':# 不删除该文件
        return {"ack":filepath}
    s=delete_file(url)
    return {"ack":s}



def delete_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        s=f"文件 {filename} 删除成功！"
        print(s)
        return s
    else:
        s=f"文件 {filename} 不存在。"
        print(s)
        return s


def get_images_by_item(db: Session, item_id: int):
    return db.query(models.Image).filter(models.Image.item_id == item_id).all()



def get_image(db: Session, id: int):
    return db.query(models.Image).filter(models.Image.id == id).first()



def create_comment(db: Session, item_id:int, uuid: str,comment:schemas.CommentCreate):
    db_item = models.Comment(**comment.model_dump(), item_id=item_id)
    db_item.owner_id=uuid
    db_item.create_time=datetime.now()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    print("db_comment",db_item.to_my_dict())
    return db_item


def delete_comment(db: Session, id:int):
    db_item = db.query(models.Comment).filter(models.Comment.id == id).first()
    db.delete(db_item)
    db.commit()
    return db_item


def get_comment_byid(db: Session, id:int):
    db_item = db.query(models.Comment).filter(models.Comment.id == id).first()
    return db_item

def get_comment_by_ownerId(db: Session, uuid:str):
    db_item = db.query(models.Comment).filter(models.Comment.owner_id == uuid).order_by(models.Comment.create_time.desc()).all()
    return db_item

def get_comment_by_itemId(db:Session,item_id:int):
    return db.query(models.Comment).filter(models.Comment.item_id==item_id).order_by(models.Comment.create_time.desc()).all()

