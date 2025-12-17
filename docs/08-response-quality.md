# 08 - Response Quality & Conversation Context

> **Priority:** 🟡 Medium  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 🎯 Goals

1. Maintain conversation context across messages
2. Generate more robust, detailed responses
3. Handle follow-up questions naturally
4. Avoid hallucinations and stay grounded in knowledge base

---

## 💬 Conversation Context

### The Problem

Currently, each query is independent. User asks:
1. "What is CODEX?" → Good answer
2. "How does it compare to IBEX?" → ❌ No context, doesn't know "it" = CODEX

### Solution: Feed Conversation History

**Yes, the standard approach is to include previous messages in each query.** This is how ChatGPT and other assistants work.

```python
def build_prompt_with_history(
    conversation_history: list[dict],
    new_question: str,
    max_history: int = 10
) -> str:
    """
    Build a prompt that includes conversation context.
    
    conversation_history: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    
    # Limit history to prevent token explosion
    recent_history = conversation_history[-max_history:]
    
    # Format conversation
    history_text = ""
    for msg in recent_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n\n"
    
    # Combine with new question
    full_prompt = f"""Previous conversation:
{history_text}

Current question: {new_question}

Please answer the current question, using the conversation context when relevant."""
    
    return full_prompt
```

### Token Cost of Conversation History

| History Length | Extra Tokens | Extra Cost/Query |
|----------------|--------------|------------------|
| Last 2 exchanges | ~500 | ~$0.00004 |
| Last 5 exchanges | ~1,500 | ~$0.00011 |
| Last 10 exchanges | ~3,000 | ~$0.00023 |

**Recommendation:** Keep last 5-10 exchanges. Cost is minimal (~$0.0001 per query extra).

### Implementation in Streamlit

```python
# Already tracking in session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# When user sends message
def get_response_with_context(new_question: str) -> str:
    # Build context from history
    history = st.session_state.messages[-10:]  # Last 10 messages
    
    # Option 1: Simple concatenation
    context_prompt = build_prompt_with_history(history, new_question)
    
    # Send to Gemini with File Search
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=context_prompt,
        config=config_with_file_search
    )
    
    return response.text
```

---

## 🔄 Query Enhancement Options

### Option 1: Prompt Engineering (Recommended ✅)

**No extra LLM call needed.** Add instructions to your system prompt.

```python
SYSTEM_PROMPT = """You are the Hickey Lab AI Assistant, an expert in spatial biology and the lab's research.

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
- For complex topics, use bullet points or numbered lists
- Break down multi-part questions into clear sections
- End with an invitation for follow-up questions when appropriate

GROUNDING:
- Only answer based on information in your knowledge base
- If information isn't available, say "I don't have specific information about that in my knowledge base"
- Never make up citations or research claims
"""
```

**Pros:** Zero extra cost, no latency  
**Cons:** Limited by model's ability to follow instructions

### Option 2: Query Rewriting (Optional)

Use a lightweight LLM call to improve the question before RAG.

```python
def rewrite_query(user_question: str, conversation_history: list) -> str:
    """
    Rewrite a follow-up question to be standalone.
    
    Example:
    - History: "What is CODEX?"
    - Follow-up: "How does it work?"
    - Rewritten: "How does CODEX technology work?"
    """
    
    rewrite_prompt = f"""Given this conversation:
{format_history(conversation_history)}

Rewrite this follow-up question to be standalone and specific:
"{user_question}"

Return ONLY the rewritten question, nothing else."""

    # Use a fast/cheap model for this
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # Faster, cheaper
        contents=rewrite_prompt
    )
    
    return response.text.strip()
```

**When to use:**
- Complex multi-turn conversations
- When RAG retrieval quality suffers with vague queries
- High-stakes applications where precision matters

**Pros:** Better RAG retrieval for follow-ups  
**Cons:** +1 API call, ~100-200ms latency, ~$0.00005 extra cost

### Option 3: Hybrid Approach

Only rewrite when needed:

```python
def needs_rewriting(question: str) -> bool:
    """Detect if question needs context expansion."""
    
    vague_indicators = [
        r"\b(it|this|that|these|those)\b",  # Pronouns
        r"\b(the same|similar|different|compare)\b",  # Comparisons
        r"\b(more|also|another|other)\b",  # Continuations
        r"^(and|but|so|why|how)\b",  # Sentence starters
    ]
    
    for pattern in vague_indicators:
        if re.search(pattern, question, re.IGNORECASE):
            return True
    return False

def smart_query(question: str, history: list) -> str:
    if needs_rewriting(question) and len(history) > 0:
        return rewrite_query(question, history)
    return question
```

