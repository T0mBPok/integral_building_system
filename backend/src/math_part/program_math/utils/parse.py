import numpy as np
import pandas as pd

def format_population_data(df):
    formatted_column_row = {str(value): idx for idx, value in enumerate(df.iloc[1:, 0])}
    formatted_header_row = {str(value): idx for idx, value in enumerate(df.iloc[0, 1:])}
    formatted_df = df.iloc[1:, 1:].apply(pd.to_numeric, errors='coerce').replace({np.nan: None})
    
    return formatted_column_row, formatted_header_row, formatted_df

def parse_weights_data(df):
    weights_dict = {}
    for idx in range(len(df)):
        try:
            indicator_name = df.iloc[idx, 0]
            weight_value = df.iloc[idx, 1]
            
            if pd.notna(indicator_name) and pd.notna(weight_value):
                weights_dict[str(indicator_name).strip()] = float(weight_value)
                
        except (ValueError, TypeError, IndexError) as e:
            print(f"Ошибка при обработке строки {idx}: {e}")
            continue
    
    return weights_dict