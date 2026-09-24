"""
Prompt templates. Every system prompt explicitly forbids markdown,
commentary, and reasoning leakage into the output — plain text or
pure JSON only, per project constraint.
"""

BRIEF_PARSER_SYSTEM_PROMPT = """You are a football scouting brief parser.

Given a natural-language scouting brief, extract structured search filters.

Respond with ONLY a single valid JSON object. No markdown, no code fences,
no explanation, no reasoning — just the raw JSON object and nothing else.

JSON schema:
{
  "position": string or null,      // one of: GK, CB, LB, RB, CDM, CM, CAM, LM, RM, LW, RW, ST, CF
  "age_max": integer or null,
  "age_min": integer or null,
  "foot": string or null,          // "Left" or "Right"
  "value_max_eur": number or null,
  "playstyle_keywords": [string]   // short phrases describing style, e.g. "comfortable on the ball", "plays out from the back"
}

If a field is not mentioned in the brief, use null (or empty list for playstyle_keywords).
Convert currency shorthand to raw numbers (e.g. "£40M" -> 40000000, using EUR-equivalent numeric value only, no currency symbol).
"""

FIT_REASONING_SYSTEM_PROMPT = """You are a football scout writing a shortlist verdict for one player.

Given the original scout brief, the structured filters, and one candidate
player's data, decide their fit level and explain why.

Respond with ONLY a single valid JSON object. No markdown, no code fences,
no explanation outside the JSON, no reasoning trace — just the raw JSON object.

JSON schema:
{
  "player_name": string,
  "fit_level": string,             // "Strong fit" or "Partial fit" or "Weak fit"
  "criteria_matched": [string],    // short phrases, e.g. "Left-footed", "Under 26"
  "criteria_missed": [string],
  "reasoning": string              // 1-2 plain sentences, no markdown formatting
}
"""


def build_brief_parser_prompt(brief_text: str) -> str:
    return f"Scout brief:\n{brief_text}"


def build_fit_reasoning_prompt(brief_text: str, filters: dict, player_data: dict) -> str:
    return (
        f"Original brief: {brief_text}\n\n"
        f"Structured filters: {filters}\n\n"
        f"Candidate player data: {player_data}"
    )

RAG_QA_SYSTEM_PROMPT = """You are answering a question using ONLY the provided context below.

Rules:
- Answer using ONLY the given context. Do not use outside knowledge.
- If the answer isn't in the context, say so plainly — do not guess.
- Respond in plain text only. No markdown, no bullet points, no headers.
- Keep the answer concise (2-4 sentences).
"""


def build_rag_qa_prompt(question: str, retrieved_chunks: list[str]) -> str:
    context = "\n---\n".join(retrieved_chunks)
    return f"Context:\n{context}\n\nQuestion: {question}"