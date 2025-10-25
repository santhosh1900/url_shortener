from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

load_dotenv()

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.username = os.getenv("ADMIN")
        self.password = os.getenv("ADMIN_PASSWORD")
        self.algorithm = "HS256"
        self.jwtSecret = os.getenv("JWT_SECRET")

    def createAccessToken(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.jwtSecret, algorithm=self.algorithm)

    async def getCurrentAdmin(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            payload = jwt.decode(credentials.credentials, self.jwtSecret, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            if username != self.username:
                raise HTTPException(status_code=401, detail="Invalid token")
            return username
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
