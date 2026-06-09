import os
from dotenv import load_dotenv
from groq import Groq

from app.database import SessionLocal
from app.models import Category, MenuItem, ItemPrice
from sqlalchemy import or_

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def build_menu_context():
    db = SessionLocal()

    try:
        context = ""

        categories = db.query(Category).all()

        for category in categories:
            context += f"\nCategory: {category.name_ar} ({category.name_en})\n"

            items = (
                db.query(MenuItem)
                .filter(MenuItem.category_id == category.id)
                .all()
            )

            for item in items:
                context += f"- {item.name_ar} ({item.name_en})\n"

                prices = (
                    db.query(ItemPrice)
                    .filter(ItemPrice.item_id == item.id)
                    .all()
                )

                for price in prices:
                    context += f"  {price.size_ar}: {price.price_lbp} LBP\n"

        return context

    finally:
        db.close()

    

def ask_juice_bar_ai(user_message: str):
    menu_context = build_menu_context()

    system_prompt = f"""
You are a friendly WhatsApp assistant for Ramadan Juice in Lebanon.

Language rules:
- If the customer writes Arabic, reply in clear Lebanese/Modern Arabic.
- IMPORTANT: If an item is not explicitly present in MENU, do not mention it.
- If you are unsure, say: "لا أجد هذا الصنف في القائمة الحالية."
- If the customer writes English, reply in English.
- Keep the answer short and natural.

Recommendation rules:
-If the customer mentions a fruit, ingredient, flavor, or craving, recommend matching menu items.
- Recommend at most 2 or 3 items.
- Do not list everything.
- Mention prices only if the customer asks for prices.
- Use only the menu below.
- Never invent items.
- If the customer wants to order, tell them to send ORDER or طلب.

Style:
- Sound like a polite restaurant employee.
- Use simple friendly language.
- Avoid long explanations.

MENU:
{menu_context}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.6
    )

    return response.choices[0].message.content