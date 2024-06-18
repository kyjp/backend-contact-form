# -*- coding: utf-8 -*-
# モデルの定義
from sqlalchemy import Column, Integer, String, Text
from pydantic import BaseModel
from db import Base
from db import ENGINE


# contactテーブルのモデルContactTableを定義
class ContactTable(Base):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)


# POSTやPUTのとき受け取るRequest Bodyのモデルを定義
class Contact(BaseModel):
    name: str
    email: str
    content: str


def main():
    # テーブルが存在しなければ、テーブルを作成
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":
    main()