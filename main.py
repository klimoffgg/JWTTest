import hashlib
# import database
from data import get_db, create_user, get_user_by_login, User
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from zoneinfo import ZoneInfo

load_dotenv()
app = FastAPI()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SERVER_TIME_ZONE = ZoneInfo('UTC')

security = HTTPBearer()

def hash_string(string):
    textb = string.encode('utf-8')
    hash = hashlib.sha256(textb)
    hashs = hash.hexdigest()
    return hashs

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    age: int

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
async def token_to_payload(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный токен"
        )
    time = payload.get("exp")
    datetime_exporation = datetime.fromtimestamp(time, tz = SERVER_TIME_ZONE)
    datetime_now = datetime.now(tz=SERVER_TIME_ZONE)
    if datetime_exporation < datetime_now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Время жизни токена истекло'
        )
    return payload
@app.get('/age')
async def age_calculate(payload: dict = Depends(token_to_payload), db: Session = Depends(get_db)):
    user = get_user_by_login(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"new_age": user.age + 10}

@app.post('/auth/register')
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_login(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = 'Такой username уже существует'
        )
    create_user(db, user_data.username, hash_string(user_data.password), user_data.age)

@app.post("/auth/login", response_model=LoginResponse)
async def login_user(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_login(db, user_data.username)
    if not user or user.password != hash_string(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Неверный логин или пароль'
        )
    expire = datetime.now(tz=SERVER_TIME_ZONE) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.login,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return LoginResponse(access_token=token, token_type = 'bearer')

@app.get('/auth/me')
async def get_current_user(payload: dict = Depends(token_to_payload), db: Session = Depends(get_db)):
    username = payload.get("sub")
    user = get_user_by_login(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.login, "role": "user"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)