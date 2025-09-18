from typing import Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict

class AgentState(TypedDict):
    """The state of the agent."""

    messages: Annotated[Sequence[BaseMessage], add_messages]