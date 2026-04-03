def test_forget_fact(client):
    # 1. Store
    client.post("/store/targeted", json={
        "content": "The secret code is 9999",
        "type": "fact",
        "namespace": "test"
    })
    
    # 2. Verify it's there
    res = client.post("/retrieve/all", json={"query": "secret code", "namespace": "test"})
    assert "The secret code is 9999" in res.json()["facts"]
    
    # 3. Forget
    client.post("/memory/forget", json={"query": "secret code", "namespace": "test"})
    
    # 4. Verify it's gone
    res = client.post("/retrieve/all", json={"query": "secret code", "namespace": "test"})
    # Chroma query might return empty list or different results
    facts = res.json()["facts"]
    assert "The secret code is 9999" not in facts

def test_update_fact(client):
    # 1. Store old
    client.post("/store/targeted", json={
        "content": "Ty is 42",
        "type": "fact",
        "namespace": "test"
    })
    
    # 2. Update to new
    client.post("/memory/update", json={
        "old_content": "Ty is 42",
        "new_content": "Ty is 43",
        "type": "fact",
        "namespace": "test"
    })
    
    # 3. Verify
    res = client.post("/retrieve/all", json={"query": "How old is Ty?", "namespace": "test"})
    assert "Ty is 43" in res.json()["facts"]
    assert "Ty is 42" not in res.json()["facts"]

def test_forget_graph(client):
    # 1. Store relationship
    client.post("/store/targeted", json={
        "content": "Ty is married to Karen",
        "type": "relationship",
        "subject": "Ty",
        "relation": "married_to",
        "object": "Karen",
        "namespace": "test"
    })
    
    # 2. Forget about 'Ty'
    client.post("/memory/forget", json={"query": "Forget everything about Ty", "namespace": "test"})
    
    # 3. Verify graph is empty for Ty
    res = client.post("/retrieve/all", json={"query": "Ty", "namespace": "test"})
    assert len(res.json()["relationships"]) == 0
