import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(page_title="AI Writing Assistant", page_icon="A", layout="centered")

# ── API Key ──────────────────────────────────────────────────
def get_api_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None

api_key = get_api_key()

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
.stApp { font-family: 'Inter', sans-serif; }

.app-header { text-align: center; padding: 1.2rem 0 0.5rem; }
.app-header h1 {
    font-size: 1.7rem; font-weight: 700;
    background: linear-gradient(135deg, #4f46e5, #7c3aed, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0.2rem 0;
}
.app-header .tagline { color: #6b7280; font-size: 0.88rem; margin: 0; }

.tip-box {
    background: #eef2ff; border-left: 4px solid #6366f1;
    border-radius: 0 8px 8px 0; padding: 0.8rem 1rem;
    margin: 0.3rem 0 1rem; font-size: 0.83rem;
    color: #3730a3; line-height: 1.55;
}
.tip-box-green {
    background: #ecfdf5; border-left: 4px solid #10b981;
    border-radius: 0 8px 8px 0; padding: 0.8rem 1rem;
    margin: 0.3rem 0 1rem; font-size: 0.83rem;
    color: #065f46; line-height: 1.55;
}

.output-block {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 10px; padding: 1.3rem 1.5rem;
    margin: 0.5rem 0; font-family: 'Inter', sans-serif;
    font-size: 0.9rem; line-height: 1.75; color: #1e293b;
    text-align: left; direction: ltr;
    white-space: pre-wrap; word-wrap: break-word;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.mode-badge {
    display: inline-block; padding: 0.3rem 0.8rem;
    border-radius: 20px; font-size: 0.78rem; font-weight: 600;
    margin-bottom: 0.5rem;
}
.mode-email { background: #eef2ff; color: #4338ca; }
.mode-summary { background: #ecfdf5; color: #065f46; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>AI Writing Assistant</h1>
    <p class="tagline">Email Drafting and Text Summarization — powered by LangChain + GPT</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Settings")
    st.markdown("")

    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        st.markdown("")

    mode = st.radio("Mode", ["Email Drafting", "Text Summarizer"], index=0)

    st.markdown("---")

    if mode == "Email Drafting":
        tone = st.selectbox("Tone", ["Professional", "Friendly", "Formal", "Casual", "Apologetic", "Urgent"])
        length = st.radio("Length", ["Short", "Medium", "Detailed"], index=1, horizontal=True)
    else:
        summary_style = st.selectbox("Summary Style", ["Brief", "Bullet Points", "Detailed", "One-Line", "ELI5 (Simple)"])
        summary_length = st.radio("Length", ["Short", "Medium", "Long"], index=0, horizontal=True)

    st.markdown("---")
    total_emails = len([m for m in st.session_state.get("messages", []) if m.get("type") == "email"])
    total_summaries = len([m for m in st.session_state.get("messages", []) if m.get("type") == "summary"])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Emails", total_emails)
    with col2:
        st.metric("Summaries", total_summaries)

    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("")
    st.caption("Built by Vignesh | LangChain + GPT")

# ── Tip Box ──────────────────────────────────────────────────
if mode == "Email Drafting":
    st.markdown("""
    <div class="tip-box">
        <strong>Email Drafting Mode</strong><br>
        Just type keywords or a short description:<br>
        <em>sick leave</em> | <em>resignation</em> | <em>follow up client</em> | <em>thank you after interview</em> | <em>salary hike request</em> | <em>work from home</em> | <em>meeting reschedule</em>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="tip-box-green">
        <strong>Text Summarizer Mode</strong><br>
        Paste any text and get an instant summary:<br>
        <em>Articles</em> | <em>Reports</em> | <em>Meeting notes</em> | <em>Research papers</em> | <em>Long emails</em> | <em>Blog posts</em> | <em>Documents</em>
    </div>
    """, unsafe_allow_html=True)

# ── LangChain Prompts ────────────────────────────────────────

EMAIL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an email drafting assistant. Your ONLY job is to turn user input into professional email drafts.

INTENT DETECTION:
When a user types anything, ask yourself: "Could this be a topic for an email?"
- If YES (even loosely) then draft the email immediately. Never ask for clarification.
- If NO (clearly unrelated like math, code, jokes, general knowledge) then reply:
  "I can only help with email drafting. Please type a topic or keywords and I will draft a professional email for you."

RULES:
- Even 1-2 word inputs like "sick leave", "resignation", "apology" are VALID email topics. Draft immediately.
- NEVER ask "do you want me to write an email?" Just write it.
- If keywords are vague, use your best judgment to fill in reasonable details.
- When in doubt, ALWAYS draft the email.

HUMANIZED WRITING RULES:
- Write like a real human being, not a robot. Use natural, conversational phrasing.
- Avoid stiff, robotic phrases like "I hope this message finds you well", "Please be informed that", "I am writing to inform you", "Kindly be advised", "I wish to bring to your notice".
- Instead use natural openers like "I wanted to reach out about...", "I am writing regarding...", "Just a quick note about...", "I wanted to let you know that...".
- Vary sentence length. Mix short and longer sentences naturally.
- Use contractions where appropriate (I am, I will, I have are fine for formal; I'm, I'll, I've for casual/friendly).
- The email should sound like something a real person would actually write, not a template.
- No filler phrases. Get to the point while remaining polite.
- No emojis anywhere in the email.

EMAIL FORMAT (clean plain text only):

Subject: <clear subject line>

Dear <appropriate recipient>,

<email body — natural, human-sounding paragraphs>

<closing>,
[Your Name]

Tone: {tone}
Length: {length} (Short = 3-5 sentences, Medium = 5-8, Detailed = 8-12)

Output clean plain text only. No bold markers, no heading markers, no bullet points, no emojis."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a text summarization assistant. Your ONLY job is to summarize text that users provide.

INTENT DETECTION:
When a user types anything, ask yourself: "Is this text that needs summarizing?"
- If the input is a paragraph or more of text then summarize it immediately.
- If the input is a short phrase like "summarize this" with no text then reply:
  "Please paste the text you would like me to summarize."
- If the input is clearly unrelated (math, code requests, general questions) then reply:
  "I can only help with text summarization. Paste any text — article, report, email, notes — and I will summarize it for you."
- If the user pastes text AND gives instructions (like "summarize this email") then summarize the text.

HUMANIZED WRITING RULES:
- Write summaries in natural, flowing language. Not robotic or mechanical.
- Avoid starting with "The text discusses..." or "This article is about..." or "The author states...".
- Instead, dive directly into the content. State the key points as if you are explaining it to a colleague.
- Use clear, plain language. No jargon unless the original text uses it.
- Vary sentence structure. Do not start every sentence the same way.
- No emojis anywhere in the summary.
- No filler phrases like "It is important to note that" or "It should be mentioned that".
- Make the summary feel like a human wrote it after reading the original, not like a machine extracted keywords.

SUMMARY STYLE: {summary_style}
- Brief = A concise paragraph capturing the main points
- Bullet Points = Key points as clean bullet points using dashes (-)
- Detailed = Comprehensive summary with all important details
- One-Line = Single sentence capturing the essence
- ELI5 (Simple) = Explain in very simple everyday language

LENGTH: {summary_length}
- Short = 2-4 sentences or 3-5 bullets
- Medium = 4-7 sentences or 5-8 bullets
- Long = 7-12 sentences or 8-12 bullets

OUTPUT RULES:
- Start directly with the summary. No preamble like "Here is the summary".
- Use clean plain text. No bold markers, no heading markers.
- For Bullet Points style, use simple dashes (-) not fancy bullets.
- Preserve important names, dates, numbers, and key terms from the original.
- If the text is very short (1-2 sentences), tell the user it is already concise."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# ── LangChain Chain Builder ──────────────────────────────────
def get_chain(chain_type):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0.8,
        max_tokens=1024,
    )
    parser = StrOutputParser()

    if chain_type == "email":
        return EMAIL_PROMPT | llm | parser
    else:
        return SUMMARY_PROMPT | llm | parser

# ── Build Chat History for LangChain ─────────────────────────
def get_langchain_history():
    history = []
    for msg in st.session_state.messages[-10:]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(AIMessage(content=msg["content"]))
    return history

# ── Session State ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Render Chat History ──────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=None):
            st.markdown(msg["content"])
    else:
        badge_class = "mode-email" if msg.get("type") == "email" else "mode-summary"
        badge_text = "Email Draft" if msg.get("type") == "email" else "Summary"
        with st.chat_message("assistant", avatar=None):
            st.markdown(
                f'<span class="mode-badge {badge_class}">{badge_text}</span>'
                f'<div class="output-block">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

# ── Chat Input ───────────────────────────────────────────────
current_mode = "email" if mode == "Email Drafting" else "summary"
placeholder = (
    "Type keywords, e.g. sick leave, follow up client..."
    if current_mode == "email"
    else "Paste your text here to summarize..."
)

if prompt := st.chat_input(placeholder):

    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar to get started.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt, "type": current_mode})
    with st.chat_message("user", avatar=None):
        st.markdown(prompt)

    chat_history = get_langchain_history()

    if current_mode == "email":
        chain = get_chain("email")
        invoke_input = {
            "input": prompt,
            "chat_history": chat_history,
            "tone": tone,
            "length": length,
        }
        spinner_text = "Drafting your email..."
        badge_class = "mode-email"
        badge_text = "Email Draft"
        file_name = "email_draft.txt"
    else:
        chain = get_chain("summary")
        invoke_input = {
            "input": prompt,
            "chat_history": chat_history,
            "summary_style": summary_style,
            "summary_length": summary_length,
        }
        spinner_text = "Summarizing your text..."
        badge_class = "mode-summary"
        badge_text = "Summary"
        file_name = "summary.txt"

    with st.chat_message("assistant", avatar=None):
        with st.spinner(spinner_text):
            try:
                reply = chain.invoke(invoke_input)

                st.markdown(
                    f'<span class="mode-badge {badge_class}">{badge_text}</span>'
                    f'<div class="output-block">{reply}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state.messages.append({"role": "assistant", "content": reply, "type": current_mode})

                col1, col2 = st.columns([3, 1])
                with col2:
                    st.download_button(
                        "Save as TXT",
                        data=reply,
                        file_name=file_name,
                        mime="text/plain",
                        use_container_width=True,
                    )

            except Exception as e:
                err = str(e).lower()
                if "auth" in err or "api key" in err or "invalid" in err or "incorrect" in err:
                    st.error("API key is invalid or expired. Get a new key from platform.openai.com/api-keys")
                elif "rate" in err or "limit" in err:
                    st.warning("Too many requests. Please wait a moment and try again.")
                elif "quota" in err or "billing" in err or "insufficient" in err:
                    st.error("OpenAI quota exceeded. Add credits at platform.openai.com/settings/organization/billing")
                else:
                    st.error("Something went wrong. Please try again.")
