import json

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_store_targeted_fact(client, mock_vector_db):
    response = client.post("/store/targeted", json={
        "content": "Paris is the capital of France",
        "type": "fact"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify in DB
    results = mock_vector_db.query_facts("France")
    assert "Paris is the capital of France" in results["documents"][0]

def test_store_targeted_relationship(client, mock_graph_db):
    response = client.post("/store/targeted", json={
        "content": "Ty is married to Karen",
        "type": "relationship",
        "subject": "Ty",
        "relation": "married_to",
        "object": "Karen"
    })
    assert response.status_code == 200
    
    # Verify in Graph
    results = mock_graph_db.get_related_entities("Ty")
    assert results[0]["object"] == "karen"

def test_retrieve_all(client, mock_vector_db, mock_graph_db):
    # Seed DB
    mock_vector_db.add_fact("The sky is blue")
    mock_graph_db.add_relationship("Sun", "heats", "Earth")
    
    response = client.post("/retrieve/all", json={"query": "weather"})
    assert response.status_code == 200
    data = response.json()
    assert "The sky is blue" in data["facts"]

def test_store_chat_extraction(client, mock_llm):
    # Mock LLM output
    mock_llm.generate_json.return_value = json.dumps({
        "facts": ["Ty likes coffee"],
        "relationships": [{"subject": "Ty", "relation": "drinks", "object": "coffee"}]
    })
    
    response = client.post("/store/chat", json={"text": "I really love coffee, it's my favorite."})
    assert response.status_code == 200
    data = response.json()
    assert "Ty likes coffee" in data["facts"]
