# 🚀 InfraGenie - Deployment Guide

## Overview

InfraGenie uses a **split deployment architecture**:
- **Frontend**: Next.js app deployed on **Vercel**
- **Backend**: FastAPI server deployed on **Render**

---

## 📋 Prerequisites

Before deploying, ensure you have:

1. ✅ GitHub account (repository pushed)
2. ✅ [Vercel account](https://vercel.com/signup) (free tier)
3. ✅ [Render account](https://render.com/register) (free tier)
4. ✅ Groq API key (from [console.groq.com](https://console.groq.com/keys))
5. ✅ Clerk API keys (from [clerk.com](https://dashboard.clerk.com))

---

## 🔧 Part 1: Deploy Backend to Render

### Step 1: Push to GitHub

```bash
# Add all files (respecting .gitignore)
git add .

# Commit changes
git commit -m "feat: production-ready InfraGenie with triple-layer SSH enforcement"

# Push to GitHub
git push origin main
```

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `InfraGenie`

### Step 3: Configure Render Service

| Setting | Value |
|---------|-------|
| **Name** | `infragenie-backend` |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install --upgrade pip && pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` |

### Step 4: Add Environment Variables

In Render dashboard, go to **"Environment"** tab and add:

| Key | Value | Example |
|-----|-------|---------|
| `GROQ_API_KEY` | Your Groq API key | `gsk_xxxxxxxxxxxxx` |
| `PYTHON_VERSION` | `3.11.0` | - |
| `ENVIRONMENT` | `production` | - |
| `CORS_ORIGINS` | Will update after Vercel deploy | `*` (temporarily) |

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Copy the deployed URL: `https://infragenie-backend.onrender.com`

**⚠️ Important:** Render free tier spins down after 15 minutes of inactivity. First request may take 50 seconds to wake up.

---

## 🎨 Part 2: Deploy Frontend to Vercel

### Step 1: Import Project to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository: `InfraGenie`

### Step 2: Configure Vercel Project

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Next.js` |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |
| **Install Command** | `npm install` |
| **Node Version** | `20.x` |

### Step 3: Add Environment Variables

In Vercel, go to **"Settings"** → **"Environment Variables"** and add:

| Key | Value | Example |
|-----|-------|---------|
| `NEXT_PUBLIC_API_URL` | Your Render backend URL | `https://infragenie-backend.onrender.com` |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | From Clerk dashboard | `pk_test_xxxxx` |
| `CLERK_SECRET_KEY` | From Clerk dashboard | `sk_test_xxxxx` |

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for build
3. Copy the deployed URL: `https://infragenie.vercel.app`

---

## 🔗 Part 3: Connect Frontend & Backend

### Update Backend CORS

1. Go to Render dashboard → Your backend service
2. **Environment** → Edit `CORS_ORIGINS`
3. Change from `*` to your Vercel URL: `https://infragenie.vercel.app`
4. Click **"Save Changes"** (will redeploy)

### Update Frontend API URL

Your frontend should already have the correct API URL from Step 2.3. Verify in:
- Vercel Dashboard → Settings → Environment Variables
- `NEXT_PUBLIC_API_URL` = `https://infragenie-backend.onrender.com`

---

## ✅ Part 4: Verify Deployment

### Test Backend

```bash
# Health check
curl https://infragenie-backend.onrender.com/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### Test Frontend

1. Visit your Vercel URL: `https://infragenie.vercel.app`
2. Sign up / Sign in with Clerk
3. Enter a test prompt: **"Create an EC2 instance with nginx"**
4. Verify:
   - ✅ Architecture diagram renders
   - ✅ Cost estimate appears
   - ✅ Security scan results shown
   - ✅ Download button generates deployment kit

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Render service won't start
- **Solution:** Check logs in Render dashboard
- Common issues:
  - Missing `GROQ_API_KEY` environment variable
  - Python version mismatch (use 3.11)
  - Missing dependencies in `requirements.txt`

**Problem:** 502 Bad Gateway
- **Solution:** Render free tier is cold starting (wait 50 seconds)
- First request after 15 minutes of inactivity takes time

**Problem:** CORS errors
- **Solution:** Verify `CORS_ORIGINS` in Render matches your Vercel URL exactly
- Should NOT have trailing slash

### Frontend Issues

**Problem:** Build fails on Vercel
- **Solution:** Check build logs for TypeScript errors
- Run locally: `cd frontend && npm run build`

**Problem:** API requests fail (Network Error)
- **Solution:** Check `NEXT_PUBLIC_API_URL` environment variable
- Must start with `https://`
- Must NOT have trailing slash

**Problem:** Clerk authentication fails
- **Solution:** Verify Clerk keys in Vercel environment variables
- Check Clerk dashboard → API Keys are correct
- Ensure domain is added to Clerk allowed domains

---

## 🔒 Security Checklist

Before going live:

- [ ] ✅ All `.env` files are in `.gitignore`
- [ ] ✅ No API keys committed to GitHub
- [ ] ✅ CORS configured to specific frontend domain (not `*`)
- [ ] ✅ Clerk authentication is working
- [ ] ✅ Groq API key is valid and has quota
- [ ] ✅ Backend `/health` endpoint returns 200
- [ ] ✅ Frontend can successfully generate infrastructure

---

## 📊 Monitoring

### Backend Health

- **Render Dashboard:** View logs, CPU, memory usage
- **Health Endpoint:** `https://infragenie-backend.onrender.com/health`

### Frontend Analytics

- **Vercel Dashboard:** Page views, errors, performance metrics
- **Clerk Dashboard:** User signups, active sessions

---

## 🚀 Scaling (Future)

### When to Upgrade from Free Tier

**Render:**
- Free tier: 512MB RAM, spins down after 15 min inactivity
- Upgrade to **Starter ($7/mo)** when:
  - ✅ 10+ daily active users
  - ✅ Need always-on (no cold starts)
  - ✅ Need more than 512MB RAM

**Vercel:**
- Free tier: 100GB bandwidth/month, hobby usage
- Upgrade to **Pro ($20/mo)** when:
  - ✅ 100+ daily active users
  - ✅ Need team collaboration
  - ✅ Need priority support

---

## 📝 Post-Deployment Updates

### Deploying Code Changes

**Backend (Render):**
```bash
git add backend/
git commit -m "fix: your change"
git push origin main
# Render auto-deploys on push to main
```

**Frontend (Vercel):**
```bash
git add frontend/
git commit -m "feat: your change"
git push origin main
# Vercel auto-deploys on push to main
```

### Updating Environment Variables

**Render:**
1. Dashboard → Service → Environment
2. Edit/Add variables
3. Click "Save Changes" (triggers redeploy)

**Vercel:**
1. Dashboard → Project → Settings → Environment Variables
2. Edit/Add variables
3. Redeploy required: Go to Deployments → Latest → "Redeploy"

---

## 🎯 Production Readiness Checklist

- [x] ✅ Frontend builds without errors
- [x] ✅ Backend has health check endpoint
- [x] ✅ Environment variables documented
- [x] ✅ `.gitignore` excludes sensitive files
- [x] ✅ CORS configured properly
- [x] ✅ Authentication working (Clerk)
- [x] ✅ API integration working
- [ ] 🔄 Custom domain configured (optional)
- [ ] 🔄 SSL/TLS enabled (automatic on Render/Vercel)
- [ ] 🔄 Monitoring/alerting setup (optional)

---

## 📞 Support

If you encounter issues:

1. **Check Logs:**
   - Render: Dashboard → Logs
   - Vercel: Dashboard → Deployments → Logs

2. **Common Issues:**
   - Cold start delays (Render free tier)
   - CORS misconfigurations
   - Missing environment variables

3. **Resources:**
   - [Render Docs](https://render.com/docs)
   - [Vercel Docs](https://vercel.com/docs)
   - [Next.js Deployment](https://nextjs.org/docs/deployment)

---

**🎉 Congratulations! Your InfraGenie is now live!**

Frontend: `https://infragenie.vercel.app`  
Backend: `https://infragenie-backend.onrender.com`
