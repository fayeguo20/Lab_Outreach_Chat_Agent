"""
Gemini File Search Store Manager
================================
A CLI tool to inspect and manage your Gemini File Search store.

Usage:
    python manage_store.py                  # Show interactive menu
    python manage_store.py status           # Quick status check
    python manage_store.py list             # List all indexed files
    python manage_store.py sync             # Sync new local files to store
    python manage_store.py upload <file>    # Upload a specific file
    python manage_store.py delete <file>    # Delete a specific file
    python manage_store.py clear            # Delete all files and store
    python manage_store.py ask "<question>" # Ask a question (query the store)
    python manage_store.py chat             # Interactive chat mode
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
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


def get_client():
    """Get Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def get_store(client):
    """Get the File Search store."""
    for store in client.file_search_stores.list():
        if store.display_name == FILE_SEARCH_STORE_NAME:
            return store
    return None


def get_local_files():
    """Get local knowledge base files."""
    supported = {".pdf", ".txt", ".md"}
    return sorted([f for f in ASSETS_DIR.glob("*") if f.suffix in supported])


def format_size(size_bytes):
    """Format bytes to human readable."""
    if size_bytes is None:
        return "Unknown"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def cmd_status():
    """Show quick status."""
    client = get_client()
    store = get_store(client)
    
    print("\n" + "="*50)
    print("📊 GEMINI FILE SEARCH STORE STATUS")
    print("="*50)
    
    if not store:
        print("\n❌ No store found. Run 'sync' to create one.")
        return
    
    print(f"\n🗂️  Store: {store.display_name}")
    print(f"   ID: {store.name}")
    print(f"   Created: {store.create_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get files
    remote_files = list(client.files.list())
    local_files = get_local_files()
    
    print(f"\n📁 Files:")
    print(f"   Indexed (remote): {len(remote_files)}")
    print(f"   Local: {len(local_files)}")
    
    # Check sync status
    local_names = {f.name for f in local_files}
    remote_names = {f.display_name for f in remote_files}
    
    new_files = local_names - remote_names
    orphaned = remote_names - local_names
    
    if new_files:
        print(f"\n⚠️  {len(new_files)} local file(s) not indexed:")
        for f in new_files:
            print(f"      - {f}")
    
    if orphaned:
        print(f"\n⚠️  {len(orphaned)} indexed file(s) not in local folder:")
        for f in orphaned:
            print(f"      - {f}")
    
    if not new_files and not orphaned:
        print("\n✅ Store is in sync with local files!")
    
    print()


def cmd_list():
    """List all indexed files with details."""
    client = get_client()
    
    print("\n" + "="*50)
    print("📄 INDEXED FILES")
    print("="*50 + "\n")
    
    files = list(client.files.list())
    
    if not files:
        print("No files indexed.")
        return
    
    for i, f in enumerate(files, 1):
        state_icon = "✅" if "ACTIVE" in str(f.state) else "⏳"
        size = format_size(getattr(f, 'size_bytes', None))
        create_time = getattr(f, 'create_time', None)
        time_str = create_time.strftime('%Y-%m-%d %H:%M') if create_time else "Unknown"
        
        print(f"{i}. {state_icon} {f.display_name}")
        print(f"      ID: {f.name}")
        print(f"      Size: {size} | Created: {time_str}")
        print()


def cmd_sync():
    """Sync local files to the store (upload new ones only)."""
    client = get_client()
    store = get_store(client)
    
    print("\n" + "="*50)
    print("🔄 SYNCING FILES")
    print("="*50 + "\n")
    
    # Create store if needed
    if not store:
        print(f"Creating store: {FILE_SEARCH_STORE_NAME}")
        store = client.file_search_stores.create(
            config={'display_name': FILE_SEARCH_STORE_NAME}
        )
        print(f"✅ Created: {store.name}\n")
    
    local_files = get_local_files()
    remote_files = {f.display_name: f for f in client.files.list()}
    
    uploaded = 0
    skipped = 0
    failed = 0
    
    for file_path in local_files:
        if file_path.name in remote_files:
            print(f"⏭️  Skipping (exists): {file_path.name}")
            skipped += 1
            continue
        
        print(f"📤 Uploading: {file_path.name}...", end=" ", flush=True)
        try:
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(file_path),
                file_search_store_name=store.name,
                config={'display_name': file_path.name}
            )
            
            while not operation.done:
                time.sleep(2)
                operation = client.operations.get(operation)
            
            print("✅")
            uploaded += 1
        except Exception as e:
            print(f"❌ {e}")
            failed += 1
    
    print(f"\n📊 Summary: {uploaded} uploaded, {skipped} skipped, {failed} failed")


def cmd_upload(filename):
    """Upload a specific file."""
    client = get_client()
    store = get_store(client)
    
    if not store:
        print("❌ No store exists. Run 'sync' first to create one.")
        return
    
    # Find file
    file_path = ASSETS_DIR / filename
    if not file_path.exists():
        # Try matching partial name
        matches = [f for f in get_local_files() if filename.lower() in f.name.lower()]
        if len(matches) == 1:
            file_path = matches[0]
        elif len(matches) > 1:
            print(f"❌ Multiple matches for '{filename}':")
            for m in matches:
                print(f"   - {m.name}")
            return
        else:
            print(f"❌ File not found: {filename}")
            return
    
    print(f"\n📤 Uploading: {file_path.name}...", end=" ", flush=True)
    try:
        operation = client.file_search_stores.upload_to_file_search_store(
            file=str(file_path),
            file_search_store_name=store.name,
            config={'display_name': file_path.name}
        )
        
        while not operation.done:
            time.sleep(2)
            operation = client.operations.get(operation)
        
        print("✅ Done!")
    except Exception as e:
        print(f"❌ Failed: {e}")


