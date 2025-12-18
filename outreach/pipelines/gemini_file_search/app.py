"""
Hickey Lab AI Assistant - Gemini File Search Pipeline
=====================================================
A production-ready Streamlit chatbot powered by Google's Gemini 2.5 Flash and File Search API.

Features:
- Cost tracking and budget management
- Rate limiting to prevent abuse
- Security and input validation
- Push notifications for critical events (ntfy.sh)
- Conversation context for better responses
- User experience enhancements

This is a standalone deployable app that can be hosted on:
- Streamlit Cloud (https://streamlit.io/cloud)
- Hugging Face Spaces (https://huggingface.co/spaces)
- Any server with Python

Setup:
1. Set GEMINI_API_KEY environment variable (or add to .env)
2. (Optional) Set NTFY_TOPIC for push notifications
3. Files are already indexed in Google's File Search store
4. Run: streamlit run app.py
"""

import os
import time
import uuid
from typing import Optional
from datetime import datetime, timedelta

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import our utility modules
from utils.cost_tracker import CostTracker
from utils.rate_limiter import RateLimiter
from utils.security import SecurityValidator
from utils.alerts import AlertSystem
import config

# Load environment variables
load_dotenv()

# Configuration
FILE_SEARCH_STORE_NAME = "hickey-lab-knowledge-base"
MODEL_NAME = "gemini-2.5-flash"

# Use enhanced system prompt from config
SYSTEM_PROMPT = config.ENHANCED_SYSTEM_PROMPT

# --------------------------------------------------------------------------
# Initialize Utility Systems
# --------------------------------------------------------------------------

@st.cache_resource
def get_cost_tracker():
    """Initialize cost tracker (cached)."""
    return CostTracker(log_dir=config.LOG_DIR)


@st.cache_resource
def get_rate_limiter():
    """Initialize rate limiter (cached)."""
    return RateLimiter(
        max_per_hour=config.RATE_LIMIT_PER_HOUR,
        max_per_day=config.RATE_LIMIT_PER_DAY,
        warning_threshold=config.RATE_LIMIT_WARNING_THRESHOLD,
        log_dir=config.LOG_DIR
    )


@st.cache_resource
def get_security_validator():
    """Initialize security validator (cached)."""
    return SecurityValidator(log_dir=config.LOG_DIR)


@st.cache_resource
def get_alert_system():
    """Initialize alert system (cached)."""
    return AlertSystem(
        topic=config.NTFY_TOPIC,
        enabled=config.ALERTS_ENABLED
    )


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


def build_prompt_with_context(new_question: str, history: list) -> str:
    """Build prompt with conversation context."""
    if not history or len(history) == 0:
        return new_question
    
    # Get recent history (last N exchanges)
    # Limit total history to prevent unbounded growth
    max_messages = config.CONVERSATION_HISTORY_LENGTH * 2  # * 2 for user + assistant pairs
    recent = history[-max_messages:] if len(history) > max_messages else history
    
    # Format history
    context_parts = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        # Truncate very long messages to prevent token explosion
        content = msg['content']
        if len(content) > 1000:
            content = content[:1000] + "... [truncated]"
        context_parts.append(f"{role}: {content}")
    
    # Combine with new question
    full_prompt = (
        "Previous conversation:\n" +
        "\n".join(context_parts) +
        f"\n\nCurrent question: {new_question}\n\n" +
        "Please answer the current question, using the conversation context when relevant."
    )
    
    return full_prompt


