import dash
from dash import html, dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
 
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from dash_bootstrap_templates import load_figure_template

load_figure_template("minty")


app = dash.Dash(external_stylesheets=[dbc.themes.YETI])
server = app.server


df_data = pd.read_csv("Vendas.csv")
df_data["Date"] = df_data["entrega"]
df_data["Valor"] = df_data["valor_entregue"]
df_data["Qtde"] = df_data["qtde_entregue"]



# =========  Layout  =========== #
app.layout = html.Div(children=[
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.H2("Linx", style={"font-family": "Voltaire", "font-size": "60px"}),
                            html.Hr(),

                            html.H5("Regiões:"),
                            dcc.Checklist(df_data["regiao"].value_counts().index,
                            df_data["regiao"].value_counts().index, id="check_region",
                            inputStyle={"margin-right": "5px", "margin-left": "20px"}),

                            html.H5("Variável de análise:", style={"margin-top": "30px"}),
                            dcc.RadioItems(["Valor", "Quantidade"], "Valor", id="main_variable",
                            inputStyle={"margin-right": "5px", "margin-left": "20px"}),

                        ], style={"height": "90vh", "margin": "20px", "padding": "20px"})
                        
                    ], sm=2),

                    dbc.Col([
                        dbc.Row([
                            dbc.Col([dcc.Graph(id="region_fig"),], sm=4),
                            dbc.Col([dcc.Graph(id="group_fig"),], sm=4),
                            dbc.Col([dcc.Graph(id="vendor_fig"),], sm=4)
                        ]),
                        # dbc.Row([dcc.Graph(id="income_per_date_fig")]),
                        dbc.Row([dcc.Graph(id="income_per_group_fig")]),
                    ], sm=10)
                ])   
            ]
        )


# =========  Callbacks  =========== #
@app.callback([
            Output('region_fig', 'figure'),
            Output('group_fig', 'figure'),
            Output('vendor_fig', 'figure'),
            # Output('income_per_date_fig', 'figure'),
            Output('income_per_group_fig', 'figure'),
        ],
            [
                Input('check_region', 'value'),
                Input('main_variable', 'value')
            ])
def render_graphs(cities, main_variable):
    # cities = ["Yangon", "Mandalay"]
    # main_variable= "gross income"

    variable = "valor_entregue" if main_variable == "Valor" else "qtde_entregue"

    operation = np.sum ##if main_variable == "gross income" else np.mean


    df_filtered = df_data[df_data["regiao"].isin(cities)]
    
    df_regiao = df_filtered.groupby("regiao")[variable].apply(operation).to_frame().reset_index()
    df_gerente = df_filtered.groupby("gerente")[variable].apply(operation).to_frame().reset_index()
    df_payment = df_filtered.groupby("grupo_produto")[variable].apply(operation).to_frame().reset_index()
    
    df_income_time = df_filtered.groupby("Date")[variable].apply(operation).to_frame().reset_index()
    df_product_income = df_filtered.groupby( "regiao")[variable].apply(operation).to_frame().reset_index()

    fig_regiao = px.bar(df_regiao, x="regiao", y=variable)
    fig_regiao.update_layout(xaxis_title = "Região")
    fig_regiao.update_layout(yaxis_title = main_variable)

    fig_payment = px.bar(df_payment, y="grupo_produto", x=variable, orientation="h")
    fig_payment.update_layout(yaxis_title = "Grupo")
    fig_payment.update_layout(xaxis_title = main_variable)
   
    fig_gerente = px.bar(df_gerente, x=variable, y="gerente",barmode="group",orientation="h")
    fig_gerente.update_layout(xaxis_title = "Gerente")
    fig_gerente.update_layout(yaxis_title = main_variable)
    
    fig_product_income = px.bar(df_product_income, x=variable, y="regiao", color="regiao", orientation="h", barmode="group")
    fig_product_income.update_layout(yaxis_title = "Região")
    fig_product_income.update_layout(xaxis_title = main_variable)

    fig_income_date = px.bar(df_income_time, y=variable, x="Date")
    

    for fig in [fig_regiao, fig_payment, fig_gerente, fig_income_date]:
        fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200, template="minty")

    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=500)
    
    # return fig_regiao, fig_payment, fig_gerente, fig_income_date, fig_product_income
    return fig_regiao, fig_payment, fig_gerente,  fig_product_income


# =========  Run server  =========== #
if __name__ == "__main__":
    app.run_server(port=8050,debug=False)