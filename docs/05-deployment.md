# 05 - Deployment & Infrastructure

> **Priority:** 🟡 Medium  
> **Status:** Planning  
> **Last Updated:** December 17, 2025

---

## 🏗️ Current Setup

| Component | Current | Notes |
|-----------|---------|-------|
| **Hosting** | HuggingFace Spaces (Free) | Sleeps after 15min inactivity |
| **Framework** | Streamlit | Simple, but limited |
| **Backend** | Gemini File Search | Google-managed |
| **Storage** | Google File Search Store | ~92MB indexed |
| **Domain** | `*.hf.space` | No custom domain (free tier) |

---

## 🎯 Deployment Options

### Option A: HuggingFace Spaces (Current)

**Free Tier:**
- ✅ Free hosting
- ✅ Easy deployment
- ✅ Git-based updates
- ❌ Sleeps after inactivity
- ❌ Limited resources (2 vCPU, 16GB RAM)
- ❌ No custom domain

**Pro Tier ($9/month):**
- ✅ No sleep
- ✅ More resources
- ✅ Custom domain possible
- ✅ Private spaces

### Option B: Streamlit Cloud

**Free Tier:**
- ✅ No sleep (stays awake)
- ✅ GitHub integration
- ✅ Easy secrets management
- ❌ 1GB memory limit
- ❌ No custom domain

**Pros:** Better uptime than HuggingFace free  
**Cons:** Resource limits

### Option C: Self-Hosted (Railway/Render/Fly.io)

**Railway (~$5-20/month):**
```yaml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT"
```

**Render (~$7/month):**
```yaml
# render.yaml
services:
  - type: web
    name: hickey-lab-assistant
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT
```

**Pros:** More control, custom domains, no sleep  
**Cons:** Costs money, more setup

### Option D: Cloud Run (Google Cloud)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

**Pros:** Scales to zero, pay-per-use, custom domain  
**Cons:** More complex setup, cold starts

---

## 📊 Comparison Matrix

| Feature | HF Free | HF Pro | Streamlit | Railway | Cloud Run |
|---------|---------|--------|-----------|---------|-----------|
| **Cost/month** | $0 | $9 | $0 | ~$5 | ~$5 |
| **Always on** | ❌ | ✅ | ✅ | ✅ | ⚡ |
| **Custom domain** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **SSL** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Easy deploy** | ✅✅ | ✅✅ | ✅✅ | ✅ | ⚡ |
| **Scaling** | ❌ | ⚡ | ❌ | ✅ | ✅✅ |

⚡ = Pay for what you use / auto-scaling

---

## 🔄 CI/CD Pipeline

### Current: Manual Upload
1. Edit files locally
2. Upload to HuggingFace manually
3. Space rebuilds automatically

### Better: GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to HuggingFace

on:
  push:
    branches: [main]
    paths:
      - 'outreach/pipelines/gemini_file_search/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Push to HuggingFace
        uses: huggingface/huggingface_hub-action@v1
        with:
          args: upload outreach/pipelines/gemini_file_search --repo-id bobbyni819/HickeyLabSocialMedia --repo-type space
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
```

### Benefits of CI/CD
- ✅ Automatic deployment on push
- ✅ Version control
- ✅ Rollback capability
- ✅ No manual upload errors

---

## 🌐 Custom Domain Setup

### If Using HuggingFace Pro

1. Go to Space Settings → Custom domain
2. Enter your domain (e.g., `chat.hickeylab.com`)
3. Add CNAME record: `chat.hickeylab.com → bobbyni819-hickeylabsocialmedia.hf.space`

### If Self-Hosting

1. Deploy to Railway/Render
2. Get assigned domain
3. Add CNAME to your DNS
4. Configure SSL (usually automatic)

---

## 📦 Environment Management

### Development
```bash
# Local testing
cd outreach
streamlit run app_gemini.py --server.port 8503
```

### Staging (Optional)
```bash
# Create a separate HF Space for testing
# e.g., bobbyni819/HickeyLabSocialMedia-staging
```

### Production
```bash
# Main HF Space
# bobbyni819/HickeyLabSocialMedia
```

### Environment Variables

| Variable | Dev | Staging | Prod |
|----------|-----|---------|------|
| GEMINI_API_KEY | .env file | HF Secret | HF Secret |
| DEBUG | true | true | false |
| RATE_LIMIT | 100 | 50 | 20 |

---

## 🔒 Secrets Management

### HuggingFace Spaces
- Settings → Variables and secrets
- Add as "Secret" (hidden from logs)

### GitHub Actions
- Repository Settings → Secrets and variables → Actions
- Add `HF_TOKEN` for deployment

### Local Development
- Use `.env` file (in .gitignore)
- Never commit secrets!

---

## 📋 Deployment Checklist

### Before Deploying
- [ ] Test locally
- [ ] Check .gitignore (no secrets)
- [ ] Update requirements.txt
- [ ] Review environment variables

### After Deploying
- [ ] Verify app loads
- [ ] Test a query
- [ ] Check logs for errors
- [ ] Verify secrets are set

### Rollback Procedure
1. Go to HuggingFace Space → Files
2. Click "History"
3. Find last working commit
4. Revert or re-upload

---

## 🗺️ Migration Path

### Current → Better Uptime
1. **Short term:** Stay on HF Free, accept sleep
2. **Medium term:** Move to Streamlit Cloud (free, always on)
3. **Long term:** Self-host if needed custom domain

### Migration Steps (to Streamlit Cloud)
1. Create account at share.streamlit.io
2. Connect GitHub repo
3. Point to `outreach/pipelines/gemini_file_search/app.py`
4. Add `GEMINI_API_KEY` secret
5. Deploy
6. Update links

---

## ❓ Open Questions

1. Is the HuggingFace sleep acceptable for now?
2. Do we need a custom domain?
3. Budget for hosting if we upgrade?
4. Who manages deployments?
5. Do we need a staging environment?

---

## 📎 References

- [HuggingFace Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Streamlit Cloud](https://streamlit.io/cloud)
- [Railway](https://railway.app/)
- [Google Cloud Run](https://cloud.google.com/run)
