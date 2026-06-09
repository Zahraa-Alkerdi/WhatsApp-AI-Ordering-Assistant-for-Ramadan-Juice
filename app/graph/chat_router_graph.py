from typing import TypedDict,List, Optional
from langgraph.graph import StateGraph, START, END


class ChatState(TypedDict):
    user_message: str
    bot_reply: str



def route_message(state: ChatState):
    return state


def menu_node(state: ChatState):
    state["bot_reply"] = "Showing menu..."
    return state


def order_node(state: ChatState):
    state["bot_reply"] = "Starting order..."
    return state


def ai_node(state: ChatState):
    state["bot_reply"] = "AI handling the message..."
    return state


def router(state: ChatState):
    message = state["user_message"].strip().lower()

    if message == "menu":
        return "menu"

    if message == "order":
        return "order"

    return "ai"

    

graph_builder = StateGraph(ChatState)

graph_builder.add_node("router", route_message)
graph_builder.add_node("menu", menu_node)
graph_builder.add_node("order", order_node)
graph_builder.add_node("ai", ai_node)

graph_builder.add_edge(START, "router")

graph_builder.add_conditional_edges(
    "router",
    router,
    {
        "menu": "menu",
        "order": "order",
        "ai": "ai"
    }
)

graph_builder.add_edge("menu", END)
graph_builder.add_edge("order", END)
graph_builder.add_edge("ai", END)

graph = graph_builder.compile()

