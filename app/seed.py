import json
from pathlib import Path

from app.database import SessionLocal, engine
from app.models import Base, Category, MenuItem, ItemPrice


Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json(filename):
    file_path = DATA_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def seed_categories(db):
    categories = load_json("categories.json")

    for category_data in categories:
        existing_category = (
            db.query(Category)
            .filter(Category.name_ar == category_data["name_ar"])
            .first()
        )

        if existing_category:
            print(f"Category already exists: {category_data['name_ar']}")
        else:
            category = Category(**category_data)
            db.add(category)
            print(f"Added category: {category_data['name_ar']}")


def seed_menu_items(db):
    menu_items = load_json("menu_items.json")

    for item_data in menu_items:
        category = (
            db.query(Category)
            .filter(Category.name_ar == item_data["category_ar"])
            .first()
        )

        if not category:
            print(f"Category not found: {item_data['category_ar']}")
            continue

        existing_item = (
            db.query(MenuItem)
            .filter(
                MenuItem.name_ar == item_data["name_ar"],
                MenuItem.category_id == category.id,
            )
            .first()
        )

        if existing_item:
            print(f"Item already exists: {item_data['name_ar']}")
        else:
            category_ar = item_data.pop("category_ar")

            item = MenuItem(
                category_id=category.id,
                **item_data
            )

            db.add(item)
            print(f"Added item: {item.name_ar}")

def seed_item_prices(db):
    prices = load_json("item_prices.json")

    for price_data in prices:
        category = (
            db.query(Category)
            .filter(Category.name_ar == price_data["category_ar"])
            .first()
        )

        if not category:
            print(f"Category not found: {price_data['category_ar']}")
            continue

        item = (
            db.query(MenuItem)
            .filter(
                MenuItem.name_ar == price_data["item_name_ar"],
                MenuItem.category_id == category.id,
            )
            .first()
        )

        if not item:
            print(f"Item not found: {price_data['item_name_ar']}")
            continue

        existing_price = (
            db.query(ItemPrice)
            .filter(
                ItemPrice.item_id == item.id,
                ItemPrice.size_ar == price_data["size_ar"],
            )
            .first()
        )

        if existing_price:
            print(
                f"Price already exists: "
                f"{price_data['item_name_ar']} - {price_data['size_ar']}"
            )
        else:
            category_ar = price_data.pop("category_ar")
            item_name_ar = price_data.pop("item_name_ar")

            price = ItemPrice(
                item_id=item.id,
                **price_data
            )

            db.add(price)
            print(f"Added price: {item.name_ar} - {price.size_ar}")



def seed_all():
    db = SessionLocal()

    try:
        seed_categories(db)
        db.commit()

        seed_menu_items(db)
        db.commit()

        seed_item_prices(db)
        db.commit()

        print("Seeding completed successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_all()