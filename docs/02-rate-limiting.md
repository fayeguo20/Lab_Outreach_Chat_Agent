# 02 - Rate Limiting & Abuse Prevention

> **Priority:** 🔴 High  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 🎯 Goals

1. Prevent automated abuse (bots, scrapers)
2. Ensure fair usage across users
3. Protect against cost spikes
4. Maintain service availability

---

## 🚦 Rate Limiting Strategy

### Recommended Limits (Soft)

| Scope | Limit | Window | Rationale |
|-------|-------|--------|-----------|
| Per session | 20 queries | 1 hour | Normal conversation |
| Per IP | 50 queries | 1 hour | Multiple sessions |
| Per IP | 200 queries | 24 hours | Daily cap |
| Global | 1,000 queries | 1 hour | Cost protection |

### Hard Limits (Circuit Breakers)

| Scope | Hard Limit | Window | Action |
|-------|------------|--------|--------|
| Per user/session | 30 queries | 1 hour | Block + notify |
| Per IP | 100 queries | 1 hour | Block IP + notify |
| Global hourly | 500 queries | 1 hour | **Service pause** + urgent notify |
| Global daily | 2,000 queries | 24 hours | **Service pause** + urgent notify |

### Hard Limit Triggers

When hard limits are hit:
1. Immediately block further requests
2. Send push notification via ntfy.sh
3. Log incident for review
4. Auto-recover after window expires (or manual override)

### User Experience

```
Query 1-15:  Normal response
Query 16-18: Warning banner "You have X queries remaining"
Query 19:    Final warning
Query 20:    Rate limit message with retry time
```

---

## 🛡️ Abuse Prevention Layers

### Layer 1: Client-Side (Deterrence)
- Visible rate limit counter
- Delay between submissions (debounce)
- Session-based tracking

### Layer 2: Application-Level
- Server-side rate limiting
- Session validation
- Input length limits

### Layer 3: Infrastructure
- IP-based throttling
- Geographic restrictions (optional)
- DDoS protection (HuggingFace provides basic)

### Layer 4: Detection & Response
- Anomaly detection
- Pattern recognition
- Manual review queue

---

## 🔍 Abuse Patterns to Detect

### Automated Attacks
| Pattern | Indicator | Response |
|---------|-----------|----------|
| Bot scraping | High frequency, sequential queries | Block IP |
| Prompt injection | Special characters, system prompts | Sanitize + log |
| Data extraction | Queries trying to dump knowledge base | Log + review |
| Spam | Repeated identical queries | Rate limit |

### Suspicious Behavior
- Queries containing code/scripts
- Attempts to change assistant persona
- Requests for harmful content
- Unusually long inputs

---

## 🛠️ Implementation Options

### Option A: Simple (Streamlit Session State)

```python
import streamlit as st
from datetime import datetime, timedelta

MAX_QUERIES_PER_HOUR = 20

def check_rate_limit():
    now = datetime.now()
    
    # Initialize session tracking
    if "query_times" not in st.session_state:
        st.session_state.query_times = []
    
    # Remove queries older than 1 hour
    st.session_state.query_times = [
        t for t in st.session_state.query_times 
        if now - t < timedelta(hours=1)
    ]
    
    # Check limit
    if len(st.session_state.query_times) >= MAX_QUERIES_PER_HOUR:
        oldest = min(st.session_state.query_times)
        retry_after = oldest + timedelta(hours=1) - now
        return False, f"Rate limit reached. Try again in {retry_after.seconds // 60} minutes."
    
    return True, len(st.session_state.query_times)

def record_query():
    st.session_state.query_times.append(datetime.now())
```

**Pros:** Simple, no external dependencies  
**Cons:** Resets on page refresh, per-session only

### Option B: Persistent (Redis/Database)

```python
import redis
from datetime import datetime

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_rate_limit(identifier: str, limit: int = 20, window: int = 3600):
    """
    identifier: IP address or session ID
    limit: max requests
    window: time window in seconds
    """
    key = f"ratelimit:{identifier}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return True, limit - 1
    
    if int(current) >= limit:
        ttl = redis_client.ttl(key)
        return False, f"Rate limited. Retry in {ttl // 60} minutes."
    
    redis_client.incr(key)
    return True, limit - int(current) - 1
```

**Pros:** Persistent, IP-based, scalable  
**Cons:** Requires Redis setup

### Option C: Third-Party Service

- **Cloudflare Rate Limiting** - If using custom domain
- **Upstash Redis** - Serverless Redis (free tier)
- **HuggingFace Pro** - Better infrastructure

---

## 🧹 Input Sanitization

### Checks to Implement

