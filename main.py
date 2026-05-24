import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=API_KEY)

MODEL = "llama-3.3-70b-versatile"


def load_sop():
    with open("sop.json", "r", encoding="utf-8") as file:
        return json.load(file)


def build_system_prompt(sop):

    return f"""
You are Aria, the virtual customer assistant for {sop['business_name']}.

You speak like a calm, professional clinic coordinator — warm, reassuring, and conversational.

Your goals:
1. Answer customer questions using ONLY the SOP information provided
2. Help customers feel comfortable and guided
3. Collect lead information naturally during conversation
4. Escalate sensitive or unsupported situations to a human when needed

IMPORTANT BEHAVIOR RULES:

- Only use information from the SOP
- Never invent treatments, pricing, medical advice, or policies
- If information is unavailable, say so honestly
- Do NOT sound robotic or overly formal
- When escalating, keep your message warm — but always set escalate to true in the JSON
- Continue being conversational even when escalation is internally triggered
- If escalation is needed, smoothly recommend a specialist or consultation
- Avoid making the customer feel rejected or blocked
- Keep responses concise and natural. Avoid overly long explanations.
- Keep responses under 2-3 sentences. Be concise. Don't over-explain or give examples unless asked.

HARD RULES — non negotiable:
- If a customer asks about ANY service or treatment NOT explicitly listed in the SOP, you MUST set escalate to true. No exceptions.
- Do not try to handle it yourself. Flag it.

MEDICAL & SENSITIVE QUESTIONS:
If the user asks medical or treatment-specific questions outside the SOP:
- avoid giving medical advice
- gently redirect toward consultation
- reassure the customer
- internally escalate if appropriate

LEAD QUALIFICATION:
Do not interrogate the customer.
Ask qualification questions naturally and only when relevant.

Examples:
Instead of:
"Before continuing, answer these questions."

Prefer:
"Just so I can guide you better — have you had treatments before?"

ESCALATION GUIDELINES:
Escalate internally when:
- customer is angry
- complaint detected
- user requests human support
- medical advice is requested outside SOP
- multiple low-confidence responses occur
- customer asks about a service or topic NOT listed in the SOP

Do not expose internal escalation logic unless necessary.

SOP DATA:
{json.dumps(sop, indent=2)}

You MUST always return valid JSON only.

Format:
{{
  "message": "natural conversational response",
  "escalate": false,
  "escalation_reason": null,
  "confidence": "high"
}}

confidence values:
- high
- medium
- low

No markdown.
Only JSON.
"""


def extract_json(text):

    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def get_ai_response(history, system_prompt):

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                *history
            ],
            temperature=0.3,
            max_tokens=500
        )

        raw_output = response.choices[0].message.content.strip()

        parsed = extract_json(raw_output)

        if parsed:
            return parsed

        return {
            "message": "Sorry, I ran into a formatting issue.",
            "escalate": True,
            "escalation_reason": "invalid model response",
            "confidence": "low"
        }

    except Exception as error:

        return {
            "message": "Something went wrong on our side. A human agent will follow up shortly.",
            "escalate": True,
            "escalation_reason": str(error),
            "confidence": "low"
        }


def collect_customer_details():

    print("\nARIA: Before we continue, can I ask a few quick questions?\n")

    questions = [
        "What treatment are you interested in?",
        "Have you had aesthetic treatments before?",
        "How did you hear about us?"
    ]

    answers = {}

    for index, question in enumerate(questions, start=1):

        print(f"ARIA: {question}")

        answer = input("YOU: ").strip()

        answers[f"question_{index}"] = {
            "question": question,
            "answer": answer
        }

        print()

    print("ARIA: Thanks for sharing that.\n")

    return answers


def generate_summary(history, qualification_data, escalations):

    prompt = f"""
A customer support session has ended.

Conversation:
{json.dumps(history, indent=2)}

Customer Qualification:
{json.dumps(qualification_data, indent=2)}

Escalations:
{json.dumps(escalations, indent=2)}

Return ONLY valid JSON in this format:

{{
  "customer_intent": "summary",
  "key_details": ["important details"],
  "sop_gaps": ["missing SOP information"],
  "escalations": ["reasons"],
  "next_action": "recommended next step"
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=600
    )

    raw_output = response.choices[0].message.content.strip()

    parsed = extract_json(raw_output)

    return parsed if parsed else {"raw_summary": raw_output}


def main():

    print("=" * 55)
    print("      Closira — AI Support Assistant")
    print("         Bloom Aesthetics Clinic")
    print("=" * 55)

    print("Type 'exit' anytime to end the session.\n")

    sop = load_sop()

    system_prompt = build_system_prompt(sop)

    conversation_history = []
    qualification_data = {}
    escalations = []

    low_confidence_count = 0
    asked_qualification = False

    print("ARIA: Hi! Welcome to Bloom Aesthetics Clinic.")
    print("ARIA: How can I help you today?\n")

    while True:

        user_input = input("YOU: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "bye"]:

            print("\nGenerating session summary...\n")

            summary = generate_summary(
                conversation_history,
                qualification_data,
                escalations
            )

            print("=" * 55)
            print("SESSION SUMMARY")
            print("=" * 55)

            print(json.dumps(summary, indent=2))

            print("=" * 55)

            break

        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        result = get_ai_response(
            conversation_history,
            system_prompt
        )

        message = result.get("message", "Something went wrong.")

        should_escalate = result.get("escalate", False)

        escalation_reason = result.get(
            "escalation_reason",
            None
        )

        confidence = result.get("confidence", "low")

        conversation_history.append({
            "role": "assistant",
            "content": message
        })

        if confidence == "low":
            low_confidence_count += 1

        if low_confidence_count >= 2 and not should_escalate:

            should_escalate = True

            escalation_reason = (
                "multiple low-confidence responses"
            )

        print(f"\nARIA: {message}\n")

        if should_escalate:

            escalations.append({
                "trigger": user_input,
                "reason": escalation_reason
            })

            print("-" * 55)
            print("[ESCALATION FLAGGED]")
            print(f"Reason : {escalation_reason}")
            print("Action : Human follow-up required")
            print("-" * 55)

            print(
                "\nARIA: I've flagged this conversation for a human specialist.\n"
            )

        if not asked_qualification and len(conversation_history) >= 2:

            asked_qualification = True

            qualification_data = collect_customer_details()


if __name__ == "__main__":
    main()