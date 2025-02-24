import chromadb
from chromadb.config import Settings
from typing import List, Optional


class ChromaDB:
    """Manager for ChromaDB connection and operations."""

    def __init__(self):
        """Initialize ChromaDB connection."""
        self.host = 'localhost'
        self.port = 8000
        self.client = self._connect()
        self.collection = None

    def _connect(self):
        """Connect to ChromaDB."""
        client = chromadb.HttpClient(host=self.host, port=self.port)
        return client

    def _get_or_create_collection(self, collection_name: str):
        """Create or get an existing collection.

        Args:
            collection_name (str): Name of the collection to create/get

        Returns:
            Collection: Created/retrieved collection object
        """
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )
        return self.collection

    async def add_documents(
        self,
        documents: List[str],
        collection_name: str,
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None
    ):
        """Add documents to the collection.

        Args:
            documents (List[str]): List of document texts
            metadatas (Optional[List[dict]]): Document metadata
            ids (Optional[List[str]]): Unique document IDs

        Raises:
            ValueError: If collection is not initialized

        Returns:
            dict: Result of add operation
        """

        self.collection = self._get_or_create_collection(collection_name)
        return self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    async def query_documents(
        self,
        query_text: str,
        collection_name: str,
        n_results: int = 5,
        where: Optional[dict] = None
    ):
        """Query similar documents in the collection.

        Args:
            query_text (str): Text to search for similarity
            n_results (int): Number of desired results
            where (Optional[dict]): Additional filters

        Raises:
            ValueError: If collection is not initialized

        Returns:
            dict: Query results
        """
        
        self.collection = self._get_or_create_collection(collection_name)
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
    
    async def list_collections(self):
        """List all collections in ChromaDB.

        Returns:
            dict: List of collections
        """
        return self.client.list_collections()
    
    async def list_documents(self, collection_name: str):
        """List all documents in a
        collection. Args:   collection_name (str): Name of the collection to list documents from Returns:     dict: List of documents in the collection"""

        self.collection = self._get_or_create_collection(collection_name)
        return self.collection.get(include=["documents", "metadatas"])

    async def delete_documents(self, ids: List[str],collection_name: str):
        """Delete documents from collection by IDs.

        Args:
            ids (List[str]): List of document IDs to delete

        Raises:
            ValueError: If collection is not initialized

        Returns:
            dict: Result of delete operation
        """
        
        self.collection = self._get_or_create_collection(collection_name)
        return self.collection.delete(ids=ids)

    def __del__(self):
        """Close ChromaDB connection and clean up resources."""
        if self.client:
            self.client.reset()