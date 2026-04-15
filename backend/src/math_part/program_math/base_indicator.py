import numpy as np
from .cube import Cube
from .exceptions import ConflictException, FormulaCalculationException, MethodNotFoundException, MissingIndicatorsException

class BaseIndicator(Cube):
    """Класс для работы с базовыми показателями и их преобразованием"""
    
    def __init__(self, population_formatted=None, name="Население"):
        super().__init__(population_formatted, name)
        
    def fill_missing_values(self, indicator_name, method='zero', custom_value=None):
        """Заменяет пропущенные значения в указанном показателе"""
        if indicator_name not in self.indicator_to_idx:
            raise MissingIndicatorsException(f"Показатель '{indicator_name}' не найден в кубе")

        indicator_idx = self.indicator_to_idx[indicator_name]
        data = self.cube[:, :, indicator_idx]

        mask = np.isnan(data)

        if method == 'zero':
            fill_value = 0
        elif method == 'mean':
            # Среднее значение по не-NaN данным
            fill_value = np.nanmean(data)
        elif method == 'median':
            # Медиана по не-NaN данным
            fill_value = np.nanmedian(data)
        elif method == 'min':
            # Минимальное значение по не-NaN данным
            fill_value = np.nanmin(data)
        elif method == 'max':
            # Максимальное значение по не-NaN данным
            fill_value = np.nanmax(data)
        elif method == 'custom' and custom_value is not None:
            fill_value = custom_value
        else:
            print(f"Метод '{method}' не поддерживается. Доступные: zero, mean, median, min, max, forward_fill, backward_fill, custom")
            return

        filled_data = data.copy()
        filled_data[mask] = fill_value
        self.cube[:, :, indicator_idx] = filled_data
        
        print(f"Заполнено {np.sum(mask)} пропущенных значений в '{indicator_name}' методом {method} (значение: {fill_value})")

    def create_custom_indicator(self, formula, new_indicator_name):
        """Создает новый показатель по пользовательской формуле"""
        if new_indicator_name in self.indicators:
            raise ConflictException(f"Показатель '{new_indicator_name}' уже существует")

        import re
        indicators_in_formula = re.findall(r'"([^"]+)"', formula)
        
        for indicator in indicators_in_formula:
            if indicator not in self.indicator_to_idx:
                raise MissingIndicatorsException(f"Показатель '{indicator}' не найден в кубе")

        new_cube = np.zeros((self.cube.shape[0], self.cube.shape[1], self.cube.shape[2] + 1))
        new_cube[:, :, :self.cube.shape[2]] = self.cube
        
        python_formula = formula
        for indicator in indicators_in_formula:
            idx = self.indicator_to_idx[indicator]
            python_formula = python_formula.replace(f'"{indicator}"', f'new_cube[:, :, {idx}]')

        try:
            result = eval(python_formula)
            result = np.where(np.isinf(result), np.nan, result)
            result = np.where(np.isnan(result), np.nan, result)
            new_cube[:, :, -1] = result
        except Exception as e:
            raise FormulaCalculationException(f"Ошибка при вычислении формулы: {e}")

        self.cube = new_cube
        self.indicators.append(new_indicator_name)
        self.indicator_to_idx[new_indicator_name] = len(self.indicators) - 1
        
        print(f"Создан показатель '{new_indicator_name}' по формуле: {formula}")