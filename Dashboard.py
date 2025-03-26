import dash
from dash import html, dcc
import pandas as pd
import plotly.graph_objs as go
import requests

# Constants
THINGSPEAK_API_KEY = "8VBQT42DSZ7SSCV3"
CHANNEL_ID = "2867238"

PREDICTED_CSV_URLS = {
    "Air_Temperature": "https://drive.google.com/uc?export=download&id=1-bNzPoA-2VWE1vpka4vy4vUXxI17MqPb",
    "Soil_Temperature": "https://drive.google.com/uc?export=download&id=1-6yBJmU4Iz2wfwg_opJdKgQVu4tLEALb",
    "Humidity": "https://drive.google.com/uc?export=download&id=1-U0-uaAyyoRo4gVM-tzyFypL1nNtINKQ",
    "Light_Intensity": "https://drive.google.com/uc?export=download&id=1-A3_3DvK0eVOotIlZq5jyEl-lM0AWn27",
}

# Map fields from ThingSpeak to names
FIELD_MAP = {
    "field1": "Air Temperature (°C)",
    "field2": "Soil Temperature (°C)",
    "field3": "Humidity (%)",
    "field4": "Light Intensity (lux)",
}

# Fetch ThingSpeak actual data
def fetch_actual_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_API_KEY}&results=100"
    response = requests.get(url)
    feeds = response.json()['feeds']
    df = pd.DataFrame(feeds)
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df

# Fetch predicted data from Google Drive
def fetch_predicted_data(url):
    df = pd.read_csv(url)
    df['Time'] = pd.to_datetime(df['Time'])
    return df

# Build graph for actual data
def build_actual_graph(df, field, label):
    return dcc.Graph(
        figure={
            'data': [go.Scatter(x=df['created_at'], y=df[field], mode='lines+markers', name="Actual")],
            'layout': go.Layout(title=f"Actual - {label}", xaxis={'title': 'Time'}, yaxis={'title': label})
        }
    )

# Build graph for predicted data
def build_predicted_graph(df, label):
    return dcc.Graph(
        figure={
            'data': [go.Scatter(x=df['Time'], y=df['Predicted Value'], mode='lines+markers', name="Predicted")],
            'layout': go.Layout(title=f"Predicted - {label}", xaxis={'title': 'Time'}, yaxis={'title': label})
        }
    )

# Load data
actual_df = fetch_actual_data()

# Dash App Setup
app = dash.Dash(__name__)
app.layout = html.Div(style={'backgroundColor': '#f0fff0', 'padding': '10px'}, children=[
    html.H1("Greenhouse Monitoring Dashboard", style={'textAlign': 'center'}),

    # Actual Data Graphs
    html.H2("Actual Sensor Readings", style={'textAlign': 'center'}),
    *[build_actual_graph(actual_df, field, label) for field, label in FIELD_MAP.items()],

    # Predicted Data Graphs
    html.H2("AI Predicted Sensor Values", style={'textAlign': 'center'}),
    *[build_predicted_graph(fetch_predicted_data(url), FIELD_MAP[f'field{i+1}']) for i, (key, url) in enumerate(PREDICTED_CSV_URLS.items())]
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