def get_response(question: str, history: list, session_id: str) -> tuple:
    """
    Generate a response using Gemini with File Search.
    
    Returns:
        Tuple of (response_text, success, error_message, usage_metadata)
    """
    client = get_client()
    store = get_file_search_store()
    cost_tracker = get_cost_tracker()
    
    if not store:
        return (
            "⚠️ File Search store not found. Please set up the knowledge base first.",
            False,
            "store_not_found",
            None
        )
    
    # Build prompt with conversation context
    prompt = build_prompt_with_context(question, history)
    
    start_time = time.time()
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
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
        
        response_time = time.time() - start_time
        
        # Extract token usage
        usage = response.usage_metadata
        
        # Log usage
        cost_tracker.log_usage(
            session_id=session_id,
            question_length=len(question),
            prompt_tokens=usage.prompt_token_count,
            response_tokens=usage.candidates_token_count,
            total_tokens=usage.total_token_count,
            response_time=response_time,
            success=True
        )
        
        return response.text, True, None, usage
        
    except Exception as e:
        response_time = time.time() - start_time
        error_msg = str(e)
        
        # Try to extract usage info even from failed requests
        # Some API errors still consume tokens
        prompt_tokens = 0
        response_tokens = 0
        total_tokens = 0
        
        try:
            if hasattr(e, 'usage_metadata'):
                usage = e.usage_metadata
                prompt_tokens = getattr(usage, 'prompt_token_count', 0)
                response_tokens = getattr(usage, 'candidates_token_count', 0)
                total_tokens = getattr(usage, 'total_token_count', 0)
        except:
            pass  # If we can't get usage, use zeros
        
        # Log failed query
        cost_tracker.log_usage(
            session_id=session_id,
            question_length=len(question),
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            total_tokens=total_tokens,
            response_time=response_time,
            success=False,
            error_msg=error_msg
        )
        
        # Provide user-friendly error messages
        if "quota" in error_msg.lower():
            return "⚠️ Service temporarily unavailable due to API quota limits. Please try again later.", False, error_msg, None
        elif "rate limit" in error_msg.lower():
            return "⚠️ Service is experiencing high demand. Please wait a moment and try again.", False, error_msg, None
        elif "timeout" in error_msg.lower():
            return "⚠️ Request timed out. Please try a shorter question or try again.", False, error_msg, None
        else:
            return f"❌ An error occurred: {error_msg}", False, error_msg, None


def get_indexed_files() -> list[str]:
    """Get list of indexed file names."""
    client = get_client()
    try:
        return [f.display_name for f in client.files.list()]
    except Exception:
        return []


