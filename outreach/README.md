# Hickey Lab AI Outreach Assistant

**Theme:** Bridging Spatial Omics & Community Engagement via AI  
**Pipelines:** OpenAI RAG (local) | Gemini File Search (cloud) ⭐  
**Deployment:** Streamlit Cloud, HuggingFace Spaces, or Self-Hosted  
**Integration:** Google Sites

---

## 📁 Project Structure

```text
outreach/
├── README.md                    # This file
├── requirements.txt             # All dependencies
├── .env                         # API keys (not in git)
│
├── assets/
│   └── knowledge_base/          # PDFs and docs for the chatbot
│       ├── lab_overview.txt     # Structured overview (helps with broad questions)
│       └── *.pdf                # Research papers
│
├── pipelines/
│   └── gemini_file_search/      # Pipeline 2: Gemini File Search ⭐
│       ├── app.py               # Standalone deployable Streamlit app
│       ├── requirements.txt     # Minimal deps for deployment
│       └── README.md            # Deployment instructions
│
├── tools/
│   └── manage_store.py          # CLI to manage Gemini File Search store
│
├── src/                         # Shared source code
│   ├── bot_logic.py             # OpenAI RAG logic
│   ├── gemini_bot_logic.py      # Gemini File Search logic
│   └── ingest.py                # ChromaDB ingestion
│
├── chroma_db/                   # Local vector store (OpenAI pipeline)
│
├── app.py                       # OpenAI RAG app (original)
└── app_gemini.py                # Gemini File Search app (full version)
```

---

## 🚀 Quick Start

### Option 1: Gemini File Search (Recommended)

Best for deployment - files stored in Google's cloud, no local vector DB needed.

```bash
cd outreach

# Install dependencies
pip install -r requirements.txt

# Set your API key in .env
echo "GEMINI_API_KEY=your-key-here" > .env

# Sync your knowledge base files to Google
python tools/manage_store.py sync

# Run the app
streamlit run app_gemini.py
```

### Option 2: OpenAI RAG (Local)

Traditional RAG with local ChromaDB vector store.

```bash
cd outreach

# Install dependencies
pip install -r requirements.txt

# Set your API key in .env
echo "OPENAI_API_KEY=your-key-here" > .env

# Ingest PDFs into ChromaDB
python -m src.ingest

# Run the app
streamlit run app.py
```

---

## 🌐 Deploy to Google Sites

### Step 1: Deploy Your Chatbot

**Streamlit Cloud (Easiest)**
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `pipelines/gemini_file_search/app.py`
4. Add `GEMINI_API_KEY` in Secrets
5. Get your URL: `https://your-app.streamlit.app`

**HuggingFace Spaces (Best for embedding)**
1. Create new Space → select "Streamlit" SDK
2. Upload `pipelines/gemini_file_search/` files
3. Add `GEMINI_API_KEY` in Settings → Secrets
4. Get your URL: `https://huggingface.co/spaces/username/app`

### Step 2: Add to Google Sites

**Option A: Link Button** (Works everywhere)
- Insert → Button → Link to your deployed URL

**Option B: Embed** (HuggingFace only)
- Insert → Embed → Embed code
- Paste: `<iframe src="https://huggingface.co/spaces/username/app" width="100%" height="600"></iframe>`

---

## 🔧 Tools

### File Search Store Manager

```bash
python tools/manage_store.py          # Interactive menu
python tools/manage_store.py status   # Quick overview
python tools/manage_store.py list     # Show indexed files  
python tools/manage_store.py sync     # Upload new local files
python tools/manage_store.py ask "question"  # Test a query
python tools/manage_store.py chat     # Interactive chat
```

---

## ⚖️ Pipeline Comparison

| Feature | OpenAI RAG | Gemini File Search |
|---------|------------|-------------------|
| **Model** | GPT-4o-mini | Gemini 2.5 Flash |
| **Vector Store** | ChromaDB (local) | Google Cloud |
| **Deployment** | Need to include ChromaDB | Just the app code |
| **Setup** | Run ingestion locally | Auto-syncs to Google |
| **Cost** | OpenAI API | Gemini API (free tier) |

---

## 🔑 Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=sk-...      # For OpenAI pipeline
GEMINI_API_KEY=AIza...     # For Gemini pipeline
```

---

## 📚 Adding Documents

1. Add PDFs/TXT files to `assets/knowledge_base/`
2. For OpenAI: Run `python -m src.ingest`
3. For Gemini: Run `python tools/manage_store.py sync`

---

## 📋 Current Knowledge Base

Files indexed (7 total, ~92MB):
- `lab_overview.txt` - Structured summary for broad questions
- `Human Tumor Atlas Network paper.pdf`
- `CODEX_paper_Cell_2018.pdf`
- `IBEX_Nat_Protocols_2022.pdf`
- `PanIN_paper.pdf`
- `Spatial_biology_paper_2024.pdf`