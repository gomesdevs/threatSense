# dashboard_integrated.py
from dash import Dash, html, dcc
import dash
import plotly.express as px
import json
import os
import threading
import time
import random
from datetime import datetime
from collections import Counter
from dash.dependencies import Input, Output, State

# Classes e funções importadas do detect.py
class ThreatDetector:
    def __init__(self, packet_threshold=1000, attempt_threshold=10, ip_repeat_threshold=5):
        self.packet_threshold = packet_threshold
        self.attempt_threshold = attempt_threshold
        self.ip_repeat_threshold = ip_repeat_threshold
        self.logs = []
        self.ip_counts = Counter()
        self.running = True
        
        # Inicializa o arquivo se não existir
        if not os.path.exists("logs.json"):
            with open("logs.json", "w") as f:
                json.dump([], f)
        else:
            # Carrega logs existentes
            try:
                with open("logs.json", "r") as f:
                    self.logs = json.load(f)
                # Atualiza contador IP
                for log in self.logs:
                    self.ip_counts[log["ip_source"]] += 1
            except (json.JSONDecodeError, FileNotFoundError):
                self.logs = []

    def simulate_log(self):
        """Simula um log de tráfego de rede."""
        possible_ips = ["192.168.1.10", "192.168.1.20", "192.168.1.30", "192.168.1.40"]
        ip_source = random.choice(possible_ips)
        log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_source": ip_source,
            "ip_dest": f"192.168.1.{random.randint(1, 255)}",
            "packets": random.randint(50, 2000),
            "attempts": random.randint(0, 15),
            "latency": random.randint(10, 100)
        }
        self.logs.append(log)
        self.ip_counts[ip_source] += 1
        return log

    def detect_threat(self, log):
        """Detecta ameaças com base no log."""
        threat_detected = False
        threat_type = None

        if log["packets"] > self.packet_threshold:
            threat_detected = True
            threat_type = "Flood Detectado"
        elif log["attempts"] > self.attempt_threshold:
            threat_detected = True
            threat_type = "Tentativa de Intrusão"
        elif self.ip_counts[log["ip_source"]] > self.ip_repeat_threshold:
            threat_detected = True
            threat_type = "Ataque Direcionado (IP Repetido)"

        return {
            "threat_detected": threat_detected,
            "threat_type": threat_type,
            "log": log
        }

    def save_logs(self, filename="logs.json"):
        """Salva os logs num arquivo JSON."""
        # Preserva apenas os últimos 100 logs para evitar que o arquivo fique muito grande
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
        
        with open(filename, "w") as f:
            json.dump(self.logs, f, indent=4)

    def run(self):
        """Executa em loop contínuo até que self.running seja False."""
        print("Detector iniciado - gerando logs...")
        while self.running:
            log = self.simulate_log()
            result = self.detect_threat(log)
            if result["threat_detected"]:
                print(f"🚨 {result['threat_type']} - {log['timestamp']}")
            self.save_logs()
            time.sleep(1)  # Gera um log por segundo
        print("Detector parado.")

    def stop(self):
        """Para o detector."""
        self.running = False

# Função para carregar logs
def load_logs(filename="logs.json"):
    try:
        if not os.path.exists(filename):
            return {"Tempo": [], "Pacotes": [], "Tentativas": [], "Latência": []}
        
        with open(filename, "r") as f:
            logs = json.load(f)
        
        # Extrai os últimos 10 logs
        recent_logs = logs[-10:] if len(logs) >= 10 else logs
        return {
            "Tempo": list(range(1, len(recent_logs) + 1)),
            "Pacotes": [log["packets"] for log in recent_logs],
            "Tentativas": [log["attempts"] for log in recent_logs],
            "Latência": [log["latency"] for log in recent_logs]
        }
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Erro ao carregar logs: {str(e)}")
        return {"Tempo": [], "Pacotes": [], "Tentativas": [], "Latência": []}

# Função para calcular proporção de tráfego
def calculate_traffic_proportion(logs):
    if not logs["Pacotes"]:
        return {"Normal": 0, "Suspeito": 0}
    
    threshold = 1000
    normal = sum(1 for p in logs["Pacotes"] if p <= threshold)
    suspeito = sum(1 for p in logs["Pacotes"] if p > threshold)
    total = normal + suspeito
    return {
        "Normal": normal / total * 100 if total > 0 else 0,
        "Suspeito": suspeito / total * 100 if total > 0 else 0
    }

