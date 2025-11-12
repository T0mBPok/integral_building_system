from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from src.user.schemas import SUserRegister, SUserAuth, SUser
from src.user.logic import UserLogic
from src.user.dependencies import get_current_user

router = APIRouter(prefix='/user', tags=['Auth'])

@router.post('/register/', response_model=SUser)
async def register_user(user_data: SUserRegister):
    return await UserLogic.register(user_data)

@router.get('/me/', response_model=SUser)
async def get_user(user: SUser = Depends(get_current_user)):
    return user

@router.get("/{id}", response_model=SUser, summary="Get user by id")
async def get_user_by_id(id: str = Path(..., description="User id")):
    user = await UserLogic.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get('/list/', response_model=list[SUser])
async def get_user_list(user: SUser = Depends(get_current_user)):
    return await UserLogic.get_except_current(current_id=str(user.id))

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    access_token = await UserLogic.auth(user_data)
    res = JSONResponse(content={
        'ok': True,
        'access_token': access_token,
        'message': "Авторизация успешна!"
    })
    res.set_cookie(
        key='access_user_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='None',
        max_age=3600
    )
    return res

@router.get("/check/")
async def check_user(user: SUser = Depends(get_current_user)):
    return {"ok": True, "user": {"id": str(user.id), "username": user.username, "email": user.email}}

@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key='access_user_token')
    return {'message': "Пользователь успешно вышел из системы!"}