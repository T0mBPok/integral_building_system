from src.user.model import User
from src.dao.base import BaseDAO

class UserDAO(BaseDAO):
    model = User