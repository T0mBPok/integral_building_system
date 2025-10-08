from fastapi import Depends, Request, WebSocket, WebSocketDisconnect, status
from src.exceptions import TokenNoFoundException, NoJwtException, TokenExpiredException, NoUserIdException, NoUserException
from src.user.auth import get_auth_data
from jose import jwt, JWTError
from datetime import datetime, timezone
from src.user.dao import UserDAO


async def get_token(request: Request):
    token = request.cookies.get("access_user_token")
    if not token:
        raise TokenNoFoundException
    return token

async def get_current_user(token: str = Depends(get_token)):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, key=auth_data['secret_key'], algorithms=auth_data['algorithm'])
    except JWTError:
        raise NoJwtException
    
    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if not expire or expire_time < datetime.now(timezone.utc):
        raise TokenExpiredException
    
    user_id: str = payload.get('sub')
    if not user_id:
        raise NoUserIdException
    
    user = await UserDAO.get_one_or_none_by_id(id = int(user_id))
    if not user:
        raise NoUserException
    return user