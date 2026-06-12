import json
from app.services.groq_service import client


def classify_intent(user_message: str) -> str:
    prompt = f"""
You are classifying customer messages for a restaurant WhatsApp assistant.

Return ONLY valid JSON.

Allowed intents:
- greeting
- menu_request
- availability_question
- recommendation
- general_chat

Examples:

Message: "hello"
Output: {{"intent":"greeting"}}

Message: "hi"
Output: {{"intent":"greeting"}}

Message: "what do you have?"
Output: {{"intent":"menu_request"}}

Message: "show me the menu"
Output: {{"intent":"menu_request"}}

Message: "is pistachio available?"
Output: {{"intent":"availability_question"}}

Message: "do you have avocado with ashta?"
Output: {{"intent":"availability_question"}}

Message: "is it found in the menu?"
Output: {{"intent":"availability_question"}}

Message: "what is popular?"
Output: {{"intent":"recommendation"}}

Message: "recommend something cold"
Output: {{"intent":"recommendation"}}

Message: "I want something refreshing"
Output: {{"intent":"recommendation"}}

Classify this message:

"{user_message}"

Return JSON only:
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return data.get("intent", "general_chat")
    except Exception:
        return "general_chat"