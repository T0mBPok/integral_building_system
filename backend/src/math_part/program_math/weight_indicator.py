import numpy as np
import pandas as pd
from .exceptions import NoIndicatorsException, MissingIndicatorsException, CutNotFoundException

class WeightedIndicator:
    def __init__(self, weights_dict):
        self.weights_dict = weights_dict  # {название_показателя: вес}
        self.weighted_indicators = {} # {name: regions x indicators]}
    
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