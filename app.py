# app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import os
from datetime import date

# Caminho para a planilha
darq = 'GESTÃO MANUTENÇÃO.xlsx'

# Carregar dados
try:
    df_manutencao = pd.read_excel(darq, sheet_name="MANUTENÇÃO POR VEÍCULO", engine="openpyxl", skiprows=2)
    df_manutencao = df_manutencao.dropna(how="all")
    df_manutencao.columns = df_manutencao.iloc[0].astype(str).str.strip().str.upper()
    df_manutencao = df_manutencao[1:].reset_index(drop=True)
except Exception as e:
    print(f"Erro ao carregar a planilha: {e}")
    exit()

# Padronização
colunas_esperadas = ['VEÍCULOS', 'VALOR PAGO', 'VALOR ECONOMIZADO', 'TIPO', 'CATEGORIA', 'DATA', 'PLACA']
for coluna in colunas_esperadas:
    if coluna not in df_manutencao.columns:
        print(f"ERRO: A coluna '{coluna}' não foi encontrada na planilha!")
        exit()

# Conversões e criação de colunas auxiliares
df_manutencao['VALOR PAGO'] = pd.to_numeric(df_manutencao['VALOR PAGO'], errors='coerce').fillna(0)
df_manutencao['VALOR ECONOMIZADO'] = pd.to_numeric(df_manutencao['VALOR ECONOMIZADO'], errors='coerce').fillna(0)
df_manutencao['DATA'] = pd.to_datetime(df_manutencao['DATA'], errors='coerce')
df_manutencao['ANO_MES'] = df_manutencao['DATA'].dt.strftime('%b/%y').str.upper()
df_manutencao['MODELO/PLACA'] = df_manutencao['VEÍCULOS'] + ' / ' + df_manutencao['PLACA'].astype(str)

# Iniciar app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Dashboard - Montenegro Business e Participações"

# Estilo premium global
app.layout = html.Div([
    dcc.Store(id="aba-salva", storage_type="local"),

    html.Div([
        html.Img(
            src="/assets/logo_montenegro.png",
            style={"height": "80px", "margin": "0 auto", "display": "block", "marginBottom": "20px"}
        ),
        html.H1("Montenegro Business e Participações", style={'textAlign': 'center', 'color': '#FFD700'}),
        html.H2("Dashboard de Gestão de Manutenção", style={'textAlign': 'center', 'color': '#AAA'})
    ], style={'marginBottom': '40px'}),

    dcc.Tabs(
        id="tabs", value=None, 
        children=[
            dcc.Tab(label="Visão Geral", value="geral", className="custom-tab", selected_className="custom-tab--selected"),
            dcc.Tab(label="Frota Leve", value="leve", className="custom-tab", selected_className="custom-tab--selected"),
            dcc.Tab(label="Frota Pesada", value="pesada", className="custom-tab", selected_className="custom-tab--selected"),
        ],
        className="custom-tabs"
    ),

    html.Div(id="tab-content", style={'padding': '20px'})
], style={
    'background': 'linear-gradient(145deg, #0a0a0a, #1a1a1a)',
    'minHeight': '100vh',
    'padding': '30px',
    'fontFamily': 'Arial, sans-serif'
})

# Callbacks de aba
@app.callback(Output("tabs", "value"), Input("aba-salva", "data"))
def definir_aba_inicial(aba_salva):
    return aba_salva if aba_salva else "geral"

@app.callback(Output("aba-salva", "data"), Input("tabs", "value"), prevent_initial_call=True)
def salvar_aba_preferida(aba_atual):
    return aba_atual

