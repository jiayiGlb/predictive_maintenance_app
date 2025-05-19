from config.thresholds import THRESHOLDS
def generate_alert_report(filtered_df, frequency):
    # Filter rows where any sensor value exceeds the threshold
    exceeded_data = filtered_df.dropna(how='all', subset=THRESHOLDS.keys())
    alert_counts = exceeded_data.groupby(['devicename', 'timestamp']).size()
    # Select device-timestamp combinations where alert frequency exceeds user-defined frequency
    alert_exceeded = alert_counts[alert_counts >= frequency].index

    # Filter original data to return only the relevant rows
    alert_report = exceeded_data[exceeded_data.set_index(['devicename', 'timestamp']).index.isin(alert_exceeded)]
    # Reshape the DataFrame
    melted_report = alert_report.melt(
        id_vars=['devicename', 'timestamp'], 
        value_vars=THRESHOLDS.keys(), 
        var_name='sensor_name', 
        value_name='value'
    )
    
    # Filter out rows where the value is NaN
    melted_report = melted_report.dropna(subset=['value'])
    
    # # Rename columns
    # melted_report = melted_report.rename(columns={
    #     'devicename': 'Device Name',
    #     'timestamp': 'Timestamp',
    #     'sensor_name': 'Sensor Name',
    #     'value': 'Value'
    # })
    
    return melted_report.reset_index(drop=True)  # Reset index for cleaner output