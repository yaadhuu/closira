# Prompt Design — Closira AI Agent

## Overview

When I started building this, I realized the hardest part wasn't the code — it was
figuring out how to make the AI behave reliably in a real customer conversation.
Anyone can get a model to chat. The challenge is making it stay within boundaries,
detect when it's out of its depth, and hand off gracefully without the customer
feeling abandoned.

This document explains the decisions I made and why.

---

## System Prompt

The system prompt is doing three things at once:
- Giving the AI its identity (Aria, a clinic support agent)
- Injecting the SOP as the only allowed knowledge source
- Enforcing a structured JSON response format

I load the SOP from `sop.json` and embed it directly into the prompt using an
f-string. The model never reaches outside that data — if it's not in the SOP,
Aria doesn't know it.

---

## Hallucination Prevention

The simplest and most effective thing I did was tell the model explicitly:
don't make things up. If it's not in the SOP, say so and escalate.

This sounds obvious but the default behaviour of most LLMs is to fill gaps
confidently. I had to actively push against that by making "I don't know"
the correct and expected answer for out-of-scope questions.

The result is the system fails gracefully — it hands off instead of guessing.

---

## Why JSON Output

Early on I thought about just parsing the model's plain text response for
keywords like "sorry" or "I can't help" to detect escalation. That's fragile
and breaks easily.

Instead I tell the model to always respond in this format:

```json
{
  "message": "what aria says to the customer",
  "escalate": false,
  "escalation_reason": null,
  "confidence": "high"
}
```

Now the code just checks `result["escalate"]`. Clean, reliable, no guessing.
The confidence field was something I added later when I noticed the model
would sometimes hedge without actually flagging escalation — tracking two
low-confidence responses in a row catches those edge cases.

---

## Escalation Logic

## Escalation Logic

| Trigger                    | How it's caught                                     |
|----------------------------|-----------------------------------------------------|
| Out-of-scope question      | Hard rule in prompt — model must set escalate: true |
| Complaint or frustration   | Model detects sentiment                             |
| Medical question           | Model identifies it's outside SOP scope             |
| Customer asks for human    | Model detects explicit intent                       |
| 2+ low-confidence responses| Tracked in code via `low_confidence_count`          |

I spent some time getting the out-of-scope escalation right. The model kept
trying to be helpful and work around the gap instead of flagging it. I had to
add an explicit hard rule — "if it's not in the SOP, escalate, no exceptions."

All escalations are logged with the trigger message and reason so a human
agent has full context when they follow up.

---

## Tone

I named the assistant Aria because it sounds human without being too casual.
The prompt tells her to be warm and concise — this is an aesthetics clinic,
customers are sometimes nervous or self-conscious, so the tone matters.

Temperature is set to 0.3. I tried higher values early on and the model started
deviating from the JSON format. Lower keeps it consistent without being robotic.

---

## Lead Qualification

Rather than interrupting the conversation with a formal questionnaire, I collect
three questions naturally after the first exchange:
1. What treatment are you interested in?
2. Have you had treatments before?
3. How did you hear about us?

These answers feed directly into the session summary so a human agent doesn't
have to start from scratch when they follow up.

---

## What I'd improve with more time

- The qualification questions currently fire after the first message regardless
  of context — smarter stage detection would make this feel more natural
- Sentiment detection relies entirely on the LLM's judgment. A dedicated
  sentiment model would be more reliable at scale
- Right now there's no memory between sessions — a production version would
  persist customer data and recognise returning users