from app.services.groq_service import ask_juice_bar_ai


def get_ai_reply(user_message: str):
    try:
        return ask_juice_bar_ai(user_message)
    except Exception:
        return (
            "Sorry, I couldn't process that right now.\n"
            "You can send MENU to browse or ORDER to start ordering."
        )