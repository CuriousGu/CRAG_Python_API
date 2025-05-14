from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from typing import Annotated, TypedDict, List, Dict

from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI

from src.infrastructure.config import settings


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    query: List[str]
    docs: List[Dict]
    model: OllamaLLM | ChatOpenAI
    index_name: str = Field(default=settings.INDEX_NAME)
    user_last_message: str
    decision_type: str


class GradeDocument(BaseModel):
    """ Evaluate the relevance of the text to the query
        The response values must be "yes" or "no".
        These documents must support the agent's response.
    """
    binary_score: str = Field(
        ...,
        description="""
            binary score of the document relevance
            The response values must be "yes" or "no".
        """
    )


class FlowDecision(BaseModel):
    decision: str


class IsSpecificFile(BaseModel):
    arquivo_relevante: bool
