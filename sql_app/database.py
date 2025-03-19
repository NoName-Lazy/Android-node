from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./user_items.db"# sqlite数据库的路径，如果数据库不存在，会自动创建
# 数据库路径：./sql_app.db
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# """
# connect_args={"check_same_thread": False}
# ...is needed only for SQLite. It's not needed for other databases.
# ”“”

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)# 创建数据库引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 创建一个SessionLocal类，用于创建数据库会话,bind=engine表示使用上面创建的数据库引擎


Base = declarative_base()# 创建一个基类，用于创建数据库模型,所有的数据库模型都要继承这个基类，采用ORM模式进行数据库操作
