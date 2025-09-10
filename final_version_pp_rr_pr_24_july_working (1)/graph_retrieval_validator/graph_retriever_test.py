import pickle
import networkx as nx
import json
import pandas as pd
from typing import Dict, List, Tuple

# --- DEBUG MODE ---
DEBUG_MODE = True # Set to True to enable detailed print statements for debugging
# --- END DEBUG MODE ---

# === Load Plan Document Graph + Auto Field Mapping ===
try:
    with open("graph_retrieval_validator/output/validation_graph_from_document.pkl", "rb") as f:
        plan_graph = pickle.load(f)
    with open("graph_retrieval_validator/new_auto_field_mapping.json", "r") as f:
        auto_field_map = json.load(f)
except Exception as e:
    if DEBUG_MODE: print(f"Warning: Could not load plan graph or auto field mapping: {e}")
    plan_graph = None
    auto_field_map = {}

def normalize(val):
    if val is None:
        return ""
    return str(val).strip().lower()

# === Field → Plan Node Mapper ===
def get_related_plan_nodes(field_name: str) -> List[str]:
    """
    Use auto_field_mapping to map technical claim fields to semantically related plan document graph nodes.
    """
    if not plan_graph or not auto_field_map:
        if DEBUG_MODE: print(f" Plan graph or mapping missing for {field_name}")
        return []

    mapped_terms = auto_field_map.get(field_name, [])
    related_nodes = set()

    for node_id, attrs in plan_graph.nodes(data=True):
        node_texts = [
            normalize(node_id),
            normalize(attrs.get("label", "")),
            normalize(attrs.get("cause", "")),
            normalize(attrs.get("effect", ""))
        ]
        for phrase in mapped_terms:
            phrase_normalized = normalize(phrase)
            if any(phrase_normalized in t for t in node_texts):
                if DEBUG_MODE: print(f"Mapped {field_name} → {node_id} (matched with '{phrase}')")
                related_nodes.add(node_id)
    if not related_nodes:
        if DEBUG_MODE: print(f" No matches found for: {field_name} → {mapped_terms}")
        
    return sorted(list(related_nodes))

