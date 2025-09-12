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
    ], className="mb-5"),


    # showing age distribution based gender
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Patient Demographics", className="card-title"),
                    dcc.Dropdown(options=[{"label": gender, "value": gender} for gender in data["Gender"].unique()], value= None, placeholder="Select a Gender", id="gender-filter"),
                    dcc.Graph(id="age-distribution")
                ])
            ])
        ], width=7),

        # showing medical condition percentages (pie chart)
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Medical Condition Distribution", className="card-title"),
                    dcc.Graph(id="condition-distribution")
                ])
            ])
        ], width=7)  
    ]),
 
      #added Graph to show Insurance Provider Data
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Insurance Provider Comparison", className="card-title"),
                    dcc.Graph(id="insurance-comparison")
                ])
            ])
        ], width=12)
    ]),

])


#callback for graph what shows gender variation
@app.callback(
    Output(component_id="age-distribution", component_property="figure"),
    Input(component_id="gender-filter", component_property="value")
)
def update_distribution(selected_gender):
    if selected_gender:
        filtered_df = data[data["Gender"] == selected_gender]
    else:
        filtered_df = data
    
    if filtered_df.empty:
        return{}
    
    fig = px.histogram(filtered_df, x="Age", color="Gender", title="Age Distribution by Gender", color_discrete_sequence=["#636EFA","#EF553B"] )

    return fig



#callback for pie chart that shows Medical Condition distribution 
@app.callback(
    Output(component_id="condition-distribution", component_property="figure"),
    Input(component_id="gender-filter", component_property="value")
)

def update_medical_condition(selected_gender):
    filtered_df = data[data["Gender"] == selected_gender] if selected_gender else data
    fig = px.pie(filtered_df, names="Medical Condition", title="Medical Condition Distribution")
    return fig



#callback for bar chart that shows Insurance Provider
@app.callback(
    Output(component_id="insurance-comparison", component_property="figure"),
    Input(component_id="gender-filter", component_property="value")
)

def update_insurance(selected_gender):
    filtered_df = data[data["Gender"] == selected_gender] if selected_gender else data
    fig = px.bar(filtered_df, x="Insurance Provider", y="Billing Amount", color="Medical Condition", barmode="group", title="Insurance Provided Price Comparison", color_discrete_sequence=px.colors.qualitative.Set2 )
    return fig





if __name__ == '__main__':
    app.run(debug=True)