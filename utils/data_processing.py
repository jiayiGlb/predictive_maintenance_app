import pandas as pd
import os
import re
from datetime import datetime
import plotly.express as px
from config.thresholds import THRESHOLDS

# Load and process data
def load_device_data(device_name, start_date, end_date, sensor):
    print(device_name, start_date, end_date, sensor)

    all_data = []

    # Ensure datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    date_range = pd.date_range(start=start_date, end=end_date)

    # Step 1: Generate file paths
    files_to_read = []
    for date in date_range:
        month_name = date.strftime('%B')  # e.g., "April"
        base_path = os.path.join('./data', month_name, device_name)
        file_name = f"DATA{date.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(base_path, file_name)

        print("File path:", file_path)

        if os.path.exists(file_path):
            files_to_read.append(file_path)

    print("Files to read:", files_to_read)

    # Step 2: Read files one by one (assuming CSV format)
    # Define expected columns manually (adjust as needed)
    column_names = [
        "TimeStamp", "",  # second column is empty
        "EHC_IncomingVoltage", "EHC_IncomingCurrent", "EHC_ConsumedPower", "EHC_Temp", "EHC_Humidity",
        "EHC_IDSKey", "EHC_Door",
        "VMS_Voltage1", "VMS_Photosensor1", "VMS_Temp1", "VMS_TileStatus1",
        "VMS_Voltage2", "VMS_Photosensor2", "VMS_Temp2", "VMS_TileStatus2",
        "VMS_Voltage3", "VMS_Photosensor3", "VMS_Temp3", "VMS_TileStatus3",
        "VMS_Current", "VMS_Door",
        "CPU", "Memory", "DiskSpace"
    ]
    for file_path in files_to_read:
        try:
            df = pd.read_csv(file_path, header=None, names=column_names, encoding='utf-8')

            # Drop the second column (empty column)
            df.drop(columns=[""], inplace=True)

            # # Rename and convert timestamp
            # df['timestamp'] = pd.to_datetime(df['TimeStamp'], errors='coerce')


            # Get date from filename
            match = re.search(r'DATA(\d{8})', os.path.basename(file_path))
            if not match:
                print(f"Could not extract date from file name: {file_path}")
                continue
            file_date = pd.to_datetime(match.group(1), format='%Y%m%d')

            # Combine file date and time
            df['timestamp'] = pd.to_datetime(file_date.strftime('%Y-%m-%d') + ' ' + df['TimeStamp'].astype(str), errors='coerce')


            # Skip file if sensor not found
            if sensor not in df.columns:
                print(f"Sensor '{sensor}' not found in {file_path}")
                continue

            df['devicename'] = device_name
            df = df[['timestamp', sensor, 'devicename']]
            all_data.append(df)

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue

    # Step 3: Final data processing
    if not all_data:
        print("No data found for the selected device and date range.")
        return None
    

    full_data = pd.concat(all_data, ignore_index=True)
    full_data.replace('garbled_data', pd.NA, inplace=True)

    if sensor not in full_data.columns:
        raise ValueError(f"Sensor '{sensor}' not found in the data.")

    full_data['timestamp'] = pd.to_datetime(full_data['timestamp'], errors='coerce')
    full_data[sensor] = pd.to_numeric(full_data[sensor], errors='coerce')
    full_data.dropna(subset=['timestamp', sensor], inplace=True)
    full_data.sort_values(by='timestamp', inplace=True)

    print(f"Cleaned data for device '{device_name}', sensor '{sensor}':")
    print(full_data[['timestamp', sensor]].head())

    return full_data[['timestamp', sensor]]




