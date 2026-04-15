import numpy as np
from .exceptions import ConflictException

class Cube:
    def __init__(self, population_formatted=None, name="Население"):
        if population_formatted is None:
            self.regions = []
            self.years = []
            self.indicators = []
            self.cube = np.zeros((0, 0, 0))
            self.region_to_idx = {}
            self.year_to_idx = {}
            self.indicator_to_idx = {}
            print("Создан пустой куб")
        else:
            self.regions = list(population_formatted[0].keys())
            self.years = list(population_formatted[1].keys())
            self.indicators = [name]
            
            self.cube = np.zeros((len(self.regions), len(self.years), len(self.indicators)))

            self.region_to_idx = {region: idx for idx, region in enumerate(self.regions)}
            self.year_to_idx = {year: idx for idx, year in enumerate(self.years)}
            self.indicator_to_idx = {indicator: idx for idx, indicator in enumerate(self.indicators)}

            data_df = population_formatted[2]
            row_labels = population_formatted[0]  
            col_labels = population_formatted[1]  
            
            for region, row_idx in row_labels.items():
                for year, col_idx in col_labels.items():
                    try:
                        value = data_df.iloc[row_idx, col_idx]
                        self.cube[row_idx, col_idx, 0] = value  
                    except (IndexError, KeyError, ValueError):
                        self.cube[row_idx, col_idx, 0] = np.nan
            
            print(f"Куб создан: {self.cube.shape}")

    def add_indicator(self, new_data_formatted, indicator_name):
        """Добавляет новый показатель в куб, автоматически дополняя регионы и годы"""
        if indicator_name in self.indicators:
            raise ConflictException(f"Показатель '{indicator_name}' уже есть в кубе")

        new_row_labels, new_col_labels, new_data_df = new_data_formatted
        
        new_regions = list(new_row_labels.keys())
        new_years = list(new_col_labels.keys())
        
        all_regions = list(set(self.regions + new_regions))
        all_years = list(set(self.years + new_years))
        
        new_cube = np.full((len(all_regions), len(all_years), len(self.indicators) + 1), np.nan)
        
        new_region_to_idx = {region: idx for idx, region in enumerate(all_regions)}
        new_year_to_idx = {year: idx for idx, year in enumerate(all_years)}
        
        if self.cube.shape[2] > 0:  
            for old_region_idx, region in enumerate(self.regions):
                new_region_idx = new_region_to_idx[region]
                for old_year_idx, year in enumerate(self.years):
                    new_year_idx = new_year_to_idx[year]
                    new_cube[new_region_idx, new_year_idx, :self.cube.shape[2]] = \
                        self.cube[old_region_idx, old_year_idx, :]
        
        for region, new_row_idx in new_row_labels.items():
            new_region_idx = new_region_to_idx[region]
            for year, new_col_idx in new_col_labels.items():
                new_year_idx = new_year_to_idx[year]
                try:
                    value = new_data_df.iloc[new_row_idx, new_col_idx]
                    new_cube[new_region_idx, new_year_idx, -1] = value
                except (IndexError, KeyError, ValueError):
                    new_cube[new_region_idx, new_year_idx, -1] = np.nan

        self.regions = all_regions
        self.years = all_years
        self.region_to_idx = new_region_to_idx
        self.year_to_idx = new_year_to_idx
        self.cube = new_cube
        self.indicators.append(indicator_name)
        self.indicator_to_idx[indicator_name] = len(self.indicators) - 1
        
        print(f"Добавлен показатель '{indicator_name}'")
        print(f"Новый размер куба: {self.cube.shape}")
        print(f"Регионы: {len(self.regions)}, Годы: {len(self.years)}")
        
    
    def get_data(self, region, year, metric="Население"):
        """Получить данные для региона и года"""
        if region in self.region_to_idx and year in self.year_to_idx and metric in self.indicator_to_idx:
            metric_idx = self.indicator_to_idx[metric]
            return self.cube[self.region_to_idx[region], self.year_to_idx[year], metric_idx]
        return None
    
    def get_row_data(self, region, metric="Население"):
        """Получить все данные по региону за все годы"""
        if region in self.region_to_idx and metric in self.indicator_to_idx:
            return self.cube[self.region_to_idx[region], :, self.indicator_to_idx[metric]]
        return None
    
    def get_col_data(self, year: str, metric="Население"):
        """Получить данные по всем регионам за определенный год"""
        if year in self.year_to_idx and metric in self.indicator_to_idx:
            return self.cube[:, self.year_to_idx[year], self.indicator_to_idx[metric]]
        return None
    
    def get_table(self, metric="Население"):
        """Получить всю таблицу по показателю"""
        if metric in self.indicator_to_idx:
            return self.cube[:, :, self.indicator_to_idx[metric]]
        return None
    
    def get_indicator_data(self, indicator_name):
        """Возвращает данные по указанному показателю в виде 2D массива [регионы × годы]"""
        if indicator_name not in self.indicator_to_idx:
            print(f"Показатель '{indicator_name}' не найден в кубе")
            return None
        
        indicator_idx = self.indicator_to_idx[indicator_name]
        return self.cube[:, :, indicator_idx].copy()

    def info(self):
        """Вывести информацию о кубе"""
        print(f"Размер куба: {self.cube.shape}")
        print(f"Регионы: {len(self.regions)}")
        print(f"Годы: {len(self.years)}")
        print(f"Показатели: {self.indicators}")
