# dashboard.py
from dash import Dash, html, dcc
import plotly.express as px

app = Dash(__name__)

data = {
    "Tempo": [1, 2, 3, 4, 5, 6],
    "Pacotes": [100, 250, 1500, 300, 1200, 400]
}
fig = px.line(
    data, 
    x="Tempo", 
    y="Pacotes", 
    title="Monitoramento de Tráfego",
    labels={"Pacotes": "Pacotes por Segundo", "Tempo": "Segundos"}
)
fig.update_layout(
    plot_bgcolor="#f0f0f0",
    paper_bgcolor="#f0f0f0",
    font=dict(size=14),
    title_x=0.5
)

app.layout = html.Div(
    style={'backgroundColor': '#f9f9f9', 'padding': '20px', 'fontFamily': 'Arial'},
    children=[
        html.H1(
            "ThreatSense",
            style={'textAlign': 'center', 'color': '#1E90FF', 'marginBottom': '20px'}
        ),
        html.Div(
            "Ameaça Detectada!" if max(data["Pacotes"]) > 1000 else "Tráfego Normal",
            style={
                'textAlign': 'center',
                'fontSize': '24px',
                'color': 'red' if max(data["Pacotes"]) > 1000 else 'green',
                'backgroundColor': '#fff',
                'padding': '10px',
                'borderRadius': '5px',
                'marginBottom': '20px'
            }
        ),
        dcc.Graph(figure=fig, style={'border': '1px solid #ddd'})
    ]
)

if __name__ == "__main__":
    app.run(debug=True)