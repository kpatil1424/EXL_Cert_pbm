import pickle
import networkx as nx
import os

RULEBOOK_GRAPH_PATH = '../output/New_validation_graph.pkl' # Adjust path if needed

def inspect_node_edges(node_id_to_check: str):
    if not os.path.exists(RULEBOOK_GRAPH_PATH):
        print(f"Error: Rulebook Graph not found at {RULEBOOK_GRAPH_PATH}.")
        return

    print(f"Loading Rulebook Graph from {RULEBOOK_GRAPH_PATH}...")
    with open(RULEBOOK_GRAPH_PATH, 'rb') as f:
        rulebook_graph = pickle.load(f)
    print("Rulebook Graph loaded.")

    if node_id_to_check not in rulebook_graph:
        print(f"Node '{node_id_to_check}' not found in the graph.")
        # Print all nodes to help diagnose if name is slightly off
        print("\n--- All Nodes in Graph (for debugging) ---")
        for node in rulebook_graph.nodes():
            print(f"- {node}")
        return

    print(f"\n--- Details for Node: '{node_id_to_check}' ---")
    print(f"Attributes: {rulebook_graph.nodes[node_id_to_check]}")

    print(f"\n--- Successor Edges from '{node_id_to_check}' ---")
    found_edges = False
    for successor in rulebook_graph.successors(node_id_to_check):
        edge_data = rulebook_graph.get_edge_data(node_id_to_check, successor)
        print(f"  → {successor} (Edge Data: {edge_data})")
        found_edges = True
    
    if not found_edges:
        print(f"  No outgoing edges from '{node_id_to_check}'.")

if __name__ == "__main__":
    # Check for the specific node name
    inspect_node_edges("Different Local Messages (Same Reject)")
    