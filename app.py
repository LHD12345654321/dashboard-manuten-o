import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# Caminho para o arquivo Excel
darq = 'GESTÃO MANUTENÇÃO.xlsx'

# Carregar o DataFrame corretamente e padronizar colunas
try:
    df_manutencao = pd.read_excel(darq, sheet_name="MANUTENÇÃO POR VEÍCULO", engine="openpyxl", skiprows=2)
    df_manutencao = df_manutencao.dropna(how="all")
    df_manutencao.columns = df_manutencao.iloc[0].astype(str).str.strip().str.upper()  # Padrão MAIÚSCULAS e sem espaços
    df_manutencao = df_manutencao[1:].reset_index(drop=True)
except Exception as e:
    print(f"Erro ao carregar a planilha: {e}")
    exit()

# Verificar se todas as colunas necessárias estão presentes
colunas_esperadas = ['VEÍCULOS', 'VALOR PAGO', 'VALOR ECONOMIZADO', 'TIPO', 'CATEGORIA', 'DATA']
for coluna in colunas_esperadas:
    if coluna not in df_manutencao.columns:
        print(f"ERRO: A coluna '{coluna}' não foi encontrada na planilha! Verifique o nome exato.")
        print("Colunas disponíveis:", df_manutencao.columns.tolist())
        exit()

# Converter colunas numéricas
for col in ['VALOR PAGO', 'VALOR ECONOMIZADO']:
    df_manutencao[col] = pd.to_numeric(df_manutencao[col], errors='coerce').fillna(0)

# Criar DataFrames separados para frota leve e pesada
df_frota_leve = df_manutencao[df_manutencao['CATEGORIA'] == 'LEVE']
df_frota_pesada = df_manutencao[df_manutencao['CATEGORIA'] == 'PESADA']

# Inicializar aplicativo Dash
app = dash.Dash(__name__)
server = app.server  # Para rodar no Render
app.title = "Dashboard - Montenegro Business e Participações"

# Layout do Dashboard
app.layout = html.Div([  
    html.H1("Montenegro Business e Participações", style={'textAlign': 'center', 'color': 'white', 'fontSize': '32px', 'fontWeight': 'bold'}),
    html.H2("Dashboard de Gestão de Manutenção", style={'textAlign': 'center', 'color': 'white', 'marginBottom': '30px'}),

    dcc.Tabs(id="tabs", value="geral", children=[
        dcc.Tab(label="Visão Geral", value="geral", style={'backgroundColor': '#1E1E1E', 'color': 'white'}),
        dcc.Tab(label="Frota Leve", value="leve", style={'backgroundColor': '#1E1E1E', 'color': 'white'}),
        dcc.Tab(label="Frota Pesada", value="pesada", style={'backgroundColor': '#1E1E1E', 'color': 'white'}),
    ]),
    
    html.Div(id="tab-content")
], style={'backgroundColor': '#111111', 'padding': '30px'})

# Callback para atualizar os gráficos conforme a aba selecionada
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def atualizar_pagina(aba_selecionada):
    if aba_selecionada == "geral":
        return html.Div([ 
            dcc.Graph(figure=px.pie(df_manutencao, names='TIPO', values='VALOR PAGO', title="Gastos Totais por Tipo", 
                                   color='TIPO', color_discrete_map={'REVISÃO': '#FF6347', 'PNEU': '#4682B4', 'OUTRO': '#32CD32'})),
            dcc.Graph(figure=px.line(df_manutencao, x='DATA', y='VALOR PAGO', title="Evolução dos Gastos", 
                                    line_shape='linear', markers=True, template="plotly_dark")),
        ])
    elif aba_selecionada == "leve":
        return html.Div([ 
            dcc.Graph(figure=px.bar(df_frota_leve, x='VEÍCULOS', y='VALOR PAGO', title="Frota Leve - Gastos por Veículo", 
                                   color='VEÍCULOS', color_continuous_scale='Viridis', template="plotly_dark")),
        ])
    elif aba_selecionada == "pesada":
        return html.Div([ 
            dcc.Graph(figure=px.bar(df_frota_pesada, x='VEÍCULOS', y='VALOR PAGO', title="Frota Pesada - Gastos por Veículo", 
                                   color='VEÍCULOS', color_continuous_scale='Viridis', template="plotly_dark")),
        ])

# Rodar o servidor Dash
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
