This is a comprehensive project plan formatted as a Markdown file. You can create a file named `README.md` or `PROJECT_PLAN.md` in your VS Code root folder and paste this content directly into it.

This plan serves as both your **development roadmap** and your **documentation** for the hackathon judges.

-----

### 1\. Visualization of the Architecture

Before you start coding, here is the architecture you are building. This visualizes how the User, the Website, and the AI interact.

-----

### 2\. The Project Plan (`.md` file)

Copy the code block below into your editor.

````markdown
# Project: Hickey Lab AI Outreach Assistant
**Theme:** Bridging Spatial Omics & Community Engagement via AI  
**Stack:** Python, Streamlit, LangChain, OpenAI (or BioMistral), Hugging Face Spaces  
**Integration:** Google Sites

---

## 📂 1. Project Directory Structure
Create this folder structure in VS Code to keep the project organized.

```text
hickey-lab-assistant/
│
├── .env                    # Stores API Keys (NEVER upload this to GitHub)
├── .gitignore              # Tells git to ignore .env and venv
├── requirements.txt        # List of python libraries
├── README.md               # This project plan
│
├── assets/                 # Static files
│   ├── lab_logo.png
│   ├── avatar.gif          # The animation created in Canva
│   └── knowledge_base/     # Folder containing PDF papers
│       ├── paper1.pdf
│       ├── paper2.pdf
│       └── ...
│
├── src/                    # Source code
│   ├── __init__.py
│   ├── ingest.py           # Script to read PDFs and create vector database
│   └── bot_logic.py        # The RAG (Retrieval Augmented Generation) pipeline
│
└── app.py                  # Main Streamlit application (Frontend)
````

-----

## 🛠️ 2. Development Phase 1: Setup & Configuration

### Step 1: Environment Setup

1.  **Install Python:** Ensure Python 3.9+ is installed.
2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (On Mac/Linux)
    # or
    venv\Scripts\activate     # (On Windows)
    ```

### Step 2: Install Dependencies

Create a `requirements.txt` file with the following:

```text
streamlit
langchain
langchain-community
langchain-openai
chromadb
pypdf
python-dotenv
tiktoken
```

Run installation: `pip install -r requirements.txt`

### Step 3: API Keys

1.  Get an OpenAI API Key (easiest for Hackathon speed).
2.  Create a `.env` file in the root directory:
    ```text
    OPENAI_API_KEY=sk-proj-your-key-here...
    ```

-----

## 🧠 3. Development Phase 2: The "Brain" (Backend)

### Goal: Make the AI read the lab's papers.

**Action Item:** Create `src/ingest.py`.

  * **Input:** Reads all PDFs from `assets/knowledge_base/`.
  * **Process:** 1.  Load PDFs using `PyPDFLoader`.
    2\.  Split text into chunks (e.g., 1000 characters).
    3\.  Convert chunks to embeddings (numbers) using OpenAIEmbeddings.
    4\.  Save to a local vector store (`chroma_db`).
  * **Output:** A folder named `chroma_db` appearing in your root.

**Action Item:** Create `src/bot_logic.py`.

  * **Function:** `get_response(user_question)`
  * **Logic:**
    1.  Search `chroma_db` for chunks similar to `user_question`.
    2.  Send the question + relevant chunks to the LLM.
    3.  System Prompt: *"You are a helpful assistant for the Hickey Lab at Duke. Explain complex spatial omics concepts simply..."*

-----

## 🎨 4. Development Phase 3: The "Body" (Frontend)

### Goal: Create the Chat Interface.

**Action Item:** Create `app.py`.
This is the file that runs the website.

**Key Features to Implement:**

1.  **Page Config:** Set the page title and favicon (use the lab logo).

2.  **Avatar Display:** Load `assets/avatar.gif` in the sidebar.

3.  **Chat History:** Use `st.session_state` to remember the conversation so it feels natural.

4.  **Input/Output:** \`\`\`python
    import streamlit as st
    from src.bot\_logic import get\_response

    st.title("🧬 Hickey Lab AI Assistant")

    # User Input

    if prompt := st.chat\_input("Ask about our research..."):
    \# Display user message
    st.chat\_message("user").markdown(prompt)

    ```
    # Get AI Response
    response = get_response(prompt)

    # Display AI message
    st.chat_message("assistant").markdown(response)
    ```

    ```
    
    ```

-----

## 🚀 5. Development Phase 4: Deployment & Integration

### Step 1: Hugging Face Spaces

1.  Create an account on Hugging Face.
2.  Create a new "Space".
3.  Select SDK: **Streamlit**.
4.  Upload your files (excluding `.env` and `venv`).
5.  **Crucial:** Go to Space Settings \> **Variables and secrets**. Add your `OPENAI_API_KEY` there.

### Step 2: Google Sites Embedding

1.  Copy the URL of your live Hugging Face Space (e.g., `https://huggingface.co/spaces/username/project`).
2.  Go to the Hickey Lab Google Site editor.
3.  **Insert \> Embed \> By URL**.
4.  Paste the link. Resize the box to look like a chat window.

-----

## 🏆 6. Hackathon Pitch Points (The "Why")

  * **Necessity:** "Science is getting more complex. Static websites leave non-experts behind. This tool actively bridges the knowledge gap."
  * **Innovation:** "We aren't just displaying data; we are using RAG (Retrieval Augmented Generation) to make our specific publications conversational."
  * **Accessibility:** "This agent can translate 'spatial transcriptomics' into plain English for a high school student or a patient advocate."

-----

## ✅ Checklist for Hackathon Day

  - [ ]  PDFs of top 5 lab papers downloaded to `assets`.
  - [ ]  Vector database created (`ingest.py` ran successfully).
  - [ ]  Avatar GIF created in Canva.
  - [ ]  Streamlit app running locally (`streamlit run app.py`).
  - [ ]  Deployed to Hugging Face.
  - [ ]  Embedded on a test Google Site page.

<!-- end list -->

```


```