# Inicia o detector em uma thread separada
detector = ThreatDetector()
detector_thread = threading.Thread(target=detector.run)
detector_thread.daemon = True  # Thread vai parar quando o programa principal parar
detector_thread.start()

# Inicializa o aplicativo Dash
app = Dash(__name__)

# Carrega dados iniciais
data = load_logs()
traffic_proportion = calculate_traffic_proportion(data)

# Gráficos
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

# Gráfico de pizza
fig_pie = px.pie(
    names=["Normal", "Suspeito"],
    values=[traffic_proportion["Normal"], traffic_proportion["Suspeito"]],
    title="Proporção de Tráfego",
    color_discrete_sequence=["#32CD32", "#FF0000"]
)
fig_pie.update_layout(
    plot_bgcolor="#000", paper_bgcolor="#000", title_x=0.5,
    title_font=dict(color="#fff"), font=dict(color="#fff")
)

# Estilos para o dropdown
dropdown_styles = {
    "options": [
        {"label": "5 segundos", "value": 5},
        {"label": "10 segundos", "value": 10},
        {"label": "30 segundos", "value": 30}
    ],
    "style": {
        "width": "150px", 
        "backgroundColor": "#444",
        "border": "1px solid #FF4500", 
        "borderRadius": "5px",
        "color": "#fff"
    }
}

# Layout
app.layout = html.Div(
    style={
        'backgroundColor': '#1A1A1A', 'padding': '20px', 'fontFamily': 'Helvetica', 
        'minHeight': '100vh', 'color': '#fff', 'margin': '0', 'boxSizing': 'border-box'
    },
    children=[
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
                    },
                    children="🟢 Tráfego Normal"  # Default text
                ),
                html.Div(
                    style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'},
                    children=[
                        html.Button(
                            id="pause-button", 
                            n_clicks=0, 
                            children="Pausar Atualização",
                            style={
                                'padding': '10px 20px', 'backgroundColor': '#FF4500', 'color': '#fff',
                                'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '16px'
                            }
                        ),
                        dcc.Dropdown(
                            id='interval-dropdown',
                            options=dropdown_styles["options"],
                            value=5,
                            style=dropdown_styles["style"],
                            optionHeight=35,
                            className='dropdown-custom',
                            clearable=False
                        )
                    ]
                )
            ]
        ),
        html.Div(
            id="summary",
            style={
                'backgroundColor': '#2A2A2A', 'padding': '15px', 'borderRadius': '10px', 
                'marginBottom': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.5)'
            },
            children=[
                html.P(f"Pico de Pacotes: 0 pacotes/s", style={'margin': '5px'}),
                html.P(f"Latência Média: 0.0 ms", style={'margin': '5px'}),
                html.P(f"Total de Tentativas: 0", style={'margin': '5px'})
            ]
        ),
        html.Div(
            style={
                'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(350px, 1fr))', 
                'gap': '20px'
            },
            children=[
                dcc.Graph(id="traffic-graph", figure=fig_traffic, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                }),
                dcc.Graph(id="attempts-graph", figure=fig_attempts, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                }),
                dcc.Graph(id="latency-graph", figure=fig_latency, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                }),
                dcc.Graph(id="pie-chart", figure=fig_pie, style={
                    'backgroundColor': '#000', 'borderRadius': '8px', 
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.3)'
                })
            ]
        ),
        html.Footer(
            "ThreatSense v1.0 - Desenvolvido por [Seu Nome] - 2025",
            style={
                'textAlign': 'center', 'marginTop': '30px', 'fontSize': '14px', 
                'color': '#B0B0B0', 'padding': '10px', 'borderTop': '1px solid #444'
            }
        ),
        dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0, disabled=False),
        # Store component to maintain state between callbacks
        dcc.Store(id="pause-state", data=False)
    ]
)

