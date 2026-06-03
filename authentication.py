import datetime
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secretKey = "FARMStackSecret"

    def get_hashed_password(self, pwd: str) -> str:
        return self.pwd_context.hash(pwd)

    def verify_password(self, plain_pwd: str, hashed_pwd: str) -> bool:
        return self.pwd_context.verify(plain_pwd, hashed_pwd)

    def encode_token(self, user_id: str, username: str) -> str:
        payload = {
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "sub": {"id": user_id, "username": username}
        } 

        return jwt.encode(payload, self.secretKey, algorithm="HS256")
    
    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secretKey, algorithms=["HS256"])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Signature is expired"
            )
        except jwt.InvalidTokenError: 
            raise HTTPException(
                status_code=401, 
                detail="Invalid token"
            )
        
    def auth_wrapper(
            self, 
            auth: HTTPAuthorizationCredentials = Security(security) 
            ) -> dict:
        return self.decode_token(auth.credentials) 
    
    
auth_handler = AuthHandler()
