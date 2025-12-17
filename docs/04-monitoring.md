# 04 - Monitoring & Analytics

> **Priority:** 🟡 Medium  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 📊 Monitoring Goals

1. **Operational:** Is the system healthy?
2. **Financial:** What are we spending?
3. **Usage:** How are people using it?
4. **Quality:** Are responses good?

---

## 🔍 Key Metrics

### Operational Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Uptime | 99% | < 95% |
| Response time | < 5s | > 10s |
| Error rate | < 1% | > 5% |
| 503 errors (overload) | < 5% | > 10% |

### Financial Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Daily cost | < $2 | > $5 |
| Monthly cost | < $50 | > $40 (80%) |
| Cost per query | ~$0.0003 | > $0.001 |
| Token usage/day | Track | Spike detection |

### Usage Metrics

| Metric | Purpose |
|--------|---------|
| Queries per day | Understand demand |
| Unique sessions | User count estimate |
| Avg queries/session | Engagement |
| Peak hours | Capacity planning |
| Geographic distribution | Audience understanding |

### Quality Metrics

| Metric | How to Measure |
|--------|----------------|
| User satisfaction | Thumbs up/down buttons |
| Response relevance | Manual review sample |
| Hallucination rate | Spot checks |
| Unanswered questions | Track "I don't know" responses |

---

## 🛠️ Implementation Options

### Option A: Simple Logging (File-Based)

```python
import json
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("logs/queries.jsonl")

def log_query(session_id: str, question: str, response_time: float, success: bool):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id[:8],  # Truncate for privacy
        "question_length": len(question),
        "response_time_ms": int(response_time * 1000),
        "success": success,
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

**Pros:** Simple, no external services  
**Cons:** Not persistent on HuggingFace, no real-time dashboard

### Option B: Google Analytics

Add to Streamlit app:
```python
import streamlit.components.v1 as components

GA_TRACKING_ID = "G-XXXXXXXXXX"

def inject_ga():
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_TRACKING_ID}');
    </script>
    """
    components.html(ga_code, height=0)
```

**Pros:** Free, powerful analytics, no infrastructure  
**Cons:** Limited custom events, privacy concerns

### Option C: PostHog (Recommended)

```python
from posthog import Posthog

posthog = Posthog(
    api_key='your-api-key',
    host='https://app.posthog.com'
)

def track_query(session_id: str, question: str, response_time: float):
    posthog.capture(
        distinct_id=session_id,
        event='query_submitted',
        properties={
            'question_length': len(question),
            'response_time_ms': response_time * 1000,
        }
    )
```

**Pros:** Open-source option, good free tier, custom events  
**Cons:** Requires setup

### Option D: Simple Dashboard (Streamlit)

Create a separate admin page:
```python
# admin_dashboard.py
import streamlit as st
import pandas as pd
from pathlib import Path

st.title("📊 Admin Dashboard")

# Password protection
if st.text_input("Password", type="password") != "your-admin-password":
    st.stop()

# Load and display metrics
if Path("logs/queries.jsonl").exists():
    df = pd.read_json("logs/queries.jsonl", lines=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Queries", len(df))
    col2.metric("Avg Response Time", f"{df['response_time_ms'].mean():.0f}ms")
    col3.metric("Success Rate", f"{df['success'].mean()*100:.1f}%")
    
    st.line_chart(df.set_index('timestamp')['response_time_ms'])
```

---

## 🔔 Alerting

### Alert Channels

| Channel | Use Case |
|---------|----------|
| Email | Daily summaries, budget alerts |
| Slack/Discord | Real-time critical alerts |
| SMS | Emergency only |

### Alert Rules

```yaml
alerts:
  - name: "High Error Rate"
    condition: error_rate > 5%
    window: 15 minutes
    action: email + slack
    
  - name: "Cost Spike"
    condition: daily_cost > $5
    action: email + slack
    
  - name: "Service Down"
    condition: uptime < 95%
    window: 5 minutes
    action: email + slack + sms
```

### Google Cloud Alerts

```bash
# Set up budget alert
gcloud alpha billing budgets create \
  --billing-account=ACCOUNT_ID \
  --display-name="Gemini Daily Alert" \
  --budget-amount=5USD \
  --threshold-rule=percent=0.8,basis=CURRENT_SPEND
```

---

## 📈 Dashboard Design

### Main Dashboard

```
┌─────────────────────────────────────────────────┐
│  Hickey Lab AI Assistant - Monitoring           │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ Queries │  │  Cost   │  │ Errors  │         │
│  │  Today  │  │  Today  │  │  Today  │         │
│  │   127   │  │  $0.04  │  │   2     │         │
│  └─────────┘  └─────────┘  └─────────┘         │
│                                                 │
│  [========== Queries Over Time ==========]     │
│  │    ╭──╮                                     │
│  │   ╭╯  ╰╮    ╭─╮                            │
│  │  ╭╯    ╰────╯ ╰╮                           │
│  │──╯              ╰──                         │
│  └─────────────────────────────────────        │
│                                                 │
│  Top Questions:                                │
│  1. "What does the Hickey Lab do?" (23)       │
│  2. "Tell me about CODEX" (18)                │
│  3. "What is spatial biology?" (15)           │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📋 Implementation Phases

### Phase 1: Basic Logging
- [ ] Add query logging to app
- [ ] Log: timestamp, response time, success/error
- [ ] Daily log rotation

### Phase 2: Cost Tracking
- [ ] Set up Google Cloud budget alerts
- [ ] Track token usage per query
- [ ] Weekly cost reports

### Phase 3: Analytics
- [ ] Choose analytics platform
- [ ] Implement event tracking
- [ ] Create basic dashboard

### Phase 4: Alerting
- [ ] Set up alert channels
- [ ] Define alert rules
- [ ] Test alert pipeline

---

## ❓ Open Questions

1. What analytics platform to use?
2. How much query data should we log (privacy)?
3. Who should receive alerts?
4. Do we need real-time monitoring or daily summaries?
5. Should we track individual questions or just metadata?

---

## 📎 References

- [Streamlit Analytics](https://github.com/jrieke/streamlit-analytics)
- [PostHog](https://posthog.com/)
- [Google Cloud Monitoring](https://cloud.google.com/monitoring)
- [Grafana](https://grafana.com/) (if self-hosting)
