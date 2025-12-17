# 06 - User Experience

> **Priority:** 🟢 Low  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 🎨 Current UI

### What We Have
- Basic Streamlit chat interface
- Title and subtitle
- System message explaining the assistant
- Chat input at bottom
- Message history in session

### Current Limitations
- No mobile optimization
- No conversation persistence
- No suggested questions
- No feedback mechanism
- Basic styling only

---

## 🎯 UX Improvements

### Priority 1: Quick Wins

#### 1.1 Suggested Questions
```python
st.markdown("**Try asking:**")
suggestions = [
    "What does the Hickey Lab research?",
    "Tell me about CODEX technology",
    "What is spatial biology?",
    "Who is Dr. Hickey?",
]

cols = st.columns(2)
for i, suggestion in enumerate(suggestions):
    if cols[i % 2].button(suggestion, key=f"suggest_{i}"):
        # Trigger the question
        st.session_state.messages.append({"role": "user", "content": suggestion})
        st.rerun()
```

#### 1.2 Loading States
```python
with st.spinner("🔍 Searching knowledge base..."):
    response = get_gemini_response(prompt)
```

#### 1.3 Error Messages
```python
# Friendly error messages
ERROR_MESSAGES = {
    "rate_limit": "🕐 You've asked a lot of questions! Please wait a few minutes.",
    "overload": "😅 Our AI is busy right now. Please try again in a moment.",
    "error": "😕 Something went wrong. Please try again.",
}
```

### Priority 2: Enhanced Features

#### 2.1 Thumbs Up/Down Feedback
```python
col1, col2, col3 = st.columns([1, 1, 8])
with col1:
    if st.button("👍", key=f"up_{msg_id}"):
        log_feedback(msg_id, "positive")
with col2:
    if st.button("👎", key=f"down_{msg_id}"):
        log_feedback(msg_id, "negative")
```

#### 2.2 Copy Response Button
```python
import streamlit.components.v1 as components

def copy_button(text: str):
    components.html(f"""
        <button onclick="navigator.clipboard.writeText(`{text}`)">
            📋 Copy
        </button>
    """, height=30)
```

#### 2.3 Dark Mode Support
```python
# In .streamlit/config.toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
```

### Priority 3: Advanced Features

#### 3.1 Conversation History (Persistent)
- Store chat history per session ID
- "Load previous conversation" button
- Clear history option

#### 3.2 Multi-modal Support
- Allow PDF upload for specific questions
- Image support (if relevant)
- Voice input (future)

#### 3.3 Citation Display
```python
# Show which documents were used
with st.expander("📚 Sources"):
    for source in response.sources:
        st.markdown(f"- {source.filename}, page {source.page}")
```

---

## 📱 Mobile Responsiveness

### Current Issues
- Chat input may be hard to tap
- Long responses hard to read
- Buttons too small

### Fixes

```python
# Custom CSS for mobile
st.markdown("""
<style>
    /* Larger touch targets */
    .stButton button {
        min-height: 44px;
        font-size: 16px;
    }
    
    /* Better text readability */
    .stMarkdown {
        font-size: 16px;
        line-height: 1.6;
    }
    
    /* Responsive width */
    .main .block-container {
        max-width: 100%;
        padding: 1rem;
    }
    
    @media (max-width: 768px) {
        .stTextInput input {
            font-size: 16px;  /* Prevents iOS zoom */
        }
    }
</style>
""", unsafe_allow_html=True)
```

---

## ♿ Accessibility

### Current Gaps
- No ARIA labels
- Color contrast may be insufficient
- No keyboard navigation hints

### Improvements Needed
- [ ] Add alt text for any images
- [ ] Ensure color contrast ratio ≥ 4.5:1
- [ ] Support keyboard navigation
- [ ] Screen reader compatibility
- [ ] Clear focus indicators

---

## 💬 Conversation Design

### Personality & Tone

```yaml
Persona: Friendly scientific communicator
Tone: Approachable but accurate
Goals:
  - Make spatial biology accessible
  - Accurately represent lab research
  - Encourage curiosity
  - Know when to say "I don't know"
```

### Response Guidelines

**Do:**
- Explain technical terms
- Use analogies where helpful
- Provide context
- Cite specific papers when relevant

**Don't:**
- Use excessive jargon
- Make up information
- Be condescending
- Provide medical advice

### Error Handling Messages

| Situation | Message |
|-----------|---------|
| No relevant info | "I don't have specific information about that in my knowledge base. You might want to check the lab website or contact the team directly." |
| Off-topic | "I'm specialized in Hickey Lab research and spatial biology. For other topics, I'd recommend [appropriate resource]." |
| Overloaded | "I'm experiencing high demand right now. Please try again in a moment! 🙏" |
| Technical error | "Something unexpected happened. Our team has been notified. Please try again." |

---

## 🎨 Visual Design

### Color Palette
```css
:root {
    --primary: #667eea;      /* Purple-blue */
    --secondary: #764ba2;    /* Purple */
    --success: #48bb78;      /* Green */
    --warning: #ecc94b;      /* Yellow */
    --error: #f56565;        /* Red */
    --text: #2d3748;         /* Dark gray */
    --background: #f7fafc;   /* Light gray */
}
```

### Typography
- Headers: Inter or system font
- Body: 16px minimum
- Line height: 1.6 for readability

### Components
- Rounded corners (8px)
- Subtle shadows
- Consistent spacing (8px grid)

---

## 📊 UX Metrics

### What to Track
- Time to first message
- Messages per session
- Feedback ratio (👍/👎)
- Drop-off points
- Error encounter rate

### Success Criteria
- 80%+ positive feedback
- < 3s response time feel
- < 5% error rate
- Clear path to human help

---

## 📋 Implementation Phases

### Phase 1: Essential Polish
- [ ] Add suggested questions
- [ ] Better loading states
- [ ] Friendly error messages
- [ ] Mobile CSS fixes

### Phase 2: Feedback Loop
- [ ] Thumbs up/down buttons
- [ ] "Was this helpful?" prompt
- [ ] Optional feedback form

### Phase 3: Enhanced UX
- [ ] Dark mode
- [ ] Copy response button
- [ ] Citation/source display
- [ ] Session management

---

## ❓ Open Questions

1. What suggested questions are most helpful?
2. Should we show "typing" indicators?
3. How long should conversation history persist?
4. Do we need user accounts?
5. What accessibility standards must we meet?

---

## 📎 References

- [Streamlit Theming](https://docs.streamlit.io/library/advanced-features/theming)
- [Web Content Accessibility Guidelines](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [Conversation Design Best Practices](https://designguidelines.withgoogle.com/conversation/)
- [Mobile UX Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
