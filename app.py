import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import os

# Carregar os dados
file_path = "dados_manutencao.xlsx"
df = pd.read_excel(file_path, sheet_name='MANUTENÇÃO POR VEÍCULO', engine='openpyxl')

# Padronizar nomes das colunas
df.columns = df.columns.str.strip().str.upper()

# Verificar se as colunas necessárias existem
colunas_esperadas = ['DATA', 'VEÍCULO', 'CUSTO']
for coluna in colunas_esperadas:
    if coluna not in df.columns:
        raise ValueError(f"A coluna esperada '{coluna}' não foi encontrada na planilha. Verifique os nomes das colunas.")

# Criar colunas derivadas para melhor análise
df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
df.dropna(subset=['DATA'], inplace=True)
df['ANO'] = df['DATA'].dt.year
df['MÊS'] = df['DATA'].dt.month_name()

# Inicializar o app Dash
app = dash.Dash(__name__)
server = app.server

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Manutenção de Frota", style={'textAlign': 'center', 'color': 'white'}),
    html.Div([
        dcc.Dropdown(
            id='filtro_ano',
            options=[{'label': str(ano), 'value': ano} for ano in sorted(df['ANO'].dropna().unique())],
            placeholder="Selecione o Ano",
            style={'color': 'black'}
        ),
        dcc.Dropdown(
            id='filtro_mes',
            options=[{'label': mes, 'value': mes} for mes in df['MÊS'].dropna().unique()],
            placeholder="Selecione o Mês",
            style={'color': 'black'}
        )
    ], style={'display': 'flex', 'gap': '10px', 'justify-content': 'center', 'padding': '10px'}),
    
    dcc.Graph(id='grafico_manutencao')
], style={'backgroundColor': '#1e1e1e', 'color': 'white', 'padding': '20px'})

# Callback para atualizar gráfico
@app.callback(
    dash.dependencies.Output('grafico_manutencao', 'figure'),
    [dash.dependencies.Input('filtro_ano', 'value'),
     dash.dependencies.Input('filtro_mes', 'value')]
)
def atualizar_grafico(ano, mes):
    df_filtrado = df.copy()
    if ano:
        df_filtrado = df_filtrado[df_filtrado['ANO'] == ano]
    if mes:
        df_filtrado = df_filtrado[df_filtrado['MÊS'] == mes]
    
    fig = px.bar(
        df_filtrado, x='VEÍCULO', y='CUSTO', title='Custo de Manutenção por Veículo', color='CUSTO',
        labels={'CUSTO': 'Valor (R$)', 'VEÍCULO': 'Nome do Veículo'}
    )
    fig.update_layout(template='plotly_dark')
    return fig

# Rodar o app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
