import os
from app.services.openai_service import ask_juice_bar_openai


def get_ai_reply(user_message: str):
    if os.getenv("AI_ENABLED", "true") == "false":
        return "🤖 AI disabled in test mode. Send MENU or ORDER."
    
    provider = os.getenv("AI_PROVIDER")

    try:
        return ask_juice_bar_openai(user_message)

    except Exception:
        return (
            "Sorry, I couldn't process that right now.\n"
            "You can send MENU to browse or ORDER to start ordering."
        )