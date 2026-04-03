import pytest
import os
from fastapi.testclient import TestClient
from app.main import app

# This test actually loads the LLM on your GPU.
# Run with: pytest tests/test_live_llm.py
@pytest.mark.skipif(not os.path.exists(os.getenv("MODEL_PATH", "models/Magistral-Small-2509-Q4_K_M.gguf")), 
                    reason="Model file not found")
def test_live_retrieval_synthesis():
    # Use a real client but point to a test DB path if we want isolation
    # For now, we'll just test the synth capability
    with TestClient(app) as client:
        # 1. Manually seed a fact
        client.post("/store/targeted", json={
            "content": "Ty's favorite hobby is skydiving.",
            "type": "fact"
        })
        
        # 2. Ask the LLM
        response = client.post("/retrieve/targeted", json={
            "query": "What does Ty enjoy doing in his free time?"
        })
        
        assert response.status_code == 200
        answer = response.json()["answer"].lower()
        assert "skydiving" in answer
