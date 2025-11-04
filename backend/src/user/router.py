from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from src.user.schemas import SUserRegister, SUserAuth, SUser
from src.user.logic import UserLogic
from src.user.dependencies import get_current_user


router = APIRouter(prefix='/user', tags=['Auth'])

@router.post('/register/', response_model=SUser)
async def register_user(user_data: SUserRegister) -> dict:
    new_user = await UserLogic.register(user_data)
    return new_user

@router.get('/me/', response_model=SUser)
async def get_user(user: str = Depends(get_current_user)):
    return user

@router.get('/list/', response_model = list[SUser])
async def get_user_list(user: str = Depends(get_current_user)):
    return await UserLogic.get_except_current(current_id=int(user.id))

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth) -> dict:
    access_token = await UserLogic.auth(user_data)
    response = JSONResponse(content={
        'ok': True,
        'access_token': access_token,
        'message': "Авторизация успешна!"   
    })
    response.set_cookie(key='access_user_token', value=access_token, httponly=True, secure=True, samesite='None', max_age=3600)
    return response

@router.get("/check/")
async def check_user(user: str = Depends(get_current_user)):
    return {"ok": True, "user": {"id": user.id, "username": user.username, "email": user.email}}

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key='access_user_token')
    return {'message': "Пользователь успешно вышел из системы!"}