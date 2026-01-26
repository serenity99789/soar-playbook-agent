import streamlit as st

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="SOAR Deployment Playbook",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SOAR Deployment Playbook")
st.caption("Production-grade SOAR execution flow (enterprise-style)")

# ---------------- Input Section ----------------
with st.container():
    st.subheader("Describe the SIEM Alert / Use Case")

    alert_text = st.text_area(
        "Example:",
        placeholder="Suspicious PowerShell execution detected on endpoint with external IP communication...",
        height=140
    )

    generate = st.button("Generate Deployment Playbook")

# ---------------- Mermaid Renderer ----------------
def render_mermaid(mermaid_code: str):
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
{mermaid_code}
            </pre>
        </div>
        """,
        height=900,
        scrolling=True,
    )

# ---------------- Generate Playbook ----------------
if generate:
    if not alert_text.strip():
        st.warning("Please enter a SIEM alert or use case.")
    else:
        st.success("Deployment playbook generated")

        mermaid_diagram = """
flowchart LR

%% ---------------- STYLES ----------------
classDef enrich fill:#1f77ff,color:#ffffff,stroke:#1f77ff,stroke-width:1px;
classDef analysis fill:#ff7f0e,color:#ffffff,stroke:#ff7f0e,stroke-width:1px;
classDef decision fill:#9467bd,color:#ffffff,stroke:#9467bd,stroke-width:1px;
classDef response fill:#d62728,color:#ffffff,stroke:#d62728,stroke-width:1px;
classDef notify fill:#2ca02c,color:#ffffff,stroke:#2ca02c,stroke-width:1px;

%% ---------------- ENRICHMENT ----------------
subgraph E["Alert Intake & Enrichment"]
    A1["Ingest SIEM Alert"]:::enrich
    A2["Normalize Fields"]:::enrich
    A3["Context Enrichment"]:::enrich
    A1 --> A2 --> A3
end

%% ---------------- TRIAGE ----------------
subgraph T["Automated Triage"]
    T1["Initial Severity Scoring"]:::analysis
    T2["Deduplication Check"]:::analysis
    A3 --> T1 --> T2
end

%% ---------------- ANALYSIS (PARALLEL) ----------------
subgraph AN["Parallel Analysis"]
    H1["Hash Analysis"]:::analysis
    F1["File Analysis"]:::analysis
    IP1["IP Reputation Check"]:::analysis
    U1["Host & User Analysis"]:::analysis
end

T2 --> H1
T2 --> F1
T2 --> IP1
T2 --> U1

%% ---------------- DECISION ----------------
D1{"Threat Confirmed?"}:::decision

H1 --> D1
F1 --> D1
IP1 --> D1
U1 --> D1

%% ---------------- RESPONSE ----------------
subgraph R["Response Actions"]
    R1["Auto Containment"]:::response
    R2["Block IP / Isolate Host"]:::response
    R3["Preserve Evidence"]:::response
    R1 --> R2 --> R3
end

D1 -->|Yes| R1

%% ---------------- HUMAN REVIEW ----------------
subgraph HR["Human Review"]
    HR1["SOC Analyst Review"]:::decision
    HR2["Manual Decision"]:::decision
    HR1 --> HR2
end

D1 -->|Uncertain| HR1

%% ---------------- NOTIFICATION ----------------
subgraph N["Closure & Reporting"]
    N1["Create / Update Incident"]:::notify
    N2["Notify IR & SOC Leads"]:::notify
    N3["Generate Final Report"]:::notify
    N1 --> N2 --> N3
end

R3 --> N1
HR2 --> N1
"""

        st.markdown("### 🧭 SOAR Execution Flow")
        render_mermaid(mermaid_diagram)

        # ---------------- Download Mermaid ----------------
        st.download_button(
            label="⬇️ Download Playbook (Mermaid)",
            data=mermaid_diagram,
            file_name="soar_deployment_playbook.mmd",
            mime="text/plain"
        )
