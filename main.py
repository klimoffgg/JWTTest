from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

load_dotenv()
app = FastAPI()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
user_db = {
    'admin' : 'secret'
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
    return payload

@app.post("/auth/login", response_model=LoginResponse)
async def login_user(user: LoginRequest):
    password = user_db.get(user.username)
    if not password or password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Неверный логин или пароль'
        )
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.username,
        "exp": expire
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