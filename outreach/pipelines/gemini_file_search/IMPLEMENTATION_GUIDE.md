# Production Features Implementation Guide

This document explains what has been implemented for the Hickey Lab AI Assistant and how to configure and use each feature.

---

## 📦 What Has Been Implemented

All the following features from the production roadmap have been implemented:

### ✅ Phase 1: Foundation - Cost & Security Controls (High Priority 🔴)

#### 1. **Cost Management Module** (`utils/cost_tracker.py`)
Tracks API token usage and costs to prevent budget overruns.

**What it does:**
- Extracts token counts from every Gemini API response
- Calculates costs based on Gemini 2.5 Flash pricing ($0.075 per 1M input tokens, $0.30 per 1M output tokens)
- Logs all usage to `logs/usage.jsonl` with timestamps
- Tracks daily and monthly usage statistics
- Enforces budget caps (blocks service when exceeded)
- Generates usage reports

**How to use it:**
1. Set budget limits in `config.py`:
   - `DAILY_QUERY_LIMIT`: Maximum queries per day (default: 200)
   - `MONTHLY_BUDGET_USD`: Monthly budget cap (default: $50)
   - `DAILY_BUDGET_WARNING`: Warning threshold (default: $5)

2. View usage stats in the sidebar by checking "📊 Show Usage Stats"

3. Generate reports manually:
   ```python
   from utils.cost_tracker import CostTracker
   tracker = CostTracker()
   print(tracker.generate_daily_report())
   print(tracker.generate_monthly_report(2024, 12))
   ```

#### 2. **Rate Limiting System** (`utils/rate_limiter.py`)
Prevents abuse through configurable rate limits.

**What it does:**
- Tracks queries per session using sliding time windows
- Enforces hourly limits (default: 20 queries per hour)
- Enforces daily limits (default: 200 queries per 24 hours)
- Shows warnings when approaching limits (at 80% by default)
- Blocks queries when limits exceeded with friendly messages
- Logs rate limit violations

**How to use it:**
1. Configure limits in `config.py`:
   - `RATE_LIMIT_PER_HOUR`: Queries per hour (default: 20)
   - `RATE_LIMIT_PER_DAY`: Queries per day (default: 200)
   - `RATE_LIMIT_WARNING_THRESHOLD`: When to warn (default: 0.8 = 80%)

2. Users will automatically see warnings like:
   - "⚠️ You have 4 questions remaining this hour"
   - "🕐 Rate limit reached! Please wait 15 minutes..."

#### 3. **Security Module** (`utils/security.py`)
Validates and sanitizes user input to prevent attacks.

**What it does:**
- Checks input length (1-2000 characters by default)
- Detects prompt injection attempts ("ignore previous instructions", etc.)
- Blocks suspicious patterns (script tags, template injection, etc.)
- Detects excessive special characters
- Logs all security violations for review

**How to use it:**
1. Configure limits in `config.py`:
   - `MAX_INPUT_LENGTH`: Maximum characters (default: 2000)
   - `MIN_INPUT_LENGTH`: Minimum characters (default: 1)

2. Security is automatic - invalid inputs are rejected with user-friendly messages

3. Review security logs in `logs/security.jsonl` to monitor threats

#### 4. **Alert System** (`utils/alerts.py`)
Sends push notifications for critical events using ntfy.sh.

**What it does:**
- Sends push notifications to your phone/browser via ntfy.sh (free, no signup)
- Alerts for rate limit violations
- Alerts for cost threshold breaches
- Alerts for suspicious activity
- Alerts for error spikes
- Supports priority levels (min, low, default, high, urgent)

**How to set it up:**

1. **Subscribe to notifications:**
   - Option A (Browser): Go to `https://ntfy.sh/YOUR-TOPIC-NAME` and click "Subscribe"
   - Option B (Mobile App):
     - Install ntfy app (iOS/Android)
     - Add subscription with your topic name

2. **Choose a SECURE topic name:**
   - ⚠️ IMPORTANT: Use a random, hard-to-guess name for security!
   - ✅ Good: `hickeylab-alerts-x9k2m7a4`
   - ❌ Bad: `hickeylab-alerts` (anyone can subscribe)

