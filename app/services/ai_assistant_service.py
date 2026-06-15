import os
from app.services.groq_service import ask_juice_bar_ai
from app.services.openai_service import ask_juice_bar_openai


def get_ai_reply(user_message: str):
    provider = os.getenv("AI_PROVIDER", "groq")

    try:
        if provider == "openai":
            return ask_juice_bar_openai(user_message)

        return ask_juice_bar_ai(user_message)

    except Exception:
        return (
            "Sorry, I couldn't process that right now.\n"
            "You can send MENU to browse or ORDER to start ordering."
        )