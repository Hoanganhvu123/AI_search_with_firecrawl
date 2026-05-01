from typing import TypedDict, Annotated, Sequence, Any
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state of the Deep Research Agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    data_collected: bool
    schema_repair_attempts: int
    final_output: str | None