# Conteúdo das abas
@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def atualizar_pagina(aba):
    if aba == 'geral':
        df_agrupado = df_manutencao.groupby('ANO_MES', as_index=False).sum(numeric_only=True)
        df_agrupado['VALOR PAGO TEXTO'] = df_agrupado['VALOR PAGO'].apply(lambda x: f"R$ {x:,.2f}")
        fig_barras = px.bar(df_agrupado, x='ANO_MES', y='VALOR PAGO', text='VALOR PAGO TEXTO',
                            title="Evolução Mensal", template='plotly_dark')
        fig_barras.update_traces(textposition='outside')
        fig_barras.update_layout(title_x=0.5)

        df_tipo = df_manutencao.groupby('TIPO', as_index=False)['VALOR PAGO'].sum()
        df_tipo['VALOR PAGO TEXTO'] = df_tipo['VALOR PAGO'].apply(lambda x: f"R$ {x:,.2f}")
        fig_pizza = px.pie(df_tipo, names='TIPO', values='VALOR PAGO', title="Distribuição por Tipo",
                           template='plotly_dark', hole=0.3)
        fig_pizza.update_layout(title_x=0.5)

        return html.Div([
            dcc.Graph(figure=fig_pizza),
            dcc.Graph(figure=fig_barras)
        ])

    elif aba in ['leve', 'pesada']:
        df_filtro = df_manutencao[df_manutencao['CATEGORIA'] == ('LEVE' if aba == 'leve' else 'PESADA')]
        tipos_disponiveis = df_filtro['TIPO'].dropna().unique()

        return html.Div([
            html.Div([
                html.Div([
                    html.H3("Indicadores", style={"color": "#FFD700", "marginBottom": "10px"}),
                    html.Div(id=f"indicadores-{aba}", style={'color': 'white', 'fontSize': '18px'})
                ])
            ], style={'marginBottom': '30px'}),

            html.Div([
                dcc.DatePickerRange(
                    id=f"data-range-{aba}",
                    start_date=df_filtro['DATA'].min().date(),
                    end_date=df_filtro['DATA'].max().date(),
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
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px', 'flexWrap': 'wrap'}),

            dcc.Graph(id=f"grafico-{aba}")
        ])

# Callbacks para leve/pesada
@app.callback([
    Output("grafico-leve", "figure"), Output("indicadores-leve", "children")
], [
    Input("data-range-leve", "start_date"), Input("data-range-leve", "end_date"),
    Input("tipo-dropdown-leve", "value")
])
def atualizar_leve(start_date, end_date, tipos):
    return gerar_grafico_e_indicadores('LEVE', start_date, end_date, tipos)

@app.callback([
    Output("grafico-pesada", "figure"), Output("indicadores-pesada", "children")
], [
    Input("data-range-pesada", "start_date"), Input("data-range-pesada", "end_date"),
    Input("tipo-dropdown-pesada", "value")
])
def atualizar_pesada(start_date, end_date, tipos):
    return gerar_grafico_e_indicadores('PESADA', start_date, end_date, tipos)

def gerar_grafico_e_indicadores(categoria, start_date, end_date, tipos):
    df = df_manutencao[df_manutencao['CATEGORIA'] == categoria]
    if start_date and end_date:
        df = df[(df['DATA'] >= pd.to_datetime(start_date)) & (df['DATA'] <= pd.to_datetime(end_date))]
    if tipos:
        df = df[df['TIPO'].isin(tipos)]

    df_agrupado = df.groupby('MODELO/PLACA', as_index=False)['VALOR PAGO'].sum()
    df_agrupado = df_agrupado.sort_values(by='VALOR PAGO', ascending=False)
    df_agrupado['VALOR PAGO TEXTO'] = df_agrupado['VALOR PAGO'].apply(lambda x: f"R$ {x:,.2f}")

    fig = px.bar(df_agrupado, x='MODELO/PLACA', y='VALOR PAGO', text='VALOR PAGO TEXTO',
                 title=f"VEÍCULOS - Gastos por Veículo ({categoria})", template="plotly_dark")
    fig.update_traces(textposition='outside')
    fig.update_layout(
        title_x=0.5,
        xaxis_tickangle=-45 if categoria == 'PESADA' else 0,
        margin=dict(b=160),
        xaxis_title="",
        yaxis_title="",
        font=dict(color='white')
    )

    valor_pago = df['VALOR PAGO'].sum()
    valor_eco = df['VALOR ECONOMIZADO'].sum()
    qtd = df.shape[0]

    indicadores = [
        html.P(f"Valor Pago: R$ {valor_pago:,.2f}"),
        html.P(f"Valor Economizado: R$ {valor_eco:,.2f}"),
        html.P(f"Qtd. Manutenções: {qtd}")
    ]

    return fig, indicadores

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
