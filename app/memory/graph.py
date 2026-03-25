import os
import networkx as nx
import json
from dotenv import load_dotenv

load_dotenv()

class GraphStorage:
    def __init__(self):
        self.db_path = os.getenv("GRAPH_DB_PATH", "data/graph.json")
        self.graph = nx.MultiDiGraph()
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                data = json.load(f)
                # Load as MultiDiGraph to support same entities in different namespaces
                self.graph = nx.node_link_graph(data, multigraph=True)
        else:
            self.graph = nx.MultiDiGraph()

    def _save_graph(self):
        with open(self.db_path, "w") as f:
            data = nx.node_link_data(self.graph)
            json.dump(data, f)

    def add_relationship(self, subject: str, relation: str, obj: str, namespace: str = "default"):
        # Normalize to lower case for consistency
        s, r, o = subject.lower().strip(), relation.lower().strip(), obj.lower().strip()
        # Using MultiDiGraph allows multiple edges between s and o. 
        # We'll use the namespace as part of the edge attributes.
        self.graph.add_edge(s, o, relation=r, namespace=namespace)
        self._save_graph()

    def get_related_entities(self, entity: str, namespace: str = "default"):
        entity = entity.lower().strip()
        if not self.graph.has_node(entity):
            return []
        
        results = []
        # MultiDiGraph.out_edges(entity, data=True) returns (u, v, data)
        for u, v, data in self.graph.out_edges(entity, data=True):
            if data.get("namespace") == namespace:
                results.append({
                    "subject": u,
                    "relation": data["relation"],
                    "object": v
                })
        
        # MultiDiGraph.in_edges(entity, data=True) returns (u, v, data)
        for u, v, data in self.graph.in_edges(entity, data=True):
            if data.get("namespace") == namespace:
                results.append({
                    "subject": u,
                    "relation": data["relation"],
                    "object": v
                })
        return results

    def find_relationships_for_query(self, query_text: str, namespace: str = "default"):
        # Very simple entity extraction (words that are in our nodes)
        found_relationships = []
        for node in self.graph.nodes:
            if node in query_text.lower():
                found_relationships.extend(self.get_related_entities(node, namespace=namespace))
        return found_relationships

# Singleton instance
graph_db = GraphStorage()
