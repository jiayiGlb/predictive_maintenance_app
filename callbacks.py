from dash import Input, Output, State, callback_context
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.data_processing import load_device_data, generate_diagram_data, generate_plot_with_thresholds
from config.thresholds import THRESHOLDS
from dash import dcc, Input, Output, State
from dash import Input, Output, State, html
from dash import dcc
from config.dynamic_thresholds import generate_threshold_card


processed_data_cache = {}

def register_callbacks(app):
    @app.callback(
        Output('diagram-container', 'children'),
        [Input('showDiagramBtn', 'n_clicks')],
        [State('device_name', 'value'), State('start_date', 'date'),
         State('interval', 'value'), State('sensor', 'value')]
    )
    def generate_diagram(n_clicks, device_name, start_date, interval, sensor):
        print("generate_diagram", n_clicks, device_name, start_date, interval, sensor)
        if not n_clicks:
            return "Click 'Show Diagram' to generate data visualization."

        # Calculate the end date
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        if "day" in interval:
            days = int(interval.split("_")[0]) - 1
            end_date_obj = start_date_obj + timedelta(days=days)
        elif "month" in interval:
            months = int(interval.split("_")[0])
            end_date_obj = start_date_obj + timedelta(days=29 * months)
        else:
            return "Invalid interval format."

        end_date = end_date_obj.strftime("%Y-%m-%d")

        # Load and process data
        data = load_device_data(device_name, start_date, end_date, sensor)
        if data is None or data.empty:
            return "No data found for the selected device and date range."


        data = generate_diagram_data(data, interval)
        # Debug the DataFrame
        print("DataFrame columns:", data.columns)
        print("DataFrame preview:\n", data.head())

        # Ensure the selected sensor column exists
        if sensor not in data.columns:
            return f"Error: Sensor column '{sensor}' not found in the data. Available columns: {list(data.columns)}"

        # Store processed data in the global dictionary
        key = f"{device_name}_{start_date}_{interval}_{sensor}"
        processed_data_cache[key] = data

       # Retrieve thresholds for the sensor
        thresholds = THRESHOLDS.get(sensor, {'high': [], 'low': []})

        # Generate the plot
        fig = generate_plot_with_thresholds(data, sensor, thresholds)

        return dcc.Graph(figure=fig)
    
    @app.callback(
        Output('threshold-card-container', 'children'),
        [Input('sensor', 'value')]
    )
    def update_threshold_card(sensor):
        if sensor:
            thresholds = THRESHOLDS.get(sensor, {'high': [], 'low': []})
            return generate_threshold_card(sensor, thresholds)
        return html.Div("Select a sensor to display thresholds.")

    @app.callback(
    Output('report-container', 'children'),
    [Input('generateReportBtn', 'n_clicks')],
    [State('device_name', 'value'), State('start_date', 'date'),
     State('interval', 'value'), State('sensor', 'value')]
)
    def generate_report(n_clicks, device_name, start_date, interval, sensor):
        if not n_clicks:
            return "Click 'Generate Report' to calculate the status."

        # Retrieve processed data from the global cache
        key = f"{device_name}_{start_date}_{interval}_{sensor}"
        data = processed_data_cache.get(key)

        if data is None or data.empty:
            return html.Div("No data available for the selected parameters.", className="alert alert-warning")

        thresholds = THRESHOLDS.get(sensor, {'high': [], 'low': []})
        monitoring_time = {'1_day': 10, '5_days': 6, '1_month': 6}  # Consistency duration in intervals
        fault_count = monitoring_time.get(interval, 0)

        # Initialize fault tracking
        high_count = [0] * len(thresholds['high'])
        low_count = [0] * len(thresholds['low'])
        high_periods = [[] for _ in thresholds['high']]
        low_periods = [[] for _ in thresholds['low']]

        for i, threshold in enumerate(thresholds['high']):
            # Track breaches
            data['above_threshold'] = data[sensor] > threshold

            # Group consecutive breaches
            data['group'] = (data['above_threshold'] != data['above_threshold'].shift()).cumsum()

            # Check consistency within each group
            for group, group_data in data.groupby('group'):
                if group_data['above_threshold'].iloc[0]:  # Only process True groups
                    if len(group_data) >= fault_count:
                        high_count[i] += 1
                        start_time = group_data['timestamp'].iloc[0]
                        end_time = group_data['timestamp'].iloc[-1]
                        high_periods[i].append((start_time, end_time))

        for i, threshold in enumerate(thresholds['low']):
            # Track breaches
            data['below_threshold'] = data[sensor] < threshold

            # Group consecutive breaches
            data['group'] = (data['below_threshold'] != data['below_threshold'].shift()).cumsum()

            # Check consistency within each group
            for group, group_data in data.groupby('group'):
                if group_data['below_threshold'].iloc[0]:  # Only process True groups
                    if len(group_data) >= fault_count:
                        low_count[i] += 1
                        start_time = group_data['timestamp'].iloc[0]
                        end_time = group_data['timestamp'].iloc[-1]
                        low_periods[i].append((start_time, end_time))

        # Determine status and generate alert messages
        alert_message = None
        periods_message = []

        # Component mapping
        SENSOR_COMPONENTS = {
            "VMS_Voltage1": "Power Supply",
            "VMS_Voltage2": "Power Supply",
            "VMS_Voltage3": "Power Supply",
            "VMS_Photosensor1": "LED Card Column",
            "VMS_Photosensor2": "LED Card Column",
            "VMS_Photosensor3": "LED Card Column",
            "VMS_Temp1": "IPC, Modem, Switch",
            "VMS_Temp2": "IPC, Modem, Switch",
            "VMS_Temp3": "IPC, Modem, Switch",
            "CPU": "IPC",
            "Memory": "IPC",
            "DiskSpace": "IPC",
        }

        # High thresholds
        for i, count in enumerate(high_count):
            if count > 0:
                for start, end in high_periods[i]:
                    periods_message.append(f"from {start} to {end}")

                component = SENSOR_COMPONENTS.get(sensor, "Unknown Component")

                if i == len(high_count) - 1:
                    alert_message = (
                        f"The {sensor} sensor has reached a Fault status (High) {count} times during periods: "
                        f"{', '.join(periods_message)}. Replace the {component}."
                    )
                elif i == len(high_count) - 2:
                    alert_message = (
                        f"The {sensor} sensor has reached a Major status (High) {count} times during periods: "
                        f"{', '.join(periods_message)}. On-site inspection required for {component}."
                    )
                else:
                    alert_message = (
                        f"The {sensor} sensor has reached a Minor status (High) {count} times during periods: "
                        f"{', '.join(periods_message)}. Monitor the {component}."
                    )
                break

        # Low thresholds
        for i, count in enumerate(low_count):
            if count > 0:
                periods_message = []
                for start, end in low_periods[i]:
                    periods_message.append(f"from {start} to {end}")

                component = SENSOR_COMPONENTS.get(sensor, "Unknown Component")

                if i == len(low_count) - 1:
                    alert_message = (
                        f"The {sensor} sensor has reached a Fault status (Low) {count} times during periods: "
                        f"{', '.join(periods_message)}. Replace the {component}."
                    )
                elif i == len(low_count) - 2:
                    alert_message = (
                        f"The {sensor} sensor has reached a Major status (Low) {count} times during periods: "
                        f"{', '.join(periods_message)}. On-site inspection required for {component}."
                    )
                else:
                    alert_message = (
                        f"The {sensor} sensor has reached a Minor status (Low) {count} times during periods: "
                        f"{', '.join(periods_message)}. Monitor the {component}."
                    )
                break

        # Default message if no thresholds are breached
        if not alert_message:
            alert_message = f"The {sensor} sensor is operating within thresholds."

        return html.Div(alert_message, className="alert alert-info")
