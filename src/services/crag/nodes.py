from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
import html

from .templates import AgentState, GradeDocument, FlowDecision, IsSpecificFile
from src.infrastructure.database import ChromaDB
from .prompts import (
    grader_prompt,
    agent_prompt,
    no_generation,
    generate_answer_prompt,
    flow_decision_prompt,
    is_specific_file
)


def flow_decision(state: AgentState):
    # decide se vai recuperar as informações de
    # um modo geral ou procurar informações mais específicas
    # sobre uma noticia específica.
    LLM = state["model"]
    flow_decision = PromptTemplate.from_template(
        flow_decision_prompt
    )
    chain = (
        flow_decision |
        LLM.with_structured_output(FlowDecision)
    )

    formatted_history = "\n".join(
        [
            f"{'user' if msg.type == 'human' else 'IA'}: " \
            f"{msg.content}" for msg in state["messages"][-5:]
        ]
    )

    response = chain.invoke(
        {
            "history": formatted_history,
            "question": state["messages"][-1].content
        }
    )

    return response.decision if hasattr(response, "decision") else "end"


def find_references(state: AgentState):
    # puxa a ultima mensagem do tipo generic
    # pega as referencias das noticias
    # consulta qual delas tem relacao com a pergunta do user.
    # submete os arquivos relevantes para o generate
    messages = state["messages"]
    LLM = state["model"]

    is_specific_file_chain = (
        PromptTemplate.from_template(is_specific_file)
        | LLM.with_structured_output(IsSpecificFile)
    )

    for i in messages[::-1]:
        if (
            i.additional_kwargs.get("docs") and
            i.additional_kwargs.get("decision_type") == "general"
        ):
            docs_last_message = i.additional_kwargs.get("docs")
            break

    formatted_history = "\n".join(
        [
            f"{'user' if msg.type == 'human' else 'IA'}: " \
            f"{msg.content}" for msg in state["messages"][-5:]
        ]
    )

    # consulta ao documento
    for doc in docs_last_message:
        found_docs = ChromaDB().find_files(doc)
        decoded_docs = [
            html.unescape(x["page_content"])
            .replace("&nbsp;", " ")
            .replace("\\r\\n", "\\n")
            .strip()
            for x in found_docs
        ]

        relevant = is_specific_file_chain.invoke(
            {
                "document": "\n".join(decoded_docs),
                "question": messages[-1].content,
                "history": formatted_history
            }
        )

        if relevant and relevant.arquivo_relevante:
            return {
                "docs": found_docs,
                "decision_type": "specific",
                "user_last_message": messages[-1]
            }

    return {
        "docs": [],
        "decision_type": "specific",
        "user_last_message": messages[-1]
    }


def agent(state: AgentState):
    LLM = state["model"]
    agent_msg = PromptTemplate.from_template(agent_prompt)
    chain = agent_msg | LLM.bind_tools(
        [ChromaDB().retrieve, ChromaDB().get_most_recent]
    )

    return {
        "user_last_message": state["messages"][-1],
        "messages": [chain.invoke(input={"question": state["messages"][-5:]})],
        "decision_type": "general"
    }


def should_continue(state: AgentState):
    if state["messages"][-1].tool_calls:
        return "continue"
    return "end"


def grade_documents(state: AgentState):
    queries = state["query"]
    messages = state.get("messages", [])
    docs_recuperados = state["docs"]
    LLM = state["model"]

    retrieval_grader_chain = (
        PromptTemplate.from_template(grader_prompt)
        | LLM.with_structured_output(GradeDocument)
    )

    filtered_docs = list()
    for d in docs_recuperados:
        score = retrieval_grader_chain.invoke(
            {
                "question": queries,
                "document": (
                    d.page_content
                    if not isinstance(d, dict)
                    else d["page_content"]
                ),
                "message": messages[:-3]
            }
        )
        if (score and score.binary_score == "yes") or (
            messages[-2].tool_calls[0]["name"] == "most_recent_files"
        ):
            filtered_docs.append(d)

    return {
        "docs": filtered_docs,
        "query": queries,
        "messages": messages
    }


def generate(state: AgentState):
    LLM = state["model"]
    docs = state.get("docs", None)
    user_last_message = state.get("user_last_message", None)
    messages = state.get("messages", [])

    if docs and len(docs) >= 1:
        answer_chain = (
            PromptTemplate(
                input_variables=["query", "context", "message"],
                template=generate_answer_prompt
            )
            | LLM
        )

        result = answer_chain.invoke(
            {
                "query": user_last_message,
                "context": docs,
                "messages": messages
            }
        )

        response = {
                "messages": result,
                "docs": [
                    x.metadata["file_name"]
                    if hasattr(x, 'metadata')
                    else x["metadata"]["file_name"]
                    for x in docs
                ],
                "decision_type": state["decision_type"]
            }
        response["docs"] = set(response["docs"])
        return response

    else:
        messages = [SystemMessage(content=no_generation)] + state["messages"]
        return {
            "messages": [LLM.invoke(messages)],
            "decision_type": "no_generation"
        }


class CustomToolNode:
    def __init__(self):
        self.tools = {
            "retriever": ChromaDB().retrieve,
            "most_recent_files": ChromaDB().get_most_recent
        }

    def __call__(self, inputs: list):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No messages found in inputs")

        for tool_call in message.tool_calls:
            tool_result = self.tools[tool_call["name"]].invoke(
                tool_call["args"]
            )

        if not isinstance(tool_call["args"], dict):
            raise TypeError("Tool call args must be a dictionary")

        query = tool_call["args"].get("query")
        docs = tool_result

        messages.append(
            ToolMessage(
                content="Documentos encontrados e adicionardos ao contexto",
                tool_call_id=tool_call["id"]
            )
        )

        return {
            "query": query,
            "docs": docs,
            "messages": messages
        }
