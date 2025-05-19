from dash import Dash
from layout import get_layout
from callbacks import register_callbacks
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set layout from a separate file
app.layout = get_layout()

# Register callbacks from a separate file
register_callbacks(app)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=False)
