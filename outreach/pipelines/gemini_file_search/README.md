---
title: Hickey Lab AI Assistant
emoji: 🧬
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.52.1
app_file: app.py
pinned: false
---

# Hickey Lab AI Assistant - Production Ready ✨

A **production-ready** Streamlit chatbot powered by **Google Gemini 2.5 Flash** and the **File Search API**.

## 🎯 Features

- ✅ **Cost Management** - Tracks usage and enforces budget limits
- ✅ **Rate Limiting** - Prevents abuse (20 queries/hour per user)
- ✅ **Security** - Input validation and prompt injection protection
- ✅ **Push Notifications** - Get alerted about important events (via ntfy.sh)
- ✅ **Conversation Context** - Remembers previous messages for better responses
- ✅ **Mobile Friendly** - Responsive design for all devices
- ✅ **Usage Statistics** - Real-time monitoring in sidebar

## 🚀 Quick Start (5 minutes)

See **[QUICK_START.md](QUICK_START.md)** for deployment instructions.

**TL;DR:**
1. Upload files to HuggingFace Space
2. Set `GEMINI_API_KEY` secret
3. (Optional) Set `NTFY_TOPIC` for notifications
4. Done!

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[QUICK_START.md](QUICK_START.md)** | 5-minute deployment guide |
| **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** | What each tool does (for non-technical users) |
| **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** | Detailed technical documentation |

## 🧪 Testing

Run the setup test to verify everything works:

```bash
python test_setup.py
```

This tests all modules and configurations.

## 📁 Project Structure

```
gemini_file_search/
├── app.py                    # Main Streamlit app (enhanced)
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── test_setup.py            # Setup verification script
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── cost_tracker.py      # Cost management
│   ├── rate_limiter.py      # Rate limiting
│   ├── security.py          # Security validation
│   └── alerts.py            # Push notifications (ntfy.sh)
└── docs/
    ├── QUICK_START.md       # Quick deployment guide
    ├── FEATURE_SUMMARY.md   # What each feature does
    └── IMPLEMENTATION_GUIDE.md  # Technical details
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Cost limits
MONTHLY_BUDGET_USD = 50.0
DAILY_QUERY_LIMIT = 200

# Rate limits
RATE_LIMIT_PER_HOUR = 20
RATE_LIMIT_PER_DAY = 200

# Suggested questions
SUGGESTED_QUESTIONS = [...]

# And more...
```

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Your Google AI API key from [aistudio.google.com](https://aistudio.google.com) |
| `NTFY_TOPIC` | ⭐ Recommended | Your ntfy.sh topic for push notifications |

## 📊 Monitoring

### In the App:
- Check "📊 Show Usage Stats" in sidebar
- See today's query count and cost
- View monthly totals

### Push Notifications (if enabled):
- Rate limit violations
- Cost threshold alerts
- Security warnings
- Budget exceeded alerts

## 🆘 Troubleshooting

**App won't start:**
- Check logs in HuggingFace Space
- Verify `GEMINI_API_KEY` is set as a Secret
- Make sure all files are uploaded

**Notifications not working:**
- Check `NTFY_TOPIC` is set
- Test with: `curl -d "test" ntfy.sh/your-topic`
- Verify you're subscribed to the correct topic

**Rate limit too strict:**
- Edit `RATE_LIMIT_PER_HOUR` in `config.py`
- Default is 20 queries/hour

See **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** for more troubleshooting.

## 💡 What's New

This is an upgraded version with production features:
- Cost tracking prevents surprise bills
- Rate limiting prevents abuse
- Security validation blocks attacks
- Push notifications keep you informed
- Conversation context improves responses

See **[FEATURE_SUMMARY.md](FEATURE_SUMMARY.md)** for detailed explanations.

## 🔗 Embedding in Google Sites

Once deployed, you'll get a public URL. To add to Google Sites:

1. **Simple Link (Always works):**
   - Add a button: "Chat with our AI Assistant →"
   - Link to your HuggingFace Space URL

2. **Embed (HuggingFace Spaces):**
   - In Google Sites: Insert → Embed → By URL
   - Paste your Space URL
   - Adjust size as needed

## 📈 Cost Estimates

Based on Gemini 2.5 Flash pricing:
- ~$0.0003 per query (average)
- 100 queries = $0.03
- 1,000 queries = $0.30
- 10,000 queries = $3.00

Default monthly cap: $50 (adjustable in config)

## 🤝 Support

For issues or questions:
1. Check the documentation files
2. Review HuggingFace Space logs
3. Run `python test_setup.py` to verify setup
4. Check that environment variables are set correctly

---

**Production ready and deployed in minutes!** 🚀
