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

    def delete_facts(self, query_text: str, namespace: str = "default"):
        # Find matches first
        results = self.query_facts(query_text, n_results=5, namespace=namespace)
        if results["ids"] and results["ids"][0]:
            # Delete the top match for now (conservative)
            self.facts_collection.delete(ids=[results["ids"][0][0]])
            return True
        return False

    def delete_chat_logs(self, query_text: str, namespace: str = "default"):
        results = self.query_chat(query_text, n_results=5, namespace=namespace)
        if results["ids"] and results["ids"][0]:
            self.chat_collection.delete(ids=[results["ids"][0][0]])
            return True
        return False

# Singleton instance
vector_db = VectorStorage()
