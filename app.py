import streamlit as st
from openai import OpenAI

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="Email Draft AI", page_icon="✉️", layout="centered")

# ── API Key (secrets for cloud, fallback to sidebar) ─────────
def get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None

api_key = get_api_key()
MODEL = "gpt-4o-mini"

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; }

.app-header { text-align: center; padding: 1.5rem 0 0.6rem; }
.app-header .icon { font-size: 2.6rem; }
.app-header h1 {
    font-size: 1.7rem; font-weight: 700;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0.2rem 0;
}
.app-header .tagline { color: #6b7280; font-size: 0.9rem; margin: 0; }

.tip-box {
    background: #eef2ff; border-left: 4px solid #6366f1;
    border-radius: 0 8px 8px 0; padding: 0.85rem 1rem;
    margin: 0.3rem 0 1.1rem; font-size: 0.84rem;
    color: #3730a3; line-height: 1.55;
}

.email-output {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 1.3rem 1.5rem;
    margin: 0.5rem 0; font-family: 'Inter', sans-serif;
    font-size: 0.9rem; line-height: 1.75; color: #1e293b;
    text-align: left; direction: ltr;
    white-space: pre-wrap; word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="icon">✉️</div>
    <h1>Email Draft AI</h1>
    <p class="tagline">Type keywords → Get a professional email draft instantly</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✉️ Email Settings")
    st.markdown("")

    if not api_key:
        api_key = st.text_input("🔑 OpenAI API Key", type="password", placeholder="sk-...")
        st.markdown("")

    tone = st.selectbox("Tone", ["Professional", "Friendly", "Formal", "Casual", "Apologetic", "Urgent"])
    length = st.radio("Length", ["Short", "Medium", "Detailed"], index=1, horizontal=True)

    st.markdown("---")
    total = len([m for m in st.session_state.get("messages", []) if m["role"] == "assistant"])
    st.metric("Emails Drafted", total)

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("")
    st.caption("Built by Vignesh · Powered by AI")

# ── Tip Box ──────────────────────────────────────────────────
st.markdown("""
<div class="tip-box">
    <strong>💡 Just type keywords or a short description:</strong><br>
    <em>sick leave</em> · <em>resignation</em> · <em>follow up client</em> · <em>thank you after interview</em> · <em>salary hike request</em> · <em>apology late delivery</em> · <em>work from home</em> · <em>meeting reschedule</em>
</div>
""", unsafe_allow_html=True)

# ── System Prompt ────────────────────────────────────────────
SYSTEM_PROMPT = """You are an email drafting assistant. Your ONLY job is to turn user input into professional email drafts.

## INTENT DETECTION:

When a user types anything, ask yourself: "Could this be a topic for an email?"
- If YES (even loosely) → Draft the email immediately. Never ask for clarification.
- If NO (clearly unrelated like math, code, jokes, general knowledge) → Reply:
  "✉️ I'm your email drafting assistant! Please type a topic or keywords and I'll draft a professional email for you."

IMPORTANT:
- Even 1-2 word inputs like "sick leave", "resignation", "apology", "invoice", "promotion" are VALID email topics — draft immediately.
- NEVER ask "do you want me to write an email?" — just write it.
- If keywords are vague, use your best judgment to fill in reasonable details.
- When in doubt, ALWAYS draft the email.

## EMAIL FORMAT (clean plain text, no markdown symbols):

Subject: <clear subject line>

Dear <appropriate recipient>,

<email body — clean left-aligned paragraphs>

<closing>,
[Your Name]

## SETTINGS:
- Tone: {tone}
- Length: {length} (Short = 3-5 sentences, Medium = 5-8, Detailed = 8-12)

Output clean plain text only. No ** bold, no ## headers, no bullet points inside the email."""

# ── Session State ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render Chat History ──────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="✉️"):
            st.markdown(f'<div class="email-output">{msg["content"]}</div>', unsafe_allow_html=True)

# ── Chat Input ───────────────────────────────────────────────
if prompt := st.chat_input("Type keywords… e.g. 'sick leave' or 'follow up client'"):

    if not api_key:
        st.error("⚠️ Please enter your OpenAI API Key in the sidebar to get started.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(tone=tone, length=length)},
    ]
    for m in st.session_state.messages[-10:]:
        api_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant", avatar="✉️"):
        with st.spinner("✍️ Drafting your email..."):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=api_messages,
                    temperature=0.7,
                    max_tokens=1024,
                )
                reply = response.choices[0].message.content

                st.markdown(f'<div class="email-output">{reply}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": reply})

                col1, col2 = st.columns([3, 1])
                with col2:
                    st.download_button(
                        "📋 Save as TXT",
                        data=reply,
                        file_name="email_draft.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

            except Exception as e:
                err = str(e).lower()
                if "auth" in err or "api key" in err or "invalid" in err or "incorrect" in err:
                    st.error("❌ API key is invalid or expired. Please get a new key from platform.openai.com/api-keys")
                elif "rate" in err or "limit" in err:
                    st.warning("⏳ Too many requests. Please wait a moment and try again.")
                elif "quota" in err or "billing" in err or "insufficient" in err:
                    st.error("❌ OpenAI quota exceeded. Add credits at platform.openai.com/settings/organization/billing")
                else:
                    st.error(f"❌ Something went wrong. Please try again.")
