from src.user.models import User
from src.dao.base import BaseDAO

class UserDAO(BaseDAO):
    model = User