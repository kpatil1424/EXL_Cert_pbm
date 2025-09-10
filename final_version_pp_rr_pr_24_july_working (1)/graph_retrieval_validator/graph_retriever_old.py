# import pickle
# import networkx as nx
# from typing import Dict, List, Tuple

# def load_graph(path="output/New_validation_graph.pkl"):
#     """
#     Load the saved causal rule graph from disk.
#     """
#     with open(path, "rb") as f:
#         return pickle.load(f)

# def normalize(val):
#     if val is None:
#         return ""
#     return str(val).strip().lower()



# def retrieve_paths_from_graph(claim: Dict, graph: nx.DiGraph, claim_type: str = "Paid→Paid") -> Tuple[List[List[str]], List[str]]:
#     matched_concepts = []
#     paths = []

#     def diff(pre_field, post_field):
#         return normalize(claim.get(pre_field)) != normalize(claim.get(post_field))

#     def contains_prior_auth_trigger(message: str) -> bool:
#         if not message:
#             return False
#         pa_keywords = [
#             "prior authorization", "prior auth", "prior auth req",
#             "requires prior authorization", "prior auth required", "pa required"
#         ]
#         return any(keyword.lower() in message.lower() for keyword in pa_keywords)

#     if claim_type == "Paid→Paid":
#         field_pairs = [
#             ("PRE_INGREDIENT_COST_CLIENT", "POST_INGREDIENT_COST_CLIENT", "Ingredient Cost Change"),
#             ("PRE_DISPENSING_FEE", "POST_DISPENSING_FEE", "Dispensing Fee Change"),
#             ("PRE_AMOUNT_ATTR_TO_SALES_TAX", "POST_AMOUNT_ATTR_TO_SALES_TAX", "Flat Sales Tax Change"),
#             ("PRE_SALEX_TAX_PERC_PAID", "POST_SALEX_TAX_PERC_PAID", "Percentage Sales Tax Change"),
#             ("PRE_INCENTIVE_FEE", "POST_INCENTIVE_FEE", "Incentive Fee Change"),
#             ("PRE_COPAY_AMOUNT", "POST_COPAY_AMOUNT", "Copay Amount Change"),
#             ("PRE_APPR_AMT_APPL_PER_DED", "POST_APPR_AMT_APPL_PER_DED", "Deductible Applied Amount Change"),
#             ("PRE_PROD_SELECTION_PENALTY", "POST_PROD_SELECTION_PENALTY", "Brand DAW Penalty Change"),
#             ("PRE_DRUG_SPECIFIC_COPAY", "POST_DRUG_SPECIFIC_COPAY", "Drug Specific Copay Change"),
#             ("PRE_CLIENT_PATIENT_SCHEDULE", "POST_CLIENT_PATIENT_SCHEDULE", "Client Patient Schedule Change"),
#             ("PRE_XREF_PLAN_CODE", "POST_XREF_PLAN_CODE", "Plan Code Change"),
#         ]

#     elif claim_type == "Reject→Reject":
#         field_pairs = [
#             ("PRE_REJECT_CODE_1", "POST_REJECT_CODE_1", "In-Scope Reject Code Pairs"),
#             ("PRE_LOCAL_MESSAGE", "POST_LOCAL_MESSAGE", "Different Local Messages")
#         ]

#         if diff("PRE_REJECT_CODE_1", "POST_REJECT_CODE_1") and diff("PRE_LOCAL_MESSAGE", "POST_LOCAL_MESSAGE"):
#             deeper_fields = [
#                 ("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS", "PA Layer Changed"),
#                 ("PRE_DRUGLIST_DETAIL", "POST_DRUGLIST_DETAIL", "Drug List Changed"),
#                 ("PRE_SMART_PA_OVERALL", "POST_SMART_PA_OVERALL", "Smart PA Overall Changed"),
#                 ("PRE_DAYS_SUPPLY", "POST_DAYS_SUPPLY", "Days Supply Changed"),
#                 ("PRE_FINAL_PLAN_CODE", "POST_FINAL_PLAN_CODE", "Final Plan Code Changed"),
#                 ("PRE_NETWORK", "POST_NETWORK", "Network Changed"),
#             ]
#             field_pairs.extend(deeper_fields)

