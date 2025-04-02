import os
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

# Configurar o caminho correto do arquivo
file_path = "GESTÃO MANUTENÇÃO.xlsx"

# Carregar os dados da planilha correta
df = pd.read_excel(file_path, sheet_name='MANUTENÇÃO POR VEÍCULO')

# Inicializar o app Dash
app = dash.Dash(__name__)
server = app.server

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Manutenção da Frota", style={'textAlign': 'center'}),
    
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Visão Geral', children=[
            html.Div([
                dcc.Dropdown(
                    id='filtro_mes',
                    options=[{'label': mes, 'value': mes} for mes in df['MÊS'].unique()],
                    placeholder="Selecione um mês"
                ),
                dcc.Graph(id='grafico_geral')
            ])
        ]),
        
        dcc.Tab(label='Frota Leve', children=[
            html.Div([
                dcc.Graph(id='grafico_frota_leve')
            ])
        ]),
        
        dcc.Tab(label='Frota Pesada', children=[
            html.Div([
                dcc.Graph(id='grafico_frota_pesada')
            ])
        ])
    ])
])

# Callback para gráfico geral
@app.callback(
    Output('grafico_geral', 'figure'),
    Input('filtro_mes', 'value')
)
def update_grafico_geral(mes):
    df_filtrado = df[df['MÊS'] == mes] if mes else df
    fig = px.bar(df_filtrado, x='VEÍCULO', y='CUSTO', title='Custo de Manutenção por Veículo')
    return fig

# Callback para gráfico frota leve
@app.callback(
    Output('grafico_frota_leve', 'figure'),
    Input('filtro_mes', 'value')
)
def update_grafico_frota_leve(mes):
    df_leve = df[(df['TIPO'] == 'Leve') & (df['MÊS'] == mes)] if mes else df[df['TIPO'] == 'Leve']
    fig = px.line(df_leve, x='VEÍCULO', y='CUSTO', title='Custo de Manutenção - Frota Leve')
    return fig

# Callback para gráfico frota pesada
@app.callback(
    Output('grafico_frota_pesada', 'figure'),
    Input('filtro_mes', 'value')
)
def update_grafico_frota_pesada(mes):
    df_pesada = df[(df['TIPO'] == 'Pesada') & (df['MÊS'] == mes)] if mes else df[df['TIPO'] == 'Pesada']
    fig = px.line(df_pesada, x='VEÍCULO', y='CUSTO', title='Custo de Manutenção - Frota Pesada')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
    