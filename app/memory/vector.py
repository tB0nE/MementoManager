import os
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

class VectorStorage:
    def __init__(self):
        db_path = os.getenv("CHROMA_DB_PATH", "data/chroma")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Collection for general facts
        self.facts_collection = self.client.get_or_create_collection(name="facts")
        # Collection for raw chat logs (for context retrieval)
        self.chat_collection = self.client.get_or_create_collection(name="chat_history")

    def add_fact(self, content: str, metadata: dict = None):
        import uuid
        fact_id = str(uuid.uuid4())
        kwargs = {
            "documents": [content],
            "ids": [fact_id]
        }
        if metadata:
            kwargs["metadatas"] = [metadata]
        self.facts_collection.add(**kwargs)
        return fact_id

    def add_chat_log(self, content: str, metadata: dict = None):
        import uuid
        chat_id = str(uuid.uuid4())
        kwargs = {
            "documents": [content],
            "ids": [chat_id]
        }
        if metadata:
            kwargs["metadatas"] = [metadata]
        self.chat_collection.add(**kwargs)
        return chat_id

    def query_facts(self, query_text: str, n_results: int = 5):
        return self.facts_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

    def query_chat(self, query_text: str, n_results: int = 5):
        return self.chat_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

# Singleton instance
vector_db = VectorStorage()
