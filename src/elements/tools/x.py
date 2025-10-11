from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
class State(TypedDict):
    messages: Annotated[list, add_messages]
from langchain_core.tools import tool
builder = StateGraph(State)
builder.add_node("chatbot", lambda state: {"messages": ("assistant", "Hello")})
builder.set_entry_point("chatbot")
builder.set_finish_point("chatbot")
graph = builder.compile()
s = graph.invoke({"messages": [("user", "Hello")]})
print(s)



gen = (i for i in range(1000000))
gen1 = (i for i in [1, 2, 3])
print(next(gen))
print(next(gen))
print(next(gen1))
print(next(gen1))