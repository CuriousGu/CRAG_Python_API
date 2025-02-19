from fastapi import FastAPI

from src.infrastructure.database.mongodb.connector import MongoDB
from src.infrastructure.config.llm import LLM
from src.services.llama_guard import LlamaGuard

from src.api.routes import chat_router, document_router


def create_app():
    app = FastAPI()

    # defining API variables
    app.database = MongoDB()
    app.llm = LLM()
    app.llama_guard = LlamaGuard()

    # including routes
    app.include_router(chat_router)
    app.include_router(document_router)

    return app
