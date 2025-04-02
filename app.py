import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

# Carregar os dados
file_path = r"C:\\Users\\lucas\\Desktop\\Recoil\\dados_manutencao.xlsx"
df = pd.read_excel(file_path, sheet_name='MANUTENÇÃO POR VEÍCULO')

# Criar colunas derivadas para melhor análise
df['Data'] = pd.to_datetime(df['Data'])
df['Ano'] = df['Data'].dt.year
df['Mês'] = df['Data'].dt.month_name()

# Inicializar o app Dash
app = dash.Dash(__name__)
server = app.server

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Manutenção de Frota", style={'textAlign': 'center', 'color': 'white'}),
    html.Div([
        dcc.Dropdown(
            id='filtro_ano',
            options=[{'label': str(ano), 'value': ano} for ano in sorted(df['Ano'].unique())],
            placeholder="Selecione o Ano",
            style={'color': 'black'}
        ),
        dcc.Dropdown(
            id='filtro_mes',
            options=[{'label': mes, 'value': mes} for mes in df['Mês'].unique()],
            placeholder="Selecione o Mês",
            style={'color': 'black'}
        )
    ], style={'display': 'flex', 'gap': '10px', 'justify-content': 'center'}),
    
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
        df_filtrado = df_filtrado[df_filtrado['Ano'] == ano]
    if mes:
        df_filtrado = df_filtrado[df_filtrado['Mês'] == mes]
    
    fig = px.bar(df_filtrado, x='Veículo', y='Custo', title='Custo de Manutenção por Veículo', color='Custo')
    fig.update_layout(template='plotly_dark')
    return fig

# Rodar o app
if __name__ == '__main__':
    app.run_server(debug=True)
