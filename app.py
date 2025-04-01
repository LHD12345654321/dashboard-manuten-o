import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# Caminho para o arquivo Excel
darq = 'GESTÃO MANUTENÇÃO.xlsx'

# Carregar o DataFrame corretamente
df_manutencao = pd.read_excel(darq, sheet_name="MANUTENÇÃO POR VEÍCULO", engine="openpyxl", skiprows=2)
df_manutencao = df_manutencao.dropna(how="all")
df_manutencao.columns = df_manutencao.iloc[0].astype(str).str.strip().str.upper()
df_manutencao = df_manutencao[1:].reset_index(drop=True)

# Convertendo colunas numéricas
for col in ['VALOR PAGO', 'VALOR ECONOMIZADO']:
    df_manutencao[col] = pd.to_numeric(df_manutencao[col], errors='coerce').fillna(0)

# Adicionando coluna de data corretamente
df_manutencao['DATA'] = pd.to_datetime(df_manutencao['DATA'], errors='coerce')

# Separação das frotas
df_frota_leve = df_manutencao[df_manutencao['CATEGORIA'] == 'LEVE']
df_frota_pesada = df_manutencao[df_manutencao['CATEGORIA'] == 'PESADA']

# Inicializar aplicativo Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Dashboard - Montenegro Business"

# Layout do Dashboard
app.layout = html.Div([
    html.H1("Montenegro Business e Participações", style={'textAlign': 'center', 'color': '#FFD700', 'fontSize': '36px'}),
    dcc.Tabs(id="tabs", value='geral', children=[
        dcc.Tab(label='Frota Geral', value='geral', style={'backgroundColor': '#1E1E1E', 'color': '#FFD700'}),
        dcc.Tab(label='Frota Leve', value='leve', style={'backgroundColor': '#1E1E1E', 'color': '#FFD700'}),
        dcc.Tab(label='Frota Pesada', value='pesada', style={'backgroundColor': '#1E1E1E', 'color': '#FFD700'})
    ], colors={"border": "#FFD700", "primary": "#FFD700", "background": "#121212"}),
    html.Div(id='tabs-content')
], style={'backgroundColor': '#121212', 'padding': '20px'})

# Callback para atualizar abas
def render_tab(tab):
    if tab == 'geral':
        return html.Div([
            dcc.DatePickerRange(
                id='date-picker',
                start_date=df_manutencao['DATA'].min(),
                end_date=df_manutencao['DATA'].max(),
                display_format='DD/MM/YYYY'
            ),
            dcc.Graph(id='graph-geral')
        ])
    elif tab == 'leve':
        return html.Div([
            dcc.Graph(id='graph-leve', figure=px.bar(df_frota_leve, x='VEÍCULOS', y='VALOR PAGO', title='Gastos Frota Leve', color='VEÍCULOS'))
        ])
    elif tab == 'pesada':
        return html.Div([
            dcc.Graph(id='graph-pesada', figure=px.bar(df_frota_pesada, x='VEÍCULOS', y='VALOR PAGO', title='Gastos Frota Pesada', color='VEÍCULOS'))
        ])

@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def update_tab(tab):
    return render_tab(tab)

# Rodar o servidor Dash
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
