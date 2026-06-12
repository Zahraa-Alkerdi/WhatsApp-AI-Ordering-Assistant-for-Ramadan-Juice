from typing import TypedDict,List, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from app.database import SessionLocal
from app.models import MenuItem, ItemPrice

memory = InMemorySaver()

class OrderState(TypedDict):
    phone_number: str
    user_message: str
    bot_reply: str
    current_step: str
    current_item: str | None
    current_size: str | None
    current_quantity: int | None
    cart: list

def router_node(state: OrderState):
    return state

def route_by_step(state: OrderState):
    step = state["current_step"]

    if step == "":
        return "start_order"

    if step == "choosing_item":
        return "choose_item"

    if step == "choosing_size":
        return "choose_size"

    if step == "choosing_quantity":
        return "choose_quantity"
    
    return "start_order"


def start_order_node(state: OrderState):
    state["bot_reply"] = "What would you like to order?"
    state["current_step"] = "choosing_item"
    return state

def choose_item_node(state: OrderState):
    item = state["user_message"]

    state["current_item"] = item
    state["current_step"] = "choosing_size"

    state["bot_reply"] = (
        f"You selected {item}. "
        "What size would you like?"
    )

    return state

def choose_size_node(state: OrderState):
    size = state["user_message"]

    state["current_size"] = size
    state["current_step"] = "choosing_quantity"

    state["bot_reply"] =(
        f"Size {size} selected. "
        "How many would you like?"
    )

    return state

def choose_quantity_node(state: OrderState):
    user_message = state["user_message"]

    if not user_message.isdigit() or int(user_message) <= 0:
        state["bot_reply"] = "Invalid quantity. Please send a positive number."
        return state

    state["current_quantity"] = int(user_message)
    return state


def add_to_cart_node(state: OrderState):
    db = SessionLocal()

    try:
        item = (
            db.query(MenuItem)
            .filter(
                (MenuItem.name_ar == state["current_item"]) |
                (MenuItem.name_en.ilike(state["current_item"]))
            )
            .first()
        )

        if not item:
            state["bot_reply"] = "Item not found. Please send a valid item name."
            state["current_step"] = "choosing_item"
            return state

        price = (
            db.query(ItemPrice)
            .filter(
                ItemPrice.item_id == item.id,
                (ItemPrice.size_ar == state["current_size"]) |
                (ItemPrice.size_en.ilike(state["current_size"]))
            )
            .first()
        )

        if not price:
            state["bot_reply"] = "Invalid size. Please send a valid size."
            state["current_step"] = "choosing_size"
            return state

        quantity = state["current_quantity"]
        subtotal = quantity * price.price_lbp

        state["cart"].append({
            "item_id": item.id,
            "item_name_ar": item.name_ar,
            "item_name_en": item.name_en,
            "size_ar": price.size_ar,
            "size_en": price.size_en,
            "quantity": quantity,
            "unit_price": price.price_lbp,
            "subtotal": subtotal
        })

        state["bot_reply"] = (
            f"Added to cart ✅\n\n"
            f"{quantity} × {item.name_ar} ({price.size_ar})\n"
            f"Subtotal: {subtotal:,} LBP\n\n"
            f"Send another item, CART, or CONFIRM."
        )

        state["current_item"] = None
        state["current_size"] = None
        state["current_quantity"] = None
        state["current_step"] = "choosing_item"

        return state

    finally:
        db.close()

graph_builder = StateGraph(OrderState)

graph_builder.add_node("router", router_node)
graph_builder.add_node("start_order", start_order_node)
graph_builder.add_node("choose_item", choose_item_node)
graph_builder.add_node("choose_size", choose_size_node)
graph_builder.add_node("choose_quantity", choose_quantity_node)
graph_builder.add_node("add_to_cart", add_to_cart_node)

graph_builder.add_edge(START, "router")

graph_builder.add_conditional_edges(
    "router",
    route_by_step,
    {
        "start_order": "start_order",
        "choose_item": "choose_item",
        "choose_size": "choose_size",
        "choose_quantity": "choose_quantity"
    }
)

graph_builder.add_edge("start_order", END)
graph_builder.add_edge("choose_item", END)
graph_builder.add_edge("choose_size", END)

graph_builder.add_edge("choose_quantity", "add_to_cart")
graph_builder.add_edge("add_to_cart", END)

order_graph = graph_builder.compile(
    checkpointer=memory
)


def process_order_message(phone_number: str, user_message: str):
    config = {
        "configurable": {
            "thread_id": phone_number
        }
    }

    current_state = order_graph.get_state(config)

    if current_state.values:
        input_state = {
            "user_message": user_message
        }
    else:
        input_state = {
            "phone_number": phone_number,
            "user_message": user_message,
            "current_step": "",
            "current_item": None,
            "current_size": None,
            "current_quantity": None,
            "cart": [],
            "bot_reply": ""
        }

    result = order_graph.invoke(
        input_state,
        config=config
    )

    return result

def get_order_state(phone_number: str):
    config = {
        "configurable": {
            "thread_id": phone_number
        }
    }

    graph_state = order_graph.get_state(config)

    return graph_state.values

def reset_order_state(phone_number: str):
    config = {
        "configurable": {
            "thread_id": phone_number
        }
    }

    order_graph.update_state(
        config,
        {
            "phone_number": phone_number,
            "user_message": "",
            "current_step": "",
            "current_item": None,
            "current_size": None,
            "current_quantity": None,
            "cart": [],
            "bot_reply": ""
        }
    )
