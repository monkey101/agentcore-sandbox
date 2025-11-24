from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
import argparse
import json
import operator
import math
import os, subprocess
import random
import string
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

def test_sub_process() -> str:
    path ="./"

    # Touch a file with a randomized filename
    random_filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '.txt'
    touch_cmd = ["touch", os.path.join(path, random_filename)]
    subprocess.run(touch_cmd, check=True)
    print(f"Created file: {random_filename}")

    cmd = ["ls", "-la", path]

    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print(p.stdout + "\n" + p.stderr)
    return p.stdout + "\n" + p.stderr

# Create a custom weather tool
@tool
def weather():
    """Get weather"""  # Dummy implementation
    return "sunny"

# Define the agent using manual LangGraph construction
def create_agent():
    """Create and configure the LangGraph agent"""
    from langchain_aws import ChatBedrock
    
    # Initialize your LLM (adjust model and parameters as needed)
    llm = ChatBedrock(
        model_id="global.anthropic.claude-haiku-4-5-20251001-v1:0",  # or your preferred model
        model_kwargs={"temperature": 0.1},
        region_name="us-west-1",
    )
    
    # Bind tools to the LLM
    tools = [weather]
    llm_with_tools = llm.bind_tools(tools)
    
    # System message
    system_message = "You're a helpful assistant. You can do simple math calculation, and tell the weather."
    
    # Define the chatbot node
    def chatbot(state: MessagesState):
        # Add system message if not already present
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_message)] + messages
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    # Create the graph
    graph_builder = StateGraph(MessagesState)
    
    # Add nodes
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools))
    
    # Add edges
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Set entry point
    graph_builder.set_entry_point("chatbot")
    
    # Compile the graph
    return graph_builder.compile()

# Initialize the agent
agent = create_agent()

@app.entrypoint
def langgraph_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    
    # Create the input in the format expected by LangGraph
    response = agent.invoke({"messages": [HumanMessage(content=user_input)]})

    ls_output = test_sub_process()
    
    # Extract the final message content
    return (response["messages"][-1].content + "\n" + ls_output)

if __name__ == "__main__":
    if (False):  # Change to False to run as a Bedrock app
        parser = argparse.ArgumentParser()
        parser.add_argument("payload", type=str)
        args = parser.parse_args()
        response = langgraph_bedrock(json.loads(args.payload))
        print(response)
    else:
        app.run()

