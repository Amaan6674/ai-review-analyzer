# AI Review Analyzer 🤖⭐

An intelligent customer review analysis system powered by LangGraph and Groq's free AI API. Automatically detects sentiment, diagnoses issues, and generates personalized responses.

## Features

- 🎯 **Sentiment Analysis**: Automatically detects if reviews are positive or negative
- 🔍 **Issue Diagnosis**: For negative reviews, identifies issue type, tone, and urgency
- 💬 **Smart Responses**: Generates personalized, empathetic responses
- 🚀 **Free AI**: Uses Groq's completely free API (no credit card required)
- 🎨 **Beautiful UI**: Clean Streamlit interface

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Free Groq API Key

1. Visit [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up (free, no credit card needed)
3. Create a new API key
4. Copy the key

### 3. Configure Environment

Create/update your `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## How It Works

The app uses a **LangGraph workflow** with conditional routing:

1. **Sentiment Detection** → Analyzes if review is positive/negative
2. **Conditional Routing**:
   - **Positive** → Generate thank-you message
   - **Negative** → Diagnose issue → Generate support response

## Deployment

### Deploy to Streamlit Cloud (Free)

1. ✅ **Code is on GitHub** - Already done!
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click **"New app"**
5. Configure:
   - **Repository:** `Amaan6674/ai-review-analyzer`
   - **Branch:** `main`
   - **Main file path:** `app.py`
6. Click **"Advanced settings"** and add your secrets (see below)
7. Click **"Deploy!"** 🎉

### Secrets Format (Streamlit Cloud)

In the Advanced Settings → Secrets section, add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Your app will be live at: `https://[your-app-name].streamlit.app`

## Project Structure

```
├── app.py              # Streamlit application
├── workflow.ipynb      # Jupyter notebook (development)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (local)
└── README.md          # This file
```

## Tech Stack

- **LangGraph**: Workflow orchestration
- **Groq**: Free AI inference (Llama 3.1)
- **Streamlit**: Web interface
- **LangChain**: LLM framework
