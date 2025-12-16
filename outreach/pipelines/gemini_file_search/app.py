"""
Hickey Lab AI Assistant - Gemini File Search Pipeline
=====================================================
A Streamlit chatbot powered by Google's Gemini 2.5 Flash and File Search API.

This is a standalone deployable app that can be hosted on:
- Streamlit Cloud (https://streamlit.io/cloud)
- Hugging Face Spaces (https://huggingface.co/spaces)
- Any server with Python

Setup:
1. Set GEMINI_API_KEY environment variable (or add to .env)
2. Files are already indexed in Google's File Search store
3. Run: streamlit run app.py
"""

import os
from typing import Optional

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
FILE_SEARCH_STORE_NAME = "hickey-lab-knowledge-base"
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """You are a warm, caring assistant for anyone curious about the Hickey Lab at Duke University.
Explain spatial omics and our research in friendly, plain language while staying accurate.
Use the uploaded documents to ground your answers. If the documents don't contain relevant information, 
gently say you don't have that info yet and invite another question.

When answering:
- Be specific and cite which paper or document the information comes from when relevant
- Provide context about why the research matters
- Use accessible language for non-experts
"""

# --------------------------------------------------------------------------
# Gemini Client & File Search
# --------------------------------------------------------------------------

@st.cache_resource
def get_client():
    """Initialize Gemini client (cached)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found. Set it in environment variables or .env file.")
        st.stop()
    return genai.Client(api_key=api_key)


@st.cache_resource
def get_file_search_store():
    """Get the File Search store (cached)."""
    client = get_client()
    for store in client.file_search_stores.list():
        if store.display_name == FILE_SEARCH_STORE_NAME:
            return store
    return None


def get_response(question: str) -> str:
    """Generate a response using Gemini with File Search."""
    client = get_client()
    store = get_file_search_store()
    
    if not store:
        return "⚠️ File Search store not found. Please set up the knowledge base first."
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[store.name]
                        )
                    )
                ]
            )
        )
        return response.text
    except Exception as e:
        return f"❌ Error: {str(e)}"


def get_indexed_files() -> list[str]:
    """Get list of indexed file names."""
    client = get_client()
    try:
        return [f.display_name for f in client.files.list()]
    except Exception:
        return []


# --------------------------------------------------------------------------
# Streamlit UI
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Hickey Lab AI Assistant",
    page_icon="🧬",
    layout="centered",
)

# Custom CSS for cleaner look
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
    }
    .main > div {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🧬 Hickey Lab AI Assistant")
st.caption("Ask about our research in spatial omics, multiplexed imaging, and computational biology.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI assistant can answer questions about the **Hickey Lab** at Duke University.
    
    **Research Areas:**
    - Spatial omics & tissue mapping
    - Multiplexed imaging (CODEX)
    - Computational modeling
    - Machine learning for biology
    
    ---
    
    **Powered by:**
    - Google Gemini 2.5 Flash
    - File Search API
    """)
    
    # Show indexed files
    with st.expander("📚 Knowledge Base"):
        files = get_indexed_files()
        if files:
            for f in files:
                st.write(f"• {f}")
        else:
            st.write("No files indexed yet.")
    
    st.markdown("---")
    st.markdown("[🔗 Hickey Lab Website](https://sites.google.com/view/hickeylab)")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about our research..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            response = get_response(prompt)
        st.markdown(response)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
