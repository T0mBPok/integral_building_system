class MathException(Exception):
    pass

class NoIndicatorsException(MathException):
    """В словаре весов нет показателей"""
    pass

class MissingIndicatorsException(MathException):
    """Показатели не найдены в кубе"""
    pass

class CutNotFoundException(MathException):
    """Срез не найден в кубе"""
    pass

class NormalizationException(MathException):
    """Ошибка нормализации"""
    pass

class MethodNotFoundException(MathException):
    """Метод не найден"""
    pass

class DataNotFoundException(MathException):
    """Данные не найдены"""
    pass

class FormulaCalculationException(MathException):
    """Ошибка вычисления формулы"""
    pass

class ConflictException(MathException):
    """Конфлик созданых ресурсов"""
    pass