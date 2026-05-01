from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from .state import AgentState
from .tools import DEEP_RESEARCH_TOOLS

# Use local FreeLLM API
llm = ChatOpenAI(
    model="gemini-2.5-pro", # Can be overridden
    api_key="dummy_key",
    base_url="http://localhost:3001/v1",
    temperature=0.2
)

llm_with_tools = llm.bind_tools(DEEP_RESEARCH_TOOLS)

def agent_node(state: AgentState):
    messages = state["messages"]
    
    # Check if this is the first message to inject system prompt
    if not messages or not any(isinstance(m, SystemMessage) for m in messages):
        sys_msg = SystemMessage(content=(
            "You are a web research agent. Use the tools provided (web_search, scrape_url) "
            "to gather information. Once you have enough information to answer the user's prompt, "
            "you MUST call the `format_output` tool with format='markdown' and data='your detailed report'. "
            "Do not answer directly without calling format_output first. "
            "Do not call format_output until you have actually gathered data."
        ))
        messages = [sys_msg] + list(messages)
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tools_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": []}
    
    tool_results = []
    data_collected = state.get("data_collected", False)
    final_output = state.get("final_output", None)
    
    tool_map = {t.name: t for t in DEEP_RESEARCH_TOOLS}
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        if tool_name == "format_output":
            if not data_collected:
                result = "Error: No data collected yet. You must use web_search or scrape_url before calling format_output."
                tool_results.append(ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_name))
            else:
                final_output = tool_args.get("data", "Output generated.")
                result = "Output formatted successfully."
                tool_results.append(ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_name))
        else:
            # Execution of real tools
            tool_func = tool_map.get(tool_name)
            if tool_func:
                try:
                    # tool.invoke will handle async correctly inside LangGraph if it's sync environment or we can use ainvoke
                    # Langchain tools handle the translation
                    result = tool_func.invoke(tool_args)
                    data_collected = True # Mark that we have collected data
                except Exception as e:
                    result = f"Error: {str(e)}"
            else:
                result = f"Error: Tool {tool_name} not found."
            
            tool_results.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"], name=tool_name))
            
    return {"messages": tool_results, "data_collected": data_collected, "final_output": final_output}

def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        # If it didn't call any tools but just output text, we can end
        return END
        
    return "tools"

def check_finished(state: AgentState) -> str:
    if state.get("final_output") is not None:
        return END
    return "agent"

# Build Graph
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tools_node)

builder.set_entry_point("agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_conditional_edges("tools", check_finished)

deep_research_graph = builder.compile()
