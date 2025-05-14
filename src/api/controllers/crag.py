from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI

from src.services.crag import CRAG
from src.infrastructure.database import MongoDB
from src.infrastructure.database import (
    add_message_to_history,
    get_messages_history
)


async def contr_new_message(
    message: str,
    user_id: str,
    crag: CRAG,
    llm: ChatOpenAI | OllamaLLM,
    database: MongoDB
) -> str:

    history = await get_messages_history(user_id, database)
    history.append({
        "role": "user",
        "content": message,
        "timestamp": datetime.now().isoformat()
    })

    response = await crag.invoke(
        messages=history,
        model=llm
    )

    history.append({
        "role": "assistant",
        "content": response["messages"],
        "timestamp": datetime.now().isoformat(),
        "docs": response.get("docs", []),
        "decision_type": response.get("decision_type", "")
    })

    _ = await add_message_to_history(
        messages=history,
        user_id=user_id,
        database=database
    )

    return response["messages"]
