def test_namespace_isolation_vector(client):
    # Store a fact in namespace 'A'
    client.post("/store/targeted", json={
        "content": "My favorite color is Blue",
        "type": "fact",
        "namespace": "A"
    })
    
    # Store a conflicting fact in namespace 'B'
    client.post("/store/targeted", json={
        "content": "My favorite color is Red",
        "type": "fact",
        "namespace": "B"
    })
    
    # Retrieve from A
    res_a = client.post("/retrieve/all", json={"query": "color", "namespace": "A"})
    assert "My favorite color is Blue" in res_a.json()["facts"]
    assert "My favorite color is Red" not in res_a.json()["facts"]
    
    # Retrieve from B
    res_b = client.post("/retrieve/all", json={"query": "color", "namespace": "B"})
    assert "My favorite color is Red" in res_b.json()["facts"]
    assert "My favorite color is Blue" not in res_b.json()["facts"]

def test_namespace_isolation_graph(client):
    # Relationship in A
    client.post("/store/targeted", json={
        "content": "Alice is the boss of Bob",
        "type": "relationship",
        "subject": "Alice",
        "relation": "boss_of",
        "object": "Bob",
        "namespace": "A"
    })
    
    # Same entities, different relationship in B
    client.post("/store/targeted", json={
        "content": "Alice is the friend of Bob",
        "type": "relationship",
        "subject": "Alice",
        "relation": "friend_of",
        "object": "Bob",
        "namespace": "B"
    })
    
    # Retrieve from A
    res_a = client.post("/retrieve/all", json={"query": "Alice", "namespace": "A"})
    rels_a = [r["relation"] for r in res_a.json()["relationships"]]
    assert "boss_of" in rels_a
    assert "friend_of" not in rels_a
    
    # Retrieve from B
    res_b = client.post("/retrieve/all", json={"query": "Alice", "namespace": "B"})
    rels_b = [r["relation"] for r in res_b.json()["relationships"]]
    assert "friend_of" in rels_b
    assert "boss_of" not in rels_b
