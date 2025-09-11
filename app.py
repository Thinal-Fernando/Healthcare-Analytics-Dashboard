import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html
import plotly.express as px


def load_data():
    df = pd.read_csv('assets/healthcare.csv')    # Loading the dataset
    df["Billing Amount"] = pd.to_numeric(df['Billing Amount'])    # converting billing amount to a numeric value
    df["Date of Admission"] = pd.to_datetime(df['Date of Admission'])    # Convert 'Date of Admission' into proper datetime
    return df

data = load_data()


num_records = len(data)
avg_billing = data["Billing Amount"].mean()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Healthcare Dashboard"), width=12, className="text-center my-5")
    ]),
    dbc.Row([
        dbc.Col(html.Div(f"Total Patient Records: {num_records}", className="text-center my-3 top-text"), width=7),
        dbc.Col(html.Div(f"Average Billing Amount: {avg_billing:,.2f}", className="text-center my-3 top-text"), width=7),
    ], className="mb-5")
])


if __name__ == '__main__':
    app.run(debug=True)