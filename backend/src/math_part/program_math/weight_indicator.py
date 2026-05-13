import numpy as np
import pandas as pd
from .exceptions import NoIndicatorsException, MissingIndicatorsException, CutNotFoundException

class WeightedIndicator:
    SUPPORTED_WEIGHT_METHODS = {
        'equal',
        'manual',
        'std',
        'standard_deviation',
        'pca',
        'modified_pca',
        'entropy',
    }

    def __init__(self, weights_dict):
        self.weights_dict = weights_dict  # {название_показателя: вес}
        self.weighted_indicators = {} # {name: regions x indicators]}

    @classmethod
    def calculate_weights(cls, cube, year: str, method='equal'):
        """Рассчитать веса показателей по срезу куба за выбранный год."""
        if year not in cube.year_to_idx:
            raise CutNotFoundException(f"Год {year} не найден в кубе")

        indicator_names = list(cube.indicators)
        if not indicator_names:
            raise NoIndicatorsException("В кубе нет показателей для расчета весов")

        method = (method or 'equal').lower()
        if method not in cls.SUPPORTED_WEIGHT_METHODS:
            available = ', '.join(sorted(cls.SUPPORTED_WEIGHT_METHODS - {'manual'}))
            raise MissingIndicatorsException(f"Метод весов '{method}' не поддерживается. Доступные: {available}")

        matrix = cls._year_matrix(cube, year, indicator_names)
        if method in {'equal', 'manual'}:
            raw_weights = np.ones(len(indicator_names), dtype=float)
        elif method in {'std', 'standard_deviation'}:
            raw_weights = cls._std_weights(matrix)
        elif method == 'pca':
            raw_weights = cls._pca_weights(matrix)
        elif method == 'modified_pca':
            raw_weights = cls._modified_pca_weights(matrix)
        elif method == 'entropy':
            raw_weights = cls._entropy_weights(matrix)
        else:
            raw_weights = np.ones(len(indicator_names), dtype=float)

        normalized_weights = cls._normalize_weights(raw_weights)
        return {
            indicator: float(weight)
            for indicator, weight in zip(indicator_names, normalized_weights)
        }

    @staticmethod
    def _year_matrix(cube, year: str, indicator_names):
        columns = []
        for indicator in indicator_names:
            values = np.asarray(cube.get_col_data(year, indicator), dtype=float)
            columns.append(values)
        matrix = np.column_stack(columns)

        for col_idx in range(matrix.shape[1]):
            column = matrix[:, col_idx]
            valid = np.isfinite(column)
            fill_value = float(np.mean(column[valid])) if np.any(valid) else 0.0
            column[~valid] = fill_value
            matrix[:, col_idx] = column
        return matrix

    @staticmethod
    def _normalize_weights(raw_weights):
        weights = np.asarray(raw_weights, dtype=float)
        weights = np.where(np.isfinite(weights), weights, 0.0)
        weights = np.abs(weights)
        total = float(np.sum(weights))
        if total <= 0:
            return np.full(weights.shape, 1 / len(weights), dtype=float)
        return weights / total

    @staticmethod
    def _std_weights(matrix):
        return np.nanstd(matrix, axis=0)

    @classmethod
    def _pca_weights(cls, matrix):
        if matrix.shape[0] < 2:
            return np.ones(matrix.shape[1], dtype=float)
        eigenvalues, eigenvectors = cls._principal_components(matrix)
        if eigenvalues.size == 0:
            return np.ones(matrix.shape[1], dtype=float)
        return np.abs(eigenvectors[:, 0]) * max(float(eigenvalues[0]), 0.0)

    @classmethod
    def _modified_pca_weights(cls, matrix, cumulative_threshold=0.8):
        if matrix.shape[0] < 2:
            return np.ones(matrix.shape[1], dtype=float)
        eigenvalues, eigenvectors = cls._principal_components(matrix)
        if eigenvalues.size == 0:
            return np.ones(matrix.shape[1], dtype=float)

        positive = np.maximum(eigenvalues, 0.0)
        total = float(np.sum(positive))
        if total <= 0:
            return np.ones(matrix.shape[1], dtype=float)

        ratios = positive / total
        component_count = int(np.searchsorted(np.cumsum(ratios), cumulative_threshold) + 1)
        component_count = min(max(component_count, 1), len(ratios))
        selected_vectors = np.abs(eigenvectors[:, :component_count])
        selected_ratios = ratios[:component_count]
        return selected_vectors @ selected_ratios

    @staticmethod
    def _principal_components(matrix):
        if matrix.shape[1] == 1:
            return np.array([1.0]), np.array([[1.0]])

        centered = matrix - np.mean(matrix, axis=0)
        std = np.std(centered, axis=0)
        std[std == 0] = 1.0
        standardized = centered / std
        covariance = np.cov(standardized, rowvar=False)
        covariance = np.atleast_2d(covariance)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        order = np.argsort(eigenvalues)[::-1]
        return eigenvalues[order], eigenvectors[:, order]

    @classmethod
    def _entropy_weights(cls, matrix):
        shifted = matrix.copy()
        min_values = np.min(shifted, axis=0)
        shifted = shifted - np.minimum(min_values, 0.0)
        shifted = np.where(shifted == 0, 0.0, shifted)

        column_sums = np.sum(shifted, axis=0)
        zero_columns = column_sums <= 0
        if np.all(zero_columns):
            return np.ones(matrix.shape[1], dtype=float)
        column_sums[zero_columns] = 1.0
        proportions = shifted / column_sums

        object_count = matrix.shape[0]
        if object_count <= 1:
            return np.ones(matrix.shape[1], dtype=float)

        safe_proportions = np.where(proportions > 0, proportions, 1.0)
        entropy = -(1 / np.log(object_count)) * np.sum(
            proportions * np.log(safe_proportions),
            axis=0,
        )
        diversity = 1 - entropy
        diversity[zero_columns] = 0.0
        return cls._normalize_weights(diversity)
    
    def apply_weights(self, cube, year: str, name='Взвешенный показатель'):
        indicator_names = list(self.weights_dict.keys())
        
        if not indicator_names:
            raise NoIndicatorsException("В словаре весов нет показателей")
        
        missing_indicators = []
        for indicator in indicator_names:
            if indicator not in cube.indicators:
                missing_indicators.append(indicator)
        
        if missing_indicators:
            print(f"Показатели не найдены в кубе: {missing_indicators}")
            raise MissingIndicatorsException("В словаре весов нет показателей")
        
        if year not in cube.year_to_idx:
            raise CutNotFoundException(f"Год {year} не найден в кубе")

        weighted_table = np.zeros((len(indicator_names), len(cube.regions)))
        
        print(f"Создаем таблицу размером: {weighted_table.shape} (показатели × регионы)")
        for i, indicator in enumerate(indicator_names):
            year_data = cube.get_col_data(year, indicator)
            print(f'{year_data=}')
            weight = self.weights_dict[indicator]
            
            weighted_data = year_data * weight
            weighted_table[i, :] = weighted_data
        self.weighted_indicators[name] = {
            'data': weighted_table,
            'indicators': indicator_names,  # список показателей
            'regions': cube.regions,        # список регионов
            'year': year,
            'weights': [self.weights_dict[ind] for ind in indicator_names]
        }
        return weighted_table

    def get_weighted_table(self, weighted_indicator_name):
        """Получить всю таблицу взвешенных данных по показателю"""
        if weighted_indicator_name not in self.weighted_indicators:
            raise MissingIndicatorsException("В словаре весов нет показателей")(f"Взвешенный показатель '{weighted_indicator_name}' не найден")
        
        return self.weighted_indicators[weighted_indicator_name]['data']
    
    def get_weighted_dataframe(self, weighted_indicator_name):
        """Получить таблицу в виде DataFrame с названиями показателей и регионов"""
        if weighted_indicator_name not in self.weighted_indicators:
            raise MissingIndicatorsException(f"Взвешенный показатель '{weighted_indicator_name}' не найден")
        
        data = self.weighted_indicators[weighted_indicator_name]
        df = pd.DataFrame(
            data['data'],
            index=data['indicators'],  # строки - показатели
            columns=data['regions']    # столбцы - регионы
        )
        return df
    
    def get_region_data(self, weighted_indicator_name, region):
        """Получить данные по всем показателям для конкретного региона"""
        if weighted_indicator_name not in self.weighted_indicators:
            raise MissingIndicatorsException(f"Взвешенный показатель '{weighted_indicator_name}' не найден")
        data = self.weighted_indicators[weighted_indicator_name]
        if region not in data['regions']:
            raise MissingIndicatorsException(f"Регион '{region}' не найден в таблице")
        idx = data['regions'].index(region)
        return {
            'indicators': data['indicators'],
            'values': data['data'][:, idx],
            'weights': data['weights'],
            'region': region,
            'year': data['year']
        }
    
    def get_indicator_data(self, weighted_indicator_name, indicator):
        """Получить данные по всем регионам для конкретного показателя"""
        if weighted_indicator_name not in self.weighted_indicators:
            raise MissingIndicatorsException(f"Взвешенный показатель '{weighted_indicator_name}' не найден")
        
        data = self.weighted_indicators[weighted_indicator_name]
        if indicator not in data['indicators']:
            raise MissingIndicatorsException(f"Показатель '{indicator}' не найден в таблице")
        
        idx = data['indicators'].index(indicator)
        return {
            'regions': data['regions'],
            'values': data['data'][idx, :],
            'weight': data['weights'][idx],
            'indicator': indicator,
            'year': data['year']
        }
    
    def get_all_regions(self, weighted_indicator_name):
        """Получить список всех регионов для взвешенного показателя"""
        if weighted_indicator_name not in self.weighted_indicators:
            raise MissingIndicatorsException(f"Взвешенный показатель '{weighted_indicator_name}' не найден")
        return self.weighted_indicators[weighted_indicator_name]['regions']
    
    def get_all_indicators(self, weighted_indicator_name):
        """Получить список всех показателей для взвешенного показателя"""
        if weighted_indicator_name not in self.weighted_indicators:
            raise MissingIndicatorsException(f"Взвешенный показатель '{weighted_indicator_name}' не найден")
        return self.weighted_indicators[weighted_indicator_name]['indicators']
    
    def info(self):
        print("Взвешенные таблицы:")
        for name, data in self.weighted_indicators.items():
            print(f"  '{name}': {data['data'].shape} (показатели × регионы), год: {data['year']}")
            print(f"    Показатели: {data['indicators']}")
            print(f"    Регионы: {len(data['regions'])} регионов")
