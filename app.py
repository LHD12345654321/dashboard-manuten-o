import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# Caminho para o arquivo Excel
darq = 'GESTÃO MANUTENÇÃO.xlsx'

# Carregar o DataFrame corretamente
try:
    df_manutencao = pd.read_excel(darq, sheet_name="MANUTENÇÃO POR VEÍCULO", engine="openpyxl", skiprows=2)
    df_manutencao = df_manutencao.dropna(how="all")
    df_manutencao.columns = df_manutencao.iloc[0].astype(str).str.strip().str.upper()
    df_manutencao = df_manutencao[1:].reset_index(drop=True)
except Exception as e:
    print(f"Erro ao carregar a planilha: {e}")
    exit()

# Verificar e padronizar nomes de colunas
colunas_esperadas = ['VEÍCULOS', 'VALOR PAGO', 'VALOR ECONOMIZADO', 'TIPO']
for coluna in colunas_esperadas:
    if coluna not in df_manutencao.columns:
        print(f"A coluna '{coluna}' não foi encontrada na planilha. Verifique os nomes das colunas.")
        print("Colunas disponíveis:", df_manutencao.columns.tolist())
        exit()

# Convertendo colunas numéricas
for col in ['VALOR PAGO', 'VALOR ECONOMIZADO']:
    df_manutencao[col] = pd.to_numeric(df_manutencao[col], errors='coerce').fillna(0)

# Inicializar aplicativo Dash
app = dash.Dash(__name__)
server = app.server  # Necessário para o Render
app.title = "Dashboard - Montenegro Business e Participações"

# Layout do Dashboard
dropdown_veiculos = dcc.Dropdown(
    id='dropdown-veiculo',
    options=[{'label': v, 'value': v} for v in df_manutencao['VEÍCULOS'].dropna().unique()],
    value=df_manutencao['VEÍCULOS'].dropna().unique()[0],
    style={'width': '50%', 'margin-bottom': '20px', 'color': 'black'}
)

app.layout = html.Div([
    html.H1("Montenegro Business e Participações", style={'textAlign': 'center', 'color': 'black', 'fontSize': '32px', 'fontWeight': 'bold'}),
    html.H2("Dashboard de Gestão de Manutenção", style={'textAlign': 'center', 'color': 'black', 'marginBottom': '30px'}),
    
    html.Label("Selecione um veículo:", style={'color': 'black'}),
    dropdown_veiculos,
    
    dcc.Graph(id='graph-veiculo'),
    dcc.Graph(id='graph-valor'),
    dcc.Graph(id='graph-frota')
], style={'backgroundColor': 'white', 'padding': '30px'})

# Callback para atualização dos gráficos
@app.callback(
    [Output('graph-veiculo', 'figure'),
     Output('graph-valor', 'figure'),
     Output('graph-frota', 'figure')],
    [Input('dropdown-veiculo', 'value')]
)
def atualizar_graficos(veiculo_selecionado):
    df_filtrado = df_manutencao[df_manutencao['VEÍCULOS'] == veiculo_selecionado]
    
    # Gráfico de quantidade de manutenções por tipo
    tipo_counts = df_filtrado['TIPO'].value_counts()
    fig1 = px.bar(
        x=tipo_counts.index, y=tipo_counts.values,
        labels={'x': 'Tipo de Manutenção', 'y': 'Quantidade'},
        title="Quantidade de Manutenções por Tipo",
        color=tipo_counts.index,
        color_discrete_sequence=['#1F2937', '#4B5563', '#6B7280']
    )
    
    # Gráfico de valores pagos e economizados
    fig2 = px.bar(
        x=['Valor Pago', 'Valor Economizado'],
        y=[df_filtrado['VALOR PAGO'].sum(), df_filtrado['VALOR ECONOMIZADO'].sum()],
        labels={'x': 'Categoria', 'y': 'Valor (R$)'},
        title="Valores de Manutenção por Veículo",
        color=['Valor Pago', 'Valor Economizado'],
        color_discrete_sequence=['#1E40AF', '#6B7280']
    )
    
    # Gráfico geral de gastos por tipo de manutenção
    df_frota = df_manutencao.groupby('TIPO')[['VALOR PAGO']].sum().reset_index()
    fig3 = px.pie(
        df_frota, names='TIPO', values='VALOR PAGO',
        title="Gastos Totais por Tipo de Manutenção",
        color_discrete_sequence=['#1F2937', '#4B5563', '#6B7280']
    )
    
    return fig1, fig2, fig3

# Rodar o servidor Dash
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
