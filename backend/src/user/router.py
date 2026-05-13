from fastapi import APIRouter, Depends, Path, Response, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
from src.config import get_cookie_settings
from src.user.schemas import SUserRegister, SUserAuth, SUser
from src.user.logic import UserLogic
from src.user.dependencies import get_current_user

router = APIRouter(prefix='/user', tags=['User'])

@router.post('/register/', response_model=SUser)
async def register_user(user_data: SUserRegister):
    return await UserLogic.register(user_data)

@router.get('/me/', response_model=SUser)
async def get_user(user: SUser = Depends(get_current_user)):
    return user

@router.get('/list/', response_model=list[SUser])
async def get_user_list(user: SUser = Depends(get_current_user)):
    return await UserLogic.get_except_current(current_id=str(user.id))

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    access_token = await UserLogic.auth(user_data)
    cookie_settings = get_cookie_settings()
    res = JSONResponse(content={
        'ok': True,
        'access_token': access_token,
        'message': "Авторизация успешна!"
    })
    res.set_cookie(
        key='access_user_token',
        value=access_token,
        httponly=True,
        secure=cookie_settings["secure"],
        samesite=cookie_settings["samesite"],
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

@router.get("/{id}", response_model=SUser, summary="Get user by id")
async def get_user_by_id(id: str = Path(..., description="User id")):
    try:
        user_id = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")
    user = await UserLogic.get_one_or_none_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
