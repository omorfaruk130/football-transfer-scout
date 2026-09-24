"""
Core scouting pipeline: takes a natural-language brief and returns
a ranked shortlist of players with fit verdicts.
"""

from src.llm.groq_client import call_llm
from src.llm.prompts import (
    BRIEF_PARSER_SYSTEM_PROMPT,
    FIT_REASONING_SYSTEM_PROMPT,
    build_brief_parser_prompt,
    build_fit_reasoning_prompt,
)
from src.utils.output_parser import parse_llm_json
from src.data.player_store import load_players, filter_players

MAX_CANDIDATES_FOR_REASONING = 8  # cap LLM calls for cost/speed


def parse_brief(brief_text: str) -> dict:
    """Step 1: turn natural-language brief into structured filters."""
    raw = call_llm(BRIEF_PARSER_SYSTEM_PROMPT, build_brief_parser_prompt(brief_text))
    return parse_llm_json(raw)


def get_candidates(filters: dict):
    """Step 2: hard-filter the player dataset using structured filters."""
    df = load_players()
    filtered = filter_players(
        df,
        position=filters.get("position"),
        age_max=filters.get("age_max"),
        age_min=filters.get("age_min"),
        foot=filters.get("foot"),
        value_max_eur=filters.get("value_max_eur"),
    )
    return filtered.head(MAX_CANDIDATES_FOR_REASONING)


def generate_fit_verdict(brief_text: str, filters: dict, player_row) -> dict:
    """Step 3: LLM generates a Strong/Partial/Weak fit verdict for one player."""
    player_data = {
        "name": player_row["short_name"],
        "age": int(player_row["age"]),
        "club": player_row["club_name"],
        "position": player_row["primary_position"],
        "preferred_foot": player_row["preferred_foot"],
        "value_eur": int(player_row["value_eur"]),
        "overall": int(player_row["overall"]),
        "pace": float(player_row["pace"]),
        "passing": float(player_row["passing"]),
        "dribbling": float(player_row["dribbling"]),
        "defending": float(player_row["defending"]),
        "physic": float(player_row["physic"]),
    }

    raw = call_llm(
        FIT_REASONING_SYSTEM_PROMPT,
        build_fit_reasoning_prompt(brief_text, filters, player_data),
    )
    return parse_llm_json(raw)


def run_scout_search(brief_text: str) -> dict:
    """
    Full pipeline: brief -> filters -> candidates -> fit verdicts.
    Returns {"filters": {...}, "shortlist": [verdict, ...]}
    """
    filters = parse_brief(brief_text)
    candidates = get_candidates(filters)

    if candidates.empty:
        return {"filters": filters, "shortlist": []}

    shortlist = []
    for _, player_row in candidates.iterrows():
        verdict = generate_fit_verdict(brief_text, filters, player_row)
        # attach raw stats so the UI can build a radar chart later without re-querying
        verdict["raw_stats"] = {
            "pace": float(player_row["pace"]),
            "shooting": float(player_row["shooting"]),
            "passing": float(player_row["passing"]),
            "dribbling": float(player_row["dribbling"]),
            "defending": float(player_row["defending"]),
            "physic": float(player_row["physic"]),
        }
        verdict["club"] = player_row["club_name"]
        verdict["age"] = int(player_row["age"])
        verdict["value_eur"] = int(player_row["value_eur"])
        shortlist.append(verdict)

    # Strong fit first, then Partial, then Weak
    fit_order = {"Strong fit": 0, "Partial fit": 1, "Weak fit": 2}
    shortlist.sort(key=lambda v: fit_order.get(v.get("fit_level"), 3))

    return {"filters": filters, "shortlist": shortlist}