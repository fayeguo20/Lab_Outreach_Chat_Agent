import os
from pathlib import Path

import streamlit as st

from src.bot_logic import get_response


ROOT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = ROOT_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "lab_logo.png"
AVATAR_PATH = ASSETS_DIR / "avatar.gif"

st.set_page_config(
    page_title="Hickey Lab AI Assistant",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🧬",
)

st.title("🧬 Hickey Lab AI Assistant")
st.caption("Ask about our research, spatial omics, and lab publications.")


def show_sidebar():
    """Render sidebar with avatar and instructions."""
    with st.sidebar:
        st.header("About")
        if AVATAR_PATH.exists():
            st.image(str(AVATAR_PATH), caption="Hickey Lab Assistant", use_column_width=True)
        else:
            st.info("Add assets/avatar.gif to show the assistant avatar.")

        st.markdown(
            """
            1. Add PDFs to `assets/knowledge_base/`.
            2. Run `python -m src.ingest` to build the vector store.
            3. Start chatting below.
            """
        )


def init_session_state():
    """Initialize chat history."""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_chat():
    """Display chat history and handle new input."""
    for message in st.session_state.messages:
        st.chat_message(message["role"]).markdown(message["content"])

    if prompt := st.chat_input("Ask about our research..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        try:
            response = get_response(prompt)
        except FileNotFoundError as exc:
            response = (
                "Vector store not found. Please add PDFs to "
                "`assets/knowledge_base/` and run `python -m src.ingest`."
            )
            st.error(str(exc))
        except Exception as exc:  # noqa: BLE001
            response = "Something went wrong while generating a response."
            st.error(str(exc))

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").markdown(response)


def main():
    show_sidebar()
    init_session_state()
    render_chat()


if __name__ == "__main__":
    main()

