import json
from app.services.openai_service import client
import os


def extract_order_info(user_message: str):
    if os.getenv("AI_ENABLED", "true") == "false":
        return {
            "items": [
                {
                    "item_name": user_message,
                    "size": None,
                    "quantity": 1,
                    "notes": None
                }
            ]
        }
     
    prompt = f"""
Extract restaurant order information from this WhatsApp message.

Return ONLY valid JSON.

Format:
{{
  "items": [
    {{
      "item_name": "string or null",
      "size": "string or null",
      "quantity": 1,
      "notes": "string or null"
    }}
  ]
}}

Rules:
- Extract all ordered items, not only one.
- If the customer mentions two or more items, return all of them in the items list.
- If quantity is missing, use 1.
- Notes include customizations like no ashta, extra pistachio, no cashew, less sugar.
- If a note applies to a specific item, put it only on that item.
- Do not invent items, sizes, or notes.

Examples:

Message: "بدي أفوكا وسط بلا قشطة"
Output:
{{
  "items": [
    {{
      "item_name": "أفوكا",
      "size": "وسط",
      "quantity": 1,
      "notes": "بلا قشطة"
    }}
  ]
}}

Message: "بدي وحدة كريب نيوتيلا وكباية افوكادو مع قشطة بلا كاجو"
Output:
{{
  "items": [
    {{
      "item_name": "كريب نيوتيلا",
      "size": null,
      "quantity": 1,
      "notes": null
    }},
    {{
      "item_name": "افوكادو",
      "size": "كباية",
      "quantity": 1,
      "notes": "مع قشطة بلا كاجو"
    }}
  ]
}}

Message: "I want 2 large avocado without ashta and one Nutella crepe"
Output:
{{
  "items": [
    {{
      "item_name": "avocado",
      "size": "large",
      "quantity": 2,
      "notes": "without ashta"
    }},
    {{
      "item_name": "Nutella crepe",
      "size": null,
      "quantity": 1,
      "notes": null
    }}
  ]
}}

Customer message:
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
      return {"items": []}