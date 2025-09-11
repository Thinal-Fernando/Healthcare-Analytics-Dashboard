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





app = dash.Dash(__name__)


if __name__ == '__main__':
    app.run(debug=True)