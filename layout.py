from dash import dcc, html
import dash_bootstrap_components as dbc
from config.thresholds import THRESHOLDS
from datetime import datetime
from dash import dcc, html
import dash_bootstrap_components as dbc

from datetime import datetime
import os


def get_layout():
    return dbc.Container([
        html.H1("Sensor Data Visualization", className="text-center my-4"),

        dbc.Row([
            # Diagram and Report Column
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Diagram")),
                    dbc.CardBody(
                        html.Div(id='diagram-container', children="Diagram will appear here.",
                                 style={"height": "400px"})
                    )
                ], className="mb-4"),

                dbc.Card([
                    dbc.CardHeader(html.H5("Report")),
                    dbc.CardBody(
                        html.Div(id='report-container', children="Report will appear here.")
                    )
                ])
            ], width=6),

            # Input Parameters and Thresholds Column
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Input Parameters")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Device Name:"),
                                dcc.Dropdown(
                                    id='device_name',
                                    options=get_device_options(),
                                    value=None,  # or set default like devices[0] if needed
                                    className="mb-3"
                                )
                            ]),

                            dbc.Col([
                                dbc.Label("Start Date:"),
                                dcc.DatePickerSingle(
                                    id='start_date',
                                    date=datetime(2023, 11, 1).strftime('%Y-%m-%d'),
                                    className="mb-3"
                                )
                            ])
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Interval:"),
                                dcc.Dropdown(
                                    id='interval',
                                    options=[
                                        {'label': '1 Day', 'value': '1_day'},
                                        {'label': '5 Days', 'value': '5_days'},
                                        {'label': '1 Month', 'value': '1_month'}
                                    ],
                                    value='1_day',
                                    className="mb-3"
                                )
                            ]),

                            dbc.Col([
                                dbc.Label("Sensor:"),
                                dcc.Dropdown(
                                    id='sensor',
                                    options=[
                                        {'label': sensor, 'value': sensor}
                                        for sensor in THRESHOLDS.keys()
                                    ],
                                    value=list(THRESHOLDS.keys())[0],
                                    className="mb-3"
                                )
                            ])
                        ]),

                        dbc.Button("Show Diagram", id='showDiagramBtn', color="primary", className="me-2"),
                        dbc.Button("Generate Report", id='generateReportBtn', color="success")
                    ])
                ], className="mb-4"),
                html.Div(id='threshold-card-container') 
            ], width=6)
        ])
    ], fluid=True)


def get_device_options():
    data_path = './data'
    if not os.path.exists(data_path):
        return []
    devices = sorted(
        [name for name in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, name))]
    )
    return [{'label': device, 'value': device} for device in devices]
