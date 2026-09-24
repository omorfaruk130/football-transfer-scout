"""
Loads and filters the structured player dataset (EA FC24 CSV).
Handles hard filters (age, position, foot, value) and exposes
attribute data needed for radar chart comparisons.
"""
import unicodedata
import pandas as pd
from src.config import PLAYERS_CSV_PATH

# Columns we actually need from the ~100+ column dataset.
# Adjust names here if your CSV headers differ slightly.
RELEVANT_COLUMNS = [
    "short_name",
    "long_name",
    "age",
    "club_name",
    "nationality_name",
    "player_positions",
    "club_position",
    "preferred_foot",
    "value_eur",
    "wage_eur",
    "overall",
    "potential",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physic",
]

# Attributes used specifically for the radar chart
RADAR_ATTRIBUTES = ["pace", "shooting", "passing", "dribbling", "defending", "physic"]


LATEST_VERSION = 24  # EA Sports FC 24

def load_players() -> pd.DataFrame:
    if not PLAYERS_CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {PLAYERS_CSV_PATH}. "
            f"Download it from Kaggle (see README) and place it there."
        )

    df = pd.read_csv(PLAYERS_CSV_PATH, low_memory=False)

    df = df[df["fifa_version"] == LATEST_VERSION]

    if "fifa_update" in df.columns and not df.empty:
        latest_update = df["fifa_update"].max()
        df = df[df["fifa_update"] == latest_update]

    missing = [c for c in RELEVANT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing expected columns: {missing}. "
            f"Check your downloaded file's actual header names."
        )

    df = df[RELEVANT_COLUMNS].copy()
    df = df.dropna(subset=RADAR_ATTRIBUTES)

    POSITION_MAP = {
        "LS": "ST", "RS": "ST", "LF": "CF", "RF": "CF",
        "LW": "LW", "RW": "RW",
        "LAM": "CAM", "RAM": "CAM",
        "LCM": "CM", "RCM": "CM",
        "LDM": "CDM", "RDM": "CDM",
        "LCB": "CB", "RCB": "CB",
        "LWB": "LB", "RWB": "RB",
    }
    NON_POSITIONS = {"SUB", "RES"}

    def resolve_position(row):
        club_pos = row["club_position"]
        if pd.isna(club_pos) or club_pos in NON_POSITIONS:
            fallback = str(row["player_positions"]).split(",")[0].strip()
            return POSITION_MAP.get(fallback, fallback)
        return POSITION_MAP.get(club_pos, club_pos)

    df["primary_position"] = df.apply(resolve_position, axis=1)

    return df


def filter_players(
    df: pd.DataFrame,
    position: str | None = None,
    age_max: int | None = None,
    age_min: int | None = None,
    foot: str | None = None,
    value_max_eur: float | None = None,
) -> pd.DataFrame:
    """Apply hard structured filters from a parsed scout brief."""
    result = df.copy()

    if position:
        result = result[result["primary_position"].str.upper() == position.upper()]

    if age_max is not None:
        result = result[result["age"] <= age_max]

    if age_min is not None:
        result = result[result["age"] >= age_min]

    if foot:
        result = result[result["preferred_foot"].str.upper() == foot.upper()]

    if value_max_eur is not None:
        result = result[result["value_eur"] <= value_max_eur]

    return result.sort_values("overall", ascending=False)


def _normalize(text: str) -> str:
    """Strip accents so 'Mbappe' matches 'Mbappé'."""
    if not isinstance(text, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()




def get_player_by_name(df: pd.DataFrame, name: str) -> pd.Series | None:
    """Accent-insensitive fuzzy lookup by short_name or long_name."""
    normalized_query = _normalize(name)

    short_norm = df["short_name"].apply(_normalize)
    long_norm = df["long_name"].apply(_normalize)

    match = df[
        short_norm.str.contains(normalized_query, na=False)
        | long_norm.str.contains(normalized_query, na=False)
    ]
    if match.empty:
        return None
    return match.iloc[0]