def get_session_id() -> str:
    """Get or create a unique session ID."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


# --------------------------------------------------------------------------
# Streamlit UI
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="Hickey Lab AI Assistant",
    page_icon="🧬",
    layout="centered",
)

# Custom CSS for cleaner look and mobile responsiveness
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
    }
    .main > div {
        padding-top: 2rem;
    }
    /* Mobile responsiveness */
    .stButton button {
        min-height: 44px;
        font-size: 16px;
    }
    .stMarkdown {
        font-size: 16px;
        line-height: 1.6;
    }
    .main .block-container {
        max-width: 100%;
        padding: 1rem;
    }
    @media (max-width: 768px) {
        .stTextInput input {
            font-size: 16px;
        }
    }
    /* Warning banner styling */
    .warning-banner {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.75rem;
        margin-bottom: 1rem;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🧬 Hickey Lab AI Assistant")
st.caption("Ask about our research in spatial omics, multiplexed imaging, and computational biology.")

# Display privacy notice
with st.expander("ℹ️ Privacy & Usage"):
    st.markdown(config.PRIVACY_NOTICE)
    st.markdown(f"""
    **Usage Limits:**
    - {config.RATE_LIMIT_PER_HOUR} questions per hour
    - {config.RATE_LIMIT_PER_DAY} questions per day
    
    These limits help us manage costs and keep the service available for everyone.
    """)

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
    
    # Usage stats (for admin)
    if st.checkbox("📊 Show Usage Stats", value=False):
        cost_tracker = get_cost_tracker()
        today_stats = cost_tracker.get_usage_stats()
        
        st.markdown("### Today's Usage")
        st.metric("Queries", today_stats.get("queries", 0))
        st.metric("Cost", f"${today_stats.get('total_cost', 0):.4f}")
        
        # Monthly stats
        now = datetime.utcnow()
        monthly_stats = cost_tracker.get_monthly_stats(now.year, now.month)
        st.markdown("### This Month")
        st.metric("Queries", monthly_stats.get("queries", 0))
        st.metric("Cost", f"${monthly_stats.get('total_cost', 0):.2f}")


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_times" not in st.session_state:
    st.session_state.query_times = []

# Clean up old query times to prevent unbounded memory growth
# Remove queries older than 24 hours
if st.session_state.query_times:
    cutoff_time = datetime.now() - timedelta(hours=24)
    st.session_state.query_times = [
        t for t in st.session_state.query_times if t > cutoff_time
    ]

# Get session ID
session_id = get_session_id()

# Initialize utility systems
rate_limiter = get_rate_limiter()
security_validator = get_security_validator()
cost_tracker = get_cost_tracker()
alert_system = get_alert_system()

# Check budget limits before allowing queries
within_budget, current_cost = cost_tracker.check_monthly_budget(config.MONTHLY_BUDGET_USD)

if not within_budget:
    st.error(f"""
    🚨 **Monthly Budget Exceeded**
    
    The service has reached its monthly budget of ${config.MONTHLY_BUDGET_USD:.2f} 
    (current: ${current_cost:.2f}).
    
    The service will resume at the start of next month. Thank you for your understanding!
    """)
    st.stop()

# Check daily limits
within_daily, daily_count = cost_tracker.check_daily_limit(config.DAILY_QUERY_LIMIT)

if not within_daily:
    st.warning(f"""
    📅 **Daily Limit Reached**
    
    The service has reached its daily limit of {config.DAILY_QUERY_LIMIT} queries.
    Please come back tomorrow!
    """)
    st.stop()

# Show suggested questions if no messages yet
if len(st.session_state.messages) == 0:
    st.markdown("**💡 Try asking:**")
    cols = st.columns(2)
    for i, suggestion in enumerate(config.SUGGESTED_QUESTIONS):
        if cols[i % 2].button(suggestion, key=f"suggest_{i}", use_container_width=True):
            # Set the suggestion as the next prompt to process
            st.session_state.pending_prompt = suggestion
            st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check for pending prompt from suggestion buttons
pending_prompt = st.session_state.get("pending_prompt", None)
if pending_prompt:
    prompt = pending_prompt
    st.session_state.pending_prompt = None
else:
    # Chat input
    prompt = st.chat_input("Ask about our research...")

if prompt:
    # Security validation
    is_valid, cleaned_input, error_msg = security_validator.validate_input(prompt, session_id)
    
    if not is_valid:
        st.error(error_msg)
        if "suspicious" in error_msg.lower():
            alert_system.alert_suspicious_activity(session_id, "Invalid input detected")
        st.stop()
    
    # Rate limiting check
    allowed, limit_msg, remaining = rate_limiter.check_rate_limit(
        st.session_state.query_times,
        session_id
    )
    
    if not allowed:
        st.error(limit_msg)
        alert_system.alert_rate_limit_hit(session_id, len(st.session_state.query_times), "hourly/daily")
        st.stop()
    
    # Show warning if approaching limit
    if limit_msg:
        st.warning(limit_msg)
    
    # Record query time
    st.session_state.query_times.append(datetime.now())
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": cleaned_input})
    with st.chat_message("user"):
        st.markdown(cleaned_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base..."):
            response_text, success, error, usage = get_response(
                cleaned_input,
                st.session_state.messages[:-1],  # History before current message
                session_id
            )
        st.markdown(response_text)
    
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Check cost thresholds and send alerts if needed
    today_stats = cost_tracker.get_usage_stats()
    if today_stats.get("total_cost", 0) >= config.DAILY_BUDGET_WARNING:
        alert_system.alert_cost_threshold(
            today_stats["total_cost"],
            config.DAILY_BUDGET_WARNING,
            "daily"
        )