def cmd_delete(filename):
    """Delete a specific file from the store."""
    client = get_client()
    
    # Find file by display name
    target = None
    for f in client.files.list():
        if f.display_name == filename or filename in f.display_name:
            target = f
            break
    
    if not target:
        print(f"❌ File not found in store: {filename}")
        return
    
    confirm = input(f"\n⚠️  Delete '{target.display_name}'? (y/N): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    print(f"🗑️  Deleting: {target.display_name}...", end=" ", flush=True)
    try:
        client.files.delete(name=target.name)
        print("✅ Done!")
    except Exception as e:
        print(f"❌ Failed: {e}")


def cmd_clear():
    """Delete all files and the store."""
    client = get_client()
    store = get_store(client)
    
    if not store:
        print("❌ No store found.")
        return
    
    files = list(client.files.list())
    
    print(f"\n⚠️  This will delete:")
    print(f"   - Store: {store.display_name}")
    print(f"   - {len(files)} indexed file(s)")
    
    confirm = input("\nType 'DELETE' to confirm: ")
    if confirm != 'DELETE':
        print("Cancelled.")
        return
    
    print("\n🗑️  Deleting files...")
    for f in files:
        print(f"   - {f.display_name}...", end=" ", flush=True)
        try:
            client.files.delete(name=f.name)
            print("✅")
        except Exception as e:
            print(f"❌ {e}")
    
    print(f"\n🗑️  Deleting store...", end=" ", flush=True)
    try:
        client.file_search_stores.delete(name=store.name, config={'force': True})
        print("✅")
    except Exception as e:
        print(f"❌ {e}")
    
    print("\n✅ Store cleared!")


def cmd_ask(question: str):
    """Ask a question - query the file search store."""
    client = get_client()
    store = get_store(client)
    
    if not store:
        print("❌ No store found. Run 'sync' first to create one and upload files.")
        return
    
    print(f"\n🤔 Question: {question}")
    print("\n" + "-"*50)
    print("🔍 Searching documents and generating answer...")
    print("-"*50 + "\n")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
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
        print(response.text)
        
        # Show grounding info if available
        if hasattr(response, 'candidates') and response.candidates:
            grounding = getattr(response.candidates[0], 'grounding_metadata', None)
            if grounding:
                print("\n" + "-"*50)
                print("📚 Sources used:")
                print("-"*50)
                # Try to extract source info
                if hasattr(grounding, 'grounding_chunks'):
                    for chunk in grounding.grounding_chunks[:3]:  # Show top 3
                        if hasattr(chunk, 'retrieved_context'):
                            print(f"  - {chunk.retrieved_context.title}")
    except Exception as e:
        print(f"❌ Error: {e}")


def cmd_chat():
    """Interactive chat mode."""
    client = get_client()
    store = get_store(client)
    
    if not store:
        print("❌ No store found. Run 'sync' first to create one and upload files.")
        return
    
    print("\n" + "="*50)
    print("💬 INTERACTIVE CHAT MODE")
    print("="*50)
    print("Ask questions about the Hickey Lab research.")
    print("Type 'quit' or 'exit' to leave.\n")
    
    while True:
        try:
            question = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Bye!")
            break
            
        if not question:
            continue
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Bye!")
            break
        
        print("\n🤖 Assistant: ", end="", flush=True)
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
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
            print(response.text)
        except Exception as e:
            print(f"Error: {e}")
        
        print()  # Blank line between exchanges)


def interactive_menu():
    """Show interactive menu."""
    while True:
        print("\n" + "="*50)
        print("🧬 HICKEY LAB FILE SEARCH STORE MANAGER")
        print("="*50)
        print("\n1. 📊 Status        - Quick overview")
        print("2. 📄 List          - Show all indexed files")
        print("3. 🔄 Sync          - Upload new local files")
        print("4. 📤 Upload        - Upload specific file")
        print("5. 🗑️  Delete        - Delete specific file")
        print("6. ⚠️  Clear         - Delete everything")
        print("7. � Chat          - Ask questions (interactive)")
        print("8. 🚪 Exit")
        
        choice = input("\nChoice (1-8): ").strip()
        
        if choice == "1":
            cmd_status()
        elif choice == "2":
            cmd_list()
        elif choice == "3":
            cmd_sync()
        elif choice == "4":
            filename = input("File name: ").strip()
            if filename:
                cmd_upload(filename)
        elif choice == "5":
            filename = input("File name to delete: ").strip()
            if filename:
                cmd_delete(filename)
        elif choice == "6":
            cmd_clear()
        elif choice == "7":
            cmd_chat()
        elif choice == "8":
            print("\n👋 Bye!")
            break
        else:
            print("Invalid choice.")


def main():
    if len(sys.argv) < 2:
        interactive_menu()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        cmd_status()
    elif command == "list":
        cmd_list()
    elif command == "sync":
        cmd_sync()
    elif command == "upload":
        if len(sys.argv) < 3:
            print("Usage: python manage_store.py upload <filename>")
        else:
            cmd_upload(sys.argv[2])
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python manage_store.py delete <filename>")
        else:
            cmd_delete(sys.argv[2])
    elif command == "clear":
        cmd_clear()
    elif command == "ask":
        if len(sys.argv) < 3:
            print("Usage: python manage_store.py ask \"<question>\"")
        else:
            cmd_ask(" ".join(sys.argv[2:]))
    elif command == "chat":
        cmd_chat()
    elif command in ["help", "-h", "--help"]:
        print(__doc__)
    else:
        print(f"Unknown command: {command}")
        print("Run 'python manage_store.py help' for usage.")


if __name__ == "__main__":
    main()
