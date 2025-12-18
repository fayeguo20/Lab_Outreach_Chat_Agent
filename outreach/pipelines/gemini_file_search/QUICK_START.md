# Quick Start Guide for HuggingFace Deployment

This is a **5-minute quick start** to get your production-ready chatbot deployed.

---

## 🚀 Step 1: Deploy to HuggingFace (2 minutes)

### If your Space is already set up:

1. Upload these files to your HuggingFace Space:
   - `app.py` (updated)
   - `config.py` (new)
   - `requirements.txt` (updated)
   - `utils/` directory (all files)

2. Your Space will automatically restart and install new dependencies

### If you need to create a new Space:

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose "Streamlit" as SDK
4. Upload all files from `outreach/pipelines/gemini_file_search/`

---

## 🔑 Step 2: Set Environment Variables (1 minute)

1. Go to your Space Settings → Variables and secrets
2. Add these secrets:

| Name | Value | Required? |
|------|-------|-----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ Yes |
| `NTFY_TOPIC` | Your random topic name (e.g., `hickeylab-x9k2m7`) | ⭐ Recommended |

**Finding your Gemini API key:**
- Go to https://aistudio.google.com/app/apikey
- Create or copy your API key

---

## 📱 Step 3: Set Up Notifications (2 minutes) - Optional but Recommended

### Choose your method:

**Option A: Mobile App (Best)**
1. Install ntfy app from App Store or Google Play
2. Open app and tap "Subscribe to topic"
3. Enter your topic name (e.g., `hickeylab-x9k2m7`)
4. Done! You'll get instant push notifications

**Option B: Browser**
1. Go to `https://ntfy.sh/your-topic-name`
2. Click "Subscribe" button
3. Allow browser notifications
4. Done! You'll get browser notifications

### Test it:
```bash
curl -d "Hello from Hickey Lab!" ntfy.sh/your-topic-name
```

You should get a notification immediately!

---

## ✅ Step 4: Test Your Chatbot (2 minutes)

1. Open your HuggingFace Space
2. Wait for it to start (first start takes ~30 seconds)
3. Ask a test question: "What does the Hickey Lab research?"
4. Verify you get a response
5. Check sidebar for "📊 Show Usage Stats" to see it logged

---

## 🎉 You're Done!

Your chatbot now has:
- ✅ Cost tracking and budget protection
- ✅ Rate limiting to prevent abuse
- ✅ Security validation
- ✅ Push notifications (if you set up ntfy.sh)
- ✅ Better responses with conversation context

---

## 🎛️ Customization (Optional)

### To change limits:

Edit `config.py` in your Space:

```python
# Cost limits
MONTHLY_BUDGET_USD = 50.0        # Change to your budget
DAILY_QUERY_LIMIT = 200          # Change to your preference

# Rate limits
RATE_LIMIT_PER_HOUR = 20         # Queries per hour
RATE_LIMIT_PER_DAY = 200         # Queries per day

# Suggested questions
SUGGESTED_QUESTIONS = [
    "Your custom question 1",
    "Your custom question 2",
    # ... add your own
]
```

Save the file and your Space will restart with new settings.

---

## 📊 Monitoring Your Usage

### Quick check:
1. Open your chatbot
2. Click "📊 Show Usage Stats" in sidebar
3. See today's queries and cost

### Get alerts:
- If you set up ntfy.sh, you'll automatically get notified when:
  - Someone hits rate limits
  - Daily cost exceeds $5
  - Monthly budget is approaching
  - Suspicious activity detected

---

## ⚠️ Troubleshooting

### "GEMINI_API_KEY not found"
- Go to Space Settings → Variables and secrets
- Make sure `GEMINI_API_KEY` is added as a **Secret** (not a variable)

### "File Search store not found"
- Your knowledge base needs to be set up first
- Check that `hickey-lab-knowledge-base` exists in your Gemini project

### Notifications not working
- Check you subscribed to the correct topic name
- Try sending a test: `curl -d "test" ntfy.sh/your-topic-name`
- Make sure `NTFY_TOPIC` is set in HuggingFace secrets

### Space keeps restarting
- Check Space logs for errors
- Make sure all files are uploaded correctly
- Verify `requirements.txt` is present

---

## 📚 More Information

- **Detailed technical guide:** See `IMPLEMENTATION_GUIDE.md`
- **Feature explanations:** See `FEATURE_SUMMARY.md`
- **Test modules:** Run `python test_setup.py` locally

---

## 🆘 Need Help?

1. Check the logs in your HuggingFace Space
2. Review `IMPLEMENTATION_GUIDE.md` for detailed instructions
3. Make sure all files were uploaded correctly
4. Verify environment variables are set

---

**That's it! Your production-ready chatbot is live.** 🎊

The implementation handles:
- 💰 Cost protection
- 🛡️ Security
- 📊 Monitoring
- 🔔 Alerts
- 💬 Better conversations

Enjoy your production-ready AI assistant!