3. **Configure the topic:**
   - Set in `config.py`: `NTFY_TOPIC = "your-topic-name"`
   - Or set environment variable: `NTFY_TOPIC=your-topic-name`

4. **Test it:**
   ```bash
   python -c "from utils.alerts import AlertSystem; AlertSystem().test_alert()"
   ```
   Or:
   ```bash
   curl -d "Test alert" ntfy.sh/your-topic-name
   ```

**What you'll be notified about:**
- ⚠️ User hits rate limit
- 💰 Daily/monthly cost thresholds (80%, 100%)
- 🔍 Suspicious activity detected
- 🚨 Service paused due to budget limits

---

### ✅ Phase 2: Monitoring & Quality (Medium Priority 🟡)

#### 5. **Enhanced Logging**
All queries are logged with metadata for analysis.

**What's logged:**
- Timestamp
- Session ID (truncated for privacy)
- Question length
- Token counts (prompt, response, total)
- Estimated cost
- Response time
- Success/failure status
- Error messages (if any)

**Log files:**
- `logs/usage.jsonl` - All API usage
- `logs/rate_limits.jsonl` - Rate limit violations
- `logs/security.jsonl` - Security violations

#### 6. **Conversation Context**
Maintains context across multiple messages for better responses.

**What it does:**
- Includes last 5 exchanges in each query (configurable)
- Allows follow-up questions to reference previous messages
- Example:
  - User: "What is CODEX?"
  - Assistant: [explains CODEX]
  - User: "How does it compare to IBEX?"
  - Assistant: [compares CODEX (from context) to IBEX]

**How to configure:**
- Adjust `CONVERSATION_HISTORY_LENGTH` in `config.py` (default: 5)

#### 7. **Enhanced System Prompt**
Improved instructions for better response quality.

**What's improved:**
- Conversation context awareness
- Response structure guidelines (2-4 paragraphs for complex topics)
- Specific citation instructions
- Technical term explanation requirements
- Grounding in knowledge base (no hallucinations)

---

### ✅ Phase 3: User Experience (Low Priority 🟢)

#### 8. **Suggested Questions**
Shows starter questions when chat is empty.

**What it does:**
- Displays 4 suggested questions as clickable buttons
- Questions are configured in `config.py`
- Helps new users get started

**How to customize:**
- Edit `SUGGESTED_QUESTIONS` in `config.py`

#### 9. **Privacy Notice**
Displays privacy and usage information.

**What it shows:**
- Data processing information
- Usage limits
- Privacy policy

**How to customize:**
- Edit `PRIVACY_NOTICE` in `config.py`

#### 10. **Usage Statistics Dashboard**
Shows real-time usage stats in sidebar.

**What it shows:**
- Today's query count and cost
- This month's query count and cost
- Optional display (checkbox in sidebar)

#### 11. **Mobile Responsive Design**
Improved CSS for mobile devices.

**What's improved:**
- Touch-friendly button sizes (44px minimum)
- Appropriate font sizes
- No iOS zoom on input focus
- Responsive layout

---

## 🚀 Deployment Instructions

### For HuggingFace Spaces:

1. **Set up secrets:**
   - Go to Space Settings → Variables and secrets
   - Add `GEMINI_API_KEY` as a Secret
   - (Optional) Add `NTFY_TOPIC` for notifications

2. **Upload files:**
   - Upload the entire `outreach/pipelines/gemini_file_search/` directory
   - Ensure all files are included:
     - `app.py`
     - `config.py`
     - `requirements.txt`
     - `utils/` directory with all modules

3. **The app will automatically:**
   - Install dependencies from `requirements.txt`
   - Start the Streamlit app
   - Create `logs/` directory when first query is made

### Environment Variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Your Google Gemini API key |
| `NTFY_TOPIC` | ❌ Optional | Your ntfy.sh topic for push notifications |

### First-Time Setup:

1. **Test the app** with a few queries
2. **Subscribe to notifications** if you set up ntfy.sh
3. **Check logs** in `logs/` directory (if accessible)
4. **Adjust limits** in `config.py` if needed

---

## 📊 Monitoring & Maintenance

### Daily Tasks:
- Check usage stats in the sidebar
- Watch for notification alerts on your phone/browser