# === Causal Reasoning via Rulebook Graph ===
def retrieve_paths_from_graph(claim: Dict, graph: nx.DiGraph, claim_type: str = "Paid→Paid") -> Tuple[List[List[str]], List[str]]:
    matched_concepts = []
    paths = []

    def diff(pre_field, post_field):
        pre = normalize(claim.get(pre_field, ""))
        post = normalize(claim.get(post_field, ""))
        result = pre != post and (pre != "" or post != "")
        if DEBUG_MODE: print(f"    Diff check for {pre_field} ({pre}) vs {post_field} ({post}): {result}")
        return result

    def contains_prior_auth_trigger(message: str) -> bool:
        if not message:
            return False
        pa_keywords = [
            "prior authorization", "prior auth", "prior auth req",
            "requires prior authorization", "prior auth required", "pa required"
        ]
        result = any(keyword.lower() in message.lower() for keyword in pa_keywords)
        if DEBUG_MODE: print(f"    PA Trigger check for message '{message[:50]}...': {result}")
        return result

    if DEBUG_MODE: print(f"\n--- retrieve_paths_from_graph for Claim Type: {claim_type} ---")

    # === Paid→Paid Field Pairs ===
    if claim_type == "Paid→Paid":
        field_pairs = [
            ("PRE_INGREDIENT_COST_CLIENT", "POST_INGREDIENT_COST_CLIENT", "Ingredient Cost Change"),
            ("PRE_DISPENSING_FEE", "POST_DISPENSING_FEE", "Dispensing Fee Change"),
            ("PRE_AMOUNT_ATTR_TO_SALES_TAX", "POST_AMOUNT_ATTR_TO_SALES_TAX", "Flat Sales Tax Change"),
            ("PRE_SALEX_TAX_PERC_PAID", "POST_SALEX_TAX_PERC_PAID", "Percentage Sales Tax Change"),
            ("PRE_INCENTIVE_FEE", "POST_INCENTIVE_FEE", "Incentive Fee Change"),
            ("PRE_COPAY_AMOUNT", "POST_COPAY_AMOUNT", "Copay Amount Change"),
            ("PRE_APPR_AMT_APPL_PER_DED", "POST_APPR_AMT_APPL_PER_DED", "Deductible Applied Amount Change"),
            ("PRE_PROD_SELECTION_PENALTY", "POST_PROD_SELECTION_PENALTY", "Brand DAW Penalty Change"),
            ("PRE_DRUG_SPECIFIC_COPAY", "POST_DRUG_SPECIFIC_COPAY", "Drug Specific Copay Change"),
            ("PRE_CLIENT_PATIENT_SCHEDULE", "POST_CLIENT_PATIENT_SCHEDULE", "Client Patient Schedule Change"),
            ("PRE_XREF_PLAN_CODE", "POST_XREF_PLAN_CODE", "Plan Code Change"),
        ]
        if DEBUG_MODE: print(f"  Processing Paid->Paid field differences.")
        for pre, post, concept in field_pairs:
            if diff(pre, post):
                matched_concepts.append(concept)
                if DEBUG_MODE: print(f"    Matched concept for Paid->Paid: {concept}")

    # === Reject→Reject Logic (Revised to match Markdown structure) ===
    elif claim_type == "Reject→Reject":
        if DEBUG_MODE: print(f"  Processing Reject->Reject logic.")
        pre_reject_code_raw = claim.get("PRE_REJECT_CODE_1", "")
        post_reject_code_raw = claim.get("POST_REJECT_CODE_1", "")
        
        pre_reject_code = normalize(str(int(float(pre_reject_code_raw)))) if pd.notna(pre_reject_code_raw) else ""
        post_reject_code = normalize(str(int(float(post_reject_code_raw)))) if pd.notna(post_reject_code_raw) else ""

        pre_local_message = normalize(claim.get("PRE_LOCAL_MESSAGE", ""))
        post_local_message = normalize(claim.get("POST_LOCAL_MESSAGE", ""))

        if DEBUG_MODE:
            print(f"    PRE_REJECT_CODE_1: '{pre_reject_code}'")
            print(f"    POST_REJECT_CODE_1: '{post_reject_code}'")
            print(f"    PRE_LOCAL_MESSAGE: '{pre_local_message}'")
            print(f"    POST_LOCAL_MESSAGE: '{post_local_message}'")

        # 1. Scope of Validation: In-Scope Reject Code Pairs
        in_scope_pairs = [("76", "76"), ("75", "76"), ("76", "75")]
        is_in_scope = False
        if (pre_reject_code, post_reject_code) in in_scope_pairs:
            matched_concepts.append("In-Scope Reject Code Pairs")
            is_in_scope = True
            if DEBUG_MODE: print(f"    Matched concept: In-Scope Reject Code Pairs")
        else:
            matched_concepts.append("Out-of-Scope Reject Code Pairs")
            if DEBUG_MODE: print(f"    Matched concept: Out-of-Scope Reject Code Pairs")

        if is_in_scope:
            # 2. Same Reject Code Case
            if pre_reject_code == post_reject_code and pre_reject_code == "76":
                if DEBUG_MODE: print(f"    Entering Same Reject Code Case (Code 76).")
                if pre_local_message == post_local_message:
                    matched_concepts.append("Matching Local Messages (Same Reject)") 
                    if DEBUG_MODE: print(f"      Matched concept: Matching Local Messages (Same Reject)")
                elif pre_local_message != post_local_message:
                    matched_concepts.append("Different Local Messages (Same Reject)")
                    if DEBUG_MODE: print(f"      Matched concept: Different Local Messages (Same Reject)")

            # 3. Cross Reject Code Cases
            elif pre_reject_code != post_reject_code:
                if DEBUG_MODE: print(f"    Entering Cross Reject Code Cases.")
                if pre_local_message == post_local_message:
                    matched_concepts.append("Matching Local Messages (Cross Reject)")
                    if DEBUG_MODE: print(f"      Matched concept: Matching Local Messages (Cross Reject)")
                elif pre_local_message != post_local_message:
                    matched_concepts.append("Different Local Messages (Cross Reject)")
                    if DEBUG_MODE: print(f"      Matched concept: Different Local Messages (Cross Reject)")

                    # If "Different Local Messages (Cross Reject)" is matched, proceed to deeper field check
                    deeper_fields_detected = False
                    deeper_field_pairs = [
                        ("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS", "PA Layer Changed"),
                        ("PRE_DRUGLIST_DETAIL", "POST_DRUGLIST_DETAIL", "Drug List Changed"),
                        ("PRE_SMART_PA_OVERALL", "POST_SMART_PA_OVERALL", "Smart PA Overall Changed"),
                        ("PRE_DAYS_SUPPLY", "POST_DAYS_SUPPLY", "Days Supply Changed"),
                        ("PRE_FINAL_PLAN_CODE", "POST_FINAL_PLAN_CODE", "Final Plan Code Changed"),
                        ("PRE_NETWORK", "POST_NETWORK", "Network Changed"),
                    ]
                    if DEBUG_MODE: print(f"      Checking deeper fields for differences.")
                    for pre_f, post_f, concept in deeper_field_pairs:
                        if diff(pre_f, post_f):
                            matched_concepts.append(concept)
                            deeper_fields_detected = True
                            if DEBUG_MODE: print(f"        Matched deeper concept: {concept}")
                    
                    if not deeper_fields_detected:
                        matched_concepts.append("No Deeper Differences")
                        if DEBUG_MODE: print(f"        Matched concept: No Deeper Differences (Fallback for Cross Reject Code Cases)")

    # === Paid→Reject logic ===
    elif claim_type == "Paid→Reject":
        if DEBUG_MODE: print(f"  Processing Paid->Reject logic.")
        post_reject_code_raw = claim.get("POST_REJECT_CODE_1", "")
        post_reject_code = normalize(str(int(float(post_reject_code_raw)))) if pd.notna(post_reject_code_raw) else ""
        post_local_message = normalize(claim.get("POST_LOCAL_MESSAGE", ""))

        if DEBUG_MODE:
            print(f"    POST_REJECT_CODE_1: '{post_reject_code}'")
            print(f"    POST_LOCAL_MESSAGE: '{post_local_message}'")

        if post_reject_code == "75":
            matched_concepts.append("Reject Code Is 75")
            if DEBUG_MODE: print(f"    Matched concept: Reject Code Is 75")
            if contains_prior_auth_trigger(post_local_message):
                matched_concepts.append("Local Message Indicates PA")
                if DEBUG_MODE: print(f"      Matched concept: Local Message Indicates PA")
                if diff("PRE_PA_REASON_CODE", "POST_PA_REASON_CODE") or diff("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS"):
                    matched_concepts.append("PA Reason or Layer Changed")
                    if DEBUG_MODE: print(f"        Matched concept: PA Reason or Layer Changed")
                else:
                    matched_concepts.append("PA Reason and Layer Same")
                    if DEBUG_MODE: print(f"        Matched concept: PA Reason and Layer Same")
            else:
                matched_concepts.append("Local Message Lacks PA Trigger")
                if DEBUG_MODE: print(f"      Matched concept: Local Message Lacks PA Trigger")
        else:
            matched_concepts.append("Reject Code Is Not 75")
            if DEBUG_MODE: print(f"    Matched concept: Reject Code Is Not 75")

    else:
        if DEBUG_MODE: print(f"  Unsupported claim type: {claim_type}")
        return [], ["Unsupported claim type"]

    if DEBUG_MODE: print(f"\n  Matched Concepts before graph traversal: {matched_concepts}")

    # === Traverse causal paths in Rulebook Graph ===
    # This loop needs to be smart about "Proceeds_To" edges
    final_paths = []
    
    # Process concepts that directly lead to outcomes or are terminal
    for concept in matched_concepts:
        if graph.has_node(concept):
            node_data = graph.nodes[concept]
            edge_type = node_data.get('Edge_Type') # Check if rule has a direct Edge_Type attribute
            edge_target = node_data.get('Edge_Target') # Check if rule has a direct Edge_Target attribute

            # If it's a "Proceeds_To" rule, it's not a final path, it's an intermediate step
            if edge_type == "Proceeds_To" and edge_target:
                # We've already handled the deeper field matching in the Reject->Reject block
                # So, if 'Different Local Messages (Cross Reject)' is matched, we don't need to
                # find a path from it to a final outcome. Its purpose is to enable deeper checks.
                if DEBUG_MODE: print(f"    Concept '{concept}' is a 'Proceeds_To' rule, not a direct outcome path. Skipping direct path finding for it.")
                continue # Skip finding paths from this node directly to Valid/Invalid Mismatch

            try:
                if DEBUG_MODE: print(f"    Attempting to find paths from concept: '{concept}'")
                concept_paths = list(nx.all_simple_paths(graph, source=concept, target="Valid_Mismatch", cutoff=4))
                concept_paths.extend(list(nx.all_simple_paths(graph, source=concept, target="Invalid_Mismatch", cutoff=4)))
                
                if concept_paths:
                    final_paths.extend(concept_paths)
                    if DEBUG_MODE: print(f"      Found paths for '{concept}': {concept_paths}")
                else:
                    if DEBUG_MODE: print(f"      No paths found from '{concept}' to Valid_Mismatch or Invalid_Mismatch within cutoff.")
            except nx.NetworkXNoPath:
                if DEBUG_MODE: print(f"      NetworkXNoPath exception for concept: '{concept}'")
                continue
        else:
            if DEBUG_MODE: print(f"    Concept '{concept}' not found as a node in the graph.")

    # === Fallback Path if No Match (Only for Paid->Paid, Paid->Reject if not handled by explicit rules) ===
    # The Reject->Reject fallback ("No Deeper Differences") is now handled within the explicit logic above.
    if not final_paths: # Use final_paths here
        fallback = None
        if claim_type == "Paid→Paid":
            fallback = "No Identified Differences"
        elif claim_type == "Paid→Reject":
            fallback = "Missing or Unexpected Data"

        if fallback and graph.has_node(fallback):
            if not graph.has_edge(fallback, "SME_Review"):
                graph.add_edge(fallback, "SME_Review")
                if DEBUG_MODE: print(f"  Added missing edge: {fallback} -> SME_Review")
            try:
                fallback_paths = list(nx.all_simple_paths(graph, source=fallback, target="Invalid_Mismatch", cutoff=2))
                final_paths.extend(fallback_paths) # Use final_paths here
                matched_concepts.append(fallback)
                if DEBUG_MODE: print(f"  Fallback path found for '{fallback}': {fallback_paths}")
            except nx.NetworkXNoPath:
                if DEBUG_MODE: print(f"  NetworkXNoPath exception for fallback concept: '{fallback}'")
                pass
        elif fallback and not graph.has_node(fallback):
            if DEBUG_MODE: print(f"  Fallback concept '{fallback}' not found as a node in the graph.")


    if DEBUG_MODE: print(f"\n--- Final paths found: {final_paths} ---")
    if DEBUG_MODE: print(f"--- Final matched concepts: {matched_concepts} ---")
    return final_paths, matched_concepts