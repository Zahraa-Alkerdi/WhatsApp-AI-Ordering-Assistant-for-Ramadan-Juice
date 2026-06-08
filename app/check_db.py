from app.database import SessionLocal
from app.models import Category

db = SessionLocal()

try:
    categories = (
        db.query(Category)
        .all()
    )

    for category in categories:
        print(
            f"ID: {category.id} | "
            f"Arabic: {category.name_ar} | "
            f"English: {category.name_en}"
        )


finally:
    db.close()