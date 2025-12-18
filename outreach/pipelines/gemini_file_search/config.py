"""
Configuration Module
====================
Central configuration for all safety features.

Adjust these values based on your needs and budget.
"""

# ============================================================================
# Cost Management Settings
# ============================================================================

# Maximum queries per day (soft limit)
DAILY_QUERY_LIMIT = 200

# Monthly budget in USD (hard limit - service pauses at this threshold)
MONTHLY_BUDGET_USD = 50.0

# Daily budget threshold for warnings (in USD)
DAILY_BUDGET_WARNING = 5.0

# ============================================================================
# Rate Limiting Settings
# ============================================================================

# Queries per session per hour (primary limit)
RATE_LIMIT_PER_HOUR = 20

# Queries per session per 24 hours
RATE_LIMIT_PER_DAY = 200

# At what percentage to show warning (0.8 = warn at 80% usage)
RATE_LIMIT_WARNING_THRESHOLD = 0.8

# ============================================================================
# Security Settings
# ============================================================================

# Maximum input length (characters)
MAX_INPUT_LENGTH = 2000

# Minimum input length (characters)
MIN_INPUT_LENGTH = 1

# ============================================================================
# Alert System Settings (ntfy.sh)
# ============================================================================

# Your private ntfy.sh topic name
# Subscribe at: https://ntfy.sh/YOUR-TOPIC-NAME
# IMPORTANT: Use a random, hard-to-guess name for security!
# Example: "hickeylab-alerts-x9k2m7" (NOT "hickeylab-alerts")
NTFY_TOPIC = ""  # Set this or use NTFY_TOPIC environment variable

# Enable/disable alerts (useful for development)
ALERTS_ENABLED = True

# ============================================================================
# Response Quality Settings
# ============================================================================

# Number of previous messages to include for context
CONVERSATION_HISTORY_LENGTH = 5

# Enhanced system prompt with quality guidelines
ENHANCED_SYSTEM_PROMPT = """You are a warm, caring assistant for anyone curious about the Hickey Lab at Duke University.
Explain spatial omics and our research in friendly, plain language while staying accurate.
Use the uploaded documents to ground your answers. If the documents don't contain relevant information, 
gently say you don't have that info yet and invite another question.

CONVERSATION GUIDELINES:
- Reference previous messages when answering follow-up questions
- If the user says "it" or "that", infer from context what they mean
- If a question is ambiguous, ask for clarification
- Connect related topics across the conversation

RESPONSE QUALITY:
- Provide detailed, substantive answers (2-4 paragraphs for complex topics)
- Start with a direct answer, then provide context and details
- Use specific examples from the lab's research when possible
- Explain technical terms in accessible language
- If citing a paper, mention the key finding, not just the title

STRUCTURE:
- For complex topics, use bullet points or numbered lists when helpful
- Break down multi-part questions into clear sections
- End with an invitation for follow-up questions when appropriate

GROUNDING:
- Only answer based on information in your knowledge base
- If information isn't available, say "I don't have specific information about that in my knowledge base"
- Never make up citations or research claims
- When answering, be specific about which paper or document the information comes from
"""

# ============================================================================
# UI/UX Settings
# ============================================================================

# Suggested starter questions for users
SUGGESTED_QUESTIONS = [
    "What does the Hickey Lab research?",
    "Tell me about CODEX technology",
    "What is spatial biology?",
    "How does CODEX compare to IBEX?",
]

# Privacy notice to display to users
PRIVACY_NOTICE = """**Privacy Notice:** Questions are processed by Google's Gemini AI. 
No personal data is stored. Conversations are not saved after you close the page."""

# ============================================================================
# Logging Settings
# ============================================================================

# Directory for all logs
LOG_DIR = "logs"

# Enable detailed logging (includes query content in logs - privacy concern)
DETAILED_LOGGING = False  # Set to False in production for privacy
