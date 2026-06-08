import os
from dotenv import load_dotenv
from openai import OpenAI   
from app.database import SessionLocal
from app.models import Category, MenuItem, ItemPrice

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_menu_context():
    db = SessionLocal()

    try:
        context = ""

        categories = db.query(Category).all()

        for category in categories:
            context += (
                f"\nCategory: {category.name_ar}"
                f" ({category.name_en})\n"
            )

            items = (
                db.query(MenuItem)
                .filter(MenuItem.category_id == category.id)
                .all()
            )

            for item in items:
                context += (
                    f"- {item.name_ar}"
                    f" ({item.name_en})\n"
                )

                prices = (
                    db.query(ItemPrice)
                    .filter(ItemPrice.item_id == item.id)
                    .all()
                )

                for price in prices:
                    context += (
                        f"  {price.size_ar}: "
                        f"{price.price_lbp} LBP\n"
                    )

        return context

    finally:
        db.close()

def ask_juice_bar_ai(user_message: str):
    menu_context = build_menu_context()

    system_prompt = f"""
You are a helpful restaurant assistant for Ramadan Juice.

Rules:
- Answer in the same language as the customer.
- Use only menu information provided below.
- Do not invent items or prices.
- Recommend drinks based on customer preferences.
- Be concise.

MENU:
{menu_context}
"""

    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content