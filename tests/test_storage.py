def test_vector_storage_add_query(mock_vector_db):
    content = "Ty is 42 years old."
    mock_vector_db.add_fact(content)
    
    results = mock_vector_db.query_facts("How old is Ty?")
    assert content in results["documents"][0]

def test_graph_storage_add_query(mock_graph_db):
    mock_graph_db.add_relationship("Ty", "married_to", "Karen")
    
    results = mock_graph_db.get_related_entities("Ty")
    assert len(results) == 1
    assert results[0]["object"] == "karen" # Normalized
    assert results[0]["relation"] == "married_to"

def test_graph_reverse_query(mock_graph_db):
    mock_graph_db.add_relationship("Ty", "married_to", "Karen")
    
    # Querying by the object should also find the relationship
    results = mock_graph_db.get_related_entities("Karen")
    assert len(results) == 1
    assert results[0]["subject"] == "ty"
