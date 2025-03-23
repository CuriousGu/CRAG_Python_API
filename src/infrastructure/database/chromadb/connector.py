import uuid
import chromadb
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool
from typing import List, Optional

from src.infrastructure.config import settings


class ChromaDB:
    def __init__(self):
        self.host = settings.CHROMA_HOST
        self.port = settings.CHROMA_PORT
        self.collection_name = settings.INDEX_NAME
        self.collection = None
        self.expected_dimension = settings.VECTOR_DIMENSION
        self.embedding_function = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL
        )
        try:
            self.client = self._connect()
            self.retriever = self._as_retriever()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ChromaDB: {e}")

    def _connect(self):
        client = chromadb.HttpClient(host=self.host, port=self.port)
        return client

    def _create_collection(self, collection_name: str = None):
        """
        Cria uma nova coleção com a dimensão configurada no .env
        """
        self.collection = self.client.get_or_create_collection(
            name=collection_name or self.collection_name,
            metadata={
                "hnsw:space": "cosine",
                "dimension": self.expected_dimension
            }
        )
        return self.collection

    def _get_collection_info(self, collection_name: str):
        """
        Obtém informações sobre a dimensão de uma coleção existente
        """
        try:
            collection = self.client.get_collection(collection_name)
            return collection
        except Exception:
            return None

    def _as_retriever(self, collection_name: str = None) -> dict:
        """
        Cria um retriever adaptado à dimensão da coleção
        """
        vector_store = Chroma(
            client=self.client,
            collection_name=collection_name or self.collection_name,
            embedding_function=self.embedding_function
        )
        retriever = vector_store.as_retriever()

        return retriever

    @staticmethod
    @tool("retriever")
    def retrieve(query: str) -> List:
        """
        Método que faz uma requisição a vector store para consultar os
        documentos que podem ajudar a responder a pergunta do usuário.

        Args:
            query (str): A query para a vector store.

        Returns:
            List[Document]: Uma lista de documentos recuperados
        """
        try:
            db = ChromaDB()
            collections = db.client.list_collections()
            if settings.INDEX_NAME not in collections:
                return []

            retriever = db._as_retriever(settings.INDEX_NAME)
            return retriever.invoke(query)
        except Exception as e:
            raise e

    async def add_documents(
        self,
        documents: List[str],
        collection_name: str,
        metadatas: Optional[List[dict]] = None,
    ):
        """
        Adiciona documentos à coleção com dimensão configurada no .env
        """
        if not self.collection or self.collection.name != collection_name:
            self.collection = self._create_collection(collection_name)

        embeddings = self.embedding_function.embed_documents(documents)

        return self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=[str(uuid.uuid4()) for _ in enumerate(documents)],
        )

    async def list_collections(self):
        return self.client.list_collections()

    async def list_documents(
        self,
        collection_name: str
    ):
        if collection := self.client.get_collection(collection_name):
            return collection.get()
        return []

    async def query_documents(
        self,
        query_text: str,
        collection_name: str,
        n_results: int = 5,
        where: Optional[dict] = None
    ):
        """
        Consulta documentos adaptando à dimensão da coleção
        """
        if not self.collection or self.collection.name != collection_name:
            self.collection = self.client.get_collection(collection_name)

        query_embedding = self.embedding_function.embed_query(query_text)

        try:
            return self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
        except Exception as e:
            if "dimension" in str(e).lower():
                raise ValueError(
                    f"Erro de dimensionalidade ao consultar coleção "
                    f"'{collection_name}'. A dimensão configurada é "
                    f"{self.expected_dimension}, mas a coleção espera outra "
                    f"dimensão. Considere recriar a coleção."
                )
            raise e

    async def delete_documents(
        self,
        ids: List[str],
        collection_name: str
    ):
        if not self.collection or self.collection.name != collection_name:
            self.collection = self.client.get_collection(collection_name)
        return self.collection.delete(ids=ids)

    async def close(self):
        if self.client:
            self.client.reset()
