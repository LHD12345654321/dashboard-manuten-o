import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os

# Carregar os dados da planilha Excel
file_path = "data.xlsx"  # Atualize conforme necessário
df = pd.read_excel(file_path, sheet_name='MANUTENÇÃO POR VEÍCULO')

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Necessário para implantação no Render

# Estilo atualizado para um design moderno e profissional
theme = {
    'background': '#121212',
    'text': '#E0E0E0',
    'primary': '#BB86FC',
    'secondary': '#03DAC6',
    'highlight': '#3700B3'
}

# Layout do aplicativo
app.layout = html.Div(style={'backgroundColor': theme['background'], 'color': theme['text'], 'padding': '20px'}, children=[
    html.H1("Montenegro Business e Participações", style={'textAlign': 'center', 'color': theme['primary']}),
    html.H3("Dashboard de Gestão de Manutenção", style={'textAlign': 'center', 'color': theme['secondary']}),
    
    dcc.Tabs(id='tabs', value='visao_geral', children=[
        dcc.Tab(label='Visão Geral', value='visao_geral', style={'backgroundColor': theme['highlight']}),
        dcc.Tab(label='Frota Leve', value='frota_leve', style={'backgroundColor': theme['highlight']}),
        dcc.Tab(label='Frota Pesada', value='frota_pesada', style={'backgroundColor': theme['highlight']})
    ], style={'fontSize': '18px', 'fontWeight': 'bold', 'color': theme['text']}),
    
    html.Div(id='tab-content')
])

# Callback para atualizar o conteúdo com base na aba selecionada
@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value')
)
def update_tab(tab_name):
    if tab_name == 'visao_geral':
        fig = px.bar(df, x='Veículo', y='Custo', color='Categoria', title='Custo de Manutenção por Veículo')
    elif tab_name == 'frota_leve':
        df_filtrado = df[df['Categoria'] == 'Leve']
        fig = px.pie(df_filtrado, names='Veículo', values='Custo', title='Distribuição de Custos - Frota Leve')
    else:
        df_filtrado = df[df['Categoria'] == 'Pesada']
        fig = px.line(df_filtrado, x='Data', y='Custo', color='Veículo', title='Evolução de Custos - Frota Pesada')
    
    return dcc.Graph(figure=fig)

# Rodar o servidor
if __name__ == '__main__':
    app.run_server(debug=True)