### Weekly Tasks:
- Review `logs/usage.jsonl` for usage patterns
- Check `logs/security.jsonl` for any threats
- Adjust rate limits if needed

### Monthly Tasks:
- Generate monthly cost report
- Review budget and adjust if needed
- Update system prompt based on user feedback

### Generating Reports:

```python
from utils.cost_tracker import CostTracker

tracker = CostTracker()

# Daily report
print(tracker.generate_daily_report())

# Monthly report
print(tracker.generate_monthly_report(2024, 12))

# Custom date
from datetime import datetime
print(tracker.generate_daily_report(datetime(2024, 12, 15)))
```

---

## ⚙️ Configuration Reference

All configuration is in `config.py`. Key settings:

### Cost Management:
```python
DAILY_QUERY_LIMIT = 200           # Max queries per day
MONTHLY_BUDGET_USD = 50.0         # Hard budget cap
DAILY_BUDGET_WARNING = 5.0        # Alert threshold
```

### Rate Limiting:
```python
RATE_LIMIT_PER_HOUR = 20          # Queries per hour
RATE_LIMIT_PER_DAY = 200          # Queries per 24 hours
RATE_LIMIT_WARNING_THRESHOLD = 0.8  # Warn at 80%
```

### Security:
```python
MAX_INPUT_LENGTH = 2000           # Max characters
MIN_INPUT_LENGTH = 1              # Min characters
```

### Alerts:
```python
NTFY_TOPIC = ""                   # Your ntfy.sh topic
ALERTS_ENABLED = True             # Enable/disable
```

### Response Quality:
```python
CONVERSATION_HISTORY_LENGTH = 5   # Messages of context
ENHANCED_SYSTEM_PROMPT = "..."   # Full prompt in file
```

### UI/UX:
```python
SUGGESTED_QUESTIONS = [...]       # Starter questions
PRIVACY_NOTICE = "..."           # Privacy text
```

---

## 🔧 Troubleshooting

### Logs not being created:
- Check file permissions
- Ensure `logs/` directory is not in `.gitignore` for deployment
- HuggingFace Spaces may not persist logs across restarts

### Notifications not working:
- Verify `NTFY_TOPIC` is set correctly
- Test with: `curl -d "test" ntfy.sh/your-topic`
- Check you're subscribed to the right topic
- Ensure `ALERTS_ENABLED = True` in config

### Rate limits too strict/lenient:
- Adjust `RATE_LIMIT_PER_HOUR` and `RATE_LIMIT_PER_DAY` in `config.py`
- Changes take effect on app restart

### Budget exceeded too quickly:
- Review `logs/usage.jsonl` for unusual activity
- Check if there's an attack (many rapid queries)
- Adjust `MONTHLY_BUDGET_USD` if legitimate traffic

### Conversation context not working:
- Verify `CONVERSATION_HISTORY_LENGTH > 0`
- Check that messages are being stored in `st.session_state.messages`

---

## 📚 Additional Resources

- **Gemini API Pricing**: https://ai.google.dev/pricing
- **ntfy.sh Documentation**: https://ntfy.sh
- **HuggingFace Spaces**: https://huggingface.co/docs/hub/spaces
- **Streamlit Documentation**: https://docs.streamlit.io

---

## 🎯 What You Need to Do

### Required:
1. ✅ Deploy the updated code to HuggingFace Spaces
2. ✅ Set `GEMINI_API_KEY` secret in HuggingFace
3. ✅ Test with a few queries to verify it works

### Optional but Recommended:
1. 📱 Set up ntfy.sh notifications:
   - Pick a random topic name
   - Subscribe on your phone/browser
   - Set `NTFY_TOPIC` in HuggingFace secrets
   - Test it works

2. ⚙️ Adjust configuration in `config.py`:
   - Set appropriate rate limits
   - Set monthly budget
   - Customize suggested questions

3. 📊 Monitor usage:
   - Check sidebar stats regularly
   - Watch for notification alerts
   - Review logs if accessible

---

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the logs (if accessible)
3. Check HuggingFace Spaces logs for errors
4. Verify environment variables are set correctly

---

**That's it!** All the production-ready features from the roadmap have been implemented. The system is now protected against cost overruns, abuse, and security threats, with monitoring and alerting in place.
