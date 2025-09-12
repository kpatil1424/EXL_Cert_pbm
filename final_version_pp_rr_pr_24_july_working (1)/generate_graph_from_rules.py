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



Here’s the high-level mapping approach, Kunal:
	1.	Map plan code → document plan
Use POST_XREF_PLAN_CODE to pick the right plan section in the BPS doc:
PCCBPPO→BASIC, PCEPPPO→ECONOMY, PCHDHP→HDHP.
	2.	Pick the correct cost-share section
From POST fields, choose which table to read:
	•	Specialty delivery → Specialty Member Cost Share
	•	POST_NETWORK ∈ {GOV90P, GOVCLP} → Stepped (VA) Member Cost Share
	•	POST_DRUG_SPECIFIC_COPAY == SX_MST-EES → Specialty Member Cost Share
	•	else → Member Cost Share (standard)
	3.	Normalize lookup keys
Clean values (uppercase/trim), cast numbers (tier, days).
Build keys: (plan_section, cost_share_section, tier, delivery, day_supply).
	4.	Apply Retail-90 rule (if applicable)
If delivery=Retail and days=90 (and your config allows), use Mail copay row for lookup.
	5.	Sanity check the target table
Confirm the chosen (plan_section, section) exists in the BPS document graph; if not, flag SME Review.
	6.	Emit a MappingResult
Return the resolved plan section, chosen cost-share section, final lookup keys, and any notes (e.g., “Retail-90→Mail applied”).

That’s it—the mapping hands a precise “where to look” pointer to your validators (e.g., Copay validator), which then performs the actual comparison.



            
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
