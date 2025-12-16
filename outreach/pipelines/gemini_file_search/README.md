---
title: Hickey Lab AI Assistant
emoji: 🧬
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.52.1
app_file: app.py
pinned: false
---

# Hickey Lab AI Assistant - Gemini File Search

A Streamlit chatbot powered by **Google Gemini 2.5 Flash** and the **File Search API**.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY="your-key-here"  # Linux/Mac
# or
set GEMINI_API_KEY=your-key-here       # Windows

# Run the app
streamlit run app.py
```

## 📦 Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and select `app.py`
4. Add `GEMINI_API_KEY` in Settings → Secrets
5. Deploy!

### Option 2: Hugging Face Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select "Streamlit" as the SDK
3. Upload these files
4. Add `GEMINI_API_KEY` as a secret in Settings
5. The app will auto-deploy

### Option 3: Self-Hosted

```bash
# Install
pip install -r requirements.txt

# Run with environment variable
GEMINI_API_KEY="your-key" streamlit run app.py --server.port 8501
```

## 🔗 Embedding in Google Sites

Once deployed, you'll get a public URL. To add to Google Sites:

1. **Simple Link (Always works):**
   - Add a button: "Chat with our AI Assistant →"
   - Link to your Streamlit/HF URL

2. **Embed (HuggingFace Spaces recommended):**
   - In Google Sites: Insert → Embed → By URL
   - Paste your HuggingFace Space URL
   - Note: Some iframes may be blocked by Google Sites

## 📁 Files

```
gemini_file_search/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## ⚙️ Configuration

The app uses these settings (edit in `app.py`):

| Setting | Value | Description |
|---------|-------|-------------|
| `FILE_SEARCH_STORE_NAME` | `hickey-lab-knowledge-base` | Your Gemini File Search store name |
| `MODEL_NAME` | `gemini-2.5-flash` | Gemini model to use |
| `SYSTEM_PROMPT` | (see code) | The assistant's personality/instructions |

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Google AI API key from [aistudio.google.com](https://aistudio.google.com) |
