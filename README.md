# Closira — AI Customer Support Agent

An AI-powered customer support workflow built for Bloom Aesthetics Clinic, developed as part of the Closira AI Engineering Intern assignment.

The agent handles inbound customer enquiries end-to-end — answering questions from a defined SOP, qualifying leads, detecting escalation triggers, and generating structured session summaries.

---

## How it works
Customer sends message
↓
Aria responds using only SOP data (no hallucination)
↓
Code checks JSON response for escalation flag
↓
If escalate → log reason, notify human agent
↓
After first answer → collect 3 qualification questions
↓
Customer types exit → structured summary generated

## Four Stages

| Stage | What happens |
|---|---|
| FAQ Answering | Responds strictly from SOP data — no guessing |
| Lead Qualification | Asks 3 natural questions to understand the customer |
| Escalation Detection | Flags complaints, out-of-scope questions, angry sentiment |
| Session Summary | Structured summary with intent, gaps, and next action |

---

## Tech Stack

- **Python 3.10+**
- **Groq API** — LLaMA 3.3 70B (`llama-3.3-70b-versatile`)
- **groq** — Groq Python SDK
- **python-dotenv** — environment variable management

---

## Project Structure
closira/
├── main.py                  # Core conversation loop and AI workflow
├── sop.json                 # Business knowledge base (single source of truth)
├── prompt_design.md         # Prompt design decisions and reasoning
├── requirements.txt         # Python dependencies
├── README.md
└── test_transcripts/
├── in_scope.txt         # Test 1: question answered from SOP
├── out_of_scope.txt     # Test 2: escalation on unknown service
├── escalation.txt       # Test 3: angry customer detected
├── qualification.txt    # Test 4: lead qualification flow
└── summary.txt          # Test 5: full session with summary

---

## Setup

**1. Clone the repo**
```bash
git clone <your-repo-url>
cd closira
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Groq API key**

Create a `.env` file in the root:
GROQ_API_KEY=your_key_here

**4. Run**
```bash
python main.py
```

Type `exit` at any point to end the session and generate the summary.

---

## Key Design Decision

The model always responds in **JSON** — not plain text.

```json
{
  "message": "response to customer",
  "escalate": false,
  "escalation_reason": null,
  "confidence": "high"
}
```

This makes escalation detection programmatic and reliable. The code checks `result["escalate"]` directly — no string matching, no guessing from plain text.

---

## Escalation Triggers

- Customer asks about a service not in the SOP
- Complaint or frustration detected
- Medical question outside SOP scope
- Customer requests a human agent
- 2 or more low-confidence responses in one session

---

## Limitations

- CLI only — no frontend or WhatsApp integration (out of scope for this prototype)
- Qualification questions currently trigger after the first message regardless of context
- Sentiment detection relies on LLM judgment, not a dedicated model
- No persistent storage between sessions