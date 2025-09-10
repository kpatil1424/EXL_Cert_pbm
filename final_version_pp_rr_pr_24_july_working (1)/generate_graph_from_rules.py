import networkx as nx
import re
import os
import pickle

def generate_graph_from_rules(rules):
    G = nx.DiGraph()

    for rule in rules:
        node = rule.get("Rule Name").strip()
        if not node:
            continue

        # Add node with attributes
        G.add_node(node, 
                   Cause=rule.get("Cause", ""),
                   Effect=rule.get("Effect", ""),
                   Node_Type=rule.get("Node_Type", "Unknown"),
                   Parent_Node=rule.get("Parent_Node", ""),
                   Precondition=rule.get("Precondition", ""),
                   Section=rule.get("Section", "")
        )

        # Add edge from rule node to target node
        edge_target = rule.get("Edge_Target","").strip()
        edge_type = rule.get("Edge_Type", "Causes").strip()

        if edge_target:
            # G.add_edge(node, edge_target, Edge_Type=edge_type)
            # print(f"📌 Added edge: {node} → {edge_target} ({edge_type})")
            
            if node == "Different Local Messages" and edge_target == "Deeper_Field_Differences" and edge_type == "Proceeds_To":
                    # Ensure it only adds this specific edge and doesn't get confused by other logic
                if not G.has_edge(node, edge_target):
                    G.add_edge(node, edge_target, Edge_Type=edge_type)
                    print(f"📌 Added specific edge: {node} → {edge_target} ({edge_type})")
                continue # Skip general edge addition for this specific case

            if not G.has_edge(node, edge_target): # Prevent duplicate edges
                G.add_edge(node, edge_target, Edge_Type=edge_type)
                print(f"📌 Added edge: {node} → {edge_target} ({edge_type})")

    # if not G.has_edge("SME_Review", "Invalid_Mismatch"):
    #     G.add_edge("SME_Review", "Invalid_Mismatch", Edge_Type="Requires")
    #     print("Added fallback edge: SME_Review → Invalid_Mismatch")

    return G

def save_graph(graph, path="output/New_validation_graph.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(graph, f)
    print(f"Graph saved as {path}")
