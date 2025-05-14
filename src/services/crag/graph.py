from typing import List, Dict
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from src.infrastructure.config import settings
from .templates import AgentState
from .nodes import (
    get_news,
    should_continue,
    generate,
    grade_documents,
    find_references,
    flow_decision,
    CustomToolNode
)


class CRAG:
    def __init__(self):
        self.index_name = settings.INDEX_NAME
        self.build()

    async def invoke(
        self,
        messages: List[Dict[str, str]],
        model: ChatOpenAI | OllamaLLM
    ):
        try:
            response = self.graph.invoke(
                {
                    "messages": messages[-10:],
                    "model": model,
                }
            )
            return {
                "messages": response["messages"][-1].content,
                "docs": list(response["docs"]) if response.get("docs") else [],
                "decision_type": response["decision_type"]
            }

        except Exception as e:
            raise ValueError(f"Error invoking CRAG: {e}")

    def build(self):
        try:
            builder = StateGraph(AgentState)
            builder.add_node("find_references", find_references)
            builder.add_node("get_news", get_news)
            builder.add_node("tools", CustomToolNode())
            builder.add_node("crag", grade_documents)
            builder.add_node("generate", generate)

            builder.add_conditional_edges(
                START,
                flow_decision,
                {
                    "general": "get_news",
                    "specific": "find_references",
                    "end": "generate"
                }
            )
            # DETAILED SEARCH
            builder.add_edge("find_references", "generate")

            # MOST RECENT OR RETRIEVER
            builder.add_conditional_edges(
                "get_news",
                should_continue,
                {
                    "continue": "tools",
                    "end": "generate"
                }
            )
            builder.add_edge("tools", "crag")
            builder.add_edge("crag", "generate")

            # END
            builder.add_edge("generate", END)
            self.graph = builder.compile()

        except Exception as e:
            raise ValueError("Error building graph") from e
