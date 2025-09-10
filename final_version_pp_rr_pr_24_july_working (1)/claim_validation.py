import pandas as pd
import re
from generate_graph_from_rules import generate_graph_from_rules, save_graph
import matplotlib.pyplot as plt
import networkx as nx

# Load the Excel file
df = pd.read_excel('data/Input_compare_report.xlsx')

# Preview the data
print(df.head())

# Step 4.1: Load rulebook markdown content
with open('graph_rulebook/GraphRAG-Compatible Rulebook Format.md', 'r') as f:
    rulebook_md = f.read()


def parse_rulebook_markdown(markdown_content):
    """
    Parses the rulebook Markdown content and extracts rule details.
    Returns a list of rule dictionaries.
    """
    rules = []
    current_section = None
    current_rule = {}

    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()

        if line.startswith('## '):  # Main section
            current_section = line[3:].strip()
            continue
        elif line.startswith('### '):  # Subsection
            current_section = line[4:].strip()
            continue
        elif line.startswith('#### Rule:'):
            if current_rule:
                rules.append(current_rule)
            current_rule = {'Rule Name': line[len('#### Rule:'):].strip()}
            current_rule['Section'] = current_section
        elif current_rule and line.startswith('**Cause**:'):
            current_rule['Cause'] = line[len('**Cause**:'):].strip()
        elif current_rule and line.startswith('**Effect**:'):
            current_rule['Effect'] = line[len('**Effect**:'):].strip()
        elif current_rule and line.startswith('**Node_Type**:'):
            current_rule['Node_Type'] = line[len('**Node_Type**:'):].strip()
        elif current_rule and line.startswith('**Parent_Node**:'):
            current_rule['Parent_Node'] = line[len('**Parent_Node**:'):].strip()
        elif current_rule and line.startswith('**Precondition**:'):
            current_rule['Precondition'] = line[len('**Precondition**:'):].strip()
        elif current_rule and line.startswith('**Edge_Type**:'):
            current_rule['Edge_Type'] = line[len('**Edge_Type**:'):].strip()
        elif current_rule and line.startswith('**Edge_Target**:'):
            current_rule['Edge_Target'] = line[len('**Edge_Target**:'):].strip()

    if current_rule:
        rules.append(current_rule)

    return rules

# Step 4.3: Parse the rulebook content
rules = parse_rulebook_markdown(rulebook_md)

# Optional: Print a few parsed rules to verify
for rule in rules[:3]:
    print(rule)

graph = generate_graph_from_rules(rules)
print(f"Graph has {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
save_graph(graph, "output/New_validation_graph.pkl")

