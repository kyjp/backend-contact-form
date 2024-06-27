from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Dict
from starlette.middleware.cors import CORSMiddleware  # CORSを回避するために必要
from sqlalchemy.orm import Session  # SQLAlchemyセッションのインポート
from db import session, create_new_session  # DBと接続するためのセッション
from models import ContactTable  # 今回使うモデルをインポート
from starlette_csrf import CSRFMiddleware
import time

app = FastAPI()

cookie_attribute = {
    "secret": 'YOUSECRET',
    "cookie_samesite": None,
    "cookie_secure": True,
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    CSRFMiddleware,
    **cookie_attribute
)

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-process-Time'] = str(process_time)
    return response

# Pydanticモデルの定義
class Contact(BaseModel):
    id: int
    name: str
    email: str
    content: str

    class Config:
        orm_mode = True

class CreateContact(BaseModel):
    name: str
    email: str
    content: str

class ValidationErrorResponse(BaseModel):
    error: List[Dict]

    class Config:
        json_schema_extra = {
            "example": {
                "error": [
                    {
                        "name": "name",
                        "message": "field required"
                    },
                    {
                        "name": "email",
                        "message": "field required"
                    },
                    {
                        "name": "content",
                        "message": "field required"
                    }
                ]
            }
        }

# カスタム例外ハンドラー
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"name": err["loc"][-1], "message": err["msg"]}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": errors}
    )

# ----------APIの実装------------
@app.get("/api/csrf_token", tags=["token"])
def get_csrf_token():
    return "トークンを発行しました。"

@app.get("/contacts", response_model=List[Contact])
def read_contacts():
    new_session = create_new_session()
    contacts = new_session.query(ContactTable).all()
    return contacts

# idにマッチする情報を取得 GET
@app.get("/contact/{contact_id}", response_model=Contact)
def read_contact(contact_id: int):
    new_session = create_new_session()
    contact = new_session.query(ContactTable).filter(ContactTable.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

# 情報を登録 POST
@app.post("/contact", response_model=Contact, status_code=status.HTTP_201_CREATED, responses={422: {"model": ValidationErrorResponse}})
async def create_contact(contact: CreateContact):
    new_session = create_new_session()
    db_contact = ContactTable(name=contact.name, email=contact.email, content=contact.content)
    new_session.add(db_contact)
    new_session.commit()
    new_session.refresh(db_contact)
    return db_contact

# 情報を確認 POST
@app.post("/confirm", response_model=CreateContact, responses={422: {"model": ValidationErrorResponse}})
async def confirm_contact(contact: CreateContact):
    if not contact.name or not contact.email or not contact.content:
        raise HTTPException(status_code=404, detail="送信データが間違っています")
    return contact