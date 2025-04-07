import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from dash.exceptions import PreventUpdate

# Caminho para o arquivo Excel
darq = 'GESTÃO MANUTENÇÃO.xlsx'

# Carregar o DataFrame corretamente e padronizar colunas
try:
    df_manutencao = pd.read_excel(darq, sheet_name="MANUTENÇÃO POR VEÍCULO", engine="openpyxl", skiprows=2)
    df_manutencao = df_manutencao.dropna(how="all")
    df_manutencao.columns = df_manutencao.iloc[0].astype(str).str.strip().str.upper()
    df_manutencao = df_manutencao[1:].reset_index(drop=True)
except Exception as e:
    print(f"Erro ao carregar a planilha: {e}")
    exit()

# Verificar colunas
colunas_esperadas = ['VEÍCULOS', 'VALOR PAGO', 'VALOR ECONOMIZADO', 'TIPO', 'CATEGORIA', 'DATA', 'PLACA']
for coluna in colunas_esperadas:
    if coluna not in df_manutencao.columns:
        print(f"ERRO: A coluna '{coluna}' não foi encontrada na planilha!")
        exit()

# Converter tipos e criar colunas auxiliares
df_manutencao['VALOR PAGO'] = pd.to_numeric(df_manutencao['VALOR PAGO'], errors='coerce').fillna(0)
df_manutencao['VALOR ECONOMIZADO'] = pd.to_numeric(df_manutencao['VALOR ECONOMIZADO'], errors='coerce').fillna(0)
df_manutencao['DATA'] = pd.to_datetime(df_manutencao['DATA'], errors='coerce')
df_manutencao['ANO_MES'] = df_manutencao['DATA'].dt.strftime('%b/%y').str.upper()
df_manutencao['MODELO/PLACA'] = df_manutencao['VEÍCULOS'] + ' / ' + df_manutencao['PLACA'].astype(str)

# Inicializar app
app = dash.Dash(__name__)
server = app.server
app.title = "Dashboard - Montenegro Business e Participações"

# Layout
app.layout = html.Div([
    dcc.Store(id="aba-salva", storage_type="local"),  # 🆕 Armazenamento local da aba preferida

    html.H1("Montenegro Business e Participações", style={'textAlign': 'center', 'color': '#FFF'}),
    html.H2("Dashboard de Gestão de Manutenção", style={'textAlign': 'center', 'color': '#CCC'}),

    dcc.Tabs(id="tabs", value=None, children=[  # 🆕 value=None para ser definido dinamicamente
        dcc.Tab(label="Visão Geral", value="geral"),
        dcc.Tab(label="Frota Leve", value="leve"),
        dcc.Tab(label="Frota Pesada", value="pesada"),
    ]),

    html.Div(id="tab-content", style={'padding': '20px'})
], style={'backgroundColor': '#111', 'padding': '30px'})

# 🆕 Callback para definir a aba inicial com base no armazenamento local
@app.callback(
    Output("tabs", "value"),
    Input("aba-salva", "data")
)
def definir_aba_inicial(aba_salva):
    return aba_salva if aba_salva else "geral"

# 🆕 Callback para salvar a aba preferida quando ela for trocada
@app.callback(
    Output("aba-salva", "data"),
    Input("tabs", "value"),
    prevent_initial_call=True
)
def salvar_aba_preferida(aba_atual):
    return aba_atual

# Callback principal
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def atualizar_pagina(aba):
    if aba == 'geral':
        df_agrupado = df_manutencao.groupby('ANO_MES', as_index=False).sum(numeric_only=True)
        return html.Div([
            dcc.Graph(figure=px.pie(df_manutencao, names='TIPO', values='VALOR PAGO', title="Gastos por Tipo")),
            dcc.Graph(figure=px.bar(df_agrupado, x='ANO_MES', y='VALOR PAGO', title="Evolução Mensal"))
        ])

    elif aba in ['leve', 'pesada']:
        df_filtro = df_manutencao[df_manutencao['CATEGORIA'] == ('LEVE' if aba == 'leve' else 'PESADA')]
        tipos_disponiveis = df_filtro['TIPO'].dropna().unique()

        return html.Div([
            html.Div([
                html.Div([
                    html.H3("Indicadores", style={"color": "white"}),
                    html.Div(id=f"indicadores-{aba}", style={'color': 'white'})
                ], style={'marginBottom': '30px'})
            ]),

            html.Div([
                dcc.DatePickerRange(
                    id=f"data-range-{aba}",
                    start_date=df_filtro['DATA'].min(),
                    end_date=df_filtro['DATA'].max(),
                    display_format='DD/MM/YYYY',
                    style={'marginRight': '20px'}
                ),

                dcc.Dropdown(
                    id=f"tipo-dropdown-{aba}",
                    options=[{'label': tipo, 'value': tipo} for tipo in tipos_disponiveis],
                    multi=True,
                    placeholder="Filtrar por tipo de manutenção",
                    style={'width': '300px'}
                )
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            dcc.Graph(id=f"grafico-{aba}")
        ])

# Callback com gráfico e indicadores juntos para frota leve
@app.callback(
    [
        Output("grafico-leve", "figure"),
        Output("indicadores-leve", "children")
    ],
    [
        Input("data-range-leve", "start_date"),
        Input("data-range-leve", "end_date"),
        Input("tipo-dropdown-leve", "value")
    ]
)
def atualizar_leve(start_date, end_date, tipos):
    return gerar_grafico_e_indicadores('LEVE', start_date, end_date, tipos)

# Callback com gráfico e indicadores juntos para frota pesada
@app.callback(
    [
        Output("grafico-pesada", "figure"),
        Output("indicadores-pesada", "children")
    ],
    [
        Input("data-range-pesada", "start_date"),
        Input("data-range-pesada", "end_date"),
        Input("tipo-dropdown-pesada", "value")
    ]
)
def atualizar_pesada(start_date, end_date, tipos):
    return gerar_grafico_e_indicadores('PESADA', start_date, end_date, tipos)

# Função de geração de gráfico + indicadores
def gerar_grafico_e_indicadores(categoria, start_date, end_date, tipos):
    df = df_manutencao[df_manutencao['CATEGORIA'] == categoria]
    if start_date and end_date:
        df = df[(df['DATA'] >= start_date) & (df['DATA'] <= end_date)]
    if tipos:
        df = df[df['TIPO'].isin(tipos)]

    df_agrupado = df.groupby('MODELO/PLACA', as_index=False)['VALOR PAGO'].sum()
    fig = px.bar(df_agrupado, x='MODELO/PLACA', y='VALOR PAGO', text='VALOR PAGO',
                 title=f"Frota {categoria.title()} - Gastos por Veículo", template="plotly_dark")
    fig.update_traces(textposition='outside')
    fig.update_layout(title_x=0.5, xaxis_tickangle=-45 if categoria == 'PESADA' else 0, margin=dict(b=150))

    valor_pago = df['VALOR PAGO'].sum()
    valor_eco = df['VALOR ECONOMIZADO'].sum()
    qtd = df.shape[0]

    indicadores = [
        html.P(f"Valor Pago: R$ {valor_pago:,.2f}"),
        html.P(f"Valor Economizado: R$ {valor_eco:,.2f}"),
        html.P(f"Qtd. Manutenções: {qtd}")
    ]

    return fig, indicadores

# Run
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
