# Deployment Guide

This guide covers deploying the Restaurant Recommendation API with Vercel (frontend) and Render (backend).

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐
│   Vercel        │         │   Render        │
│   (Frontend)    │◄────────►│   (Backend)     │
│   Next.js       │  HTTPS   │   FastAPI       │
└─────────────────┘         └─────────────────┘
                                    │
                                    ▼
                            ┌─────────────────┐
                            │   LLM APIs      │
                            │   (OpenRouter/  │
                            │    Groq)        │
                            └─────────────────┘
```

- **Frontend**: Next.js application deployed on Vercel
- **Backend**: FastAPI application deployed on Render
- **Communication**: HTTPS with CORS configuration
- **LLM Providers**: OpenRouter (primary) and Groq (fallback)

## Prerequisites

- GitHub account
- Vercel account (free)
- Render account (free)
- API keys for OpenRouter and/or Groq

## Environment Variables

### Backend (Render)
Create these environment variables in your Render dashboard:

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
GROQ_API_KEY=your_groq_key_here
FRONTEND_URL=https://your-vercel-app.vercel.app
```

### Frontend (Vercel)
Create this environment variable in your Vercel dashboard:

```bash
NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
```

## Backend Deployment (Render)

### Step 1: Prepare Repository
Ensure your code is pushed to GitHub with:
- `.env` in `.gitignore` (API keys not committed)
- `.env.example` as template
- `requirements.txt` with all dependencies

### Step 2: Create Render Web Service
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `restaurant-reco-api`
   - **Region**: Choose nearest region
   - **Branch**: `main`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Configure Environment Variables
In the Render dashboard for your service:
1. Go to "Environment"
2. Add the following variables:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `GROQ_API_KEY`: Your Groq API key
   - `FRONTEND_URL`: Your Vercel app URL (will be added after frontend deployment)

### Step 4: Deploy
Click "Create Web Service" and wait for deployment. Your backend will be available at:
```
https://restaurant-reco-api.onrender.com
```

### Step 5: Verify Deployment
Test the health endpoint:
```bash
curl https://restaurant-reco-api.onrender.com/health
```

## Frontend Deployment (Vercel)

### Step 1: Prepare Repository
Ensure your code is pushed to GitHub with:
- `frontend/.env.local` in `.gitignore`
- `frontend/package.json` with all dependencies

### Step 2: Import Project to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### Step 3: Configure Environment Variables
In the Vercel dashboard for your project:
1. Go to "Settings" → "Environment Variables"
2. Add:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
   - Example: `https://restaurant-reco-api.onrender.com`

### Step 4: Deploy
Click "Deploy" and wait for deployment. Your frontend will be available at:
```
https://your-project-name.vercel.app
```

### Step 5: Update Backend CORS
After Vercel deployment:
1. Copy your Vercel app URL
2. Go to Render dashboard → your service → Environment
3. Update `FRONTEND_URL` with your Vercel app URL
4. Render will automatically redeploy with the new CORS configuration

## CORS Configuration

The backend uses the `FRONTEND_URL` environment variable to configure CORS. This ensures:
- Local development: `http://localhost:3000` is allowed
- Production: Your Vercel domain is allowed
- Security: Only allowed origins can access the API

## Troubleshooting

### Backend Deployment Issues

**Build fails on Render**
- Check that `requirements.txt` includes all dependencies
- Verify Python version compatibility (3.11)
- Check Render build logs for specific errors

**API returns 404**
- Verify the start command is correct: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check that the port is set to `$PORT` (Render's environment variable)

**CORS errors**
- Verify `FRONTEND_URL` is set correctly in Render
- Check that the Vercel URL is correct (no trailing slash)
- Ensure the backend has redeployed after updating CORS settings

### Frontend Deployment Issues

**Build fails on Vercel**
- Check that `frontend/package.json` has all dependencies
- Verify Node.js version compatibility
- Check Vercel build logs for specific errors

**API calls fail**
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- Check that the Render backend is running
- Test the backend health endpoint directly
- Check browser console for CORS errors

**Environment variables not working**
- Ensure variables start with `NEXT_PUBLIC_` for client-side access
- Verify variables are set in the correct environment (Production vs Preview)
- Redeploy after adding environment variables

### Common Issues

**Cold start delays**
- First request may take 2-5 seconds (serverless cold start)
- Subsequent requests are faster
- Consider a keep-alive cron job for production

**Rate limiting**
- Free tier API keys have rate limits
- Monitor usage and upgrade to paid tiers if needed
- Implement caching to reduce API calls

**Dataset loading errors**
- Ensure Hugging Face dataset is accessible
- Check internet connectivity
- Verify `datasets` library is installed

## Local Development

### Backend
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```powershell
cd frontend
npm run dev
```

The frontend will use `http://localhost:8000` by default (configured in `frontend/.env.local`).

## Monitoring

### Render Monitoring
- Render provides built-in metrics for CPU, memory, and response times
- Check the Render dashboard for your service
- Set up alerts for high error rates or slow response times

### Vercel Monitoring
- Vercel Analytics provides insights into frontend performance
- Check the Vercel dashboard for your project
- Monitor build times and deployment status

### LLM API Monitoring
- Monitor token usage on OpenRouter and Groq dashboards
- Track rate limits and upgrade if needed
- Implement logging to track API call failures

## Cost Summary

### Free Tier Limits
- **Vercel**: 100GB bandwidth/month, unlimited deployments
- **Render**: 750 hours/month, 512MB RAM
- **OpenRouter**: Limited tokens per day
- **Groq**: Limited requests per day

### Estimated Monthly Costs (Free Tier)
- **Vercel**: $0 (within limits)
- **Render**: $0 (within limits)
- **LLM APIs**: $0 (within free tier limits)

### When to Upgrade
- Exceeding 750 hours/month on Render → Upgrade to paid tier ($7/month)
- High traffic → Consider Render paid tier for more resources
- Frequent LLM calls → Upgrade to paid API tiers for reliability

## Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use environment variables** for all sensitive data
3. **Restrict CORS** to only allowed origins
4. **Monitor logs** for suspicious activity
5. **Rotate API keys** periodically
6. **Use HTTPS** for all communications
7. **Implement rate limiting** on the backend if needed

## Rollback Procedure

If a deployment causes issues:

### Render Rollback
1. Go to Render dashboard → your service
2. Click "Deployments"
3. Find the previous successful deployment
4. Click "Rollback to this deployment"

### Vercel Rollback
1. Go to Vercel dashboard → your project
2. Click "Deployments"
3. Find the previous successful deployment
4. Click "..." → "Rollback"

## Support

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Project Issues**: Check GitHub issues or create a new one
