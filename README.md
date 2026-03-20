# AI Job Matcher

> Match your profile, tailor your resume, and ace your interview.

AI Job Matcher is a Streamlit-based web app that takes your skills and a job description and instantly produces a tailored resume, a match score, real interview questions sourced from the web, and AI-generated practice questions — all in one place.

---

## What It Does

| Feature | Description |
|---|---|
| **Job Summary** | Breaks down the role into key responsibilities, required technologies, and (if a company URL is provided) a scraped company overview |
| **Match Score** | Rates how well your profile fits the job (0–100) with strengths and weaknesses |
| **Tailored Resume** | Generates a job-specific resume with a headline, summary, skills, fictional-but-realistic experience, and 3–7 relevant projects |
| **Interview Prep** | Shows real questions previously asked at the company (via Tavily) + AI-generated Easy / Medium / Hard questions |
| **Take My Interview** | *(Coming soon)* — Conversational interview bot that asks questions, corrects your answers, and moves to the next question |

---

## Tech Stack

- **Frontend** — [Streamlit](https://streamlit.io)
- **LLM** — [Groq](https://console.groq.com) via `langchain-groq`
  - Simple mode: `llama-3.3-70b-versatile` (fast, free)
  - Deep Search mode: `openai/gpt-o3-mini` (more accurate)
- **Web Search** — [Tavily](https://app.tavily.com) for real interview questions and website scraping
- **Python** — 3.10+

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/ai-job-fit.git
cd ai-job-fit
```

### 2. Install dependencies

Uses [uv](https://github.com/astral-sh/uv) (recommended):

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables (optional)

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
```

You can also enter these keys directly in the app sidebar.

### 4. Run the app

```bash
streamlit run main.py
```

---

## How to Use

1. **Enter your Groq API key** in the sidebar (required). Get one free at [console.groq.com](https://console.groq.com).
2. **Fill in your profile** — years of experience, skills, and any extra info (certifications, achievements).
3. **Enter the job details** — role title, company name, and paste the full job description.
4. *(Optional)* Add a **Company Website URL** to auto-scrape a company summary.
5. *(Optional)* Add a **Tavily API key** + **Company Name** to fetch real questions previously asked at that company.
6. Choose your **Search Mode**:
   - `Simple` — faster, uses Llama 3.3 70B
   - `Deep Search` — more thorough, uses GPT-o3-mini via Groq
7. Click **Analyze** and explore the results across five tabs.

---

## Project Structure

```
├── main.py          # Streamlit UI — sidebar inputs, tabs, and result rendering
├── client.py        # Core logic — LLM calls, web scraping, Tavily search
├── prompt.py        # System prompt and user prompt builder
├── pyproject.toml   # Dependencies
└── .env             # API keys (not committed)
```

---

## API Keys

| Key | Required | Where to get |
|---|---|---|
| Groq API Key | Yes | [console.groq.com](https://console.groq.com) |
| Tavily API Key | Optional | [app.tavily.com](https://app.tavily.com) |

---

## Notes

- The resume generated is **fictional** — it is designed to help you understand what a strong resume for this role looks like, not to be submitted as-is.
- The app does **not store** any of your data. Everything runs in-session.
- Interview questions sourced via Tavily are pulled from public web sources (Glassdoor, LinkedIn, forums, etc.) and attributed with source and date.
