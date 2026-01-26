import streamlit as st
import os

from core.diagram_engine import build_soar_mermaid
import streamlit.components.v1 as components

from google import genai


# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="SOAR Learning Platform",
    layout="wide"
)

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "lp_state" not in st.session_state:
    # intro | level_select | learning
    st.session_state.lp_state = "intro"

if "learning_level" not in st.session_state:
    st.session_state.learning_level = None

if "mentor_open" not in st.session_state:
    st.session_state.mentor_open = False

if "mentor_history" not in st.session_state:
    st.session_state.mentor_history = []


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def reset_level():
    st.session_state.lp_state = "level_select"
    st.session_state.learning_level = None
    st.session_state.mentor_history = []


def load_learning_markdown(level: str) -> str:
    path_map = {
        "Beginner": "learning/beginner.md",
        "Intermediate": "learning/intermediate.md",
        "Advanced": "learning/advanced.md",
    }

    path = path_map.get(level)

    if not path or not os.path.exists(path):
        return "_Learning content will be added here._"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_mermaid_diagram():
    blocks = [
        {"title": "Alert Intake", "type": "enrichment"},
        {"title": "Normalization & Parsing", "type": "enrichment"},
        {"title": "Context Enrichment", "type": "enrichment"},
        {"title": "Threat Confirmed?", "type": "decision"},
        {"title": "Automated Containment", "type": "automation"},
        {"title": "Human Review", "type": "human"},
        {"title": "Incident Closure", "type": "human"},
    ]

    mermaid = build_soar_mermaid(blocks)

    html = f"""
    <html>
      <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
          mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
      </head>
      <body>
        <div class="mermaid">{mermaid}</div>
      </body>
    </html>
    """

    components.html(html, height=600, scrolling=True)


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def ask_ai_mentor(question: str) -> str:
    client = get_gemini_client()
    if not client:
        return "AI mentor is not configured. API key not found."

    prompt = f"""
You are a SOAR Learning Mentor.

Context:
- User learning level: {st.session_state.learning_level}
- Purpose: Explain SOC, SIEM, and SOAR concepts clearly.
- Do NOT generate playbooks.
- Do NOT invent tools or procedures.
- Be concise, calm, and mentor-like.

User question:
{question}
""".strip()

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
        )
        return response.text or "No response."
    except Exception as e:
        return f"AI mentor error: {e}"


# =================================================
# STATE 0 — INTRO
# =================================================
if st.session_state.lp_state == "intro":

    st.markdown(
        """
        <div style="text-align:center; padding: 6rem 2rem;">
            <h1>SOAR Learning Platform</h1>
            <h4 style="font-weight:400; color:#666;">
                Learn how SOC teams think — not just what they automate.
            </h4>
            <p style="max-width:700px; margin: 1.5rem auto; color:#777;">
                A guided onboarding experience for SOC analysts, focused on SIEM alerts,
                SOAR playbooks, and real-world security workflows.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Learning", type="primary", use_container_width=True):
            st.session_state.lp_state = "level_select"


# =================================================
# STATE 1 — LEVEL SELECTION
# =================================================
elif st.session_state.lp_state == "level_select":

    st.title("Choose your learning path")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🔰 Beginner")
        st.write("New to SOC, SIEM, and SOAR.")
        if st.button("Select Beginner", use_container_width=True):
            st.session_state.learning_level = "Beginner"
            st.session_state.lp_state = "learning"

    with c2:
        st.markdown("### ⚙️ Intermediate")
        st.write("Understand alerts, want to learn automation.")
        if st.button("Select Intermediate", use_container_width=True):
            st.session_state.learning_level = "Intermediate"
            st.session_state.lp_state = "learning"

    with c3:
        st.markdown("### 🧠 Advanced")
        st.write("Focus on SOAR design and governance.")
        if st.button("Select Advanced", use_container_width=True):
            st.session_state.learning_level = "Advanced"
            st.session_state.lp_state = "learning"


# =================================================
# STATE 2 — LEARNING MODE
# =================================================
elif st.session_state.lp_state == "learning":

    top_l, top_r = st.columns([4, 1])

    with top_l:
        st.title("SOAR Learning Platform")
        st.caption(f"Level: {st.session_state.learning_level}")

    with top_r:
        st.button("Change level", on_click=reset_level)

    st.markdown("---")

    left, right = st.columns([2, 1])

    # -------- Learning Content --------
    with left:
        st.subheader("Learning Content")

        with st.expander("Open learning sections", expanded=True):
            st.markdown(load_learning_markdown(st.session_state.learning_level))

    # -------- Diagram --------
    with right:
        st.subheader("SOAR Workflow")
        render_mermaid_diagram()

    st.markdown("---")

    # -------- AI Mentor --------
    st.subheader("🤖 SOAR Learning Mentor")

    if st.button(
        "Open / Close Mentor",
        help="Ask questions about SOC, SIEM, and SOAR concepts"
    ):
        st.session_state.mentor_open = not st.session_state.mentor_open

    if st.session_state.mentor_open:
        question = st.text_input(
            "Ask a question",
            placeholder="Why do SOAR playbooks include human review?",
        )

        if st.button("Ask Mentor") and question:
            answer = ask_ai_mentor(question)
            st.session_state.mentor_history.append(
                {"q": question, "a": answer}
            )

        for item in reversed(st.session_state.mentor_history[-5:]):
            st.markdown(f"**You:** {item['q']}")
            st.markdown(f"**Mentor:** {item['a']}")
            st.markdown("---")

    st.caption("Build Step 3 complete: AI Mentor added (safe, controlled, optional).")
