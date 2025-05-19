import pandas as pd

# Define thresholds for each sensor
# THRESHOLDS = {
#     # 'EHC_IncomingVoltage': (235, 246.8),   # Voltage range in Volts
#     # 'EHC_IncomingVoltage': (216.2, 220),   # Voltage range in Volts
#     # 'EHC_ConsumedPower': (0, 1947),          # Power less than 1947W
#     # 'EHC_Temp': (0, 70),                     # Temperature less than 70°C
#     # 'EHC_Humidity': (0, 95),                 # Humidity less than 95%
#     'VMS_Voltage1': (3.8, 4.2),              # Voltage range in Volts (VMS 1)
#     'VMS_Voltage2': (3.8, 4.2),              # Voltage range in Volts (VMS 2)
#     'VMS_Voltage3': (3.8, 4.2),              # Voltage range in Volts (VMS 3)
#     'VMS_Photosensor1': (0, 255),            # Photosensor range (0 to 255) (VMS 1)
#     'VMS_Photosensor2': (0, 255),            # Photosensor range (0 to 255) (VMS 2)
#     'VMS_Photosensor3': (0, 255),            # Photosensor range (0 to 255) (VMS 3)
#     'VMS_Temp1': (0, 70),                    # Temperature less than 70°C (VMS 1)
#     'VMS_Temp2': (0, 70),                    # Temperature less than 70°C (VMS 2)
#     'VMS_Temp3': (0, 70),                    # Temperature less than 70°C (VMS 3)
#     'CPU': (0, 100),                         # CPU usage less than 100%
#     'Memory': (0, 100),                      # Memory usage less than 100%
#     'DiskSpace': (0, 100),                   # Disk space usage less than 100%
# }

THRESHOLDS = {
    # 'VMS_Voltage1': {'high': [4.2, 4.1, 4.05], 'low': [3.9, 3.85, 3.8]},
    # 'VMS_Voltage2': {'high': [4.2, 4.1, 4.05], 'low': [3.9, 3.85, 3.8]},
    # 'VMS_Voltage3': {'high': [4.2, 4.1, 4.05], 'low': [3.9, 3.85, 3.8]},
    'VMS_Voltage1': {'high': [4.2, 4.1, 4.05], 'low': [3.97, 3.94, 3.92]},
    'VMS_Voltage2': {'high': [4.2, 4.1, 4.05], 'low': [4.01, 4.00, 3.90]},
    'VMS_Voltage3': {'high': [4.2, 4.1, 4.05], 'low': [3.97, 3.94, 3.92]},
    'VMS_Photosensor1': {'high': [255], 'low': [0]},
    'VMS_Photosensor2': {'high': [255], 'low': [0]},
    'VMS_Photosensor3': {'high': [255], 'low': [0]},
    'VMS_Temp1': {'high': [70, 69.5, 69], 'low': [0]},
    'VMS_Temp2': {'high': [70, 69.5, 69], 'low': [0]},
    'VMS_Temp3': {'high': [70, 69.5, 69], 'low': [0]},
    'CPU': {'high': [100], 'low': [0]},
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
