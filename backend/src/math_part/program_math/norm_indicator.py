import numpy as np
import pandas as pd
from math import erf, sqrt
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
        
        method = (method or 'minmax').lower()

        if method == 'rank':
            normalized_data = self._rank_normalize(data)

        elif method == 'z-score':
            # Z-score нормализация в диапазон [0, 1]:
            # сначала стандартизируем, затем переводим z в вероятность через CDF N(0, 1).
            mean = np.nanmean(data)
            std = np.nanstd(data)
            if std == 0:
                raise NormalizationException("Стандартное отклонение равно 0, нормализация невозможна")
            z_scores = (data - mean) / std
            normal_cdf = np.vectorize(lambda value: 0.5 * (1 + erf(value / sqrt(2))))
            normalized_data = normal_cdf(z_scores)
            
        elif method in {'minmax', 'linear'}:
            # Min-Max нормализация: (x - min) / (max - min)
            normalized_data = self._minmax_scale(data)

        elif method == 'abs-minmax':
            max_abs = np.nanmax(np.abs(data))
            if max_abs == 0:
                raise NormalizationException("Максимальное абсолютное значение равно 0, нормализация невозможна")
            normalized_data = (data / max_abs + 1) / 2

        elif method == 'threshold':
            threshold = np.nanmean(data)
            if threshold == 0:
                raise NormalizationException("Пороговое значение равно 0, нормализация невозможна")
            normalized_data = np.clip(data / threshold, 0, 1)

        elif method == 'cyclic':
            cycle_mean = np.nanmean(data, axis=0, keepdims=True)
            if np.any(cycle_mean == 0):
                raise NormalizationException("Среднее значение цикла равно 0, нормализация невозможна")
            normalized_data = self._minmax_scale(data / cycle_mean)

        elif method == 'proportional':
            total = np.nansum(data)
            if total == 0:
                raise NormalizationException("Сумма значений равна 0, пропорциональная нормализация невозможна")
            normalized_data = data / total

        elif method == 'boxcox':
            if np.nanmin(data) <= 0:
                raise NormalizationException("Box-Cox применим только к положительным значениям")
            transformed = self._boxcox_transform(data)
            normalized_data = self._minmax_scale(transformed)

        elif method == 'yeo-johnson':
            transformed = self._yeo_johnson_transform(data)
            normalized_data = self._minmax_scale(transformed)

        elif method == 'log':
            min_val = np.nanmin(data)
            shifted = data - min_val if min_val <= 0 else data
            transformed = np.log1p(shifted)
            normalized_data = self._minmax_scale(transformed)

        elif method == 'quantile':
            normalized_data = self._rank_normalize(data)
            
        elif method == 'robust':
            # Robust-нормализация в диапазон [0, 1]:
            # квартильная версия Min-Max, устойчивая к выбросам.
            q75, q25 = np.nanpercentile(data, [75, 25])
            iqr = q75 - q25
            if iqr == 0:
                raise NormalizationException("IQR равно 0, нормализация невозможна")
            normalized_data = (data - q25) / iqr
            normalized_data = np.clip(normalized_data, 0, 1)
            
        else:
            available = (
                "rank, z-score, minmax, abs-minmax, linear, threshold, cyclic, "
                "proportional, boxcox, yeo-johnson, log, quantile, robust"
            )
            raise MethodNotFoundException(f"Метод '{method}' не поддерживается. Доступные: {available}")
        self._add_normalized_data(normalized_data, new_indicator_name)
        print(f"Создан нормализованный показатель '{new_indicator_name}' методом {method}")

    @staticmethod
    def _minmax_scale(data):
        min_val = np.nanmin(data)
        max_val = np.nanmax(data)
        if max_val == min_val:
            raise NormalizationException("Минимум и максимум равны, нормализация невозможна")
        return (data - min_val) / (max_val - min_val)

    @staticmethod
    def _rank_normalize(data):
        flat = np.asarray(data, dtype=float).ravel()
        valid = np.isfinite(flat)
        if np.sum(valid) <= 1:
            raise NormalizationException("Недостаточно значений для ранжирования")
        order = np.argsort(flat[valid], kind='mergesort')
        ranks = np.empty(np.sum(valid), dtype=float)
        ranks[order] = np.arange(np.sum(valid), dtype=float)
        normalized_valid = ranks / (np.sum(valid) - 1)
        result = np.full(flat.shape, np.nan, dtype=float)
        result[valid] = normalized_valid
        return result.reshape(data.shape)

    @classmethod
    def _boxcox_transform(cls, data):
        values = np.asarray(data, dtype=float)
        lam = cls._best_power_lambda(values, family='boxcox')
        if abs(lam) < 1e-9:
            return np.log(values)
        return (np.power(values, lam) - 1) / lam

    @classmethod
    def _yeo_johnson_transform(cls, data):
        values = np.asarray(data, dtype=float)
        lam = cls._best_power_lambda(values, family='yeo-johnson')
        positive = values >= 0
        result = np.empty_like(values, dtype=float)
        if abs(lam) < 1e-9:
            result[positive] = np.log1p(values[positive])
        else:
            result[positive] = (np.power(values[positive] + 1, lam) - 1) / lam

        if abs(lam - 2) < 1e-9:
            result[~positive] = -np.log1p(-values[~positive])
        else:
            result[~positive] = -(np.power(1 - values[~positive], 2 - lam) - 1) / (2 - lam)
        return result

    @classmethod
    def _best_power_lambda(cls, data, family):
        candidates = np.linspace(-2, 2, 81)
        best_lambda = 1.0
        best_score = float('-inf')
        for lam in candidates:
            transformed = cls._power_transform_for_lambda(data, lam, family)
            valid = transformed[np.isfinite(transformed)]
            if valid.size < 2:
                continue
            variance = np.var(valid)
            if variance <= 0:
                continue
            # Упрощенная максимизация нормальности: штрафуем дисперсию и асимметрию.
            centered = valid - np.mean(valid)
            skewness = abs(np.mean(centered ** 3) / (np.std(valid) ** 3 + 1e-12))
            score = -np.log(variance) - skewness
            if score > best_score:
                best_score = score
                best_lambda = float(lam)
        return best_lambda

    @classmethod
    def _power_transform_for_lambda(cls, data, lam, family):
        if family == 'boxcox':
            if abs(lam) < 1e-9:
                return np.log(data)
            return (np.power(data, lam) - 1) / lam
        return cls._yeo_johnson_for_lambda(data, lam)

    @staticmethod
    def _yeo_johnson_for_lambda(data, lam):
        values = np.asarray(data, dtype=float)
        positive = values >= 0
        result = np.empty_like(values, dtype=float)
        if abs(lam) < 1e-9:
            result[positive] = np.log1p(values[positive])
        else:
            result[positive] = (np.power(values[positive] + 1, lam) - 1) / lam
        if abs(lam - 2) < 1e-9:
            result[~positive] = -np.log1p(-values[~positive])
        else:
            result[~positive] = -(np.power(1 - values[~positive], 2 - lam) - 1) / (2 - lam)
        return result

    def _add_normalized_data(self, normalized_data, indicator_name):
        """Внутренний метод для добавления нормализованных данных в куб"""
        new_cube = np.zeros((self.cube.shape[0], self.cube.shape[1], self.cube.shape[2] + 1))
        if self.cube.shape[2] > 0:
            new_cube[:, :, :self.cube.shape[2]] = self.cube
        new_cube[:, :, -1] = normalized_data
        self.cube = new_cube
        self.indicators.append(indicator_name)
        self.indicator_to_idx[indicator_name] = len(self.indicators) - 1
