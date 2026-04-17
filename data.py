import os

from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import create_engine, Column, Integer, String

engine = create_engine('sqlite:///mydata.db', echo=True)
Base = declarative_base()
session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    password = Column(String)
    login = Column(String)
    age = Column(Integer)

Base.metadata.create_all(engine)

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def get_user_by_login(db:Session, login:str):
    return db.query(User).filter(User.login == login).first()

def create_user(db:Session, login:str, password:str, age:int):
    new_user = User(login = login, password = password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
