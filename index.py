import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

# Load the bootstrap template:
load_figure_template("minty")

# Define external stylesheet for CSS styling:
# external_stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Instantiate the app:
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])

# Instantiate the server:
server = app.server

# Import the dataset:
df = pd.read_csv('assets/supermarket_sales.csv')

# Convert data types:
df['Date'] = pd.to_datetime(df['Date'])


# ========================= BUILD THE LAYOUT =========================

app.layout = html.Div(
    id = 'div1',
    children = [
        # Create the main row where all div will be wrapped:
        dbc.Row(children=[
            # Define the first column:
            dbc.Col(children=[
                # Create a card where the filters and selectors will be located:
                dbc.Card(children=[
                    # Add a logo at the top of the card:
                    html.H2("ASIMOV", style={"font-family": "Voltaire", "font-size": "55px"}),
                    # Add a horizontal separator:
                    html.Hr(),
                    # Add a subtitle for the selector of cities:
                    html.H5("Cities:"),
                    # Add a checklist for selecting the cities:
                    dcc.Checklist(
                        options=df['City'].unique(),
                        value=df['City'].unique(),
                        id='check-city',
                        inputStyle={"margin-right": "5px"}
                    ),
                    # Add a subtitle for the variable of analysis:
                    html.H5("Variable of Analysis", style={"margin-top": "30px"}),
                    # Add a radio selector for the 'gross income' and 'rating':
                    dcc.RadioItems(
                        options=['gross income', 'Rating'],
                        value='gross income',
                        id='main-variable',
                        inputStyle={"margin-right": "5px"}
                    )
                ], style={"margin": "10px", "height": "90vh", "padding": "10px"})
            ],
            sm=3),

            # Define the second column:
            dbc.Col(children=[
                # Create the first row:
                dbc.Row([
                    dbc.Col([dcc.Graph(id='city-fig')],   sm=3),
                    dbc.Col([dcc.Graph(id='gender-fig')], sm=3),
                    dbc.Col([dcc.Graph(id='paym-fig')],   sm=3)
                ]),
                # Create the second row:
                dbc.Row([
                    dcc.Graph(id='income-per-date-fig')
                ]),
                # Create the third row:
                dbc.Row([
                    dcc.Graph(id='income-per-product-fig')
                ])
            ],
            sm=9)
        ])
    ]
)


# ====================== DEFINE THE CALLBACKS ========================

@app.callback(
    [
        Output(component_id='city-fig', component_property='figure'),
        Output(component_id='paym-fig', component_property='figure'),
        Output(component_id='gender-fig', component_property='figure'),
        Output(component_id='income-per-date-fig', component_property='figure'),
        Output(component_id='income-per-product-fig', component_property='figure')
    ],
    [
        Input(component_id='check-city', component_property='value'),
        Input(component_id='main-variable', component_property='value')
    ]
)
def reder_graphs(cities, main_var):
    """
    Renders the graphs based on modifications made by the callbacks.
    :param cities:
    :param main_var:
    :return: Rendered charts.
    """

    # Define which operation to be used by the 1st chart:
    operation = np.sum if main_var == 'gross income' else np.mean
    # Define the filtered dataframe to be sourced by the charts:
    df_filter = df[df['City'].isin(cities)]

    # Define the df to be used by the bar chart grouped by city:
    df_city = df_filter.groupby('City')[main_var].apply(operation).to_frame().reset_index()
    # Define the df to be used by the bar chart grouped by payment method:
    df_payment = df_filter.groupby('Payment')[main_var].apply(operation).to_frame().reset_index()
    # Define the df to be used by the bar chart grouped by gender:
    df_gender = df_filter.groupby(['Gender', 'City'])[main_var].apply(operation).to_frame().reset_index()
    # Define the df to be used by the bar chart grouped by date (time series):
    df_income_time = df_filter.groupby('Date')[main_var].apply(operation).to_frame().reset_index()
    # Define the df to be used by the bar chart grouped by city and product line:
    df_product_income = df_filter.groupby(['Product line', 'City'])[main_var].apply(operation).to_frame().reset_index()

    # Construct the bar chart grouped by city:
    fig_city = px.bar(data_frame=df_city, x='City', y=main_var, color='City')
    # Construct the bar chart grouped by payment method:
    fig_payment = px.bar(data_frame=df_payment, x=main_var, y='Payment', orientation='h')
    # Construc the bar chart grouped by gender:
    fig_gender = px.bar(data_frame=df_gender, x='Gender', y=main_var, color='City', barmode='group')
    # Construct the bar chart grouped by date:
    fig_income_time = px.bar(data_frame=df_income_time, x='Date', y=main_var)
    # Construct the bar chart grouped by product line and city:
    fig_product_income = px.bar(data_frame=df_product_income,
                                x=main_var, y='Product line', color='City',
                                orientation='h', barmode='group')

    # Define the layout of the figures iteratively:
    for fig in [fig_city, fig_payment, fig_gender, fig_income_time]:
        fig.update_layout(margin = dict(l=0, r=0, t=20, b=20), height = 200, template="minty")

    fig_product_income.update_layout(margin = dict(l=0, r=0, t=20, b=20), height = 500)

    return fig_city, fig_payment, fig_gender, fig_income_time, fig_product_income


# ========================== RUN THE SERVER ==========================

if __name__ == '__main__':
    app.run_server(port=8050, debug=True)