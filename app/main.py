from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.database import SessionLocal, engine
from app.models import Base, Category, MenuItem, Customer, Order, OrderItem
from app.services.ai_assistant_service import get_ai_reply
from app.graph.order_graph import process_order_message, get_order_state, reset_order_state
from app.services.intent_service import classify_intent
from app.services.menu_service import (build_menu_text, build_category_text, build_item_text)

app = FastAPI()
Base.metadata.create_all(bind=engine)

active_order_threads = set()

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
        active_order_threads.discard(From)
        reset_order_state(From)

        response.message(
            "Order cancelled ❌\n\n"
            "تم إلغاء الطلب ❌"
        )

        return Response(
            content=str(response),
            media_type="application/xml"
        )

    elif normalized_message in ["cart", "الفاتورة"]:
        order_state = get_order_state(From)

        if not order_state:
            response.message(
                "Your cart is empty.\n"
                "الفاتورة فارغة."
            )
            return Response(content=str(response), media_type="application/xml")

        cart = order_state.get("cart", [])

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
    
    elif normalized_message in ["confirm", "تأكيد"]:

        order_state = get_order_state(From)

        if not order_state:
            response.message(
                "No active order.\n"
                "لا يوجد أي طلب."
            )
            return Response(
                content=str(response),
                media_type="application/xml"
            )

        cart = order_state.get("cart", [])

        if not cart:
            response.message(
                "Your cart is empty.\n"
                "الفاتورة فارغة."
            )
            return Response(
                content=str(response),
                media_type="application/xml"
            )

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

            active_order_threads.discard(From)
            reset_order_state(From)

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
    
    elif normalized_message in ["menu", "مينو", "المنيو", "القائمة"]:
        db = SessionLocal()
        try:
            response.message(build_menu_text(db))
        finally:
            db.close()

    elif normalized_message in ["order", "طلب"]:
        active_order_threads.add(From)

        result = process_order_message(
            From,
            user_message
        )

        response.message(result["bot_reply"])

    elif From in active_order_threads:

        result = process_order_message(
            From,
            user_message
        )

        response.message(result["bot_reply"])

    else:
        intent = classify_intent(user_message)

        if intent == "greeting":
            response.message(
                "👋 Hello! Welcome to Ramadan Juice.\n\n"
                "I can help you browse the menu, recommend drinks, or place an order.\n"
                "Send MENU to browse or ORDER to start ordering."
            )

        elif intent == "menu":
            db = SessionLocal()
            try:
                response.message(build_menu_text(db))
            finally:
                db.close()

        elif intent == "order":
            active_order_threads.add(From)
            result = process_order_message(From, user_message)
            response.message(result["bot_reply"])

        elif intent == "recommendation":
            response.message(get_ai_reply(user_message))

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
                    response.message(build_category_text(db, category))

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
                        response.message(build_item_text(db, item))

                    else:
                        try:
                            response.message(get_ai_reply(user_message))
                        except Exception:
                            response.message(
                                "Welcome to Ramadan Juice! Send MENU to see our juices."
                            )

            finally:
                db.close()

    return Response(content=str(response), media_type="application/xml")
