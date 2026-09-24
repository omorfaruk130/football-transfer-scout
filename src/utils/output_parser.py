"""
Cleans raw LLM output before use. Per project constraint: always
strip markdown fences/prefixes and safely parse JSON, never trust
raw model output directly.
"""

import json
import re


def clean_llm_text(raw_output: str) -> str:
    """
    Strip markdown code fences, leading/trailing whitespace, and
    common prefixes models sometimes add despite instructions.
    """
    text = raw_output.strip()

    # Remove ```json ... ``` or ``` ... ``` fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Strip common leaking prefixes like "Here is the JSON:" if the model adds them anyway
    text = re.sub(r"^(here('?s| is)( the)?( json)?[:\-]?\s*)", "", text, flags=re.IGNORECASE)

    return text.strip()


def parse_llm_json(raw_output: str) -> dict:
    """
    Clean and parse LLM output as JSON. Raises a clear error if
    parsing fails, rather than silently returning garbage.
    """
    cleaned = clean_llm_text(raw_output)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM did not return valid JSON after cleaning.\n"
            f"Cleaned text was: {cleaned!r}\n"
            f"Error: {e}"
        )


def take_first_line(raw_output: str) -> str:
    """
    For cases where you only want a single-line query/value from
    LLM output (e.g. a search query), per project constraint.
    """
    cleaned = clean_llm_text(raw_output)
    return cleaned.splitlines()[0].strip() if cleaned else ""