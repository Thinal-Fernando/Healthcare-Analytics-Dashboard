import dash
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, Input, Output, html
import plotly.express as px
import os
import base64


def load_data():
    df = pd.read_csv('assets/healthcare.csv')    # Loading the dataset
    df["Billing Amount"] = pd.to_numeric(df['Billing Amount'])    # converting billing amount to a numeric value
    df["Date of Admission"] = pd.to_datetime(df['Date of Admission'])    # Convert 'Date of Admission' into proper datetime
    df["YearMonth"] = df['Date of Admission'].dt.to_period("M")  #create a new column 'YearMonth' from the admission date with months
    return df

data = load_data()


num_records = len(data)
avg_billing = data["Billing Amount"].mean()


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/style.css"])


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Healthcare Dashboard"), width=12, className="text-center my-5")
    ]),
    dbc.Row([
        dbc.Col(html.Div(f"Total Patient Records: {num_records}", className="text-center my-3 top-text"), width=12),
        dbc.Col(html.Div(f"Average Billing Amount: {avg_billing:,.2f}", className="text-center my-3 top-text"), width=12)
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
        ], width=6),

        # showing medical condition percentages (pie chart)
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Medical Condition Distribution", className="card-title"),
                    dcc.Graph(id="condition-distribution")
                ]),
                className="special-card"
            )
        ], width=6)  
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
    
    #graph to show billing amount distribution with a slider to select a required Amount range 
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Billing Amount Distribution", className="card-title"),
                    dcc.Slider(id="billing-slider", min=data["Billing Amount"].min(), max=data["Billing Amount"].max(), value = data["Billing Amount"].median(), marks={int(value): f"${int(value):,}" for value in data["Billing Amount"].quantile([0,0.25,0.5,0.75,1]).values}, step=100
                     ),
                    dcc.Graph(id="billing-distribution")
                ])
            ])
        ], width=12)
    ]),
    # graph to display the trends in admission and radio buttons to select graph type and a drop down menu to specify the condition
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Trends in Admission", className="card-title"),
                    dcc.RadioItems(options=[{"label": "Line Chart", 'value': 'line'}, {"label": "Bar Chart", 'value': 'bar'}], value='line', inline=True, className='mb-4 my-radio' , id="chart-type"),
                    dcc.Dropdown(id="condition-filter", options=[{'label': condition , 'value': condition} for condition in data["Medical Condition"].unique()], value=None, placeholder="Select a Medical Condition"),
                    dcc.Graph(id="admission-trends")
                ])
            ])
        ], width=12)

    # Added section so user can upload csv file  
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data' , 
                children=html.Div(['Drag and Drop or', html.A('Select Files')]), 
                style={
                    'width': 'auto', 'height': '100px', 'lineHeight' : '100px', 
                    'borderWidth': '1px', 'borderStyle': 'dashed', 
                    'textAlign' : 'center', 'margin': '10px'
                }, multiple=False
            ),
            html.Div(id='output-data')
        ])
    ])
], fluid=True)


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



#callback for histogram that shows billing amount distribution with slider to change the range and gender selection
@app.callback(
    Output(component_id="billing-distribution", component_property="figure"),
    Input(component_id="gender-filter", component_property="value"),
    Input(component_id="billing-slider", component_property="value")
)

def update_billing(selected_gender, slider_value):
    filtered_df = data[data["Gender"] == selected_gender] if selected_gender else data
    filtered_df = filtered_df[filtered_df["Billing Amount"] <= slider_value]
    fig = px.histogram(filtered_df, x="Billing Amount", nbins=10 , title="Billing Amount Distribution")
    return fig




#callback for a bar or line graph that shows number of patients with conditions and the option to specify the condition

@app.callback(
    Output(component_id="admission-trends", component_property="figure"),
    Input(component_id="chart-type", component_property="value"),
    Input(component_id="condition-filter", component_property="value")
)

def update_billing(chart_type, selected_condition):
    filtered_df = data[data["Medical Condition"] == selected_condition] if selected_condition else data
    trend_df = filtered_df.groupby("YearMonth").size().reset_index(name="Count")
    trend_df["YearMonth"] = trend_df["YearMonth"].astype(str)

    if chart_type =="line":
        fig = px.line(trend_df, x="YearMonth", y="Count", title="Admission Trends over Time")
    else:
        fig = px.bar(trend_df, x="YearMonth", y="Count", title="Admission Trends over Time")

    return fig



#created callback that 

@app.callback(
    Output(component_id="output-data", component_property="children"),
    Input(component_id="upload-data", component_property="contents"),
    Input(component_id="upload-data", component_property="filename")
)

def save_file(contents, filename):
    if contents is None:
        return "No file uploaded yet."
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    save_to_path = os.path.join(os.getcwd(), filename)
    with open(save_to_path, "wb") as f:
        f.write(decoded)



if __name__ == '__main__':
    app.run(debug=True)