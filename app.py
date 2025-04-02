import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Carregar dados
file_path = "seu_arquivo.xlsx"  # Substitua pelo caminho real
sheet_name = "MANUTENÇÃO POR VEÍCULO"
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Inicializar o app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Layout
app.layout = dbc.Container([
    html.H1("Dashboard de Manutenção de Frota", className="text-center text-light"),
    
    dbc.Tabs([
        dbc.Tab(label="Frota Geral", tab_id="geral"),
        dbc.Tab(label="Frota Leve", tab_id="leve"),
        dbc.Tab(label="Frota Pesada", tab_id="pesada"),
    ], id="tabs", active_tab="geral"),
    
    html.Div(id="tab-content", className="p-4"),
])

# Callbacks para atualizar o conteúdo das abas
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def update_tab(active_tab):
    if active_tab == "geral":
        fig = px.bar(df, x="Veiculo", y="Custo_Manutencao", title="Custo de Manutenção por Veículo")
        return dcc.Graph(figure=fig)
    elif active_tab == "leve":
        df_leve = df[df["Tipo"] == "Leve"]
        fig = px.pie(df_leve, names="Veiculo", values="Custo_Manutencao", title="Frota Leve")
        return dcc.Graph(figure=fig)
    elif active_tab == "pesada":
        df_pesada = df[df["Tipo"] == "Pesada"]
        fig = px.line(df_pesada, x="Data", y="Custo_Manutencao", title="Frota Pesada")
        return dcc.Graph(figure=fig)
    return "Selecione uma aba"

# Executar o app
if __name__ == "__main__":
    app.run_server(debug=True)