#     elif claim_type == "Paid→Reject":
#         post_reject_code_raw = claim.get("POST_REJECT_CODE_1", "")
#         post_reject_code = normalize(str(int(float(post_reject_code_raw)))) if post_reject_code_raw else ""
#         post_local_message = normalize(claim.get("POST_LOCAL_MESSAGE"))

#         if post_reject_code == "75":
#             matched_concepts.append("Reject Code Is 75")
#             if contains_prior_auth_trigger(post_local_message):
#                 matched_concepts.append("Local Message Indicates PA")
#                 if diff("PRE_PA_REASON_CODE", "POST_PA_REASON_CODE") or diff("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS"):
#                     matched_concepts.append("PA Reason or Layer Changed")
#                 else:
#                     matched_concepts.append("PA Reason and Layer Same")
#             else:
#                 matched_concepts.append("Local Message Lacks PA Trigger")
#         else:
#             matched_concepts.append("Reject Code Is Not 75")
#     else:
#         return [], ["Unsupported claim type"]

#     # Match field diffs for Paid→Paid / Reject→Reject
#     if claim_type in ["Paid→Paid", "Reject→Reject"]:
#         for pre, post, concept in field_pairs:
#             if diff(pre, post):
#                 matched_concepts.append(concept)

#     # Traverse graph from each matched concept
#     for concept in matched_concepts:
#         if graph.has_node(concept):
#             try:
#                 concept_paths = list(nx.all_simple_paths(graph, source=concept, target="Valid_Mismatch", cutoff=3))
#                 paths.extend(concept_paths)
#             except nx.NetworkXNoPath:
#                 continue

#     # Fallback logic
#     if not paths:
#         if claim_type == "Paid→Paid":
#             fallback = "No Identified Differences"
#         elif claim_type == "Reject→Reject":
#             fallback = "No Deeper Differences"
#         elif claim_type == "Paid→Reject":
#             fallback = "Missing or Unexpected Data"
#         else:
#             fallback = None

#         if fallback and graph.has_node(fallback):
#             if not graph.has_edge(fallback, "SME_Review"):
#                 graph.add_edge(fallback, "SME_Review")
#             try:
#                 fallback_paths = list(nx.all_simple_paths(graph, source=fallback, target="Invalid_Mismatch", cutoff=2))
#                 paths.extend(fallback_paths)
#                 matched_concepts.append(fallback)
#             except nx.NetworkXNoPath:
#                 pass

#     return paths, matched_concepts  


# File: graph_retriever.py

import pickle
import networkx as nx
import json
from typing import Dict, List, Tuple

# === Load Plan Document Graph + Auto Field Mapping ===
try:
    with open("graph_retrieval_validator/output/validation_graph_from_document.pkl", "rb") as f:
        plan_graph = pickle.load(f)
    with open("graph_retrieval_validator/auto_field_mapping_enchanced.json", "r") as f:
        auto_field_map = json.load(f)
except:
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
        print(f" Plan graph or mapping missing for {field_name}")
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
                print(f"Mapped {field_name} → {node_id} (matched with '{phrase}')")
                related_nodes.add(node_id)
    if not related_nodes:
        print(f" No matches found for: {field_name} → {mapped_terms}")
        
    return sorted(list(related_nodes))

# Kunal's logic
# === Causal Reasoning via Rulebook Graph ===
# def retrieve_paths_from_graph(claim: Dict, graph: nx.DiGraph, claim_type: str = "Paid→Paid") -> Tuple[List[List[str]], List[str]]:
#     matched_concepts = []
#     paths = []

#     def diff(pre_field, post_field):
#         return normalize(claim.get(pre_field)) != normalize(claim.get(post_field))
#     # def diff(pre_field, post_field):
#     #     pre = normalize(claim.get(pre_field, ""))
#     #     post = normalize(claim.get(post_field, ""))
#     #     return pre != post and pre != "" and post != ""

#     def contains_prior_auth_trigger(message: str) -> bool:
#         if not message:
#             return False
#         pa_keywords = [
#             "prior authorization", "prior auth", "prior auth req",
#             "requires prior authorization", "prior auth required", "pa required"
#         ]
#         return any(keyword.lower() in message.lower() for keyword in pa_keywords)