def is_valid_float(value):
    """Check if the value can be converted to float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def extract_data(file_path, line):
    parts = line.split(',')
    time_str = re.search(r'\d{2}:\d{2}:\d{2}', parts[0]).group(0)
    date = datetime.strptime(os.path.basename(file_path)[:8], '%Y%m%d').date()
    combined_datetime_str = f'{date} {time_str}'

    # Extract the original values
    memory_value = float(parts[24]) if is_valid_float(parts[24]) else None
    disk_space_value = float(parts[25]) if is_valid_float(parts[25]) else None


    # Compute the new values based on threshold - current value
    memory_threshold = THRESHOLDS['Memory']['high'][0] if 'Memory' in THRESHOLDS else None
    disk_space_threshold = THRESHOLDS['DiskSpace']['high'][0] if 'DiskSpace' in THRESHOLDS else None

    memory_adjusted = (memory_threshold - memory_value) if memory_value is not None and memory_threshold is not None else None
    disk_space_adjusted = (disk_space_threshold - disk_space_value) if disk_space_value is not None and disk_space_threshold is not None else None


    data = {
        'timestamp': datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M:%S'),
        'EHC_IncomingVoltage': float(parts[2]) if is_valid_float(parts[2]) else None,
        'EHC_IncomingCurrent': float(parts[3]) if is_valid_float(parts[3]) else None,
        'EHC_ConsumedPower': float(parts[4]) if is_valid_float(parts[4]) else None,
        'EHC_Temp': float(parts[5]) if is_valid_float(parts[5]) else None,
        'EHC_Humidity': float(parts[6]) if is_valid_float(parts[6]) else None,
        'VMS_Photosensor1': float(parts[10]) if is_valid_float(parts[10]) else None,
        'VMS_Temp1': float(parts[11]) if is_valid_float(parts[11]) else None,
        'VMS_Voltage1': float(parts[12]) if is_valid_float(parts[12]) else None,
        'VMS_Photosensor2': float(parts[14]) if is_valid_float(parts[14]) else None,
        'VMS_Temp2': float(parts[15]) if is_valid_float(parts[15]) else None,
        'VMS_Voltage2': float(parts[16]) if is_valid_float(parts[16]) else None,
        'VMS_Photosensor3': float(parts[18]) if is_valid_float(parts[18]) else None,
        'VMS_Temp3': float(parts[19]) if is_valid_float(parts[19]) else None,
        'VMS_Voltage3': float(parts[20]) if is_valid_float(parts[20]) else None,
        'VMS_Current': float(parts[21]) if is_valid_float(parts[21]) else None,
        'CPU': float(parts[23]) if is_valid_float(parts[23]) else None,
        'Memory': memory_adjusted,
        'DiskSpace': disk_space_adjusted,
    }
    return data


def clean_garbled_data(line):
    parts = re.split(r'[|,]', line)
    cleaned_parts = []
    for part in parts:
        part = part.strip()
        if re.search(r'[^a-zA-Z0-9\[\]|_.:\s-]', part):
            cleaned_parts.append('')
        else:
            cleaned_parts.append(part)
    return ','.join(cleaned_parts)


import pandas as pd

def generate_diagram_data(sensor_data, interval):
    print("generate_diagram_data", sensor_data, interval)
    
    # Convert the timestamp column to datetime
    sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'], errors='coerce')
    
    # Set timestamp as the index
    sensor_data.set_index('timestamp', inplace=True)
    
    numeric_columns = sensor_data.select_dtypes(include=['float64', 'int64']).columns
    
    if interval == '1_day':
        # Resample data to 1-minute intervals
        aggregated_data = sensor_data.resample('1min')[numeric_columns].mean().interpolate(method='linear')
    elif interval == '5_days':
        # Resample data to 10-minute intervals
        aggregated_data = sensor_data.resample('10min')[numeric_columns].mean().interpolate(method='linear')
    elif interval == '1_month':
        # Resample data to 1-hour intervals
        aggregated_data = sensor_data.resample('1H')[numeric_columns].mean().interpolate(method='linear')
    else:
        raise ValueError("Unsupported interval. Please choose from '1_day', '5_days', or '30_days'.")
    
    # Reset the index to make the timestamp a column again
    aggregated_data.reset_index(inplace=True)

    return aggregated_data


def generate_plot_with_thresholds(data, sensor, thresholds):
    """
    Generate a plot with high and low thresholds for the given sensor.
    """
    fig = px.line(
        data_frame=data,
        x='timestamp',
        y=sensor,
        title=f"{sensor} Data Visualization",
        labels={'timestamp': 'Time', sensor: 'Sensor Value'}
    )
    

    # Add high thresholds
    if 'high' in thresholds:
        for i, threshold in enumerate(thresholds['high']):
            fig.add_hline(
                y=threshold,
                line_color=f"rgb({200 - i*30}, 0, 0)",  # Gradient red tones
                line_width=1,
            )
    
    # Add low thresholds
    if 'low' in thresholds:
        for i, threshold in enumerate(thresholds['low']):
            fig.add_hline(
                y=threshold,
                line_color = f"rgb(0, {i * 50}, 0)",  # Gradient green tones
                line_width=1,
            )
    
    # Explicitly set the x-axis range
    fig.update_xaxes(
        range=[data['timestamp'].min(), data['timestamp'].max()],
        type='date'
    )

    # Ensure layout doesn't restrict the view
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(fixedrange=False),
        yaxis=dict(fixedrange=False)  # Allow users to zoom in/out
    )
    return fig
