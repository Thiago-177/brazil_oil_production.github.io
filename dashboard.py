import dash
from dash import dcc, html
from dash.dependencies import Input, Output, ClientsideFunction
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import json

CENTER_LAT, CENTER_LON = -21.18, -42.16

# splitting the dataset for work better
# df = pd.read_csv("brazil_oil_production.csv", sep=";")
# df_bacias = df.loc[df.Basin.isin(["Campos", "Santos"])]
# # df_santos = df.loc[df.Basin.isin(["Santos"])]
# df_bacias.to_csv("df_bacias.csv")
# df_santos.to_csv("df_santos.csv")

df_campos = pd.read_csv("df_campos.csv")
df_santos = pd.read_csv("df_santos.csv")
df_bacias = pd.read_csv("df_bacias.csv")

brazil_fields = json.load(open("campos_de_producao_jan2023/arquivo.json", "r", encoding="utf8"))

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
config_graph={"displayModeBar": False, "showTips": False}
# ========= Fig 1 ========= #
for df_ in (df_bacias,df_santos,df_campos):
    df_.loc[df_['Field'].isin(['ANC_LULA','LULA']), 'Field'] = 'TUPI'
    df_["Oil (m³)"] = df_["Oil (m³)"].astype(float)
    

df1 = df_bacias.groupby("Field")["Oil (m³)"].sum()
df1.sort_values(ascending=False, inplace=True)
df1 = df1.reset_index()

select_columns = {
                    "Oil (m³)": "Top 10 Campos Produtores",
                    "Year": "Evolução da Produção"
                    }

fig1 = px.choropleth_mapbox(df1, locations=df1.Field,
    geojson=brazil_fields, center={"lat": -21.18, "lon": -42.16},  # https://www.google.com/maps/ -> right click -> get lat/lon
    featureidkey="properties.NOM_CAMPO",
    zoom=5, color="Oil (m³)", color_continuous_scale="Redor", opacity=0.9,
    hover_data={"Field": True},
    labels={'Oil (m³)':'Oil production'},
    )
fig1.update_layout(
                # mapbox_accesstoken=token,
                paper_bgcolor= 'rgb(200,200,200)',
                mapbox_style="carto-positron",
                autosize=True,
                font={'color':'rgb(0,0,0)','family':'sans-serif'},
                margin=go.layout.Margin(l=0, r=10, t=10, b=0),
                showlegend=False,)

df1["Oil (m³)"] = df1["Oil (m³)"].astype(int)
df1["Oil text"] = df1["Oil (m³)"].apply(lambda x: "{:_.0f} m³".format(x).replace('.', ',').replace('_', '.'))

fig2 = go.Figure(go.Bar(
    x=df1['Field'][:10],
    y=df1['Oil (m³)'][:10],
    orientation='v',
    textposition='auto',
    text=df1["Oil text"] ,
    insidetextfont=dict(family='Times', size=12)))


#fig1.show()

# ======================== layout ========================== #
app.layout = dbc.Container(
    children=[
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(id="logo", src=app.get_asset_url("logo-eliis.png"), height='70px',),
                    html.H5(children="Bacias Produção de Óleo até 2020", style={'margin':'5px'}),
                ],style={"background-color": "#1E1E1E", "margin": "10px", "padding": "15px"}),
                html.P("Informe qual a Bacia deseja obter informações:", style={"margin-top": "40px"}),
                dbc.RadioItems(
                                id="radio-basin",
                                options=[{"label":"Total","value":"Total"},{"label":"Santos","value":"Santos"},
                                         {"label":"Campos","value":"Campos"}],
                                value="Total",
                                inline=True,
                                labelCheckedClassName="text-success",
                                inputCheckedClassName="border border-success bg-success",
                            ),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span('Produção total', className="card-text"),
                                html.H5(style={'color':'#adfc92'}, 
                                        id='bacia-prod-total'),
                                html.Span("Campo Mais Produtivo", className="card-text"),
                                html.H6(style={'color':'#2D9809'},
                                    id='campo-produtor')
                            ])
                        ], color='light', outline=True, 
                            style={"margin-top":'10px',
                                'box-shadow':"0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                                'color':'#FFFFFF'})], width=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Span('Poço Mais Produtivo', className="card-text"),
                                html.H5(style={'color':"#389fd6"}, 
                                        id='poco-name'),
                                html.Span("Poço Produção Total", className="card-text"),
                                html.H6(
                                    id='poco-product', style={'color':"#18AEE6"})
                            ])
                        ], color='light', outline=True, 
                            style={"margin-top":'10px',
                                'box-shadow':"0 4px 4px 0 rgba(0,0,0,0.15), 0 4px 20px 0 rgba(0,0,0,0.19)",
                                'color':'#FFFFFF'})], width=6),
                ]),
                
                html.Div([
                    html.P("Selecione o Parâmetro a se visualizar:", style={"margin-top": "25px"}),
                    dcc.Dropdown(
                                    id="select-graph",
                                    options=[{"label": j, "value": i}
                                            for i, j in select_columns.items()],
                                    value = "Oil (m³)",
                                    style = {"margin-top":"10px"},
                                ),
                dcc.Graph(
                            id="line-graph", figure=fig2, style={
                                "background-color": "#242424",
                            }, config=config_graph),
                ], id='teste')
            ],  width=5, style={
                          "padding": "25px",
                          "background-color": "#242424"}
            ),
            dbc.Col([
                dcc.Graph(id="basin-map", figure=fig1, 
                            style={'height': '100vh', 'margin-right': '10px',
                                    "background-color": "#111111"},
                            config=config_graph
                                                                 
                )], width=7
            )
        ])
    ], fluid=True
)

