import os
import json
import pickle
import pandas as pd
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, List, Tuple
#from graph_retriever import retrieve_paths_from_graph
from graph_retriever_test import retrieve_paths_from_graph



# === Load Env & Gemini ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = genai.GenerativeModel(model_name="gemini-2.0-flash")


# === Paths ===
RULEBOOK_GRAPH_PATH = "../output/New_validation_graph.pkl"
CLAIMS_PATH = "../data/Input_compare_report.xlsx"
FIELD_MAPPING_PATH = "../graph_retrieval_validator/new_auto_field_mapping.json"
OUTPUT_PATH = "output/graph_validation_results_llm.xlsx"

# === Load Files ===
with open(RULEBOOK_GRAPH_PATH, "rb") as f:
    rulebook_graph = pickle.load(f)

df = pd.read_excel(CLAIMS_PATH)
claims = df.to_dict(orient="records")

with open(FIELD_MAPPING_PATH, "r") as f:
    field_mapping = json.load(f)

# === Utility ===
def detect_claim_type(claim: Dict[str, Any]) -> str:
    match = str(claim.get("MATCH_OVERALL", "")).strip().upper()
    pre = str(claim.get("PRE_CLAIM_STATUS", "")).strip().upper()
    post = str(claim.get("POST_CLAIM_STATUS", "")).strip().upper()
    if match == "NO" and pre == "P" and post == "P":
        return "Paid→Paid"
    elif match == "NO" and pre == "R" and post == "R":
        return "Reject→Reject"
    elif match == "NO" and pre == "P" and post == "R":
        return "Paid→Reject"
    elif match == "NO" and pre == "R" and post == "P":
        return "Reject→Paid"
    return "Exact Match"

def generate_llm_explanation(claim_type, matched_concepts, rule_paths, mapped_concepts, outcome) -> str:
    prompt = f"""
You are a healthcare claims analyst assistant. Given the following mismatched claim information, write a short, clear explanation for the user:

- Claim Type: {claim_type}
- Matched Concepts: {matched_concepts}
- Rule Paths: {rule_paths}
- Mapped Plan Concepts: {mapped_concepts}
- Outcome: {outcome}

Write a one-sentence explanation for the mismatch reason.
"""
    try:
        response = llm.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"LLM Error: {str(e)}"


def validate_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    claim_type = detect_claim_type(claim)
    paths, matched_concepts = retrieve_paths_from_graph(claim, rulebook_graph, claim_type)

    mismatched_fields = []
    field_changes = []
    related_plan_nodes = {}

    for key in claim.keys():
        if key.startswith("PRE_"):
            post_key = key.replace("PRE_", "POST_")
            pre_val = claim.get(key)
            post_val = claim.get(post_key)

            if str(pre_val).strip() != str(post_val).strip():
                field_name = key.replace("PRE_", "")
                mismatched_fields.append(field_name)
                field_changes.append(f"{field_name}: {pre_val} → {post_val}")
                related = field_mapping.get(key, []) + field_mapping.get(post_key, [])
                if related:
                    related_plan_nodes[field_name] = list(set(related))

    outcome = "Valid_Mismatch" if any("Valid_Mismatch" in p for p in paths) else "Invalid_Mismatch"

    llm_explanation = generate_llm_explanation(
        claim_type,
        "; ".join(matched_concepts),
        " | ".join([" → ".join(p) for p in paths]),
        json.dumps(related_plan_nodes),
        outcome
    )

    return {
        "PRE_RXCLAIM_NUMBER": claim.get("PRE_RXCLAIM_NUMBER", ""),
        "POST_RXCLAIM_NUMBER": claim.get("POST_RXCLAIM_NUMBER", ""),
        "PRE_CLAIM_STATUS": claim.get("PRE_CLAIM_STATUS", ""),
        "POST_CLAIM_STATUS": claim.get("POST_CLAIM_STATUS", ""),
        "PRE_REJECT_CODE_1": claim.get("PRE_REJECT_CODE_1", ""),
        "POST_REJECT_CODE_1": claim.get("POST_REJECT_CODE_1", ""),
        "Claim Type": claim_type,
        "Matched Concepts": "; ".join(matched_concepts),
        "Rule Paths": " | ".join([" → ".join(p) for p in paths]),
        "Mapped Plan Concepts": json.dumps(related_plan_nodes),
        "Outcome": outcome,
        "LLM Explanation": llm_explanation
    }

# # === Run for All Claims ===
# results = [validate_claim(claim) for claim in claims]
# df_results = pd.DataFrame(results)
# os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
# df_results.to_excel(OUTPUT_PATH, index=False)

# print(f"✅ Graph validation results saved to: {OUTPUT_PATH}")

# === Batched Parallel Execution ===
def process_claims_in_batches(claims: List[Dict[str, Any]], batch_size=50, max_workers=10):
    all_results = []
    total_batches = (len(claims) + batch_size - 1) // batch_size

    for batch_index in range(total_batches):
        start = batch_index * batch_size
        end = min(start + batch_size, len(claims))
        batch = claims[start:end]
        print(f"\nProcessing batch {batch_index + 1}/{total_batches} (Claims {start + 1} to {end})")

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_claim = {executor.submit(validate_claim, claim): claim for claim in batch}
            for future in tqdm(as_completed(future_to_claim), total=len(batch), desc="Batch Progress"):
                try:
                    results.append(future.result())
                except Exception as e:
                    claim = future_to_claim[future]
                    results.append({
                        "PRE_RXCLAIM_NUMBER": claim.get("PRE_RXCLAIM_NUMBER", ""),
                        "POST_RXCLAIM_NUMBER": claim.get("POST_RXCLAIM_NUMBER", ""),
                        "Outcome": f"Validation Error: {str(e)}"
                    })
        all_results.extend(results)
    return all_results

# === Run ===
if __name__ == "__main__":
    print(" Starting batched parallel claim validation...")
    results = process_claims_in_batches(claims, batch_size=50, max_workers=10)

    df_results = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df_results.to_excel(OUTPUT_PATH, index=False)

    print(f"\n Graph validation results saved to: {OUTPUT_PATH}")