#     # === Paid→Paid Field Pairs ===
#     if claim_type == "Paid→Paid":
#         field_pairs = [
#             ("PRE_INGREDIENT_COST_CLIENT", "POST_INGREDIENT_COST_CLIENT", "Ingredient Cost Change"),
#             ("PRE_DISPENSING_FEE", "POST_DISPENSING_FEE", "Dispensing Fee Change"),
#             ("PRE_AMOUNT_ATTR_TO_SALES_TAX", "POST_AMOUNT_ATTR_TO_SALES_TAX", "Flat Sales Tax Change"),
#             ("PRE_SALEX_TAX_PERC_PAID", "POST_SALEX_TAX_PERC_PAID", "Percentage Sales Tax Change"),
#             ("PRE_INCENTIVE_FEE", "POST_INCENTIVE_FEE", "Incentive Fee Change"),
#             ("PRE_COPAY_AMOUNT", "POST_COPAY_AMOUNT", "Copay Amount Change"),
#             ("PRE_APPR_AMT_APPL_PER_DED", "POST_APPR_AMT_APPL_PER_DED", "Deductible Applied Amount Change"),
#             ("PRE_PROD_SELECTION_PENALTY", "POST_PROD_SELECTION_PENALTY", "Brand DAW Penalty Change"),
#             ("PRE_DRUG_SPECIFIC_COPAY", "POST_DRUG_SPECIFIC_COPAY", "Drug Specific Copay Change"),
#             ("PRE_CLIENT_PATIENT_SCHEDULE", "POST_CLIENT_PATIENT_SCHEDULE", "Client Patient Schedule Change"),
#             ("PRE_XREF_PLAN_CODE", "POST_XREF_PLAN_CODE", "Plan Code Change"),
#         ]

#     # === Reject→Reject Field Pairs ===
#     elif claim_type == "Reject→Reject":
#         field_pairs = [
#             ("PRE_REJECT_CODE_1", "POST_REJECT_CODE_1", "In-Scope Reject Code Pairs"),
#             ("PRE_LOCAL_MESSAGE", "POST_LOCAL_MESSAGE", "Different Local Messages")
#         ]

           
#         if diff("PRE_REJECT_CODE_1", "POST_REJECT_CODE_1") and diff("PRE_LOCAL_MESSAGE", "POST_LOCAL_MESSAGE"):
#             deeper_fields = [
#                 ("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS", "PA Layer Changed"),
#                 ("PRE_DRUGLIST_DETAIL", "POST_DRUGLIST_DETAIL", "Drug List Changed"),
#                 ("PRE_SMART_PA_OVERALL", "POST_SMART_PA_OVERALL", "Smart PA Overall Changed"),
#                 ("PRE_DAYS_SUPPLY", "POST_DAYS_SUPPLY", "Days Supply Changed"),
#                 ("PRE_FINAL_PLAN_CODE", "POST_FINAL_PLAN_CODE", "Final Plan Code Changed"),
#                 ("PRE_NETWORK", "POST_NETWORK", "Network Changed"),
#             ]
#             field_pairs.extend(deeper_fields)

#     # === Paid→Reject logic ===
#     elif claim_type == "Paid→Reject":
#         post_reject_code_raw = claim.get("POST_REJECT_CODE_1", "")
#         post_reject_code = normalize(str(int(float(post_reject_code_raw)))) if post_reject_code_raw else ""
#         post_local_message = normalize(claim.get("POST_LOCAL_MESSAGE"))

#         if post_reject_code == "75":
#             matched_concepts.append("Reject Code Is 75")
#             if contains_prior_auth_trigger(post_local_message):
#                 matched_concepts.append("Local Message Indicates PA")
#                 if diff("PRE_PA_REASON_CODE", "POST_PA_REASON_CODE") or diff("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS"):
#                     matched_concepts.append("PA Reason or Layer Changed")
#                 else:
#                     matched_concepts.append("PA Reason and Layer Same")
#             else:
#                 matched_concepts.append("Local Message Lacks PA Trigger")
#         else:
#             matched_concepts.append("Reject Code Is Not 75")
#         field_pairs = []
#     else:
#         return [], ["Unsupported claim type"]

#     # === Apply field-pair-based matching for Paid→Paid and Reject→Reject
#     if claim_type in ["Paid→Paid", "Reject→Reject"]:
#         for pre, post, concept in field_pairs:
#             if diff(pre, post):
#                 matched_concepts.append(concept)

