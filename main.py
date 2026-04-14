import hashlib

from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
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
user_db = {
    'admin' : {"password":hash_string('secret'), "age": 0}
}
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
async def age_calculate(payload: dict = Depends(token_to_payload)):
    new_age = user_db[payload.get("sub")]["age"] + 10
    return {"new_age": new_age}

@app.post('/auth/register')
async def register(user: RegisterRequest):
    if user.username in user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = 'Такой username уже существует'
        )
    user_db[user.username] = {"password": hash_string(user.password), "age": user.age}

@app.post("/auth/login", response_model=LoginResponse)
async def login_user(user: LoginRequest):
    password = user_db.get(user.username)["password"]
    user_password = hash_string(user.password)
    if not password or password != user_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Неверный логин или пароль'
        )
    expire = datetime.now(tz=SERVER_TIME_ZONE) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.username,
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return LoginResponse(access_token=token, token_type = 'bearer')

@app.get('/auth/me')
async def get_current_user(payload: dict = Depends(token_to_payload)):
    username = payload.get("sub")
    return {"username": username, "role": "user"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)