# File: graph_retrieval_validator/mapping_generator.py

import pickle
import re
import json
import os
import networkx as nx
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai

def extract_post_fields_from_rulebook(rulebook_path: str) -> List[str]:
    with open(rulebook_path, "r") as f:
        content = f.read()

    # Find all lines with "**Cause**: ..."
    cause_lines = re.findall(r"\*\*Cause\*\*: (.+)", content)

    post_fields = set()
    for line in cause_lines:
        # Extract all POST_ fields
        fields = re.findall(r"\b(POST_[A-Z0-9_]+)\b", line)
        post_fields.update(fields)

    return sorted(post_fields)


# === CONFIG ===
PLAN_GRAPH_PATH = "output/semantic_document_graph.pkl"
OUTPUT_MAPPING_PATH = "../graph_retrieval_validator/new_auto_field_mapping.json"
RULEBOOK_PATH = "../graph_rulebook/GraphRAG-Compatible Rulebook Format.md"
CLAIM_FIELDS = extract_post_fields_from_rulebook(RULEBOOK_PATH)
#     "PRE_INGREDIENT_COST_CLIENT",
#     "POST_COPAY_AMOUNT",
#     "PRE_TIER_CODE",
#     "POST_QUANTITY_LIMIT",
#     "PRE_DRUG_SPECIFIC_COPAY",
#     "PRE_CLIENT_PATIENT_SCHEDULE",
#     "PRE_DISPENSING_FEE"
# ]

# === Load Environment ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Initialize Gemini Model ===
llm = genai.GenerativeModel(model_name="gemini-2.0-flash")

# === Load Semantic Plan Graph ===
with open(PLAN_GRAPH_PATH, "rb") as f:
    graph: nx.DiGraph = pickle.load(f)

# === Extract Plan Concept Phrases from Semantic Graph ===
doc_concepts = set()
for node_id, data in graph.nodes(data=True):
    if "label" in data:
        doc_concepts.add(data["label"])
    if "cause" in data:
        doc_concepts.add(data["cause"])
    if "effect" in data:
        doc_concepts.add(data["effect"])

# Clean and sort
doc_concepts = sorted({text.strip() for text in doc_concepts if len(text.strip()) > 4})

# === Gemini-Powered Semantic Mapper ===
def ask_gemini(field: str, candidates: List[str]) -> List[str]:
    prompt = f"""
You are aligning healthcare claim field names with relevant policy phrases from a structured insurance document graph.

Given the claim field: **{field}**, return only 2 to 4 semantically matching phrases from the plan document concepts listed below.
Reply only with exact matches (no explanation, no formatting).

Example:
Field: PRE_COPAY_AMOUNT
Output:
Copay is $10
Tier 1 Copay
Deductible is $50

Plan document phrases:
{json.dumps(candidates, indent=2)}
"""
    response = llm.generate_content(prompt)
    lines = response.text.splitlines()
    return [line.strip().lstrip("*•-– ").strip('"').strip() for line in lines if len(line.strip()) > 4]

# === Perform Field Mapping ===
field_mapping: Dict[str, List[str]] = {}

print("🔍 Generating semantic field mappings with Gemini...")
for field in CLAIM_FIELDS:
    print(f"\n🔗 Mapping for: {field}")
    matches = ask_gemini(field, doc_concepts)
    cleaned_matches = [m.strip() for m in matches if len(m.strip()) > 4]
    field_mapping[field] = cleaned_matches
    print(f"✅ Mapped to: {cleaned_matches}")

# === Save Mapping Output ===
os.makedirs(os.path.dirname(OUTPUT_MAPPING_PATH), exist_ok=True)
with open(OUTPUT_MAPPING_PATH, "w") as f:
    json.dump(field_mapping, f, indent=2)

print(f"\n✅ Mapping complete. Saved to: {OUTPUT_MAPPING_PATH}")