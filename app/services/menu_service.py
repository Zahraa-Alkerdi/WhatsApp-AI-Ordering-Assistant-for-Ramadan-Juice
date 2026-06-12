from app.models import Category
from app.models import MenuItem
from app.models import ItemPrice

def build_menu_text(db):
        menu_text = "🍹 Ramadan Juice Menu 🍹\n\n"

        categories = db.query(Category).all()

        for number, category in enumerate(categories, start=1):
            menu_text += (
                f"{number}. "
                f"{category.name_ar} - "
                f"{category.name_en}\n"
            )

        menu_text += (
            "\nSend a category name to view items.\n"
            "أرسل اسم القسم لعرض الأصناف."
        )

        return menu_text

def build_category_text(db, category):
    items = (
        db.query(MenuItem)
        .filter(MenuItem.category_id == category.id)
        .all()
    )

    items_text = (
        f"🧃 {category.name_en} - {category.name_ar}\n\n"
    )

    for number, item in enumerate(items, start=1):
        items_text += (
            f"{number}. "
            f"{item.name_ar} - "
            f"{item.name_en}\n"
        )

    items_text += (
        "\nSend an item name to view details.\n"
        "أرسل اسم الصنف لعرض التفاصيل."
    )

    return items_text


def build_item_text(db, item):
    prices = (
        db.query(ItemPrice)
        .filter(ItemPrice.item_id == item.id)
        .all()
    )

    item_text = (
        f"🍹 {item.name_ar} - {item.name_en}\n\n"
    )

    if item.description_ar:
        item_text += f"{item.description_ar}\n\n"

    if item.description_en:
        item_text += f"{item.description_en}\n\n"

    item_text += "💰 Prices / الأسعار:\n\n"

    for price in prices:
        item_text += (
            f"• {price.size_ar} / {price.size_en}: "
            f"{price.price_lbp:,} LBP\n"
        )

    item_text += (
        "\n🛒 Send ORDER to start ordering.\n"
        "أرسل ORDER لبدء الطلب."
    )

    return item_text