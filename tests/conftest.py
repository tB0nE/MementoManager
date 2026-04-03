import pytest
import os
import shutil
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import chromadb
from app.main import app
from app.memory.vector import VectorStorage
from app.memory.graph import GraphStorage
from app.llm.engine import LLMEngine

@pytest.fixture
def temp_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

@pytest.fixture
def mock_vector_db(temp_dir):
    # Create a fresh vector storage for each test
    v = VectorStorage()
    # Override client to use temp directory
    v.client = chromadb.PersistentClient(path=os.path.join(temp_dir, "chroma"))
    v.facts_collection = v.client.get_or_create_collection(name="facts_test")
    v.chat_collection = v.client.get_or_create_collection(name="chat_test")
    return v

@pytest.fixture
def mock_graph_db(temp_dir):
    # Fresh graph storage for each test
    g = GraphStorage()
    g.db_path = os.path.join(temp_dir, "graph_test.json")
    # Reset internal graph to MultiDiGraph
    import networkx as nx
    g.graph = nx.MultiDiGraph()
    return g

@pytest.fixture
def mock_llm():
    llm = MagicMock(spec=LLMEngine)
    llm.generate.return_value = "Mocked LLM Response"
    llm.generate_json.return_value = '{"facts": ["Mocked fact"], "relationships": [{"subject": "A", "relation": "is", "object": "B"}]}'
    return llm

@pytest.fixture
def client(mock_vector_db, mock_graph_db, mock_llm, monkeypatch):
    # Dependency injection via monkeypatching
    
    # 1. Patch the global singletons in their respective modules
    monkeypatch.setattr("app.memory.vector.vector_db", mock_vector_db)
    monkeypatch.setattr("app.memory.graph.graph_db", mock_graph_db)
    monkeypatch.setattr("app.llm.engine.engine", mock_llm)
    
    # 2. Patch where they are imported in processor.py
    monkeypatch.setattr("app.memory.processor.vector_db", mock_vector_db)
    monkeypatch.setattr("app.memory.processor.graph_db", mock_graph_db)
    monkeypatch.setattr("app.memory.processor.engine", mock_llm)
    
    # 3. Patch where they are imported in main.py
    monkeypatch.setattr("app.main.vector_db", mock_vector_db)
    monkeypatch.setattr("app.main.graph_db", mock_graph_db)
    
    # Patch the internals of the existing 'processor' instance in main.py
    from app.main import processor as main_processor
    monkeypatch.setattr(main_processor, "vector_db", mock_vector_db)
    monkeypatch.setattr(main_processor, "graph_db", mock_graph_db)
    monkeypatch.setattr(main_processor, "engine", mock_llm)

    with TestClient(app) as c:
        yield c
