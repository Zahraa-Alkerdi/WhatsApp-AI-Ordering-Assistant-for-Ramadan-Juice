from urllib import response

from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.database import SessionLocal, engine
from app.models import Base, Category, MenuItem, ItemPrice, Customer, Order, OrderItem
from app.state import active_conversations
from app.services.ai_service import ask_juice_bar_ai
from app.services.groq_service import ask_juice_bar_ai

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "WhatsApp AI Agent backend is running"}


@app.get("/orders")
def get_orders():
    db = SessionLocal()

    try:
        orders = db.query(Order).all()
        result = []

        for order in orders:
            order_items = []

            for item in order.items:
                order_items.append({
                    "name": item.menu_item.name_ar,
                    "size": item.size_ar,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "subtotal": item.subtotal
                })

            result.append({
                "order_id": order.id,
                "phone_number": order.customer.phone_number,
                "status": order.status,
                "total_price": order.total_price,
                "items": order_items
            })

        return result

    finally:
        db.close()

@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...)
):
    print("Incoming message:", Body)
    print("From:", From)

    user_message = Body.strip()
    normalized_message = user_message.lower()

    response = MessagingResponse()
            
    if normalized_message in ["cancel", "إلغاء"]:
        if From in active_conversations:
            del active_conversations[From]

            response.message(
                "Order cancelled ❌\n\n"
                "تم إلغاء الطلب ❌"
            )
        else:
            response.message(
                "No active order.\n"
                "لا يوجد أي طلب."
            )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    if normalized_message in ["cart", "الفاتورة"]:
        if From not in active_conversations:
            response.message(
                "Your cart is empty.\n"
                "الفاتورة فارغة."
            )
            return Response(content=str(response), media_type="application/xml")

        cart = active_conversations[From]["cart"]

        if not cart:
            response.message(
                "Your cart is empty.\n"
                "الفاتورة فارغة."
            )
            return Response(content=str(response), media_type="application/xml")

        total = sum(item["subtotal"] for item in cart)

        cart_text = "🛒 Your Cart\n\n"

        for number, item in enumerate(cart, start=1):
            cart_text += (
                f"{number}. {item['quantity']} × "
                f"{item['item_name_ar']} "
                f"({item['size_ar']})\n"
                f"   {item['subtotal']:,} LBP\n\n"
            )

        cart_text += (
            f"------------------\n"
            f"Total: {total:,} LBP\n\n"
            f"Send CONFIRM to place the order.\n"
            f"Send CANCEL to cancel the order.\n\n"
            f"المجموع: {total:,} ل.ل\n"
            f"أرسل CONFIRM لتأكيد الطلب.\n"
            f"أرسل CANCEL لإلغاء الطلب."
        )

        response.message(cart_text)

        return Response(content=str(response), media_type="application/xml")
    
    if normalized_message in ["confirm", "تأكيد"]:
        if From not in active_conversations:
            response.message(
                "No active order.\n"
                "لا يوجد أي طلب ."
            )
            return Response(content=str(response), media_type="application/xml")

        cart = active_conversations[From]["cart"]

        if not cart:
            response.message(
                "Your cart is empty.\n"
                "الفاتورة فارغة."
            )
            return Response(content=str(response), media_type="application/xml")

        db = SessionLocal()

        try:
            customer = (
                db.query(Customer)
                .filter(Customer.phone_number == From)
                .first()
            )

            if not customer:
                customer = Customer(
                    phone_number=From
                )

                db.add(customer)
                db.commit()
                db.refresh(customer)

            total_price = sum(
                item["subtotal"]
                for item in cart
            )

            order = Order(
                customer_id=customer.id,
                status="confirmed",
                total_price=total_price
            )

            db.add(order)
            db.commit()
            db.refresh(order)

            for item in cart:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item["item_id"],
                    quantity=item["quantity"],
                    size_ar=item["size_ar"],
                    size_en=item["size_en"],
                    unit_price=item["unit_price"],
                    subtotal=item["subtotal"]
                )

                db.add(order_item)

            db.commit()

            del active_conversations[From]

            response.message(
                f"Order confirmed ✅\n\n"
                f"Order Number: #{order.id}\n"
                f"Total: {total_price:,} LBP\n\n"
                f"Thank you for your order!\n\n"
                f"تم تأكيد الطلب ✅\n"
                f"رقم الطلب: #{order.id}\n"
                f"المجموع: {total_price:,} ل.ل"
            )

        finally:
            db.close()

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    if From in active_conversations:
        conversation = active_conversations[From]

        if conversation["state"] == "choosing_item":
            db = SessionLocal()
            try:
                item = (
                    db.query(MenuItem)
                    .filter(
                        (MenuItem.name_ar == user_message) |
                        (MenuItem.name_en.ilike(user_message))
                    )
                    .first()
                )

                if not item:
                    response.message(
                        "Item not found. Please send a valid item name.\n"
                        "لم يتم العثور على الصنف. أرسل اسم صنف صحيح."
                    )
                else:
                    prices = (
                        db.query(ItemPrice)
                        .filter(ItemPrice.item_id == item.id)
                        .all()
                    )

                    conversation["current_item"] = item.id
                    conversation["state"] = "choosing_size"

                    size_text = f"You selected: {item.name_ar} - {item.name_en}\n\n"
                    size_text += "Available sizes / الأحجام المتوفرة:\n"

                    for number, price in enumerate(prices, start=1):
                        size_text += (
                            f"{number}. {price.size_ar} / {price.size_en} "
                            f"- {price.price_lbp:,} LBP\n"
                        )

                    size_text += "\nSend the size name.\nأرسل اسم الحجم."

                    response.message(size_text)

            finally:
                db.close()

            return Response(content=str(response), media_type="application/xml")
    
        elif conversation["state"] == "choosing_size":
           db = SessionLocal()
           try:
                prices = (
                    db.query(ItemPrice)
                    .filter(
                        ItemPrice.item_id == conversation["current_item"]
                    )
                    .all()
                )

                selected_price = None

                for price in prices:
                    if (
                        user_message == price.size_ar
                        or user_message.lower() == price.size_en.lower()
                    ):
                        selected_price = price
                        break

                if not selected_price:
                    response.message(
                        "Invalid size.\n"
                        "Please send one of the available sizes.\n\n"
                        "حجم غير صحيح.\n"
                        "أرسل أحد الأحجام المتوفرة."
                    )
                else:
                    conversation["selected_price_id"] = selected_price.id
                    conversation["state"] = "choosing_quantity"

                    response.message(
                        f"You selected: {selected_price.size_ar}\n\n"
                        f"How many would you like?\n"
                        f"كم الكمية المطلوبة؟"
                    )

           finally:
                db.close()

           return Response(content=str(response),media_type="application/xml")
        
        elif conversation["state"] == "choosing_quantity":
            if not user_message.isdigit() or int(user_message) <= 0:
                response.message(
                    "Invalid quantity.\n"
                    "Please send a positive number.\n\n"
                    "كمية غير صحيحة.\n"
                    "أرسل رقمًا موجبًا."
                )
            else:
                quantity = int(user_message)

                db = SessionLocal()
                try:
                    price = (
                        db.query(ItemPrice)
                        .filter(ItemPrice.id == conversation["selected_price_id"])
                        .first()
                    )

                    item = (
                        db.query(MenuItem)
                        .filter(MenuItem.id == conversation["current_item"])
                        .first()
                    )

                    conversation["cart"].append({
                        "item_id": item.id,
                        "item_name_ar": item.name_ar,
                        "item_name_en": item.name_en,
                        "size_ar": price.size_ar,
                        "size_en": price.size_en,
                        "quantity": quantity,
                        "unit_price": price.price_lbp,
                        "subtotal": quantity * price.price_lbp
                    })

                    conversation["current_item"] = None
                    conversation["selected_price_id"] = None
                    conversation["state"] = "choosing_item"

                    response.message(
                        f"Added to cart ✅\n\n"
                        f"{quantity} × {item.name_ar} ({price.size_ar})\n"
                        f"Subtotal: {quantity * price.price_lbp:,} LBP\n\n"
                        f"Send another item name to add more.\n"
                        f"Or send CART to view your cart.\n"
                        f"Or send CONFIRM to place the order.\n\n"
                        f"تمت الإضافة إلى السلة ✅\n\n"
                        f"{quantity} × {item.name_ar} ({price.size_ar})\n"
                        f"المجموع: {quantity * price.price_lbp:,} ل.ل\n\n"
                        f"أرسل اسم صنف آخر للإضافة.\n"
                        f"أو أرسل CART لعرض السلة.\n"
                        f"أو أرسل CONFIRM لتأكيد الطلب."
                    )

                finally:
                    db.close()

            return Response(content=str(response), media_type="application/xml")
    
    if normalized_message in ["menu", "مينو", "المنيو", "القائمة"]:
        db = SessionLocal()
        try:
            menu_text = "Ramadan Juice Menu 🧃\n\n"

            categories = db.query(Category).all()

            for number, category in enumerate(categories, start=1):
                menu_text += f"{number}. {category.name_ar} - {category.name_en}\n"

            menu_text += "\nSend a category name to view items.\nأرسل اسم القسم لعرض الأصناف."

            response.message(menu_text)
        finally:
            db.close()

    elif normalized_message in ["order", "طلب"]:
        if From in active_conversations:
            response.message(
                "You already have an active order 🛒\n\n"
                "Send the item name to continue, or send CANCEL to cancel.\n"
                "لديك طلب قيد التحضير.\n"
                "أرسل اسم الصنف للمتابعة أو CANCEL للإلغاء."
            )
        else:
            active_conversations[From] = {
                "state": "choosing_item",
                "current_item": None,
                "current_size": None,
                "cart": []
            }

            response.message(
                "Order started 🛒\n\n"
                "What would you like to order?\n"
                "Send the item name.\n\n"
                "بدأنا الطلب 🛒\n"
                "ماذا تريد أن تطلب؟\n"
                "أرسل اسم الصنف."
            )
    else:
        db = SessionLocal()
        try:
            category = (
                db.query(Category)
                .filter(
                    (Category.name_ar == user_message) |
                    (Category.name_en.ilike(user_message))
                )
                .first()
            )

            if category:
                items = (
                    db.query(MenuItem)
                    .filter(MenuItem.category_id == category.id)
                    .all()
                )

                items_text = f"{category.name_en} 🧃 - {category.name_ar}\n\n"

                for number, item in enumerate(items, start=1):
                    items_text += f"{number}. {item.name_ar} - {item.name_en}\n"

                items_text += "\nSend an item name to view details.\nأرسل اسم الصنف لعرض التفاصيل."

                response.message(items_text)

            else:
                item = (
                    db.query(MenuItem)
                    .filter(
                        (MenuItem.name_ar == user_message) |
                        (MenuItem.name_en.ilike(user_message))
                    )
                    .first()
                )

                if item:
                    prices = (
                        db.query(ItemPrice)
                        .filter(ItemPrice.item_id == item.id)
                        .all()
                    )

                    item_text = f"{item.name_ar} - {item.name_en}\n\n"

                    if item.description_ar:
                        item_text += f"{item.description_ar}\n\n"

                    item_text += "Prices / الأسعار:\n"

                    for price in prices:
                        item_text += (
                            f"- {price.size_ar} / {price.size_en}: "
                            f"{price.price_lbp:,} LBP\n"
                        )

                    response.message(item_text)

                else:
                    try:
                        ai_reply = ask_juice_bar_ai(user_message)
                        response.message(ai_reply)
                    except Exception:
                        response.message("Welcome to Ramadan Juice! Send MENU to see our juices.")

        finally:
            db.close()

    return Response(content=str(response), media_type="application/xml")
