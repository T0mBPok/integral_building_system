import numpy as np
import pandas as pd
from .cube import Cube
from .exceptions import MethodNotFoundException, MissingIndicatorsException, NoIndicatorsException, NormalizationException

class NormalizedIndicator(Cube):    
    def __init__(self, source_cube):
        super().__init__(None)
        
        self.source_cube = source_cube
        self.regions = source_cube.regions.copy()
        self.years = source_cube.years.copy()
        self.region_to_idx = source_cube.region_to_idx.copy()
        self.year_to_idx = source_cube.year_to_idx.copy()
        
        self.cube = np.zeros((len(self.regions), len(self.years), 0))
        self.indicators = []
        self.indicator_to_idx = {}
        
        print(f"Создан NormalizedIndicator для куба: {source_cube.cube.shape}")
        
    def create_normalized_indicator(self, indicator_name, method='minmax', new_indicator_name=None):
        """Создает нормализованную версию указанного показателя и добавляет в свой куб"""
        if indicator_name not in self.source_cube.indicator_to_idx:
            raise MissingIndicatorsException(f"Показатель '{indicator_name}' не найден в исходном кубе")
        
        if new_indicator_name is None:
            new_indicator_name = f"{indicator_name} ({method})"
        
        if new_indicator_name in self.indicators:
            raise MissingIndicatorsException(f"Нормализованный показатель '{new_indicator_name}' уже существует")

        data = self.source_cube.get_indicator_data(indicator_name)

        if data is None:
            raise MissingIndicatorsException(f"Не удалось получить данные из показателя {indicator_name}")
        
        if method == 'z-score':
            # Z-нормализация: (x - mean) / std
            mean = np.nanmean(data)
            std = np.nanstd(data)
            if std == 0:
                raise NormalizationException("Стандартное отклонение равно 0, нормализация невозможна")
            normalized_data = (data - mean) / std
            
        elif method == 'minmax':
            # Min-Max нормализация: (x - min) / (max - min)
            min_val = np.nanmin(data)
            max_val = np.nanmax(data)
            if max_val == min_val:
                raise NormalizationException("Минимум и максимум равны, нормализация невозможна")
            normalized_data = (data - min_val) / (max_val - min_val)
            
        elif method == 'robust':
            # Robust нормализация: (x - median) / IQR
            median = np.nanmedian(data)
            q75, q25 = np.nanpercentile(data, [75, 25])
            iqr = q75 - q25
            if iqr == 0:
                raise NormalizationException("IQR равно 0, нормализация невозможна")
            normalized_data = (data - median) / iqr
            
        else:
            raise MethodNotFoundException(f"Метод '{method}' не поддерживается. Доступные: z-score, minmax, robust")
        self._add_normalized_data(normalized_data, new_indicator_name)
        print(f"Создан нормализованный показатель '{new_indicator_name}' методом {method}")

    def _add_normalized_data(self, normalized_data, indicator_name):
        """Внутренний метод для добавления нормализованных данных в куб"""
        new_cube = np.zeros((self.cube.shape[0], self.cube.shape[1], self.cube.shape[2] + 1))
        if self.cube.shape[2] > 0:
            new_cube[:, :, :self.cube.shape[2]] = self.cube
        new_cube[:, :, -1] = normalized_data
        self.cube = new_cube
        self.indicators.append(indicator_name)
        self.indicator_to_idx[indicator_name] = len(self.indicators) - 1