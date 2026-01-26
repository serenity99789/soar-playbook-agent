import streamlit as st
import textwrap
import uuid

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="SOAR Deployment Playbook",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")
st.caption("Production-grade SOAR execution flow driven by the alert use-case")

# ---------------- Input ----------------
st.subheader("SIEM Alert / Use Case Input")

alert_text = st.text_area(
    "Describe the alert that triggered SOAR",
    placeholder="Example: Suspicious PowerShell execution detected on endpoint with outbound C2 communication...",
    height=140
)

generate = st.button("Generate Deployment Playbook")

# ---------------- Mermaid Renderer ----------------
def render_mermaid(code: str, height: int = 900):
    st.components.v1.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: "dark",
                flowchart: {{
                    useMaxWidth: false,
                    htmlLabels: true,
                    curve: "basis"
                }}
            }});
        </script>

        <div style="overflow-x:auto; padding:20px;">
            <pre class="mermaid">
{code}
            </pre>
        </div>
        """,
        height=height,
        scrolling=True
    )

# ---------------- Generate ----------------
if generate:
    if not alert_text.strip():
        st.warning("Please enter a SIEM alert before generating the playbook.")
        st.stop()

    # Force fresh render every time (prevents stuck state)
    run_id = str(uuid.uuid4())[:8]

    # Compact alert summary for node
    alert_summary = textwrap.shorten(
        alert_text.replace("\n", " "),
        width=90,
        placeholder="..."
    )

    st.success("Deployment playbook generated")

    mermaid = f"""
flowchart LR

%% ---------------- STYLES ----------------
classDef ingest fill:#1f77ff,color:#ffffff,stroke:#1f77ff;
classDef enrich fill:#1f77ff,color:#ffffff,stroke:#1f77ff;
classDef triage fill:#ff7f0e,color:#ffffff,stroke:#ff7f0e;
classDef analysis fill:#9467bd,color:#ffffff,stroke:#9467bd;
classDef decision fill:#f1c40f,color:#000000,stroke:#f1c40f;
classDef response fill:#e74c3c,color:#ffffff,stroke:#e74c3c;
classDef notify fill:#2ecc71,color:#ffffff,stroke:#2ecc71;

%% ---------------- ALERT ----------------
A0["SIEM Alert<br/><small>{alert_summary}</small>"]:::ingest

%% ---------------- ENRICHMENT ----------------
subgraph E["Alert Intake & Enrichment"]
    A1["Normalize Fields"]:::enrich
    A2["Context Enrichment"]:::enrich
    A0 --> A1 --> A2
end

%% ---------------- TRIAGE ----------------
subgraph T["Automated Triage"]
    T1["Initial Severity Scoring"]:::triage
    T2["Deduplication Check"]:::triage
    A2 --> T1 --> T2
end

%% ---------------- PARALLEL ANALYSIS ----------------
subgraph AN["Parallel Analysis"]
    H["Hash / File Analysis"]:::analysis
    IP["IP Reputation Check"]:::analysis
    U["Host & User Analysis"]:::analysis
end

T2 --> H
T2 --> IP
T2 --> U

%% ---------------- DECISION ----------------
D{{"Threat Confirmed?"}}:::decision

H --> D
IP --> D
U --> D

%% ---------------- RESPONSE ----------------
subgraph R["Automated Response"]
    R1["Auto Containment"]:::response
    R2["Block IP / Isolate Host"]:::response
    R3["Preserve Evidence"]:::response
    R1 --> R2 --> R3
end

%% ---------------- HUMAN ----------------
subgraph HR["Human Review"]
    HR1["SOC Analyst Review"]:::analysis
end

D -->|Yes| R1
D -->|Uncertain| HR1

%% ---------------- CLOSURE ----------------
subgraph C["Closure & Reporting"]
    C1["Create / Update Incident"]:::notify
    C2["Notify IR & SOC"]:::notify
    C3["Final Report"]:::notify
    C1 --> C2 --> C3
end

R3 --> C1
HR1 --> C1

%% ---------------- RUN ----------------
%% Run ID: {run_id}
"""

    st.markdown("### 🧭 SOAR Execution Flow")
    render_mermaid(mermaid)

    st.download_button(
        "⬇️ Download Playbook (Mermaid)",
        data=mermaid,
        file_name="soar_deployment_playbook.mmd",
        mime="text/plain"
    )
