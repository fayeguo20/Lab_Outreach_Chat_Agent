"""Gemini-based pipeline using Google's File Search API for document Q&A.

Uses the new File Search tool which provides semantic search over uploaded documents.
Docs: https://ai.google.dev/gemini-api/docs/file-search
"""

import os
import time
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets" / "knowledge_base"
FILE_SEARCH_STORE_NAME = "hickey-lab-knowledge-base"

SYSTEM_PROMPT = """You are a warm, caring assistant for anyone curious about the Hickey Lab at Duke University.
Explain spatial omics and our research in friendly, plain language while staying accurate.
Use the uploaded documents to ground your answers. If the documents don't contain relevant information, 
gently say you don't have that info yet and invite another question.

When answering:
- Be specific and cite which paper or document the information comes from when relevant
- Provide context about why the research matters
- Use accessible language for non-experts
"""

# Global cache
_client: Optional[genai.Client] = None
_file_search_store = None
_files_checked = False  # Track if we've verified files are uploaded


def get_client() -> genai.Client:
    """Get or create the Gemini client."""
    global _client
    if _client is None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        _client = genai.Client(api_key=api_key)
    return _client


def get_knowledge_files() -> list[Path]:
    """Get all supported files from the knowledge base."""
    supported_extensions = {".pdf", ".txt", ".md"}
    files = []
    for ext in supported_extensions:
        files.extend(ASSETS_DIR.glob(f"*{ext}"))
    return sorted(files)


def get_or_create_file_search_store():
    """Get existing or create new File Search store."""
    global _file_search_store
    
    if _file_search_store is not None:
        return _file_search_store
    
    client = get_client()
    
    # Check if store already exists
    try:
        for store in client.file_search_stores.list():
            if store.display_name == FILE_SEARCH_STORE_NAME:
                _file_search_store = store
                print(f"Found existing File Search store: {store.name}")
                return store
    except Exception as e:
        print(f"Error listing stores: {e}")
    
    # Create new store
    print(f"Creating new File Search store: {FILE_SEARCH_STORE_NAME}")
    _file_search_store = client.file_search_stores.create(
        config={'display_name': FILE_SEARCH_STORE_NAME}
    )
    print(f"Created store: {_file_search_store.name}")
    return _file_search_store


def upload_files_to_file_search_store(force_reupload: bool = False) -> dict:
    """Upload knowledge base files to the File Search store.
    
    Only uploads files that aren't already in the store (smart sync).
    Set force_reupload=True to re-upload everything.
    """
    global _files_checked
    
    client = get_client()
    store = get_or_create_file_search_store()
    
    files_to_upload = get_knowledge_files()
    if not files_to_upload:
        raise FileNotFoundError(
            f"No files found in {ASSETS_DIR}. Add PDFs or text files to the knowledge base."
        )
    
    # Get already uploaded files from the Files API
    existing_files = {}
    try:
        for f in client.files.list():
            existing_files[f.display_name] = f
    except Exception as e:
        print(f"Warning: Could not list existing files: {e}")
    
    results = {"uploaded": [], "skipped": [], "failed": []}
    
    for file_path in files_to_upload:
        # Skip if already exists and not forcing re-upload
        if file_path.name in existing_files and not force_reupload:
            print(f"Skipping (already indexed): {file_path.name}")
            results["skipped"].append(file_path.name)
            continue
            
        print(f"Uploading: {file_path.name}")
        try:
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store.name,
                config={
                    'display_name': file_path.name,
                }
            )
            
            # Wait for processing to complete
            while not operation.done:
                time.sleep(2)
                operation = client.operations.get(operation)
            
            print(f"  ✓ Uploaded and indexed: {file_path.name}")
            results["uploaded"].append(file_path.name)
        except Exception as e:
            print(f"  ✗ Failed: {file_path.name} - {e}")
            results["failed"].append({"file": file_path.name, "error": str(e)})
    
    _files_checked = True
    return results


def ensure_files_uploaded():
    """Ensure files are uploaded, but only check once per session."""
    global _files_checked
    
    if not _files_checked:
        # Check if store has any files, if not upload
        client = get_client()
        existing_files = list(client.files.list())
        
        if not existing_files:
            print("No files in store, uploading...")
            upload_files_to_file_search_store()
        else:
            # Just check for new files without re-uploading existing
            local_files = {f.name for f in get_knowledge_files()}
            remote_files = {f.display_name for f in existing_files}
            
            new_files = local_files - remote_files
            if new_files:
                print(f"Found {len(new_files)} new files to upload: {new_files}")
                upload_files_to_file_search_store()
            else:
                print(f"All {len(remote_files)} files already indexed, skipping upload.")
        
        _files_checked = True


def get_response(user_question: str) -> str:
    """Generate a response using Gemini with File Search."""
    client = get_client()
    store = get_or_create_file_search_store()
    
    # Smart check - only uploads if needed, skips if files already indexed
    ensure_files_uploaded()
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_question,
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
        return f"Error generating response: {str(e)}"


def get_grounding_metadata(user_question: str) -> dict:
    """Get response with grounding/citation metadata."""
    client = get_client()
    store = get_or_create_file_search_store()
    
    upload_files_to_file_search_store()
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_question,
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
    
    return {
        "text": response.text,
        "grounding_metadata": response.candidates[0].grounding_metadata if response.candidates else None
    }


def list_store_documents() -> list[dict]:
    """List all documents in the File Search store."""
    client = get_client()
    
    try:
        files = list(client.files.list())
        return [
            {
                "name": f.name, 
                "display_name": f.display_name,
                "state": f.state.name if hasattr(f.state, 'name') else str(f.state),
                "size_bytes": getattr(f, 'size_bytes', None),
                "create_time": str(getattr(f, 'create_time', 'Unknown')),
            } 
            for f in files
        ]
    except Exception as e:
        return [{"error": str(e)}]


def get_store_info() -> dict:
    """Get detailed info about the File Search store."""
    client = get_client()
    store = get_or_create_file_search_store()
    
    files = list(client.files.list())
    local_files = get_knowledge_files()
    
    return {
        "store_name": store.name,
        "display_name": store.display_name,
        "create_time": str(store.create_time),
        "indexed_files": len(files),
        "local_files": len(local_files),
        "files": [
            {
                "display_name": f.display_name,
                "state": f.state.name if hasattr(f.state, 'name') else str(f.state),
            }
            for f in files
        ]
    }


def delete_file_search_store():
    """Delete the File Search store and all uploaded files."""
    global _file_search_store, _files_checked
    client = get_client()
    
    # Delete all files
    try:
        for f in client.files.list():
            client.files.delete(name=f.name)
            print(f"Deleted file: {f.display_name}")
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    # Delete store
    try:
        for store in client.file_search_stores.list():
            if store.display_name == FILE_SEARCH_STORE_NAME:
                client.file_search_stores.delete(name=store.name, config={'force': True})
                print(f"Deleted store: {store.name}")
        _file_search_store = None
        _files_checked = False
    except Exception as e:
        print(f"Error deleting store: {e}")


if __name__ == "__main__":
    print("Knowledge base files:")
    for f in get_knowledge_files():
        print(f"  - {f.name}")
    
    print("\nSetting up File Search store...")
    results = upload_files_to_file_search_store()
    print(f"\nUpload results: {results}")
    
    print("\nTesting query...")
    response = get_response("What does the Hickey Lab do?")
    print(f"Response: {response[:500]}...")
