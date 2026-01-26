# core/diagram_engine.py

def generate_mermaid_flow():
    """
    Returns Mermaid flowchart code for SOAR Deployment execution
    """

    return """
flowchart TD

%% ===== Styles =====
classDef start fill:#2563eb,color:#ffffff,stroke:#1e40af,stroke-width:2px;
classDef process fill:#3b82f6,color:#ffffff,stroke:#1e40af;
classDef decision fill:#f59e0b,color:#000000,stroke:#b45309,stroke-width:2px;
classDef auto fill:#dc2626,color:#ffffff,stroke:#7f1d1d;
classDef human fill:#7c3aed,color:#ffffff,stroke:#4c1d95;
classDef evidence fill:#2563eb,color:#ffffff,stroke:#1e40af;
classDef notify fill:#16a34a,color:#ffffff,stroke:#14532d;

%% ===== Nodes =====
A[Alert Validation & Enrichment]:::start
B[Threat Intelligence Lookup]:::process
C{Threat Confirmed?}:::decision

D[Auto Containment]:::auto
E[Isolate Host / Block IP]:::auto
F[Preserve Evidence]:::evidence
G[Notify IR Team]:::notify

H[Human Review]:::human
I[SOC Analyst Decision]:::human

%% ===== Flow =====
A --> B --> C
C -- Yes --> D --> E --> F --> G
C -- Uncertain --> H --> I
"""
