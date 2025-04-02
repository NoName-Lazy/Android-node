import datetime

from pydantic import BaseModel
from sqlalchemy import DateTime



class ImageUploadAck(BaseModel):
    src:str

class DeleteAck(BaseModel):
    ack:str


class ImageBase(BaseModel):
    name:str=""
    url:str=""




class ImageCreate(ImageBase):
    pass


class ImageModify(ImageBase):
    img_content:str|None=None
    order:int|None=None


class ImageSimple(ImageModify):
    id:int




class Image(ImageBase):
    id:int
    item_id:int
    owner_id:str
    class Config:
        from_attributes=True

class ImageDetail(Image):
    img_content:str|None=None
    order:int|None=None


class ItemBase(BaseModel):
    title: str|None=None
    description: str | None = None
    src:str|None=None
    price:float|None=None
    vipPrice:float|None=None
    content: str | None = None



class ItemCreate(ItemBase):#创建数据是不知道id和owner_id的，所以不需要id和owner_id
    pass

class ItemModify(ItemBase):
    pass


class UserItem(BaseModel):
    name:str

class UserBase(UserItem):
    avatar: str | None = None




class Item(ItemBase):
    id: int
    owner_id: str
    star: int=0
    modify_time:datetime.datetime
    create_time:datetime.datetime
    owner:UserBase
    comment_count:int=0
    class Config:
        from_attributes = True




class UserUpdate(UserBase):
    pass


class UserCreate(UserBase):#创建用户是不知道id和items的，所以不需要id和items
    pass


class User(UserBase):#读用户数据
    id: int
    uuid: str
    class Config:
        from_attributes = True
    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict,
    # but an ORM model (or any other arbitrary object with attributes). like
    # 　user.id


class CommentBase(BaseModel):
    content:str
    order:int
    hint:str




class CommentCreate(CommentBase):
    pass


class CommentShow(CommentCreate):

    id:int
    create_time:datetime.datetime
    owner_id: str
    owner: UserBase
    class Config:
        from_attributes = True


class CommentDetail(CommentShow):
    item_id:int
    item: ItemBase




class UserDetail(User):#读用户数据
    items: list[Item] = []
    comments:list[CommentShow]=[]
    class Config:
        from_attributes = True


class UserProfile(UserDetail):#读取“我的”页面的用户数据
    email:str
    class Config:
        from_attributes = True


class ItemDetail(Item):
    content: str|None=None
    images: list[ImageSimple] = []
    comments:list[CommentShow]=[]
    class Config:
        from_attributes = True



class StarBase(BaseModel):
    item_id: int
    uuid: str
    item_title: str
    star_time: datetime.datetime
class StarCreate(StarBase):
    pass

class Star(StarBase):
    id: int

    class Config:
        from_attributes = True  # 允许从 ORM 对象转换

class CommentImageBase(BaseModel):
    imageurl:str
    content:str
class CommentImageCreate(CommentImageBase):
    pass
class CommentImage(CommentImageBase):
    id:int
    class Config:
        from_attributes = True