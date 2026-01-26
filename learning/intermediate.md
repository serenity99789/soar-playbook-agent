# Intermediate Level — SOC Workflows & Automation

## What you will learn
By the end of this level, you should understand:
- How SOC investigations flow
- How SOAR playbooks are structured
- Where automation helps most
- Where automation must stop

---

## 1. SOC Investigation Flow
A typical investigation includes:
1. Alert review
2. Context enrichment
3. Threat validation
4. Decision making
5. Response or closure

This flow is **repeatable** — which makes it automatable.

---

## 2. Context Enrichment
Enrichment answers questions like:
- Who owns this asset?
- Is this IP malicious?
- Has this user done this before?

SOAR excels at enrichment.

---

## 3. Decision Points
Not all decisions should be automated.

Good automation decisions:
- Known bad indicators
- Clear policy violations

Bad automation decisions:
- Ambiguous behavior
- High business impact actions

---

## 4. What is a SOAR Playbook?
A playbook is:
- A structured workflow
- With steps, conditions, and actions
- Designed to handle a specific scenario

Playbooks encode **experience**, not just logic.

---

## 5. Human-in-the-Loop
Human approval is required when:
- Actions affect users or systems
- Confidence is low
- Business risk is high

This is intentional design, not a limitation.

---

## 6. Common SOAR Mistakes
- Over-automation
- Ignoring false positives
- Treating SOAR like magic

Good SOAR design is **conservative and deliberate**.

---

## What’s next?
You’re ready to learn:
- How playbooks are governed
- How SOAR scales
- How leadership evaluates automation risk

