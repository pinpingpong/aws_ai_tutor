# 🧠 AIP-C01 AWS Generative AI Developer — Practice Tutor

An AI-powered exam tutor for the **AWS Certified Generative AI Developer – Professional (AIP-C01)** certification, built with Streamlit and Google Gemini.

---

## Features

- 🎯 **AI-generated exam questions** at real exam difficulty, scenario-based with 4 plausible options, powered by Google Gemini
- 📚 **Domain filtering** — drill any of 8 exam domains or mix them all
- 🔍 **Web research integration** — scrapes forums, Reddit, and blogs via Jina AI to gather real-world exam feedback, then uses Gemini to synthesize insights for current, relevant questions
- 💬 **Smart feedback** — instant explanations for correct and incorrect answers based on question details
- 📊 **Score tracking** with exam-readiness indicator (target: 85%+)
- 📋 **Question history** so you can review what you got wrong

---

## Quick Start (Local)

### 1. Clone / download this folder

```bash
cd aip_tutor
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

Edit `.streamlit/secrets.toml`:

```toml
GOOGLE_API_KEY = "your-google-api-key-here"
JINA_API_KEY = "your-jina-api-key-here"
```

- **Google API key**: https://aistudio.google.com/apikey (free, no credit card)
- **Jina API key**: https://jina.ai/reader/ (free tier available for API calls)

**Note:** Jina is used to scrape current exam discussion forums and blogs. If you skip it, the app still works — questions will use Gemini's base knowledge instead of latest community insights.

### 4. Run the app

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Using the Research Feature

1. **Gather Research** — Click "Search Latest AWS" in the sidebar to scrape current discussions and synthesize insights with Gemini
2. **Save to Cache** — Click "💾 Save" to persist research to `research_cache.json` (survives app restarts and Streamlit Cloud redeployments)
3. **Load from Cache** — Click "📂 Load Cache" to reload previously saved research without making new API calls
4. **Generate Questions** — All questions generated will be informed by your cached research context
5. **Clear** — Remove research and cache file anytime

**Cost optimization:** Research is expensive (multiple API calls). Save it once, reuse it for dozens of questions.

---

## Deploy to Streamlit Community Cloud (Free, Public URL)

This is the easiest way to share it.

1. Push this folder to a **GitHub repo** (the `.gitignore` will protect your secrets file)
2. Go to https://share.streamlit.io and sign in with GitHub
3. Click **"New app"** → select your repo → set main file to `app.py`
4. Under **"Advanced settings → Secrets"**, add both keys:
   ```
   GOOGLE_API_KEY = "your-google-api-key-here"
   JINA_API_KEY = "your-jina-api-key-here"
   ```
5. Click **Deploy** — you'll get a public URL like `https://yourname-aip-tutor.streamlit.app`

---

## Other Hosting Options

### Railway (easy, free tier)
1. Push to GitHub
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Add env vars:
   - `GOOGLE_API_KEY=your-google-api-key-here`
   - `JINA_API_KEY=your-jina-api-key-here`
4. Set start command: `streamlit run app.py --server.port $PORT --server.headless true`

### Render
1. Push to GitHub
2. Go to https://render.com → New Web Service
3. Build command: `pip install -r requirements.txt`
4. Start command: `streamlit run app.py --server.port $PORT --server.headless true`
5. Add env vars:
   - `GOOGLE_API_KEY=your-google-api-key-here`
   - `JINA_API_KEY=your-jina-api-key-here`

### Hugging Face Spaces (free, great for portfolios)
1. Create a Space at https://huggingface.co/spaces
2. Choose **Streamlit** as the SDK
3. Upload your files
4. Add your API key in Space **Settings → Repository secrets**

---

## Exam Tips (from real AIP-C01 takers)

- Passing score is **750/1000** — higher than most associate exams
- Questions have **2–3 plausible answers** — find the subtle detail that eliminates them
- Almost every question has **multi-dimensional constraints**: cost + latency + security + scalability
- Biggest candidate gap: not enough hands-on time with **Bedrock Agents** and **Knowledge Bases**
- Target **85%+ on practice** before booking the real exam

---

Built with ❤️ using [Streamlit](https://streamlit.io) + [Google Gemini API](https://ai.google.dev/)
