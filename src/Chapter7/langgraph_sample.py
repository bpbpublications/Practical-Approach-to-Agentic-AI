from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel
from typing import Optional, List

import shutup
shutup.please()

# Define the structured conversation state
class ConversationState(BaseModel):
    user_input: Optional[str] = None
    reply: Optional[str] = None
    history: List[str] = []

# State reducer to update conversation state immutably
def reducer(state: ConversationState, updates: dict) -> ConversationState:
    return state.copy(update=updates)

# Node to capture user input
def capture_input(state: ConversationState) -> ConversationState:
    user_message = input("You: ")
    return reducer(state, {"user_input": user_message})

# Node to process input and generate a reply
def respond(state: ConversationState) -> ConversationState:
    user_msg = state.user_input or ""
    bot_reply = f"Echo: {user_msg}"
    return reducer(state, {"reply": bot_reply})

# Node to update conversation history
def update_history(state: ConversationState) -> ConversationState:
    new_history = state.history + [f"You: {state.user_input}", f"Bot: {state.reply}"]
    return reducer(state, {"history": new_history})

# Node to display response
def display(state: ConversationState) -> ConversationState:
    print(state.history)
    return state

# Create the LangGraph flow
builder = StateGraph(ConversationState)

builder.add_node("capture_input", RunnableLambda(capture_input))
builder.add_node("respond", RunnableLambda(respond))
builder.add_node("update_history", RunnableLambda(update_history))
builder.add_node("display", RunnableLambda(display))

# Define flow sequence
builder.set_entry_point("capture_input")
builder.add_edge("capture_input", "respond")
builder.add_edge("respond", "update_history")
builder.add_edge("update_history", "display")
builder.add_edge("display", "capture_input")  # loop to continue conversation

# Compile and launch
app = builder.compile()
app.invoke(ConversationState())
