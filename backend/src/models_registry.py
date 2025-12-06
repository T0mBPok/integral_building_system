from src.module.model import Module
from src.level.model import Level
from src.project.model import Project
from src.function.model import Function
from src.indicator.model import Indicator
from src.user.model import User

User.model_rebuild()
Module.model_rebuild()
Level.model_rebuild()
Project.model_rebuild()
Function.model_rebuild()
Indicator.model_rebuild()
