"""
Looks up players by name and prepares data for radar chart comparison.
"""

from src.data.player_store import load_players, get_player_by_name
from src.visualization.radar_chart import build_radar_chart, RADAR_KEYS


def compare_players(names: list[str]):
    if not (2 <= len(names) <= 3):
        raise ValueError("Provide 2-3 player names to compare.")

    df = load_players()
    found_players = []
    not_found = []
    player_info = []

    for name in names:
        player_row = get_player_by_name(df, name)
        if player_row is None:
            not_found.append(name)
            continue

        stats = {key: float(player_row[key]) for key in RADAR_KEYS}
        found_players.append({"name": player_row["short_name"], "stats": stats})
        player_info.append({
            "name": player_row["short_name"],
            "club": player_row["club_name"],
            "age": int(player_row["age"]),
            "position": player_row["primary_position"],
            "value_eur": int(player_row["value_eur"]),
        })

    if len(found_players) < 2:
        return None, None, not_found, []

    fig = build_radar_chart(found_players)
    table = get_comparison_table(found_players)
    return fig, table, not_found, player_info

STAT_DESCRIPTIONS = {
    "pace": "How fast the player is",
    "shooting": "Ability to score goals",
    "passing": "Accuracy and range of passing",
    "dribbling": "Ball control and beating defenders",
    "defending": "Tackling and defensive positioning",
    "physic": "Strength and physical presence",
}

def get_comparison_table(players: list[dict]) -> list[dict]:
    """
    players: same shape as used for the radar chart.
    Returns a list of rows for a plain-language stat-by-stat comparison:
    [{"attribute": "Pace", "description": ..., "values": {"Mbappé": 97, "Haaland": 89}, "leader": "Mbappé"}, ...]
    """
    from src.visualization.radar_chart import RADAR_KEYS, RADAR_LABELS

    rows = []
    for key, label in zip(RADAR_KEYS, RADAR_LABELS):
        values = {p["name"]: p["stats"].get(key, 0) for p in players}
        leader = max(values, key=values.get)
        rows.append({
            "attribute": label,
            "description": STAT_DESCRIPTIONS[key],
            "values": values,
            "leader": leader,
        })
    return rows