#     # === Traverse causal paths in Rulebook Graph ===
#     for concept in matched_concepts:
#         if graph.has_node(concept):
#             try:
#                 concept_paths = list(nx.all_simple_paths(graph, source=concept, target="Valid_Mismatch", cutoff=3))
#                 paths.extend(concept_paths)
#             except nx.NetworkXNoPath:
#                 continue

#     # === Fallback Path if No Match ===
#     if not paths:
#         fallback = None
#         if claim_type == "Paid→Paid":
#             fallback = "No Identified Differences"
#         elif claim_type == "Reject→Reject":
#             fallback = "No Deeper Differences"
#         elif claim_type == "Paid→Reject":
#             fallback = "Missing or Unexpected Data"

#         if fallback and graph.has_node(fallback):
#             if not graph.has_edge(fallback, "SME_Review"):
#                 graph.add_edge(fallback, "SME_Review")
#             try:
#                 fallback_paths = list(nx.all_simple_paths(graph, source=fallback, target="Invalid_Mismatch", cutoff=2))
#                 paths.extend(fallback_paths)
#                 matched_concepts.append(fallback)
#             except nx.NetworkXNoPath:
#                 pass

#     return paths, matched_concepts



#Rishabh's Logic
def retrieve_paths_from_graph(claim: Dict, graph: nx.DiGraph, claim_type: str = "Paid→Paid") -> Tuple[List[List[str]], List[str]]:
    matched_concepts = []
    paths = []

    # Re-enabled more robust diff function
    def diff(pre_field, post_field):
        pre = normalize(claim.get(pre_field, ""))
        post = normalize(claim.get(post_field, ""))
        # Check for difference and ensure at least one of them is not empty if a diff is to be considered
        # This handles cases where '' vs None might be seen as diff if not normalized, or where empty to empty is not a diff
        return pre != post and (pre != "" or post != "")

    def contains_prior_auth_trigger(message: str) -> bool:
        if not message:
            return False
        pa_keywords = [
            "prior authorization", "prior auth", "prior auth req",
            "requires prior authorization", "prior auth required", "pa required"
        ]
        return any(keyword.lower() in message.lower() for keyword in pa_keywords)

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
        # Apply field-pair-based matching for Paid→Paid
        for pre, post, concept in field_pairs:
            if diff(pre, post):
                matched_concepts.append(concept)

    # === Reject→Reject Logic (Revised to match Markdown structure) ===
    elif claim_type == "Reject→Reject":
        pre_reject_code = normalize(str(int(float(claim.get("PRE_REJECT_CODE_1", 0.0))))) if claim.get("PRE_REJECT_CODE_1") else ""
        post_reject_code = normalize(str(int(float(claim.get("POST_REJECT_CODE_1", 0.0))))) if claim.get("POST_REJECT_CODE_1") else ""
        pre_local_message = normalize(claim.get("PRE_LOCAL_MESSAGE", ""))
        post_local_message = normalize(claim.get("POST_LOCAL_MESSAGE", ""))

        # 1. Scope of Validation: In-Scope Reject Code Pairs
        # Cause: PRE_REJECT_CODE_1 and POST_REJECT_CODE_1 are one of the following pairs: (76, 76), (75, 76), (76, 75)
        in_scope_pairs = [("76", "76"), ("75", "76"), ("76", "75")]
        is_in_scope = False
        if (pre_reject_code, post_reject_code) in in_scope_pairs:
            matched_concepts.append("In-Scope Reject Code Pairs")
            is_in_scope = True
        else:
            # Rule: Out-of-Scope Reject Code Pairs
            # Cause: PRE_REJECT_CODE_1 and POST_REJECT_CODE_1 are not among valid pairs
            matched_concepts.append("Out-of-Scope Reject Code Pairs") # This will lead to Invalid_Mismatch via the graph

        if is_in_scope:
            # 2. Same Reject Code Case
            if pre_reject_code == post_reject_code and pre_reject_code == "76": # Check for specific code 76 as per rulebook example
                if pre_local_message == post_local_message:
                    # Rule: Matching Local Messages (Same Reject Code Case)
                    matched_concepts.append("Matching Local Messages")
                elif pre_local_message != post_local_message:
                    # Rule: Different Local Messages (Same Reject Code Case)
                    matched_concepts.append("Different Local Messages")

            # 3. Cross Reject Code Cases
            elif pre_reject_code != post_reject_code:
                if pre_local_message == post_local_message:
                    # Rule: Matching Local Messages (Cross Reject Code Cases)
                    matched_concepts.append("Matching Local Messages")
                elif pre_local_message != post_local_message:
                    # Rule: Different Local Messages (Cross Reject Code Cases)
                    # This rule proceeds to Deeper_Field_Differences
                    matched_concepts.append("Different Local Messages")

                    # Now, if this rule is matched, we check for deeper field differences
                    deeper_fields_detected = False
                    deeper_field_pairs = [
                        ("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS", "PA Layer Changed"),
                        ("PRE_DRUGLIST_DETAIL", "POST_DRUGLIST_DETAIL", "Drug List Changed"),
                        ("PRE_SMART_PA_OVERALL", "POST_SMART_PA_OVERALL", "Smart PA Overall Changed"),
                        ("PRE_DAYS_SUPPLY", "POST_DAYS_SUPPLY", "Days Supply Changed"),
                        ("PRE_FINAL_PLAN_CODE", "POST_FINAL_PLAN_CODE", "Final Plan Code Changed"),
                        ("PRE_NETWORK", "POST_NETWORK", "Network Changed"),
                    ]
                    for pre_f, post_f, concept in deeper_field_pairs:
                        if diff(pre_f, post_f):
                            matched_concepts.append(concept)
                            deeper_fields_detected = True
                    
                    if not deeper_fields_detected:
                        # Rule: No Deeper Differences (Fallback for Cross Reject Code Cases)
                        # This should lead to Invalid Mismatch via SME_Review
                        matched_concepts.append("No Deeper Differences")

    # === Paid→Reject logic (No changes needed, already explicit) ===
    elif claim_type == "Paid→Reject":
        post_reject_code_raw = claim.get("POST_REJECT_CODE_1", "")
        post_reject_code = normalize(str(int(float(post_reject_code_raw)))) if post_reject_code_raw else ""
        post_local_message = normalize(claim.get("POST_LOCAL_MESSAGE"))

        if post_reject_code == "75":
            matched_concepts.append("Reject Code Is 75")
            if contains_prior_auth_trigger(post_local_message):
                matched_concepts.append("Local Message Indicates PA")
                if diff("PRE_PA_REASON_CODE", "POST_PA_REASON_CODE") or diff("PRE_PA_LAYER_DETAILS", "POST_PA_LAYER_DETAILS"):
                    matched_concepts.append("PA Reason or Layer Changed")
                else:
                    matched_concepts.append("PA Reason and Layer Same")
            else:
                matched_concepts.append("Local Message Lacks PA Trigger")
        else:
            matched_concepts.append("Reject Code Is Not 75")
        field_pairs = [] # Ensure field_pairs is empty as logic is handled above
    else:
        return [], ["Unsupported claim type"]

    # === Traverse causal paths in Rulebook Graph ===
    # This loop remains the same, as matched_concepts are now more accurately identified
    for concept in matched_concepts:
        if graph.has_node(concept):
            try:
                # Cutoff might need adjustment based on max path length from new explicit rules
                concept_paths = list(nx.all_simple_paths(graph, source=concept, target="Valid_Mismatch", cutoff=4)) # Increased cutoff slightly
                paths.extend(concept_paths)
            except nx.NetworkXNoPath:
                continue

    # === Fallback Path if No Match (Only for Paid->Paid, Paid->Reject if not handled by explicit rules) ===
    # The Reject->Reject fallback ("No Deeper Differences") is now handled within the explicit logic above.
    if not paths:
        fallback = None
        if claim_type == "Paid→Paid":
            fallback = "No Identified Differences"
        elif claim_type == "Paid→Reject":
            # This fallback is for Paid->Reject if no specific 75 code path was found
            fallback = "Missing or Unexpected Data"

        if fallback and graph.has_node(fallback):
            if not graph.has_edge(fallback, "SME_Review"):
                graph.add_edge(fallback, "SME_Review")
            try:
                fallback_paths = list(nx.all_simple_paths(graph, source=fallback, target="Invalid_Mismatch", cutoff=2))
                paths.extend(fallback_paths)
                matched_concepts.append(fallback)
            except nx.NetworkXNoPath:
                pass

    return paths, matched_concepts


