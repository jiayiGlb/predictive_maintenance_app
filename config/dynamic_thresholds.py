from dash import dcc, html
import dash_bootstrap_components as dbc

def generate_threshold_card(sensor_name, thresholds):
    high_thresholds = thresholds['high']
    low_thresholds = thresholds['low']

    return dbc.Card([
        dbc.CardHeader(html.H5(f"Thresholds for {sensor_name}")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Label(f"High Threshold {i + 1}:"),
                        dcc.Input(
                            id=f'{sensor_name}_high_threshold_{i + 1}',
                            type='number',
                            value=high_thresholds[i] if i < len(high_thresholds) else None,
                            className="mb-3"
                        )
                    ]) for i in range(max(len(high_thresholds), 3))
                ], width=6),
                dbc.Col([
                    html.Div([
                        dbc.Label(f"Low Threshold {i + 1}:"),
                        dcc.Input(
                            id=f'{sensor_name}_low_threshold_{i + 1}',
                            type='number',
                            value=low_thresholds[i] if i < len(low_thresholds) else None,
                            className="mb-3"
                        )
                    ]) for i in range(max(len(low_thresholds), 3))
                ], width=6)
            ])
        ])
    ])

