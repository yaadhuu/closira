# Closira — AI Customer Support Agent

An AI-powered customer support workflow built for **Bloom Aesthetics Clinic** as part of the **Closira AI Engineering Intern Assignment**.

The system handles inbound customer conversations end-to-end by:
- answering questions using SOP-based knowledge
- qualifying leads through structured questions
- detecting escalation scenarios
- generating structured conversation summaries

---

# Features

## 1. FAQ Answering
Answers customer questions strictly from the provided SOP data.

- No hallucinated responses
- SOP acts as the single source of truth
- Graceful handling of unknown questions

---

## 2. Lead Qualification
Collects structured customer information through natural conversation.

Questions include:
- treatment interest
- previous aesthetic experience
- referral source

---

## 3. Escalation Detection
Detects when a conversation should be handed to a human agent.

Escalation triggers include:
- out-of-scope questions
- complaints or frustration
- medical questions outside SOP scope
- explicit request for human support
- repeated low-confidence responses

---

## 4. Conversation Summary
Generates a structured session summary at the end of each interaction.

Summary includes:
- customer intent
- important details collected
- SOP gaps
- escalation reasons
- recommended next action

---

# Workflow

```text
Customer Message
       ↓
AI responds using SOP only
       ↓
JSON response parsed by backend
       ↓
Escalation logic checked
       ↓
Lead qualification questions collected
       ↓
Session summary generated on exit
```

---

# Tech Stack

- Python 3.10+
- Groq API
- LLaMA 3.3 70B (`llama-3.3-70b-versatile`)
- groq Python SDK
- python-dotenv

---

# Project Structure

```text
closira/
├── main.py
├── sop.json
├── prompt_design.md
├── README.md
├── requirements.txt
└── test_transcripts/
    ├── in_scope.txt
    ├── out_of_scope.txt
    ├── escalation.txt
    ├── qualification.txt
    └── summary.txt
```

---

# Setup

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd closira
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
```

## 4. Run the Application

```bash
python main.py
```

Type `exit` anytime to end the conversation and generate the session summary.

---

# Structured JSON Output

The AI always responds in structured JSON format:

```json
{
  "message": "response to customer",
  "escalate": false,
  "escalation_reason": null,
  "confidence": "high"
}
```

This allows the backend to:
- detect escalation programmatically
- avoid unreliable text parsing
- track confidence levels cleanly

---

# Design Decisions

- SOP-grounded responses to prevent hallucinations
- Structured JSON outputs for reliable workflow control
- Confidence-based escalation for uncertain conversations
- Lightweight CLI implementation focused on AI workflow logic

---

# Limitations

- CLI only — no frontend or messaging integration
- No persistent memory between sessions
- Sentiment detection relies on LLM reasoning
- Qualification flow is rule-based, not dynamically timed
- Full conversation history is sent each turn, which may increase token usage in long sessions

---

# Test Scenarios Included

The `test_transcripts/` folder contains sample conversations for:

1. In-SOP FAQ handling  
2. Out-of-scope escalation  
3. Complaint/escalation detection  
4. Lead qualification flow  
5. Session summary generation
