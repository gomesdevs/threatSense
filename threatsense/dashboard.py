# dashboard.py
from dash import Dash, html, dcc
import plotly.express as px
import random
from dash.dependencies import Input, Output, State

app = Dash(__name__)

# Dados simulados
def generate_data():
    return {
        "Tempo": list(range(1, 11)),
        "Pacotes": [random.randint(50, 2000) for _ in range(10)],
        "Tentativas": [random.randint(0, 15) for _ in range(10)],
        "Latência": [random.randint(10, 100) for _ in range(10)]
    }

data = generate_data()
threshold = 1000

# Gráficos com fundo preto e texto claro
fig_traffic = px.line(data, x="Tempo", y="Pacotes", title="Tráfego de Rede", 
                      labels={"Pacotes": "Pacotes/s"}, color_discrete_sequence=["#FF4500"])
fig_traffic.update_layout(
    plot_bgcolor="#000", paper_bgcolor="#000", title_x=0.5,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#444", zerolinecolor="#666", tickfont=dict(color="#fff"), title_font=dict(color="#fff")),
    yaxis=dict(gridcolor="#444", zerolinecolor="#666", tickfont=dict(color="#fff"), title_font=dict(color="#fff")),
    title_font=dict(color="#fff"), font=dict(color="#fff")
)

fig_attempts = px.bar(data, x="Tempo", y="Tentativas", title="Tentativas Suspeitas",
                      color_discrete_sequence=["#FF69B4"])
fig_attempts.update_layout(
    plot_bgcolor="#000", paper_bgcolor="#000", title_x=0.5,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#444", zerolinecolor="#666", tickfont=dict(color="#fff"), title_font=dict(color="#fff")),
    yaxis=dict(gridcolor="#444", zerolinecolor="#666", tickfont=dict(color="#fff"), title_font=dict(color="#fff")),
    title_font=dict(color="#fff"), font=dict(color="#fff")
)

fig_latency = px.area(data, x="Tempo", y="Latência", title="Latência da Rede",
                      labels={"Latência": "ms"}, color_discrete_sequence=["#1E90FF"])
fig_latency.update_layout(
    plot_bgcolor="#000", paper_bgcolor="#000", title_x=0.5,
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor="#444", zerolinecolor="#666", tickfont=dict(color="#fff"), title_font=dict(color="#fff")),
    yaxis=dict(gridcolor="#444", zerolinecolor="#666", tickfont=dict(color="#fff"), title_font=dict(color="#fff")),
    title_font=dict(color="#fff"), font=dict(color="#fff")
)

# Layout com mais elementos
app.layout = html.Div(
    style={
        'backgroundColor': '#1A1A1A', 'padding': '20px', 'fontFamily': 'Helvetica', 
        'minHeight': '100vh', 'color': '#fff', 'margin': '0', 'boxSizing': 'border-box'
    },
    children=[
        # Cabeçalho
        html.Div(
            style={
                'backgroundColor': '#2A2A2A', 'padding': '20px', 'borderRadius': '10px', 
                'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)'
            },
            children=[
                html.H1("ThreatSense", style={
                    'textAlign': 'center', 'color': '#FF4500', 'fontSize': '42px', 
                    'margin': '0', 'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                }),
                html.P("Monitoramento de Ameaças em Tempo Real", style={
                    'textAlign': 'center', 'fontSize': '18px', 'color': '#B0B0B0', 'margin': '5px 0'
                })
            ]
        ),
        # Status e controles
        html.Div(
            style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'},
            children=[
                html.Div(
                    id="status",
                    style={
                        'textAlign': 'center', 'fontSize': '30px', 'padding': '20px', 
                        'backgroundColor': '#2A2A2A', 'borderRadius': '10px', 
                        'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 'border': '2px solid #FF4500',
                        'flex': '1', 'marginRight': '20px'
                    }
                ),
                html.Button("Pausar Atualização", id="pause-button", n_clicks=0, style={
                    'padding': '10px 20px', 'backgroundColor': '#FF4500', 'color': '#fff',
                    'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '16px'
                })
            ]
        ),
        # Resumo numérico
        html.Div(
            id="summary",
            style={
                'backgroundColor': '#2A2A2A', 'padding': '15px', 'borderRadius': '10px', 
                'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)'
            }
        ),
        # Gráficos
        html.Div(
            style={
                'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(350px, 1fr))', 
                'gap': '20px'
            },
            children=[
                dcc.Graph(figure=fig_traffic, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                }),
                dcc.Graph(figure=fig_attempts, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                }),
                dcc.Graph(figure=fig_latency, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                })
            ]
        ),
        # Rodapé
        html.Footer(
            "ThreatSense v1.0 - Desenvolvido por [Seu Nome] - 2025",
            style={
                'textAlign': 'center', 'marginTop': '30px', 'fontSize': '14px', 
                'color': '#B0B0B0', 'padding': '10px', 'borderTop': '1px solid #444'
            }
        ),
        dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0, disabled=False)
    ]
)

# Callback pra atualizar status e resumo
@app.callback(
    Output('status', 'children'),
    Output('status', 'style'),
    Output('summary', 'children'),
    Output('interval-component', 'disabled'),
    Input('interval-component', 'n_intervals'),
    Input('pause-button', 'n_clicks'),
    State('interval-component', 'disabled')
)
def update_dashboard(n, n_clicks, is_paused):
    global data
    if n_clicks % 2 == 1:  # Pausar
        is_paused = True
    else:  # Retomar
        is_paused = False
        data = generate_data()

    max_packets = max(data["Pacotes"])
    avg_latency = sum(data["Latência"]) / len(data["Latência"])
    total_attempts = sum(data["Tentativas"])

    status_text = "🔴 Ameaça Detectada!" if max_packets > threshold else "🟢 Tráfego Normal"
    status_style = {
        'textAlign': 'center', 'fontSize': '30px', 'padding': '20px', 
        'backgroundColor': '#2A2A2A', 'borderRadius': '10px', 
        'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 'border': '2px solid #FF4500',
        'color': '#FF0000' if max_packets > threshold else '#32CD32', 'fontWeight': 'bold'
    }
    summary_text = [
        html.P(f"Pico de Pacotes: {max_packets} pacotes/s", style={'margin': '5px'}),
        html.P(f"Latência Média: {avg_latency:.1f} ms", style={'margin': '5px'}),
        html.P(f"Total de Tentativas: {total_attempts}", style={'margin': '5px'})
    ]
    return status_text, status_style, summary_text, is_paused

if __name__ == "__main__":
    app.run(debug=True)
