from sqlalchemy import or_
from app.models import MenuItem


def find_matching_items(db, query: str):
    query = query.strip()

    items = (
        db.query(MenuItem)
        .filter(
            or_(
                MenuItem.name_ar.ilike(f"%{query}%"),
                MenuItem.name_en.ilike(f"%{query}%")
            )
        )
        .all()
    )

    return items