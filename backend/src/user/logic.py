from src.user.dao import UserDAO
from src.exceptions import UserAlreadyExistsException, PasswordMismatchException, IncorrectEmailOrPasswordException
from src.user.auth import get_pass_hashed, authenticate_user, create_token


class UserLogic(UserDAO):
    @classmethod
    async def register(cls, user_data) -> dict:
        user = await cls.get_one_or_none(email=user_data.email)
        if user:
            raise UserAlreadyExistsException
        
        print(user_data)
        hashed_password = get_pass_hashed(user_data.password)
        
        new_user = await UserDAO.add(
            email = user_data.email,
            username = user_data.username,
            hashed_password = hashed_password
        )
        return new_user

    async def auth(user_data) -> dict:
        check = await authenticate_user(**user_data.model_dump())
        if check is None:
            raise IncorrectEmailOrPasswordException
        return create_token({'sub': str(check.id)})