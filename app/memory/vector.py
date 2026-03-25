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

    def add_fact(self, content: str, metadata: dict = None, namespace: str = "default"):
        import uuid
        fact_id = str(uuid.uuid4())
        meta = metadata or {}
        meta["namespace"] = namespace
        
        self.facts_collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[fact_id]
        )
        return fact_id

    def add_chat_log(self, content: str, metadata: dict = None, namespace: str = "default"):
        import uuid
        chat_id = str(uuid.uuid4())
        meta = metadata or {}
        meta["namespace"] = namespace
        
        self.chat_collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[chat_id]
        )
        return chat_id

    def query_facts(self, query_text: str, n_results: int = 5, namespace: str = "default"):
        return self.facts_collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"namespace": namespace}
        )

    def query_chat(self, query_text: str, n_results: int = 5, namespace: str = "default"):
        return self.chat_collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"namespace": namespace}
        )

# Singleton instance
vector_db = VectorStorage()
