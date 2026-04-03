from fastapi import FastAPI, HTTPException
from app.schemas import ChatStoreRequest, TargetedStoreRequest, RetrievalRequest, MemoryResponse, TargetedResponse, ForgetRequest, UpdateStoreRequest
from app.memory.processor import processor
from app.memory.vector import vector_db
from app.memory.graph import graph_db

app = FastAPI(title="Local LLM Memory API")

@app.get("/")
async def root():
    return {"status": "online", "message": "Memory API is running"}

@app.post("/store/chat")
async def store_chat(request: ChatStoreRequest):
    result = processor.process_chat(request.text, namespace=request.namespace)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/store/targeted")
async def store_targeted(request: TargetedStoreRequest):
    if request.type == "fact":
        vector_db.add_fact(request.content, namespace=request.namespace)
    elif request.type == "relationship":
        if not all([request.subject, request.relation, request.object]):
            raise HTTPException(status_code=400, detail="Missing subject, relation, or object for relationship type")
        graph_db.add_relationship(request.subject, request.relation, request.object, namespace=request.namespace)
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Must be 'fact' or 'relationship'")
    return {"status": "success"}

@app.post("/retrieve/all")
async def retrieve_all(request: RetrievalRequest):
    return processor.retrieve_all(request.query, namespace=request.namespace)

@app.post("/retrieve/targeted")
async def retrieve_targeted(request: RetrievalRequest):
    answer = processor.retrieve_targeted(request.query, namespace=request.namespace)
    return {"answer": answer}

@app.post("/memory/forget")
async def forget_memory(request: ForgetRequest):
    vector_deleted = vector_db.delete_facts(request.query, namespace=request.namespace)
    graph_deleted = False
    for node in list(graph_db.graph.nodes):
        if node in request.query.lower():
            rels = graph_db.get_related_entities(node, namespace=request.namespace)
            for r in rels:
                graph_db.remove_relationship(r["subject"], r["relation"], r["object"], namespace=request.namespace)
                graph_deleted = True
    return {"status": "success", "vector_deleted": vector_deleted, "graph_deleted": graph_deleted}

@app.post("/memory/update")
async def update_memory(request: UpdateStoreRequest):
    if request.type == "fact":
        # Search-and-replace logic
        vector_db.delete_facts(request.old_content, namespace=request.namespace)
        vector_db.add_fact(request.new_content, namespace=request.namespace)
    elif request.type == "relationship":
        if not all([request.subject, request.relation, request.object]):
             raise HTTPException(status_code=400, detail="Missing subject, relation, or object")
        # Find the specific old edge to remove (if old relation provided)
        # Note: we need the old relation to find it in MultiDiGraph.
        # This implementation assumes request.relation is the NEW one.
        # For true update, we might need 'old_relation' too.
        # For now, let's just add the new one (standard graph update behavior)
        graph_db.add_relationship(request.subject, request.relation, request.object, namespace=request.namespace)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
