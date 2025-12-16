"""Streamlit app using Google Gemini's File Search API for the Hickey Lab Assistant.

Uses the new File Search tool for semantic retrieval over uploaded documents.
Docs: https://ai.google.dev/gemini-api/docs/file-search
"""

import os
from pathlib import Path

import streamlit as st

from src.gemini_bot_logic import (
    get_response, 
    get_client,
    get_knowledge_files,
    get_or_create_file_search_store,
    upload_files_to_file_search_store,
    list_store_documents,
    get_store_info,
    delete_file_search_store,
)


ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "lab_logo.png"
AVATAR_PATH = ASSETS_DIR / "avatar.gif"

st.set_page_config(
    page_title="Hickey Lab AI Assistant (Gemini)",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🧬",
)

st.title("🧬 Hickey Lab AI Assistant")
st.caption("Powered by Google Gemini 2.5 Flash | Ask about our research, spatial omics, and lab publications.")


def show_sidebar():
    """Render sidebar with info and file status."""
    with st.sidebar:
        st.header("About")
        if AVATAR_PATH.exists():
            st.image(str(AVATAR_PATH), caption="Hickey Lab Assistant", use_column_width=True)
        
        st.markdown("---")
        st.subheader("🔧 Pipeline: Gemini File Search")
        st.markdown(
            """
            This version uses **Google's Gemini 2.5 Flash** with the 
            **File Search API** - Google's managed semantic search 
            over your documents.
            
            **How it works:**
            1. Files uploaded to File Search store
            2. Google chunks & embeds automatically
            3. Semantic search finds relevant passages
            4. Gemini generates grounded answers
            
            **Pros:**
            - Google handles RAG infrastructure
            - Semantic search (not just keywords)
            - Citations available
            - Storage is free
            
            **Cons:**
            - Files on Google's servers
            - Pay for embedding at upload time
            """
        )
        
        st.markdown("---")
        st.subheader("📁 Knowledge Base")
        
        # Show local files
        knowledge_files = get_knowledge_files()
        if knowledge_files:
            st.write(f"**{len(knowledge_files)} local files:**")
            for f in knowledge_files:
                st.write(f"- {f.name}")
        else:
            st.warning("No files in knowledge base!")
        
        # Show indexed files
        st.markdown("---")
        st.subheader("🗂️ File Search Store")
        
        try:
            store_info = get_store_info()
            st.write(f"**Store:** `{store_info['display_name']}`")
            st.write(f"**Created:** {store_info['create_time'][:19]}")
            st.write(f"**Indexed:** {store_info['indexed_files']} files")
            
            with st.expander("📄 View indexed files"):
                for f in store_info['files']:
                    status_icon = "✅" if f['state'] == "ACTIVE" else "⏳"
                    st.write(f"{status_icon} {f['display_name']}")
                    
            # Check for sync status
            local_names = {f.name for f in knowledge_files}
            indexed_names = {f['display_name'] for f in store_info['files']}
            
            new_files = local_names - indexed_names
            if new_files:
                st.warning(f"⚠️ {len(new_files)} new file(s) not yet indexed")
                for f in new_files:
                    st.write(f"  - {f}")
            else:
                st.success("✅ All local files are indexed")
                
        except Exception as e:
            st.info(f"Store not initialized yet. Ask a question to set it up.")
        
        # Actions
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Re-index"):
                with st.spinner("Re-uploading files..."):
                    try:
                        delete_file_search_store()
                        results = upload_files_to_file_search_store(force_reupload=True)
                        st.success(f"Indexed {len(results['uploaded'])} files!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")
        with col2:
            if st.button("🗑️ Clear Store"):
                with st.spinner("Deleting store..."):
                    try:
                        delete_file_search_store()
                        st.success("Store deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {e}")


def init_session_state():
    """Initialize chat history and Gemini."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "gemini_initialized" not in st.session_state:
        try:
            get_client()  # This will initialize and validate the API key
            st.session_state.gemini_initialized = True
        except Exception as e:
            st.error(f"Failed to initialize Gemini: {e}")
            st.session_state.gemini_initialized = False


def render_chat():
    """Display chat history and handle new input."""
    if not st.session_state.get("gemini_initialized", False):
        st.error("Gemini not initialized. Check your GEMINI_API_KEY in .env")
        return
    
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    if prompt := st.chat_input("Ask about our research..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.spinner("Thinking..."):
            try:
                response = get_response(prompt)
            except FileNotFoundError as exc:
                response = (
                    "No files found in the knowledge base. Please add PDFs or text files to "
                    "`assets/knowledge_base/`."
                )
                st.error(str(exc))
            except Exception as exc:
                response = f"Something went wrong: {str(exc)}"
                st.error(str(exc))

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)


def main():
    show_sidebar()
    init_session_state()
    render_chat()


if __name__ == "__main__":
    main()
