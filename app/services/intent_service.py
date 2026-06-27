import os
import json
from app.services.openai_service import client


def _keyword_classify(user_message: str) -> str:
    msg = user_message.lower().strip()

    greetings = [
        "hi", "hello", "hey", "good morning", "good evening",
        "مرحبا", "هلا", "يسلمو", "سلام", "صباح الخير", "مساء الخير",
        "هلو", "هاي"
    ]
    menu_words = [
        "menu", "what do you have", "show me", "what's available",
        "مينو", "المنيو", "القائمة", "شو عندكم", "شو في"
    ]
    availability = [
        "available", "do you have", "is there", "can i get",
        "في عندكم", "موجود", "في", "عندكم"
    ]
    recommendation = [
        "recommend", "popular", "best", "suggest", "what's good",
        "شو بتنصح", "شو أحلى", "شو منيح", "شو مشهور", "شو الأحسن"
    ]
    order_words = [
        "i want", "i'd like", "can i order", "give me",
        "بدي", "عطني", "خدلي", "اطلبلي"
    ]

    if any(w in msg for w in greetings):
        return "greeting"
    if any(w in msg for w in menu_words):
        return "menu_request"
    if any(w in msg for w in order_words):
        return "order_request"
    if any(w in msg for w in availability):
        return "availability_question"
    if any(w in msg for w in recommendation):
        return "recommendation"

    return None  # unknown — let AI decide


def classify_intent(user_message: str) -> str:
    # Step 1 — try keywords first (free, instant)
    keyword_result = _keyword_classify(user_message)

    if keyword_result:
        return keyword_result

    # Step 2 — only call AI if keywords couldn't classify
    if os.getenv("AI_ENABLED", "true") == "false":
        return "general_chat"

    prompt = f"""
You are classifying customer messages for a restaurant WhatsApp assistant.

Return ONLY valid JSON.

Allowed intents:
- greeting
- menu_request
- availability_question
- recommendation
- order_request
- general_chat

Classify this message:
"{user_message}"

Return JSON only:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20
        )
        data = json.loads(response.choices[0].message.content)
        return data.get("intent", "general_chat")
    except Exception:
        return "general_chat"