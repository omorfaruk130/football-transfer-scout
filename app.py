"""
Football Transfer Scout — Streamlit app.
Two main features: (1) natural-language scout brief -> shortlist,
(2) player-vs-player radar chart comparison.
"""

import streamlit as st
from src.core.scout_agent import run_scout_search
from src.core.player_compare import compare_players
from src.core.rag_qa import ingest_csv, ask_question

st.set_page_config(page_title="Football Transfer Scout", layout="wide")

st.title("⚽ Football Transfer Scout")

tab_search, tab_compare = st.tabs(["Scout Search", "Compare Players"])

# ---------------------------------------------------------------------
# TAB 1: Scout Brief -> Shortlist
# ---------------------------------------------------------------------
with tab_search:
    st.subheader("Describe who you're looking for")
    brief_text = st.text_area(
        "Scout brief",
        placeholder="e.g. We need a left-footed centre-back, under 26, "
        "comfortable with the ball, can play out from the back. Budget under £40M.",
        height=100,
    )

    if st.button("Find Players", type="primary"):
        if not brief_text.strip():
            st.warning("Enter a scout brief first.")
        else:
            with st.spinner("Parsing brief and searching..."):
                try:
                    result = run_scout_search(brief_text)
                except Exception as e:
                    st.error(f"Search failed: {e}")
                    result = None

            if result:
                st.session_state["last_search_result"] = result

    if "last_search_result" in st.session_state:
        result = st.session_state["last_search_result"]
        filters = result["filters"]
        shortlist = result["shortlist"]

        with st.expander("Parsed filters", expanded=False):
            st.json(filters)

        if not shortlist:
            st.info("No players matched these filters. Try loosening the brief.")
        else:
            fit_colors = {
                "Strong fit": "🟢",
                "Partial fit": "🟡",
                "Weak fit": "🔴",
            }

            for player in shortlist:
                icon = fit_colors.get(player.get("fit_level"), "⚪")
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(
                            f"### {icon} {player['player_name']} — {player['club']}"
                        )
                        st.caption(
                            f"Age {player['age']} · €{player['value_eur']:,}"
                        )
                        st.write(player["reasoning"])

                        if player["criteria_matched"]:
                            st.markdown(
                                "**Matched:** " + ", ".join(player["criteria_matched"])
                            )
                        if player["criteria_missed"]:
                            st.markdown(
                                "**Missed:** " + ", ".join(player["criteria_missed"])
                            )

                    with col2:
                        stats = player["raw_stats"]
                        st.metric("Pace", int(stats["pace"]))
                        st.metric("Passing", int(stats["passing"]))
                        st.metric("Defending", int(stats["defending"]))

# ---------------------------------------------------------------------
# TAB 2: Player Comparison (Radar Chart)
# ---------------------------------------------------------------------
with tab_compare:
    st.subheader("Compare 2-3 players")

    col1, col2, col3 = st.columns(3)
    with col1:
        player1 = st.text_input("Player 1", placeholder="e.g. Mbappe")
    with col2:
        player2 = st.text_input("Player 2", placeholder="e.g. Haaland")
    with col3:
        player3 = st.text_input("Player 3 (optional)", placeholder="e.g. Messi")

    if st.button("Compare", type="primary"):
        names = [n for n in [player1, player2, player3] if n.strip()]

        if len(names) < 2:
            st.warning("Enter at least 2 player names.")
        else:
            try:
                fig, table, not_found, player_info = compare_players(names)
            except Exception as e:
                st.error(f"Comparison failed: {e}")
                fig, table, not_found, player_info = None, None, [], []

            if not_found:
                st.warning(f"Could not find: {', '.join(not_found)}")

            if fig:
                # Player info cards
                info_cols = st.columns(len(player_info))
                for col, info in zip(info_cols, player_info):
                    with col:
                        st.markdown(f"**{info['name']}**")
                        st.caption(
                            f"{info['position']} · {info['club']} · Age {info['age']} · "
                            f"€{info['value_eur']:,}"
                        )

                st.plotly_chart(fig, use_container_width=True)

                # Plain-language stat-by-stat breakdown
                st.markdown("#### Attribute breakdown")
                names_ordered = list(table[0]["values"].keys())

                for row in table:
                    st.markdown(f"**{row['attribute']}** — {row['description']}")
                    bar_cols = st.columns(len(names_ordered))
                    for col, name in zip(bar_cols, names_ordered):
                        val = row["values"][name]
                        is_leader = name == row["leader"] and len(names_ordered) > 1
                        with col:
                            label = f"⭐ {name}" if is_leader else name
                            st.progress(val / 100, text=f"{label}: {int(val)}")
                            



# third tab:
tab_search, tab_compare, tab_upload = st.tabs(
    ["Scout Search", "Compare Players", "Ask Your Own Data"]
)

with tab_upload:
    st.subheader("Upload a CSV and ask questions about it")
    st.caption("Your uploaded data is kept in memory for this session only — never saved to disk.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file and st.button("Build knowledge base"):
        with st.spinner("Reading and embedding your data..."):
            try:
                store, row_count = ingest_csv(uploaded_file)
                st.session_state["rag_store"] = store
                st.success(f"Indexed {row_count} rows. You can now ask questions.")
            except Exception as e:
                st.error(f"Failed to process file: {e}")

    if "rag_store" in st.session_state:
        question = st.text_input("Ask a question about your uploaded data")
        if st.button("Ask") and question.strip():
            with st.spinner("Searching and answering..."):
                result = ask_question(st.session_state["rag_store"], question)

            st.write(result["answer"])

            with st.expander("Sources used to answer this"):
                for i, source_text in enumerate(result["sources"], 1):
                    st.caption(f"{i}. {source_text}")