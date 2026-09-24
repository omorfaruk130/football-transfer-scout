"""
Builds Plotly radar charts comparing 2-3 players across core attributes.
"""

import plotly.graph_objects as go

RADAR_LABELS = ["Pace", "Shooting", "Passing", "Dribbling", "Defending", "Physical"]
RADAR_KEYS = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]


def build_radar_chart(players: list[dict]) -> go.Figure:
    if not (2 <= len(players) <= 3):
        raise ValueError("Radar chart comparison supports 2-3 players only.")

    fig = go.Figure()

    for player in players:
        values = [player["stats"].get(key, 0) for key in RADAR_KEYS]
        values.append(values[0])
        labels = RADAR_LABELS + [RADAR_LABELS[0]]

        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=labels,
                fill="toself",
                name=player["name"],
                opacity=0.7,
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            domain=dict(x=[0.1, 0.9], y=[0.05, 0.95]),
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, x=0.5, xanchor="center"),
        title=None,
        margin=dict(l=40, r=40, t=40, b=40),
        height=500,
    )

    return fig