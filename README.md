# ⚽ Football Transfer Scout

An AI-powered scouting assistant — describe the kind of player you need
in plain English, and get a ranked, explained shortlist drawn from a
real dataset of 16,000+ professional footballers.

## Features
- 🔍 Natural-language scout briefs → structured filters → shortlisted players
- 🧠 AI-generated fit verdicts — "Strong fit" / "Partial fit" / "Weak fit", with reasoning
- 📊 Radar chart comparison between 2–3 players, plus a plain-language stat breakdown
- 📁 Upload your own CSV and ask free-form questions — answered via retrieval-augmented generation (RAG),     grounded in your uploaded data
- 🔒 Uploaded data is embedded and searched in-memory only — never persisted to disk
- 💰 Completely free — no paid APIs

## Tech Stack
- **LLM:** Groq (`openai/gpt-oss-120b`) — free tier
- **Framework:** LangChain
- **Embeddings:** sentence-transformers (local, free)
- **Vector Store:** ChromaDB (local)
- **Data Source:** EA Sports FC 24 Complete Player Dataset (Kaggle)
- **Frontend:** Streamlit
- **Charts:** Plotly

## Pipeline

**Scout Search:** 
Scout brief → LLM parses into structured filters → pandas filters
16,000+ players → LLM generates fit verdict per candidate → Streamlit UI

**Ask Your Own Data (RAG):**
CSV upload → rows converted to text → embedded locally → stored in
Chroma (in-memory) → question embedded → similarity search retrieves
relevant rows → LLM answers grounded in retrieved context → Streamlit UI


## Setup

### 1. Clone the repository
```powershell
git clone https://github.com/omorfaruk130/football-transfer-scout.git
cd football-transfer-scout
```

### 2. Create virtual environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
GROQ_API_KEY=your_key_here


### 5. Download the dataset
Get the **EA Sports FC 24 Complete Player Dataset** from Kaggle:
`kaggle.com/datasets/stefanoleone992/ea-sports-fc-24-complete-player-dataset`

Place the male players CSV at:data/players_fc24.csv


### 6. Run the app
```powershell
streamlit run app.py
```

## API Keys Required

| `GROQ_API_KEY` | https://console.groq.com |

## Example Briefs to Try
- "We need a left-footed centre-back, under 26, comfortable with the ball, can play out from the back. Budget under £40M."
- "Find a right-winger under 23 who's fast and a good dribbler."
- "A cheap, physical defensive midfielder under €20M."

## Known Limitations
- Player valuations are EA FC 24 in-game values, used as a proxy for real transfer-market value
- Uploaded CSVs (RAG feature) are session-scoped — cleared when the app restarts
- Dataset covers men's football only (`male_players.csv`)

## Architecture

The project is organized into four layers, each with a single responsibility:

- **Data layer** (`src/data/`) — loads and cleans the structured player dataset
- **LLM layer** (`src/llm/`) — prompts, the Groq client, and output validation
- **Core layer** (`src/core/`) — orchestrates search, comparison, and RAG pipelines
- **UI layer** (`app.py`) — thin Streamlit shell with no business logic
