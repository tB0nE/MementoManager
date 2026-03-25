import os
import networkx as nx
import json
from dotenv import load_dotenv

load_dotenv()

class GraphStorage:
    def __init__(self):
        self.db_path = os.getenv("GRAPH_DB_PATH", "data/graph.json")
        self.graph = nx.DiGraph()
        self._load_graph()

    def _load_graph(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                data = json.load(f)
                self.graph = nx.node_link_graph(data)
        else:
            self.graph = nx.DiGraph()

    def _save_graph(self):
        with open(self.db_path, "w") as f:
            data = nx.node_link_data(self.graph)
            json.dump(data, f)

    def add_relationship(self, subject: str, relation: str, obj: str):
        # Normalize to lower case for consistency
        s, r, o = subject.lower().strip(), relation.lower().strip(), obj.lower().strip()
        self.graph.add_edge(s, o, relation=r)
        self._save_graph()

    def get_related_entities(self, entity: str, depth: int = 1):
        entity = entity.lower().strip()
        if not self.graph.has_node(entity):
            return []
        
        # Simple depth-1 search for neighbors
        results = []
        for neighbor in self.graph.neighbors(entity):
            edge_data = self.graph.get_edge_data(entity, neighbor)
            results.append({
                "subject": entity,
                "relation": edge_data["relation"],
                "object": neighbor
            })
        # Reverse edges (who relates to this entity?)
        for predecessor in self.graph.predecessors(entity):
            edge_data = self.graph.get_edge_data(predecessor, entity)
            results.append({
                "subject": predecessor,
                "relation": edge_data["relation"],
                "object": entity
            })
        return results

    def find_relationships_for_query(self, query_text: str):
        # Very simple entity extraction (words that are in our nodes)
        found_relationships = []
        query_words = query_text.lower().split()
        for node in self.graph.nodes:
            if node in query_text.lower():
                found_relationships.extend(self.get_related_entities(node))
        return found_relationships

# Singleton instance
graph_db = GraphStorage()
