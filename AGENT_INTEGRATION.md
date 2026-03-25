# Agentic Tool Integration Guide

Use this guide to help other AI agents or developers build "tools" that connect to the MementoManager API.

## 🤖 System Prompt for the Agent
When giving an agent access to these tools, include this in their system instructions:
> "You have access to a Long-Term Memory API. Use `store_memory` when you learn something new about the user or world. Use `search_memory` to get broad context, and `ask_memory` for specific questions about things you might have forgotten. Always use your unique `namespace` to keep your memories isolated."

---

## 🛠️ Python Tool Implementation (Template)
This is a standard implementation using `requests`. A coding agent can copy-paste this to quickly build a toolset.

```python
import requests

BASE_URL = "http://localhost:7087"
NAMESPACE = "my_unique_agent_id"

def store_chat_memory(text: str):
    """Summarizes and stores a conversation snippet."""
    payload = {"text": text, "namespace": NAMESPACE}
    return requests.post(f"{BASE_URL}/store/chat", json=payload).json()

def store_fact(fact: str):
    """Stores a direct fact (e.g. 'The user prefers dark mode')."""
    payload = {
        "content": fact, 
        "type": "fact", 
        "namespace": NAMESPACE
    }
    return requests.post(f"{BASE_URL}/store/targeted", json=payload).json()

def store_relationship(subject: str, relation: str, obj: str):
    """Stores a relationship (e.g. 'Alice', 'works_at', 'TechCorp')."""
    payload = {
        "content": f"{subject} {relation} {obj}",
        "type": "relationship",
        "subject": subject,
        "relation": relation,
        "object": obj,
        "namespace": NAMESPACE
    }
    return requests.post(f"{BASE_URL}/store/targeted", json=payload).json()

def search_memory(query: str):
    """Retrieves all relevant facts, chat logs, and relationships."""
    payload = {"query": query, "namespace": NAMESPACE}
    return requests.post(f"{BASE_URL}/retrieve/all", json=payload).json()

def ask_memory(question: str):
    """Asks the memory a specific question and gets a synthesized answer."""
    payload = {"query": question, "namespace": NAMESPACE}
    return requests.post(f"{BASE_URL}/retrieve/targeted", json=payload).json()

def forget_memory(query: str):
    """Removes facts or relationships matching the query."""
    payload = {"query": query, "namespace": NAMESPACE}
    return requests.post(f"{BASE_URL}/memory/forget", json=payload).json()

def update_fact(old_fact: str, new_fact: str):
    """Replaces an old fact with a new one."""
    payload = {
        "old_content": old_fact,
        "new_content": new_fact,
        "type": "fact",
        "namespace": NAMESPACE
    }
    return requests.post(f"{BASE_URL}/memory/update", json=payload).json()
```

---

## 📦 OpenAI Tool Definition (JSON)
If you are using an agent that supports OpenAI-style tool calling, provide these schemas:

### 1. Store Targeted
```json
{
  "name": "store_memory_item",
  "description": "Store a specific fact or relationship in long-term memory.",
  "parameters": {
    "type": "object",
    "properties": {
      "content": {"type": "string", "description": "The fact to remember."},
      "type": {"type": "string", "enum": ["fact", "relationship"]},
      "subject": {"type": "string", "description": "For relationships only (e.g. 'Ty')"},
      "relation": {"type": "string", "description": "For relationships only (e.g. 'is_married_to')"},
      "object": {"type": "string", "description": "For relationships only (e.g. 'Karen')"}
    },
    "required": ["content", "type"]
  }
}
```

### 2. Ask Memory
```json
{
  "name": "query_memory",
  "description": "Search long-term memory for an answer to a specific question.",
  "parameters": {
    "type": "object",
    "properties": {
      "question": {"type": "string", "description": "The question to ask your memory."}
    },
    "required": ["question"]
  }
}
```