---

## 📝 Prompting Framework for Better Responses

### The CRAFT Framework

Add this to your system prompt or wrap user queries:

```
C - Context: What background does the user need?
R - Relevance: How does this relate to Hickey Lab specifically?
A - Accuracy: Ground in knowledge base, cite sources
F - Format: Structure for readability
T - Tone: Accessible but scientifically accurate
```

### Query Wrapper Template

```python
def enhance_query(user_question: str, conversation_history: list) -> str:
    """Wrap user query with instructions for better responses."""
    
    history_context = ""
    if conversation_history:
        last_exchange = conversation_history[-2:]  # Just last Q&A
        history_context = f"""
Recent context:
{format_history(last_exchange)}
"""
    
    enhanced = f"""{history_context}
User's question: {user_question}

Please provide a comprehensive answer that:
1. Directly addresses the question
2. Provides relevant context from Hickey Lab research
3. Explains any technical terms
4. Uses specific examples when available
5. Is 2-4 paragraphs for substantive topics (shorter for simple questions)
"""
    
    return enhanced
```

### Response Quality Checklist

Good responses should:
- [ ] Directly answer the question in first sentence
- [ ] Provide 2-4 paragraphs for complex topics
- [ ] Reference specific lab research/papers
- [ ] Explain technical terms
- [ ] Acknowledge limitations ("I don't have info on X")
- [ ] Invite follow-up questions

---

## 🎚️ Response Length Control

### Dynamic Length Based on Question Type

```python
def get_response_instructions(question: str) -> str:
    """Add length guidance based on question type."""
    
    # Simple factual questions
    if re.match(r"^(what is|who is|when did|where)", question, re.I):
        return "Provide a concise answer (1-2 paragraphs)."
    
    # Explanation questions
    if re.match(r"^(how does|why|explain|describe)", question, re.I):
        return "Provide a detailed explanation (2-4 paragraphs) with examples."
    
    # Comparison questions
    if re.search(r"(compare|difference|versus|vs)", question, re.I):
        return "Compare systematically, using a structured format. Include key similarities and differences."
    
    # Default
    return "Provide an appropriately detailed response."
```

---

## 🧪 Testing Response Quality

### Test Questions for QA

```markdown
## Factual (should be concise)
- "Who is Dr. Hickey?"
- "What year was the CODEX paper published?"

## Explanatory (should be detailed)
- "How does CODEX technology work?"
- "Explain the significance of spatial biology"

## Follow-up (should use context)
- Q1: "What is CODEX?"
- Q2: "How does it compare to IBEX?"
- Q2 should reference CODEX from Q1

## Edge cases
- "Tell me everything" (should scope to knowledge base)
- "What's the weather?" (should redirect)
- Vague: "More info" (should ask for clarification)
```

### Quality Metrics

| Metric | How to Measure | Target |
|--------|----------------|--------|
| Relevance | Manual review | 90%+ on-topic |
| Accuracy | Fact-check vs papers | 95%+ accurate |
| Completeness | Did it fully answer? | 85%+ |
| Groundedness | Cites real sources | 100% (no hallucinations) |
| Context usage | Follow-ups work | 90%+ |

---

## 🏗️ Implementation Plan

### Phase 1: Conversation Context (Quick Win)
- [ ] Include last 5-10 messages in each query
- [ ] Update system prompt with context instructions
- [ ] Test with follow-up questions

### Phase 2: Prompt Engineering
- [ ] Implement enhanced system prompt
- [ ] Add response length guidance
- [ ] Test and iterate on quality

### Phase 3: Optional Enhancements
- [ ] Consider query rewriting for complex cases
- [ ] Add quality logging for review
- [ ] Implement user feedback on responses

---

## 💰 Cost Impact

| Enhancement | Extra Cost/Query | Latency |
|-------------|------------------|---------|
| Conversation history (5 msgs) | ~$0.0001 | +0ms |
| Enhanced system prompt | ~$0.00002 | +0ms |
| Query rewriting | ~$0.00005 | +100-200ms |
| **Total (without rewriting)** | **~$0.0001** | **+0ms** |

**Recommendation:** Start with conversation history + prompt engineering. Add query rewriting only if needed.

---

## ❓ Open Questions

1. How many messages of history to keep? (Recommend: 5-10)
2. Should we summarize long conversations instead of full history?
3. Do we want user-adjustable verbosity?
4. Should responses include source citations?

---

## 📎 References

- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Gemini System Instructions](https://ai.google.dev/gemini-api/docs/system-instructions)
- [RAG Best Practices](https://docs.llamaindex.ai/en/stable/optimizing/production_rag/)
