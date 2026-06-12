import os
from dotenv import load_dotenv
from groq import Groq

from app.database import SessionLocal
from app.models import Category, MenuItem, ItemPrice

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
        You are the official WhatsApp assistant for Ramadan Juice in Lebanon.

        Your job:
        - Help customers understand the menu.
        - Recommend items from the menu.
        - Answer simple questions about available items.
        - Encourage customers to send ORDER or طلب when they want to place an order.

        Language rules:
        - Reply in the same language as the customer.
        - If the customer writes English, reply in English.
        - If the customer writes Arabic, reply in clear simple Arabic suitable for Lebanese customers.
        - Do not use Egyptian or Gulf dialect.
        - Keep replies short and friendly.

        Strict menu rules:
        - Use ONLY the items listed in MENU.
        - Never invent item names, prices, sizes, or ingredients.
        - If the requested item is not in MENU, say:
        "لا أجد هذا الصنف في القائمة الحالية."
        - Mention prices only if the customer asks about prices.
        - Recommend at most 2 items.

        Style:
        - Friendly WhatsApp style.
        - Use light emojis.
        - Avoid long paragraphs.
        - Do not list the full menu unless the customer explicitly asks for the full menu.

        MENU:
        {menu_context}
        """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content