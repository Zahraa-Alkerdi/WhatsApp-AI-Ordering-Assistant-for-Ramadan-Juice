import json
from app.services.openai_service import client


def extract_order_info(user_message: str):
    prompt = f"""
Extract order information from this restaurant WhatsApp message.

Return ONLY valid JSON.

Fields:
- item_name: string or null
- size: string or null
- quantity: integer or null
- notes: string or null

Rules:
- Extract only what the customer clearly mentioned.
- If quantity is missing, use 1.
- Notes include customizations like no ashta, extra pistachio, less sugar.
- Do not invent item names.

Examples:

Message: "بدي أفوكا وسط بلا قشطة"
Output:
{{"item_name":"أفوكا","size":"وسط","quantity":1,"notes":"بلا قشطة"}}

Message: "I want 2 large avocado without ashta"
Output:
{{"item_name":"avocado","size":"large","quantity":2,"notes":"without ashta"}}

Message: "حليب وموز كبير"
Output:
{{"item_name":"حليب وموز","size":"كبير","quantity":1,"notes":null}}

Message:
"{user_message}"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=120
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "item_name": None,
            "size": None,
            "quantity": None,
            "notes": None
        }