import matplotlib.pyplot as plt
import networkx as nx
import os
import pickle

def visualize_graph(graph, title="Rulebook Graph"):
    """
    Visualizes a NetworkX graph with color-coded nodes and labeled edges.
    Saves the figure in the output folder as 'graph_visualization.png'.
    """
    print("Starting graph visualization...")

    plt.figure(figsize=(18, 12))
    pos = nx.spring_layout(graph, k=0.9, iterations=50)

    # Assign colors based on node type
    node_colors = []
    for node, data in graph.nodes(data=True):
        node_type = data.get('type')
        if node_type == 'Validation_Rule':
            node_colors.append('skyblue')
        elif node_type == 'Scope_Rule':
            node_colors.append('lightcoral')
        elif node_type == 'Section_Header':
            node_colors.append('lightgreen')
        elif node_type == 'Outcome':
            node_colors.append('gold')
        elif node_type == 'Precondition':
            node_colors.append('plum')
        elif node_type == 'Fallback_Rule':
            node_colors.append('orange')
        else:
            node_colors.append('lightgray')

    nx.draw_networkx_nodes(
        graph, pos, node_color=node_colors, node_size=3000, alpha=0.9
    )
    nx.draw_networkx_edges(
        graph, pos, edge_color='gray', arrows=True, arrowsize=20
    )
    nx.draw_networkx_labels(
        graph, pos, font_size=8, font_weight='bold'
    )

    edge_labels = nx.get_edge_attributes(graph, 'relation')
    nx.draw_networkx_edge_labels(
        graph, pos, edge_labels=edge_labels, font_size=7
    )

    plt.title(title, size=20)
    plt.axis('off')
    plt.tight_layout()

    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)
    output_path = "output/graph_from_rulebook.png"
    print(f"Saving image to {output_path} ...")
    plt.savefig(output_path)
    print("Image saved successfully.")
    plt.show()
    print("Graph visualization complete.")

if __name__ == "__main__":
    # 
    # 
    # print("Loading graph from graph_retrieval_validator/output/new_validation_graph.pkl ...")
    with open("output/New_validation_graph.pkl", "rb") as f:
    #with open("graph_retrieval_validator/output/semantic_document_graph.pkl", "rb") as f:
        graph = pickle.load(f)
    print("Graph loaded successfully.")
    visualize_graph(graph, title="Claim Validation Rulebook Graph")