```python
def sanitize_input(user_input: str) -> tuple[bool, str]:
    # Length check
    if len(user_input) > 2000:
        return False, "Question too long. Please keep under 2000 characters."
    
    if len(user_input) < 3:
        return False, "Question too short."
    
    # Suspicious patterns
    suspicious_patterns = [
        r"ignore.*instructions",
        r"system.*prompt",
        r"you are now",
        r"pretend to be",
        r"<script>",
        r"{{.*}}",
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            log_suspicious_query(user_input)
            return False, "Invalid query detected."
    
    return True, user_input.strip()
```

---

## � Push Notifications via ntfy.sh

### What is ntfy.sh?
- Free, open-source push notification service
- No app needed (or use Android/iOS app)
- Simple HTTP POST to send notifications
- Self-hostable if needed

### Setup

1. **Subscribe to your topic** (on phone or browser):
   - Go to: `https://ntfy.sh/hickeylab-alerts` (choose your own topic name)
   - Or install ntfy app and subscribe to `hickeylab-alerts`

2. **Test notification**:
   ```bash
   curl -d "Test alert from Hickey Lab Assistant" ntfy.sh/hickeylab-alerts
   ```

### Implementation

```python
import requests
from datetime import datetime

NTFY_TOPIC = "hickeylab-alerts"  # Change to your private topic
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

def send_alert(title: str, message: str, priority: str = "default", tags: list = None):
    """
    Send push notification via ntfy.sh
    
    priority: "min", "low", "default", "high", "urgent"
    tags: emoji tags like ["warning", "rotating_light"]
    """
    headers = {
        "Title": title,
        "Priority": priority,
    }
    if tags:
        headers["Tags"] = ",".join(tags)
    
    try:
        requests.post(NTFY_URL, data=message, headers=headers, timeout=10)
    except Exception as e:
        print(f"Failed to send notification: {e}")

# Example usage
def alert_rate_limit_hit(user_id: str, count: int):
    send_alert(
        title="⚠️ Rate Limit Hit",
        message=f"User {user_id[:8]} hit rate limit ({count} queries)",
        priority="high",
        tags=["warning"]
    )

def alert_global_limit_hit(hourly_count: int):
    send_alert(
        title="🚨 GLOBAL LIMIT - Service Paused",
        message=f"Global hourly limit reached: {hourly_count} queries. Service auto-paused.",
        priority="urgent",
        tags=["rotating_light", "stop_sign"]
    )

def alert_suspicious_activity(user_id: str, reason: str):
    send_alert(
        title="🔍 Suspicious Activity",
        message=f"User {user_id[:8]}: {reason}",
        priority="high",
        tags=["mag", "warning"]
    )
```

### Alert Triggers

| Event | Priority | Notification |
|-------|----------|-------------|
| 80% of hourly limit | `default` | "Approaching hourly limit" |
| User hard limit hit | `high` | "User X blocked" |
| Global limit hit | `urgent` | "🚨 SERVICE PAUSED" |
| Suspicious pattern | `high` | "Potential abuse detected" |
| Daily cost > $3 | `high` | "Daily cost alert" |

### Privacy Note
- Use a **private/random topic name** (not easily guessable)
- Example: `hickeylab-alerts-a7x9k2m` instead of `hickeylab-alerts`
- Or self-host ntfy for full control

---

## 🚨 Response to Abuse

### Automated Responses

| Severity | Trigger | Action |
|----------|---------|--------|
| Low | 80% of rate limit | Warning message |
| Medium | Rate limit hit | Temporary block (1 hour) + ntfy alert |
| High | Repeated violations | Extended block (24 hours) + ntfy alert |
| Critical | Attack pattern | Permanent block + urgent ntfy alert |

### Manual Review Queue

Log these for human review:
- Blocked queries
- Sanitization failures
- Repeated rate limit hits
- Unusual patterns

---

## 📊 Metrics to Track

- [ ] Queries per IP per hour
- [ ] Rate limit triggers per day
- [ ] Blocked query count
- [ ] Sanitization failures
- [ ] Geographic distribution
- [ ] Peak usage times

---

## ❓ Open Questions

1. Should we require any form of authentication?
2. What's the right balance between security and friction?
3. Should we implement CAPTCHA? When?
4. Do we want to whitelist certain IPs (lab members)?
5. How do we handle legitimate heavy users?

---

## 🔄 Rollout Plan

### Week 1: Basic Protection
- [ ] Session-based rate limiting
- [ ] Input length limits
- [ ] Basic sanitization

### Week 2: Enhanced Protection
- [ ] IP-based tracking (if feasible)
- [ ] Suspicious pattern detection
- [ ] Logging infrastructure

### Week 3: Monitoring
- [ ] Dashboard for abuse metrics
- [ ] Alert system
- [ ] Review queue

---

## 📎 References

- [OWASP Rate Limiting](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Redis Rate Limiting Patterns](https://redis.io/commands/incr/#pattern-rate-limiter)
