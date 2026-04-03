import json
from app.llm.engine import engine
from app.memory.vector import vector_db
from app.memory.graph import graph_db

class MemoryProcessor:
    def __init__(self):
        self.vector_db = vector_db
        self.graph_db = graph_db
        self.engine = engine
        self.extraction_prompt = """
Extract all key facts and entity relationships from the following chat text. 
Format the output as a JSON object with two keys: "facts" (a list of strings) and "relationships" (a list of objects with "subject", "relation", and "object").

Chat Text:
{text}

JSON Output:
"""

    def process_chat(self, text: str, namespace: str = "default"):
        # 1. Store the raw chat log for future context
        self.vector_db.add_chat_log(text, namespace=namespace)
        
        # 2. Extract facts and relationships
        prompt = self.extraction_prompt.format(text=text)
        raw_output = self.engine.generate_json(prompt)
        
        try:
            # Basic cleanup of LLM output to ensure valid JSON
            start_idx = raw_output.find("{")
            end_idx = raw_output.rfind("}") + 1
            if start_idx != -1 and end_idx != -1:
                data = json.loads(raw_output[start_idx:end_idx])
            else:
                return {"error": "Failed to extract structured data", "raw": raw_output}

            # 3. Store extracted facts
            for fact in data.get("facts", []):
                self.vector_db.add_fact(fact, namespace=namespace)
            
            # 4. Store extracted relationships
            for rel in data.get("relationships", []):
                self.graph_db.add_relationship(rel["subject"], rel["relation"], rel["object"], namespace=namespace)
                
            return data
        except Exception as e:
            return {"error": str(e), "raw": raw_output}

    def retrieve_all(self, query: str, namespace: str = "default"):
        # 1. Vector Search (Facts and Chat logs)
        facts = self.vector_db.query_facts(query, n_results=5, namespace=namespace)
        chat_logs = self.vector_db.query_chat(query, n_results=3, namespace=namespace)
        
        # 2. Graph Search
        relationships = self.graph_db.find_relationships_for_query(query, namespace=namespace)
        
        return {
            "facts": facts["documents"][0] if facts["documents"] else [],
            "chat_logs": chat_logs["documents"][0] if chat_logs["documents"] else [],
            "relationships": relationships
        }

    def retrieve_targeted(self, query: str, namespace: str = "default"):
        # 1. Get all relevant context
        context_data = self.retrieve_all(query, namespace=namespace)
        
        # 2. Format context for the LLM
        context_str = "Relevant Facts:\n" + "\n".join(context_data["facts"])
        context_str += "\n\nRelevant Relationships:\n" + "\n".join([f"{r['subject']} {r['relation']} {r['object']}" for r in context_data["relationships"]])
        context_str += "\n\nRelevant Past Conversations:\n" + "\n".join(context_data["chat_logs"])
        
        # 3. Synthesize answer
        prompt = f"""
Using the provided context, answer the following question as accurately and concisely as possible. 
If you don't know the answer, say you don't know.

Context:
{context_str}

Question:
{query}

Answer:
"""
        return self.engine.generate(prompt, max_tokens=256)

# Singleton instance
processor = MemoryProcessor()