# Definindo estilos CSS corretamente
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>ThreatSense</title>
        {%metas%}
        {%favicon%}
        {%css%}
        <style>
            .dropdown-custom .Select-control {
                background-color: #444 !important;
                color: #fff !important;
                border: 1px solid #FF4500 !important;
            }
            .dropdown-custom .Select-value {
                color: #fff !important;
            }
            .dropdown-custom .Select-menu-outer {
                background-color: #444 !important;
                border: 1px solid #FF4500 !important;
            }
            .dropdown-custom .Select-option {
                background-color: #444 !important;
                color: #fff !important;
            }
            .dropdown-custom .Select-option.is-focused {
                background-color: #FF4500 !important;
                color: #fff !important;
            }
            .dropdown-custom .Select-arrow {
                border-color: #FF4500 transparent transparent !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callback para pausar/resumir
@app.callback(
    Output('pause-state', 'data'),
    Output('pause-button', 'children'),
    Output('interval-component', 'disabled'),
    Input('pause-button', 'n_clicks'),
    State('pause-state', 'data')
)
def toggle_pause(n_clicks, is_paused):
    if n_clicks == 0:
        return False, "Pausar Atualização", False
    
    is_paused = not is_paused
    button_text = "Retomar Atualização" if is_paused else "Pausar Atualização"
    return is_paused, button_text, is_paused

# Callback para atualizar o intervalo
@app.callback(
    Output('interval-component', 'interval'),
    Input('interval-dropdown', 'value')
)
def update_interval(value):
    return value * 1000

# Callback para atualizar dashboard
@app.callback(
    Output('status', 'children'),
    Output('status', 'style'),
    Output('summary', 'children'),
    Output('traffic-graph', 'figure'),
    Output('attempts-graph', 'figure'),
    Output('latency-graph', 'figure'),
    Output('pie-chart', 'figure'),
    Input('interval-component', 'n_intervals'),
    Input('pause-state', 'data')
)
def update_dashboard(n, is_paused):
    # Não atualiza se estiver pausado
    if is_paused:
        # Recupera os dados atuais para não perder informações
        traffic_fig = dash.no_update
        attempts_fig = dash.no_update
        latency_fig = dash.no_update
        pie_fig = dash.no_update
        status_text = dash.no_update
        status_style = dash.no_update
        summary_text = dash.no_update
        return status_text, status_style, summary_text, traffic_fig, attempts_fig, latency_fig, pie_fig

    # Carrega os logs
    data = load_logs()
    max_packets = max(data["Pacotes"]) if data["Pacotes"] else 0
    avg_latency = sum(data["Latência"]) / len(data["Latência"]) if data["Latência"] else 0
    total_attempts = sum(data["Tentativas"]) if data["Tentativas"] else 0

    # Atualiza status
    status_text = "🔴 Ameaça Detectada!" if max_packets > 1000 else "🟢 Tráfego Normal"
    status_style = {
        'textAlign': 'center', 'fontSize': '30px', 'padding': '20px', 
        'backgroundColor': '#2A2A2A', 'borderRadius': '10px', 
        'boxShadow': '0 4px 8px rgba(0,0,0,0.5)', 'border': '2px solid #FF4500',
        'color': '#FF0000' if max_packets > 1000 else '#32CD32', 'fontWeight': 'bold',
        'flex': '1', 'marginRight': '20px'  # Mantém o flex layout
    }
    summary_text = [
        html.P(f"Pico de Pacotes: {max_packets} pacotes/s", style={'margin': '5px'}),
        html.P(f"Latência Média: {avg_latency:.1f} ms", style={'margin': '5px'}),
        html.P(f"Total de Tentativas: {total_attempts}", style={'margin': '5px'})
    ]

    # Atualiza gráficos
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

    traffic_proportion = calculate_traffic_proportion(data)
    fig_pie = px.pie(
        names=["Normal", "Suspeito"],
        values=[traffic_proportion["Normal"], traffic_proportion["Suspeito"]],
        title="Proporção de Tráfego",
        color_discrete_sequence=["#32CD32", "#FF0000"]
    )
    fig_pie.update_layout(
        plot_bgcolor="#000", paper_bgcolor="#000", title_x=0.5,
        title_font=dict(color="#fff"), font=dict(color="#fff")
    )

    return status_text, status_style, summary_text, fig_traffic, fig_attempts, fig_latency, fig_pie

# Função limpa ao encerrar
def cleanup():
    print("Encerrando detector...")
    detector.stop()
    detector_thread.join(timeout=1)
    print("ThreatSense encerrado.")

# Registra função de limpeza para ser chamada ao encerrar
import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    print("Iniciando ThreatSense...")
    app.run(debug=False)  # Importante: debug=False para evitar que o detector seja iniciado duas vezes
