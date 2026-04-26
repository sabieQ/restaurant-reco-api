# Streamlit Deployment Guide

This guide covers running the Streamlit app locally and deploying to Streamlit Community Cloud.

## Local Run

### Prerequisites
- Python 3.11
- Dependencies installed from `requirements.txt`

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Run Locally
```powershell
streamlit run streamlit_app.py
```

The app will open at [http://localhost:8501](http://localhost:8501)

## Streamlit Community Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Community Cloud account (free)

### Step 1: Push to GitHub
Ensure your code is pushed to a GitHub repository.

### Step 2: Connect Repository to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository
5. Set the main file path: `streamlit_app.py`
6. Click "Deploy"

### Step 3: Configure Secrets
In the Streamlit Cloud dashboard for your app:
1. Go to "Settings" → "Secrets"
2. Add the following secrets:

```
OPENROUTER_API_KEY=your_openrouter_key_here
GROQ_API_KEY=your_groq_key_here
```

**Important:** Never commit actual API keys to your repository. Use environment variables or Streamlit secrets.

### Step 4: Deploy
Click "Deploy" and wait for the build to complete. The app will be available at a URL like `https://your-app-name.streamlit.app`

## Environment Variables

The app expects the following environment variables (set in `.env` locally or secrets in Cloud):

- `OPENROUTER_API_KEY` (optional) - Primary LLM provider
- `GROQ_API_KEY` (optional) - Fallback LLM provider

At least one key should be configured for LLM-powered recommendations.

## Features

- **Location-based search**: Select from available locations in the dataset
- **Budget filtering**: Low, Medium, or High budget options
- **Cuisine preferences**: Choose from available cuisines
- **Rating filters**: Set minimum rating requirements with a slider
- **Additional preferences**: Optional text input for specific requirements
- **AI-powered explanations**: LLM-generated personalized recommendations
- **Fallback support**: Graceful degradation if LLM services are unavailable
- **Real-time feedback**: Loading states and error messages
- **Metadata display**: Shows LLM provider used, fallback status, and filter strategy
- **Raw JSON view**: Expandable section to see API response

## Limitations

- **Free tier constraints**: Streamlit Community Cloud free tier has resource limits and cold starts
- **Dataset size**: The full Zomato dataset is loaded on each request; consider caching for production
- **LLM rate limits**: Free tier API keys may have rate limits
- **Cold starts**: First request after deployment may be slower due to cold start

## Troubleshooting

### App fails to load dataset
- Ensure the dataset is accessible from Hugging Face
- Check internet connectivity
- Verify `datasets` library is installed

### LLM recommendations fail
- Check that API keys are configured in secrets
- Verify API keys are valid and have available quota
- Check the error message in the app for specific issues

### Deployment fails
- Ensure `streamlit_app.py` exists in the repository root
- Check that all dependencies are in `requirements.txt`
- Verify the main file path in Streamlit Cloud settings

## Alternative Deployment Options

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
```

### Render/Fly
Deploy as a Python web service with Streamlit. Configure the start command to run `streamlit run streamlit_app.py --server.port=$PORT`.
