import numpy as np
import pandas as pd
from backend.src.math_part.program_math.norm_indicator import NormalizedIndicator
from backend.src.math_part.program_math.utils.parse import format_population_data
from backend.src.math_part.program_math.base_indicator import BaseIndicator
from backend.src.math_part.program_math.integral_indicator import IntegralIndicator
from backend.src.math_part.program_math.weight_indicator import WeightedIndicator

# population = pd.read_excel('src/data/Demography.xls', sheet_name="1.1", skiprows=6, header=None)
population = pd.read_excel('src/data/Demography_v2.xls',  header=None)

population_formatted = format_population_data(population)
cube = BaseIndicator()
cube.add_indicator(population_formatted, 'Население')
avg_age_formatted = format_population_data(population)
cube.add_indicator(avg_age_formatted, "Средний возраст")
cube.info()
cube.create_custom_indicator('"Население"*"Средний возраст"', "Базовый показатель")


norm = NormalizedIndicator(cube)
# print(cube.get_table('Базовый показатель'))
norm.create_normalized_indicator("Базовый показатель", method='minmax', new_indicator_name="Базовый показатель")
norm.create_normalized_indicator("Средний возраст", method='minmax', new_indicator_name="Средний возраст")
# print(norm.get_table("Базовый показатель"))
print(norm.years)
print(norm.get_row_data("г. Севастополь", 'Базовый показатель'))

weights_data = {'Базовый показатель': 0.2, 'Средний возраст': 0.8}
weighted_calc = WeightedIndicator(weights_data)

result = weighted_calc.apply_weights(
    cube=norm,
    year='2005',
    name='Взвешенный'
)
# print(weighted_calc.get_weighted_table('Взвешенный'))
# print(weighted_calc.weighted_indicators)
print(weighted_calc.get_region_data('Взвешенный', "г. Севастополь"))

indicator = IntegralIndicator()
integral_result = indicator.calculate_integral_from_weights(
    weighted_indicator=weighted_calc,
    weighted_indicator_name='Взвешенный',
    year='2005',
    method='sum',
    name='Интегральный_демографический_показатель_2005'
)
print(integral_result)
# print(indicator.get('Интегральный_демографический_показатель_2005'))

if hasattr(integral_result, 'to_frame'):
    df = integral_result.to_frame()
else:
    df = pd.DataFrame([integral_result])
filename = 'src\data\output\integral_result.xlsx'
df.to_excel(filename, index=True, sheet_name='Результаты')
print(f"Результат сохранен в файл: {filename}")