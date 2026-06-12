from app.services.groq_service import ask_juice_bar_ai

def classify_intent(user_message: str) -> str:
    message = user_message.lower().strip()

    if message in ["hi", "hello", "hey", "مرحبا", "اهلا", "أهلا"]:
        return "greeting"

    if any(word in message for word in ["menu", "منيو", "المنيو", "القائمة", "شو عندكن"]):
        return "menu"

    if any(word in message for word in ["order", "طلب", "بدي اطلب", "i want to order"]):
        return "order"

    if any(word in message for word in ["recommend", "popular", "best", "بتنصح", "منعش", "بارد"]):
        return "recommendation"

    return "ai"