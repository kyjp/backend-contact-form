from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session


# 接続したいDBの基本情報を設定
user_name = "user"
password = "password"
host = "db"  # docker-composeで定義したMySQLのサービス名
database_name = "sample_db"

DATABASE = 'mysql://user:password@db:3306/sample_db'

# DBとの接続
ENGINE = create_engine(DATABASE)

# Sessionの作成
session = scoped_session(
    # ORM実行時の設定。自動コミットするか、自動反映するか
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=ENGINE
    )
)

def create_new_session():
    return  scoped_session(sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=ENGINE))

# modelで使用する
Base = declarative_base()
# DB接続用のセッションクラス、インスタンスが作成されると接続する
Base.query = session.query_property()