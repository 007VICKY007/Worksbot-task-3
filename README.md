# 🤖 AI Writing Assistant

An AI-powered writing tool that provides two core features — **Email Drafting** and **Text Summarization** — in a simple chat interface.

Built with LangChain, OpenAI GPT, and Streamlit.

---

## What It Does

### ✉️ Email Drafting
Users type a few keywords — like "sick leave" or "follow up client" — and the AI instantly generates a complete professional email ready to copy and send.

### 📝 Text Summarizer
Users paste any long text — articles, reports, meeting notes, documents — and the AI produces a clean, concise summary in seconds.

---

## How It Works

1. User opens the web app
2. Selects mode — Email Drafting or Text Summarizer
3. Types keywords (for email) or pastes text (for summary)
4. AI generates the output instantly
5. User copies or downloads the result as a .txt file

No login required. No complex forms. Just type and get results.

---

## Example Usage

### Email Drafting

| User Types | Output |
|---|---|
| sick leave | Complete sick leave email to manager |
| resignation | Professional resignation letter |
| follow up client invoice | Polite invoice follow-up email |
| thank you after interview | Post-interview thank-you note |
| meeting reschedule | Meeting reschedule request |
| work from home | WFH request email |

### Text Summarizer

| User Pastes | Output |
|---|---|
| A long news article | Brief summary of key points |
| Meeting notes (2 pages) | Concise bullet-point summary |
| Research paper abstract | Simplified one-line summary |
| Long email thread | Quick summary of decisions made |

---

## Features

- **Two Modes** — switch between Email Drafting and Text Summarizer instantly
- **Smart Intent Detection** — understands what the user wants from just 1-2 keywords
- **Tone Control** (Email) — Professional, Friendly, Formal, Casual, Apologetic, Urgent
- **Summary Styles** (Summarizer) — Brief, Bullet Points, Detailed, One-Line, ELI5 (Simple)
- **Length Control** — Short, Medium, or Detailed/Long
- **Download Option** — save any output as a .txt file
- **Session Stats** — tracks emails drafted and texts summarized
- **Chat Memory** — remembers conversation context within a session
- **LangChain Powered** — uses LangChain prompt templates, chains, and output parsers

---

## Tech Stack

| Component | Technology |
|---|---|
| AI Framework | LangChain |
| Language Model | OpenAI GPT-4o-mini |
| Frontend | Streamlit (Python) |
| Deployment | Streamlit Community Cloud (free) |

---

## Deployment

The app is deployed on **Streamlit Community Cloud** — a free hosting platform that runs 24/7 and is accessible via a web link from any browser.

### Files in This Project

| File | Purpose |
|---|---|
| `app.py` | Main application code |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | UI theme configuration |
| `README.md` | This documentation |

### Steps to Deploy

1. Push code to a GitHub repository (private recommended)
2. Go to share.streamlit.io → sign in with GitHub
3. Click "New app" → select the repository → set main file as `app.py`
4. Add the OpenAI API key in Settings → Secrets
5. Click Deploy

---

## Developed By

**Vignesh Pandiya G**
AI / Full Stack Engineer
