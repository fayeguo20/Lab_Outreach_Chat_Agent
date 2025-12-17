# 01 - Cost Management

> **Priority:** 🔴 High  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 📊 Current Cost Structure

### Gemini API Pricing (as of Dec 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Free Tier |
|-------|----------------------|------------------------|-----------|
| Gemini 2.5 Flash | $0.075 | $0.30 | 500 req/day |
| Gemini 2.0 Flash | $0.10 | $0.40 | 1,500 req/day |
| Gemini 1.5 Pro | $1.25 | $5.00 | 50 req/day |

### File Search API Costs
- **Storage:** First 1GB free, then $0.10/GB/day
- **Queries:** Included in model token costs
- **Current storage:** ~92MB (within free tier)

---

## 💰 Cost Estimation

### Per-Query Estimate (Gemini 2.5 Flash)

| Component | Tokens | Cost |
|-----------|--------|------|
| System prompt | ~200 | $0.000015 |
| User question | ~50 | $0.0000038 |
| Retrieved context | ~2,000 | $0.00015 |
| Response | ~500 | $0.00015 |
| **Total per query** | ~2,750 | **~$0.0003** |

### Monthly Projections

| Usage Level | Queries/Day | Monthly Cost |
|-------------|-------------|--------------|
| Light (testing) | 50 | ~$0.45 |
| Moderate | 200 | ~$1.80 |
| Heavy | 1,000 | ~$9.00 |
| Viral spike | 10,000 | ~$90.00 |

---

## 🎯 Budget Limits

### Recommended Settings

```yaml
Monthly Budget Cap: $50
Daily Budget Cap: $5
Alert Threshold: 80% of cap
Emergency Shutoff: 100% of cap
```

### Implementation Options

1. **Google Cloud Budget Alerts**
   - Set up in Google Cloud Console
   - Email notifications at thresholds
   - Can't auto-shutoff API

2. **Application-Level Controls**
   - Track queries in database
   - Check against daily/monthly limits
   - Return friendly error when exceeded

3. **Gemini API Key Restrictions**
   - Create project-specific key
   - Set quota limits per key

---

## 🛠️ Implementation Tasks

### Phase 1: Visibility
- [ ] Set up Google Cloud billing alerts
- [ ] Add query logging to track usage
- [ ] Create dashboard for cost monitoring

### Phase 2: Soft Limits
- [ ] Implement daily query counter
- [ ] Add warning messages at 80% threshold
- [ ] Email alerts to admin

### Phase 3: Hard Limits
- [ ] Auto-disable at budget cap
- [ ] Graceful error message to users
- [ ] Admin override capability

---

## 📝 Code Snippets

### Query Counter (Conceptual)

```python
# Store in database or file
def check_budget():
    today = datetime.now().date()
    query_count = get_query_count(today)
    
    if query_count >= DAILY_LIMIT:
        return False, "Daily limit reached. Please try again tomorrow."
    
    if get_monthly_cost() >= MONTHLY_BUDGET:
        return False, "Monthly budget exceeded. Service paused."
    
    return True, None

def log_query(user_session, tokens_used):
    # Log for cost tracking
    save_to_db({
        "timestamp": datetime.now(),
        "session": user_session,
        "tokens": tokens_used,
        "estimated_cost": calculate_cost(tokens_used)
    })
```

### Google Cloud Budget Alert Setup

```bash
# Via gcloud CLI
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Gemini API Budget" \
  --budget-amount=50USD \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.8 \
  --threshold-rule=percent=1.0
```

---

## 🚨 Emergency Procedures

### If costs spike unexpectedly:

1. **Immediate:** Disable API key in Google Cloud Console
2. **Investigate:** Check logs for abuse patterns
3. **Mitigate:** Implement rate limiting before re-enabling
4. **Report:** Document incident and update limits

### Contact Points
- Google Cloud Support: [console.cloud.google.com/support](https://console.cloud.google.com/support)
- Billing inquiries: Via Cloud Console

---

## � Token Usage Tracking

### Can We See Exact Token Counts?

**Yes!** The Gemini API returns token usage in the response metadata.

### Extracting Token Counts from Response

```python
from google import genai

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_question,
    config=config
)

# Access token usage from response
usage = response.usage_metadata
print(f"Prompt tokens: {usage.prompt_token_count}")
print(f"Response tokens: {usage.candidates_token_count}")
print(f"Total tokens: {usage.total_token_count}")

# Calculate cost
INPUT_COST_PER_1M = 0.075  # Gemini 2.5 Flash
OUTPUT_COST_PER_1M = 0.30

input_cost = (usage.prompt_token_count / 1_000_000) * INPUT_COST_PER_1M
output_cost = (usage.candidates_token_count / 1_000_000) * OUTPUT_COST_PER_1M
total_cost = input_cost + output_cost

print(f"Query cost: ${total_cost:.6f}")
```

### Token Breakdown by Component

| Component | What It Includes |
|-----------|------------------|
| `prompt_token_count` | System prompt + user question + retrieved context (File Search) |
| `candidates_token_count` | Model's response |
| `total_token_count` | Sum of all tokens |

### Logging Implementation

```python
import json
from datetime import datetime

def log_usage(session_id: str, question: str, response, log_file="logs/usage.jsonl"):
    usage = response.usage_metadata
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id[:8],  # Truncated for privacy
        "question_length": len(question),
        "prompt_tokens": usage.prompt_token_count,
        "response_tokens": usage.candidates_token_count,
        "total_tokens": usage.total_token_count,
        "estimated_cost_usd": calculate_cost(usage),
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

### What You CAN'T See (Limitations)

- ❌ Exact breakdown of File Search retrieval tokens vs system prompt
- ❌ Which specific documents were retrieved (not in standard response)
- ❌ Token costs for failed/error requests

### Daily Usage Report Script

```python
import json
from collections import defaultdict
from datetime import datetime

def daily_report(log_file="logs/usage.jsonl"):
    today = datetime.utcnow().date().isoformat()
    daily_stats = defaultdict(int)
    
    with open(log_file) as f:
        for line in f:
            entry = json.loads(line)
            if entry["timestamp"].startswith(today):
                daily_stats["queries"] += 1
                daily_stats["prompt_tokens"] += entry["prompt_tokens"]
                daily_stats["response_tokens"] += entry["response_tokens"]
                daily_stats["total_cost"] += entry["estimated_cost_usd"]
    
    print(f"=== Daily Report: {today} ===")
    print(f"Queries: {daily_stats['queries']}")
    print(f"Prompt tokens: {daily_stats['prompt_tokens']:,}")
    print(f"Response tokens: {daily_stats['response_tokens']:,}")
    print(f"Total cost: ${daily_stats['total_cost']:.4f}")
```

---

## 📊 Monitoring Dashboard (Future)

Track these metrics:
- [ ] Queries per hour/day/month
- [ ] Token usage breakdown (prompt vs response)
- [ ] Cost by time period
- [ ] Cost per unique user
- [ ] Trend analysis
- [ ] Average tokens per query

---

## ❓ Open Questions

1. What's the acceptable monthly budget?
2. Should we implement user authentication to track per-user costs?
3. Do we want a freemium model (X free queries, then rate limit)?
4. Should heavy users be redirected to contact the lab directly?

---

## 📎 References

- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Google Cloud Budgets](https://cloud.google.com/billing/docs/how-to/budgets)
- [Token Counting Guide](https://ai.google.dev/gemini-api/docs/tokens)