# ========= Callbacks ================== #
@app.callback(
    [
        Output("bacia-prod-total", "children"),
        Output("campo-produtor", "children"),
        Output("poco-name", "children"),
        Output("poco-product", "children"),
        # Output("obitos-text", "children"),
        # Output("obitos-na-data-text", "children"),
    ], [Input("radio-basin", "value")])#, Input("location-button", "children")])


def display_basin(basin):
    
    def value_extract(basin):
        if basin == "Total":
            df_uso = df_bacias
        else:
            df_uso = df_bacias.loc[df_bacias.Basin.isin([basin])]
        
        producao = df_uso["Oil (m³)"].astype(float).sum()
        ##
        df_topcampo = df_uso.groupby("Field")["Oil (m³)"].sum()
        df_topcampo.sort_values(ascending=False, inplace=True)
        df_topcampo = df_topcampo.reset_index()
        top_campo = df_topcampo['Field'][0]
        top_campo_prod = df_topcampo["Oil (m³)"][0]
        ##
        top_well = df_uso.groupby(['Field','Well'])['Oil (m³)'].sum()
        top_well = top_well.reset_index()
        top_well = top_well.sort_values(['Oil (m³)'], ascending=False)
        top_well.loc[top_well['Field']==top_campo]
        well = top_well.loc[top_well['Field']==top_campo, ['Well', 'Oil (m³)']].values[0]
        well_name, well_prod = well[0], well[1]

        return producao, top_campo, top_campo_prod, well_name, well_prod
    
    if basin == "Total":
        producao, top_campo, top_campo_prod, well_name, well_prod = value_extract(basin)

    elif basin == "Santos":
        producao, top_campo, top_campo_prod, well_name, well_prod = value_extract(basin)
        

    elif basin == "Campos":
        producao, top_campo, top_campo_prod, well_name, well_prod = value_extract(basin)
        
    producao = "{:_.0f} m³".format(producao).replace('.', ',').replace('_', '.')
    campo_ret = "{}: {:_.0f} m³".format(top_campo,top_campo_prod).replace('.', ',').replace('_', '.')
    well_prod = "{:_.0f} m³".format(well_prod).replace('.', ',').replace('_', '.')

    return (producao, campo_ret, well_name, well_prod)

@app.callback(
    [
        Output("line-graph", "figure"),
        # Output("obitos-na-data-text", "children"),
    ], [Input("select-graph", "value"), Input("radio-basin", "value")])


def graphs1(plot_, basin):
    def value_extract1(basin):
        if basin == "Total":
            df_uso = df_bacias
        else:
            df_uso = df_bacias.loc[df_bacias.Basin.isin([basin])]
        
        df_plot = df_uso.groupby(["Basin","Field"])["Oil (m³)"].sum()
        df_plot.sort_values(ascending=False, inplace=True)
        df_plot = df_plot.reset_index()
        df_plot["Oil (m³)"] = df_plot["Oil (m³)"].astype(int)
        df_plot["Oil text"] = df_plot["Oil (m³)"].apply(lambda x: "{:_.0f} m³".format(x).replace('.', ',').replace('_', '.'))
        df_plot['bar'] = df_plot['Field'] + " ("+ df_plot['Basin'] +")" 
        return df_plot, df_plot['Field'][:10].to_list()

    def value_extract2(basin):
        if basin == "Total":
            df_uso = df_bacias
        else:
            df_uso = df_bacias.loc[df_bacias.Basin.isin([basin])]

        df_plot2 = df_uso.groupby(["Basin","Year","Field"])['Oil (m³)'].sum()
        df_plot2 = df_plot2.reset_index()
        df_plot2 = df_plot2.sort_values(["Field",'Year'])
        return df_plot2

    if plot_ == 'Oil (m³)':
        df_bar, lista = value_extract1(basin)
        fig2 = go.Figure(go.Bar(
                            x=df_bar['bar'][:10],
                            y=df_bar['Oil (m³)'][:10],
                            orientation='v',
                            textposition='auto',
                            text=df_bar["Oil text"] ,
                            insidetextfont=dict(family='Times', size=12)))
    else:
        df_bar, lista = value_extract1(basin)
        df_lines = value_extract2(basin)
        fig2 = px.line(df_lines.loc[df_lines['Field'].isin(lista)], y="Oil (m³)", x="Year", color="Field",
                       hover_data={'Basin':True})
    
    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        font={'color':'rgb(255,255,255)','family':'sans-serif'},
        margin=dict(l=10, r=10, b=10, t=10),
        )
    
    return (fig2,)

if __name__ == "__main__":
    app.run(debug=True)  