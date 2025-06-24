import logging
import sqlite3
from typing import Annotated

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def build_graph():
    graph_builder = StateGraph(State)

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")

    tool = TavilySearch(max_results=2)
    tools = [tool]

    llm = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot)

    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_conditional_edges("chatbot", tools_condition)

    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    conn = sqlite3.connect("/db/checkpoints.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=memory)

    return graph
