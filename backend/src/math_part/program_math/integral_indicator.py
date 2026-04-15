import numpy as np
import pandas as pd
from backend.src.math_part.program_math.weight_indicator import WeightedIndicator
from .exceptions import CutNotFoundException, DataNotFoundException, MissingIndicatorsException

class IntegralIndicator:
    def __init__(self):
        self.integral_indicators = {}
    
    def calculate_integral_from_weights(self, weighted_indicator: WeightedIndicator, weighted_indicator_name, 
                        year=None, method='sum', name='Интегральный показатель'):
        """
        Расчет интегрального показателя методом суммы для определенного года
        """
        weighted_table = weighted_indicator.get_weighted_dataframe(weighted_indicator_name)
        
        if weighted_table is None:
            raise DataNotFoundException(f"Не удалось получить взвешенную таблицу '{weighted_indicator_name}'")

        if weighted_indicator_name not in weighted_indicator.weighted_indicators:
            raise DataNotFoundException(f"Метаданные для '{weighted_indicator_name}' не найдены")
        
        metadata = weighted_indicator.weighted_indicators[weighted_indicator_name]
        indicators = metadata['indicators']
        regions = metadata['regions']
        base_year = metadata['year']  
        weights = metadata['weights']
        print(type(base_year))
        
        if year is not None and year != base_year:
            raise CutNotFoundException(f"Запрашиваемый год {year} не совпадает с годом данных {base_year}")
        year = base_year
        
        print(f"Расчет интегрального показателя '{name}'")
        integral_values = np.sum(weighted_table, axis=0)

        self.integral_indicators[name] = {
            'values': integral_values,
            'regions': regions,
            'year': year,
            'method': method,
            'source_indicator': weighted_indicator_name,
            'component_indicators': indicators,
            'weights': weights
        }
        return integral_values
    
    def get_integral_dataframe(self, integral_indicator_name):
        """Получить интегральный показатель в виде DataFrame"""
        if integral_indicator_name not in self.integral_indicators:
            raise MissingIndicatorsException(f"Интегральный показатель '{integral_indicator_name}' не найден")
        
        data = self.integral_indicators[integral_indicator_name]
        df = pd.DataFrame({
            'Регион': data['regions'],
            'Интегральный_показатель': data['values']
        })
        return df
    
    def get_region_value(self, integral_indicator_name, region):
        """Получить значение интегрального показателя для региона"""
        if integral_indicator_name not in self.integral_indicators:
            raise MissingIndicatorsException(f"Интегральный показатель '{integral_indicator_name}' не найден")
        
        data = self.integral_indicators[integral_indicator_name]
        if region not in data['regions']:
            raise MissingIndicatorsException(f"Регион '{region}' не найден")
        
        idx = data['regions'].index(region)
        return data['values'][idx]
    
    def info(self):
        """Информация о всех интегральных показателях"""
        print("Интегральные показатели:")
        for name, data in self.integral_indicators.items():
            print(f"  '{name}':")
            print(f"    Метод: {data['method']}")
            print(f"    Год: {data['year']}")