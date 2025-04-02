from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,Float,DateTime
from sqlalchemy.orm import relationship, DeclarativeBase


# from .database import Base

class Base(DeclarativeBase):
    pass

def my_model_dump(self,data:Base,exclude:tuple=()):
    return {c.name: getattr(self, c.name) for c in data.__table__.columns if c.name not in exclude}

class User(Base):# 所有对象表都要继承Base类
    __tablename__ = "users"#表名

    id = Column(Integer, primary_key=True)#主键字段
    uuid= Column(String, unique=True, index=True)
    name= Column(String, unique=True)
    email= Column(String, unique=True)
    avatar= Column(String)
    create_time=Column(DateTime)
    modify_time=Column(DateTime)
    items = relationship("Item", back_populates="owner")
    comments=relationship("Comment",back_populates="owner")


    def to_my_dict(self):
        # return my_model_dump(self,self,exclude=("items"))
        return my_model_dump(self,self) #数据字段里的relation字段不在__table__.columns里，所以不会被返回，因此不需要exclude参数

    def updateData(self,data:dict):
        for key in data:
            setattr(self,key,data[key])
        return self


    # Item的列表对象
    #关联Item表，back_populates="owner"表示在Item表中也有一个owner字段，用于关联User表，这样就可以通过User表找到Item表，也可以通过Item表找到User表
    #User表对item是一对多的关系，一个用户可以有多个item，所以在User表中有一个items字段，用于关联Item表
    #而Item表对user是多对一的关系，一个item只能属于一个用户，所以在Item表中有一个owner字段，用于关联User表，并且有ForeignKey("users.id")字段，表示外键关联User表


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    price=Column(Float)
    vipPrice=Column(Float)
    src= Column(String)
    content= Column(String)
    star=Column(Integer)
    create_time = Column(DateTime)
    modify_time=Column(DateTime)
    owner_id = Column(String, ForeignKey("users.uuid"))#外键字段，关联users表的uuid字段
    owner = relationship("User", back_populates="items")
    images= relationship("Image", back_populates="item")
    comments=relationship("Comment",back_populates="item")
    @property
    def comment_count(self):
        return len(self.comments)
    # 该属性不作为原始的列表字段，而是一个计算属性，返回评论的数量

    def to_my_dict(self):
        # return my_model_dump(self, self, exclude=("owner","images"))
        return my_model_dump(self, self)#数据字段里的relation字段不在__table__.columns里，所以不会被返回，因此不需要exclude参数

    def updateData(self, data: dict):
        for key in data:
            setattr(self, key, data[key])
        return self


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    url = Column(String, index=True)
    name= Column(String)
    order=Column(Integer)
    img_content=Column(String)
    item_id = Column(Integer, ForeignKey("items.id"))
    item = relationship("Item", back_populates="images")
    owner_id = Column(String, ForeignKey("users.uuid"))
    def to_my_dict(self):
        # return my_model_dump(self, self, exclude=("item"))
        return my_model_dump(self, self)#数据字段里的relation字段不在__table__.columns里，所以不会被返回，因此不需要exclude参数

    def updateData(self, data: dict):
        for key in data:
            setattr(self, key, data[key])
        return self


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    content= Column(String)
    order=Column(Integer)
    hint=Column(String)
    item_id = Column(Integer, ForeignKey("items.id"))
    item=relationship("Item",back_populates="comments")
    owner_id = Column(String, ForeignKey("users.uuid"))
    owner=relationship("User",back_populates="comments")
    create_time=Column(DateTime)

    def to_my_dict(self):
        # return my_model_dump(self, self, exclude=("item"))
        return my_model_dump(self, self)#数据字段里的relation字段不在__table__.columns里，所以不会被返回，因此不需要exclude参数

    def updateData(self, data: dict):
        for key in data:
            setattr(self, key, data[key])
        return self

class Star(Base):
    __tablename__ = "stars"

    id = Column(Integer, primary_key=True)  # 主键
    uuid = Column(String, ForeignKey("users.uuid"))  # 外键，关联 users.uuid
    item_id = Column(Integer, ForeignKey("items.id"))  # 外键，关联 items.id
    item_title = Column(String)  # 文章标题
    star_time = Column(DateTime)  # 点赞时间

class CommentImage(Base):
    __tablename__ = "commentimages"

    id = Column(Integer, primary_key=True)
    imageurl = Column(String)
    content = Column(String, ForeignKey("comments.content"))
