import fitz  # PyMuPDF
import re
import os
import pickle
import networkx as nx

# === CONFIGURATION ===
PDF_PATH = "../data/HealthSelect_of_Texas_Prescription_Drug_Program_ERS.pdf"
OUTPUT_PATH = "output/semantic_document_graph.pkl"
DEBUG = True

# === UTILITIES ===
def clean_id(text: str) -> str:
    return re.sub(r'\W+', '_', text.strip()).upper()[:100]

def classify_node_type(label: str) -> str:
    label_lower = label.lower()
    if "copay" in label_lower:
        return "Outcome"
    elif "deductible" in label_lower:
        return "Precondition"
    elif "coverage" in label_lower or "covered" in label_lower:
        return "Scope_Rule"
    elif "exception" in label_lower or "exclusion" in label_lower:
        return "Exclusion"
    elif "section" in label_lower:
        return "Section_Header"
    elif any(k in label_lower for k in ["cost", "charge", "fee"]):
        return "Outcome"
    elif "definition" in label_lower or "means" in label_lower:
        return "Definition"
    else:
        return "Definition"

# === STEP 1: Extract all PDF text ===
def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text() for page in doc])

# === STEP 2: Extract rule-like lines ===
def extract_rules(text: str):
    rules = []
    lines = text.splitlines()
    context = "DOCUMENT"
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 6:
            continue

        if re.match(r"^(Section|SECTION)\s+\d+", line):
            context = line.upper()

        rule_type = "Fact"
        cause = context
        effect = line

        if re.match(r"(?i)if (.+?) then (.+)", line):
            match = re.match(r"(?i)if (.+?) then (.+)", line)
            rule_type = "IfThen"
            cause = match.group(1).strip()
            effect = match.group(2).strip()
        elif re.match(r"(.+?) causes (.+)", line, re.IGNORECASE):
            match = re.match(r"(.+?) causes (.+)", line, re.IGNORECASE)
            rule_type = "Causal"
            cause = match.group(1).strip()
            effect = match.group(2).strip()
        elif re.match(r"Due to (.+?), (.+)", line, re.IGNORECASE):
            match = re.match(r"Due to (.+?), (.+)", line, re.IGNORECASE)
            rule_type = "DueTo"
            cause = match.group(1).strip()
            effect = match.group(2).strip()
        elif "$" in line or "copay" in line.lower() or "deductible" in line.lower():
            rule_type = "Fact"

        rules.append({
            "title": line,
            "cause": cause,
            "effect": effect,
            "type": rule_type,
            "context": context
        })

    return rules

# === STEP 3: Build a semantic graph ===
def build_graph(rules: list) -> nx.DiGraph:
    G = nx.DiGraph()
    root = "ROOT"
    G.add_node(root, type="Conceptual_Root", label="Document Root")

    for rule in rules:
        context_node = clean_id(rule["context"])
        rule_node = clean_id(rule["title"])

        node_type = classify_node_type(rule["title"])
        G.add_node(context_node, type="Section_Header", label=rule["context"])
        G.add_node(rule_node, type=node_type, cause=rule["cause"], effect=rule["effect"], label=rule["title"])

        G.add_edge(root, context_node, type="belongs_to")
        G.add_edge(context_node, rule_node, type="has_rule")

        if DEBUG:
            print(f"✅ {node_type}: {context_node} → {rule_node}")

    return G

# === STEP 4: Save graph ===
def save_graph(graph: nx.DiGraph, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump(graph, f)
    print(f"💾 Graph saved to: {output_path}")

# === MAIN DRIVER ===
def generate_semantic_graph():
    print("📖 Extracting text...")
    text = extract_text(PDF_PATH)

    print("🔍 Extracting rule-like statements...")
    rules = extract_rules(text)
    print(f"📦 Found {len(rules)} rules")

    print("🧠 Building semantic graph...")
    graph = build_graph(rules)

    print("💾 Saving graph to .pkl...")
    save_graph(graph, OUTPUT_PATH)

    print("✅ Done.")

# === Run ===
if __name__ == "__main__":
    generate_semantic_graph()