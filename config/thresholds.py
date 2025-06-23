import pandas as pd


THRESHOLDS = {
    'VMS_Voltage1': {'high': [4.62, 4.51, 4.41], 'low': [3.99, 3.89, 3.78]},
    'VMS_Voltage2': {'high': [4.62, 4.51, 4.41], 'low': [3.99, 3.89, 3.78]},
    'VMS_Voltage3': {'high': [4.62, 4.51, 4.41], 'low': [3.99, 3.89, 3.78]},
    'VMS_Photosensor1': {'high': [255], 'low': [0]},
    'VMS_Photosensor2': {'high': [255], 'low': [0]},
    'VMS_Photosensor3': {'high': [255], 'low': [0]},
    'VMS_Temp1': {'high': [70, 69.5, 69], 'low': [0]},
    'VMS_Temp2': {'high': [70, 69.5, 69], 'low': [0]},
    'VMS_Temp3': {'high': [70, 69.5, 69], 'low': [0]},
    'CPU': {'high': [75], 'low': [0]},
    'Memory': {'high': [4], 'low': [0]},
    'DiskSpace': {'high': [59], 'low': [0]},
}


def filter_data(df):
    relevant_columns = list(THRESHOLDS.keys())
    relevant_columns.extend(['devicename', 'timestamp'])
    filtered_df = df[relevant_columns].copy()

    # Create a mask for invalid values
    for column, (min_val, max_val) in THRESHOLDS.items():
        if column in df.columns:
            # Mark values outside thresholds as False
            filtered_df[column] = filtered_df[column].apply(
                lambda x: pd.NA if pd.isna(x) or min_val <= x <= max_val else x
            )
    
    filtered_df = filtered_df.dropna(how='all', subset=relevant_columns[:-2])
    
    return filtered_df
