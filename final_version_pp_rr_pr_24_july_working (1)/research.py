High-level flow (what happens on each claim)
	1.	Gate: claim is Paid→Paid and MATCH_OVERALL = 'No'.
	2.	Run TCC rules (ingredient/dispensing/tax/incentive).
	•	If any fire → Valid_Mismatch (done).
	3.	Patient Pay → Copay changed? (PRE_COPAY_AMOUNT != POST_COPAY_AMOUNT)
	4.	Map plan/section (from POST fields):
	•	Plan code → BASIC/ECONOMY/HDHP
	•	Section: Specialty vs VA (GOV90P/GOVCLP) vs Drug-specific (SX_MST-EES) vs Member
	•	Retail-90 rule: Retail + 90 → use Mail copay (if enabled)
	5.	LLM IDs → doc lookup (inside that section):
	•	Ask LLM to return IDs (not phrases) for the COPAY column and the correct row (Retail 90 / Mail / etc.).
	•	Dereference IDs → plan copay value + locator (page/anchor).
	6.	Compare & classify:
	•	If plan_copay == POST_COPAY → Valid_Mismatch (“system moved to plan”)
	•	If plan_copay != POST_COPAY → Plan_Value_Mismatch (flag with both numbers)
	•	If HDHP coinsurance row / not flat → SME_Review (coinsurance)
	•	If no row/value found → SME_Review (no matching plan row)
	7.	Explain (1–3 lines): what changed, which table you used, the value, the page anchor.






What the SME/explanation will look like
	•	Valid_Mismatch:
“As per ECONOMY PLAN › Member Cost Share (pg p4), Copay=$105.00. POST matches plan.”
	•	Plan_Value_Mismatch:
“As per ECONOMY PLAN › Member Cost Share (pg p4), Copay=$105.00, but POST shows $35.00.”
	•	SME_Review (coinsurance):
“Plan row has no flat copay (likely coinsurance); HDHP percentage applies.”


# cert_validation_pipeline.py
# End-to-end: mapping → LLM IDs → doc lookup → classification for Copay rule
# ------------------------------------------------------------------------------

import re
import json
import pickle
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable

# =========================
# 0) Core data structures
# =========================

@dataclass
class TableRow:
    label: str                 # e.g., "RETAIL 90", "MAIL", "GENERIC - TIER 1"
    day_supply: Optional[int]  # 30/90/None
    tier: Optional[int]        # 1/2/3/None
    values: Dict[str, Any]     # e.g. {"COPAY":"$105.00", "COINSURANCE":"N/A"}

@dataclass
class Table:
    plan_section: str                          # "BASIC PLAN" | "ECONOMY PLAN" | "HDHP PLAN"
    cost_share_section: str                    # "Member Cost Share" | "Specialty Member Cost Share" | ...
    columns: List[str]                         # headers: ["DELIVERY","DAY_SUPPLY","TIER","COPAY","COINSURANCE"]
    rows: List[TableRow]
    locator: str = "p?"                        # page/anchor for audit

# Minimal “doc graph” API the rest of the code expects
class SimpleDocGraph:
    def __init__(self, tables: List[Table]):
        self._tables = tables

    def tables(self) -> List[Table]:
        return self._tables

    def has_table(self, plan_section: str, cost_share_section: str) -> bool:
        ps, cs = plan_section.upper(), cost_share_section.upper()
        return any(t.plan_section.upper()==ps and t.cost_share_section.upper()==cs for t in self._tables)

    # Accepts a list of IDs (expects one COL + one ROW), and returns (value, locator)
    # ID format: "{PLAN}|{SECTION}|COL|{COL_KEY}" or "{PLAN}|{SECTION}|ROW|{ROW_KEY}"
    def lookup_by_ids(self, ids: List[str], tier: Optional[int], day_supply: Optional[int]):
        if not ids:
            return None, None

        def _parts(i: str):
            sp = i.split("|")
            if len(sp) < 4:
                return None
            return {"plan": sp[0], "section": sp[1], "kind": sp[2], "key": sp[3]}

        col_key = None
        row_key = None
        meta = None
        for i in ids:
            p = _parts(i)
            if not p:
                continue
            meta = p
            if p["kind"] == "COL":
                col_key = p["key"].upper()
            elif p["kind"] == "ROW":
                row_key = p["key"].upper()

        if not meta or not col_key or not row_key:
            return None, None

        plan, section = meta["plan"], meta["section"]
        for t in self._tables:
            if t.plan_section.upper()==plan.upper() and t.cost_share_section.upper()==section.upper():
                for r in t.rows:
                    lab = canonical_row_key(r.label)
                    if lab == row_key:
                        if tier is not None and r.tier not in (None, tier):
                            continue
                        if day_supply is not None and r.day_supply not in (None, day_supply):
                            continue
                        return r.values.get(col_key), t.locator
        return None, None


# ========================================
# 1) Load your GraphRAG doc graph (.pkl)
#    and adapt to SimpleDocGraph
# ========================================

class DocGraphAdapterFromPickle(SimpleDocGraph):
    """
    Adapter over your validation_graph_from_document.pkl that exposes SimpleDocGraph.
    TODO: Adjust _extract_tables() to your pickle's node/edge schema.
    """
    def __init__(self, pickle_path: str):
        nx_graph = self._load_graph(pickle_path)
        tables = self._extract_tables(nx_graph)
        super().__init__(tables)

    @staticmethod
    def _load_graph(path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    def _extract_tables(self, G) -> List[Table]:
        tables: List[Table] = []

        # ---- TODO: map your graph nodes/edges to Table/TableRow ----
        # Example structure (edit to match your pickle):
        # - table nodes: data = {"kind":"table","plan":"ECONOMY PLAN","section":"Member Cost Share",
        #                        "columns":["DELIVERY","DAY_SUPPLY","TIER","COPAY","COINSURANCE"],
        #                        "locator":"p4"}
        # - row nodes:   data = {"kind":"row","label":"RETAIL 90","day":90,"tier":2,
        #                        "values":{"COPAY":"$105.00","COINSURANCE":"N/A"}}
        for n, data in G.nodes(data=True):
            if str(data.get("kind")).lower() == "table":
                plan = data.get("plan") or data.get("plan_section")
                section = data.get("section") or data.get("cost_share_section")
                columns = data.get("columns") or []
                locator = data.get("locator") or data.get("page") or "p?"

                rows: List[TableRow] = []
                # If rows are neighbors; adjust if your edges differ
                for m in G.neighbors(n):
                    r = G.nodes[m]
                    if str(r.get("kind")).lower() == "row":
                        rows.append(TableRow(
                            label=r.get("label") or "",
                            day_supply=r.get("day") or r.get("day_supply"),
                            tier=r.get("tier"),
                            values=r.get("values") or {}
                        ))
                tables.append(Table(
                    plan_section=plan,
                    cost_share_section=section,
                    columns=columns,
                    rows=rows,
                    locator=locator
                ))
        # ------------------------------------------------------------
        return tables


# ==========================================
# 2) Candidate index (IDs for rows/columns)
# ==========================================

@dataclass
class Candidate:
    cand_id: str
    plan_section: str
    cost_share_section: str
    kind: str         # "COL" or "ROW"
    field_key: str    # e.g. COPAY / COINSURANCE / RETAIL_90 / MAIL / TIER_2
    text: str
    source_locator: str

def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def canonical_col_key(col: str) -> str:
    c = col.upper().strip().replace(" ", "_")
    return {"COPAYMENT":"COPAY","CO_PAY":"COPAY"}.get(c, c)

def canonical_row_key(label: str) -> str:
    lab = label.upper()
    lab = lab.replace("/", " ").replace("-", " ").replace("(", " ").replace(")", " ")
    lab = re.sub(r"\s+", " ", lab).strip()
    if "RETAIL" in lab and "90" in lab: return "RETAIL_90"
    if "RETAIL" in lab: return "RETAIL"
    if "MAIL" in lab: return "MAIL"
    if "SPECIALTY" in lab: return "SPECIALTY"
    m = re.search(r"TIER\s*(\d+)", lab)
    if m: return f"TIER_{m.group(1)}"
    return lab.replace(" ", "_")

def build_candidates_from_doc_graph(doc_graph: SimpleDocGraph) -> List[Candidate]:
    cands: List[Candidate] = []
    for t in doc_graph.tables():
        ps = normalize_space(t.plan_section)
        cs = normalize_space(t.cost_share_section)
        for col in t.columns:
            key = canonical_col_key(col)
            cid = f"{ps}|{cs}|COL|{key}"
            cands.append(Candidate(cid, ps, cs, "COL", key, col, t.locator))
        for r in t.rows:
            key = canonical_row_key(r.label)
            cid = f"{ps}|{cs}|ROW|{key}"
            cands.append(Candidate(cid, ps, cs, "ROW", key, r.label, t.locator))
    return cands

def filter_candidates(cands: List[Candidate], plan_section: str, cost_share_section: str) -> List[Candidate]:
    ps = normalize_space(plan_section).upper()
    cs = normalize_space(cost_share_section).upper()
    return [c for c in cands if c.plan_section.upper()==ps and c.cost_share_section.upper()==cs]


# ==========================================
# 3) LLM mapping (IDs only) + fallback
# ==========================================

def make_llm_prompt(field_name: str, narrowed: List[Candidate]) -> str:
    menu = "\n".join(f"[{c.cand_id}] {c.text}" for c in narrowed)
    return f"""
Return ONLY 2–4 candidate IDs (one per line) that are most relevant to the claim field.

Claim field: {field_name}

Candidates (format: [ID] surface text):
{menu}

Rules:
- Output only the IDs (text inside [ ... ]).
- No commentary. No extra text.
""".strip()

def parse_llm_ids(raw_text: str) -> List[str]:
    ids = []
    for line in raw_text.splitlines():
        m = re.search(r"\[(.+?)\]", line)
        if m:
            ids.append(m.group(1).strip())
    seen=set(); out=[]
    for i in ids:
        if i not in seen:
            out.append(i); seen.add(i)
    return out[:4]

def ids_exist(ids: List[str], narrowed: List[Candidate]) -> List[str]:
    ok = {c.cand_id for c in narrowed}
    return [i for i in ids if i in ok]

def keyword_backoff(field_name: str, narrowed: List[Candidate]) -> List[str]:
    n = field_name.upper()
    picks = []
    if "COPAY" in n:
        picks += [c.cand_id for c in narrowed if c.kind=="COL" and c.field_key=="COPAY"]
        # pair with likely rows
        rows = [c.cand_id for c in narrowed if c.kind=="ROW" and c.field_key in {"RETAIL_90","MAIL","RETAIL"}]
        picks += rows[:2]
    if not picks:
        col = next((c.cand_id for c in narrowed if c.kind=="COL" and c.field_key=="COPAY"), None)
        row = next((c.cand_id for c in narrowed if c.kind=="ROW"), None)
        if col and row: picks = [col, row]
    seen=set(); out=[]
    for p in picks:
        if p not in seen:
            out.append(p); seen.add(p)
    return out[:4]

def map_field_with_ids(field_name: str,
                       plan_section: str,
                       cost_share_section: str,
                       all_candidates: List[Candidate],
                       call_llm: Callable[[str], str]) -> Dict[str, Any]:
    narrowed = filter_candidates(all_candidates, plan_section, cost_share_section)
    if not narrowed:
        return {"field": field_name, "ids": [], "reason": "no candidates for section"}

    prompt = make_llm_prompt(field_name, narrowed)
    try:
        raw = call_llm(prompt)             # <-- plug your Vertex AI call here
        ids = parse_llm_ids(raw)
        ids = ids_exist(ids, narrowed)
        if ids:
            return {"field": field_name, "ids": ids, "reason": "llm"}
    except Exception:
        pass

    ids = keyword_backoff(field_name, narrowed)
    return {"field": field_name, "ids": ids, "reason": "fallback"}


# ==========================================
# 4) Plan/Section mapping (deterministic)
# ==========================================

@dataclass
class MappingConfig:
    plan_map: Dict[str, str]
    retail_90_uses_mail: bool
    section_priority: List[Dict[str, Any]]   # rules list

@dataclass
class MappingInput:
    post_xref_plan_code: str
    post_delivery_system: str
    post_tier_num: int
    post_days_supply: int
    post_drug_specific_copay: Optional[str] = None
    post_network: Optional[str] = None

@dataclass
class MappingResult:
    plan_section: str
    cost_share_section: str
    row_key: Dict[str, Any]
    notes: List[str]

def _norm_s(x): return (x or "").strip().upper()

def _norm_delivery(x):
    d = _norm_s(x)
    return {"RETAIL":"RETAIL","MAIL":"MAIL","SPECIALTY":"SPECIALTY","PAPER":"PAPER"}.get(d, d)

def resolve_costshare_section(delivery: str, network: str, drug_specific: str, cfg: MappingConfig) -> str:
    D, N, G = _norm_delivery(delivery), _norm_s(network), _norm_s(drug_specific)
    for rule in cfg.section_priority:
        cond = rule.get("if")
        if not cond and rule.get("else"): return rule["use_section"]
        ok = True
        if cond:
            if "delivery" in cond: ok = ok and (_norm_delivery(cond["delivery"]) == D)
            if "network_in" in cond: ok = ok and (N in [_norm_s(x) for x in cond["network_in"]])
            if "drug_specific" in cond: ok = ok and (_norm_s(cond["drug_specific"]) == G)
        if ok: return rule["use_section"]
    return "Member Cost Share"

def adjust_delivery(delivery: str, days: int, retail90_uses_mail: bool):
    D = _norm_delivery(delivery)
    notes=[]
    if D=="RETAIL" and int(days)==90 and retail90_uses_mail:
        notes.append("Applied Retail-90 → Mail copay rule")
        return "MAIL", notes
    return D, notes

def build_row_key(plan_section: str, section: str, tier: int, delivery: str, days: int) -> Dict[str, Any]:
    return {"plan_section": plan_section, "cost_share_section": section,
            "tier": int(tier), "delivery": _norm_delivery(delivery), "day_supply": int(days)}

def resolve_mapping(inp: MappingInput, cfg: MappingConfig, doc_graph: SimpleDocGraph) -> MappingResult:
    plan_section = cfg.plan_map.get(_norm_s(inp.post_xref_plan_code))
    if not plan_section:
        raise ValueError(f"Unknown plan code: {inp.post_xref_plan_code!r}")

    section = resolve_costshare_section(inp.post_delivery_system, inp.post_network, inp.post_drug_specific_copay, cfg)
    lookup_delivery, notes = adjust_delivery(inp.post_delivery_system, inp.post_days_supply, cfg.retail_90_uses_mail)
    row_key = build_row_key(plan_section, section, inp.post_tier_num, lookup_delivery, inp.post_days_supply)

    if not doc_graph.has_table(plan_section, section):
        notes.append(f"Table not found for ({plan_section}, {section}); SME review may be needed.")

    return MappingResult(plan_section, section, row_key, notes)


# ==========================================
# 5) Copay validator (uses everything)
# ==========================================

def money(x: Any) -> str:
    s = re.sub(r"[^\d.]", "", str(x or "0"))
    if s == "": s = "0"
    from decimal import Decimal
    return f"{Decimal(s):.2f}"

def validate_copay_row(post_row: Dict[str, Any],
                       cfg: MappingConfig,
                       doc_graph: SimpleDocGraph,
                       all_candidates: List[Candidate],
                       call_llm: Callable[[str], str]) -> Dict[str, Any]:
    # mapping
    inp = MappingInput(
        post_xref_plan_code=post_row["POST_XREF_PLAN_CODE"],
        post_delivery_system=post_row["POST_DELIVERY_SYSTEM"],
        post_tier_num=int(post_row["POST_TIER_NUM"]),
        post_days_supply=int(post_row["POST_DAYS_SUPPLY"]),
        post_drug_specific_copay=post_row.get("POST_DRUG_SPECIFIC_COPAY"),
        post_network=post_row.get("POST_NETWORK"),
    )
    mres = resolve_mapping(inp, cfg, doc_graph)
    plan_section, cost_share_section = mres.plan_section, mres.cost_share_section
    tier, days = inp.post_tier_num, inp.post_days_supply

    # LLM chooses IDs (inside chosen section)
    pick = map_field_with_ids(
        field_name="POST_COPAY_AMOUNT",
        plan_section=plan_section,
        cost_share_section=cost_share_section,
        all_candidates=all_candidates,
        call_llm=call_llm
    )

    # deref
    plan_value, locator = doc_graph.lookup_by_ids(pick["ids"], tier=tier, day_supply=days)

    # classify
    post_copay = str(post_row["POST_COPAY_AMOUNT"]).strip()
    if plan_value in (None, "", "N/A"):
        # Try coinsurance column as a hint (optional)
        return {
            "classification": "SME_Review",
            "trigger": "Copay Amount Validation from BPS Plan",
            "evidence": {"plan_value": plan_value, "locator": locator, "notes": mres.notes + [pick["reason"]]},
            "explanation": "No flat copay found for this row (possibly coinsurance/HDHP or missing row)."
        }

    if money(plan_value) == money(post_copay):
        return {
            "classification": "Valid_Mismatch",
            "trigger": "Copay Amount Validation from BPS Plan",
            "evidence": {"plan_value": plan_value, "locator": locator, "notes": mres.notes + [pick["reason"]]},
            "explanation": f"As per {plan_section} › {cost_share_section} ({locator}), Copay={plan_value}. POST matches plan."
        }
    else:
        return {
            "classification": "Plan_Value_Mismatch",
            "trigger": "Copay Amount Validation from BPS Plan",
            "evidence": {"plan_value": plan_value, "locator": locator, "notes": mres.notes + [pick["reason"]]},
            "explanation": f"As per {plan_section} › {cost_share_section} ({locator}), Copay={plan_value}, but POST shows {post_copay}."
        }


# ==========================================
# 6) Wire it together (example usage)
# ==========================================

def call_llm(prompt: str) -> str:
    """
    TODO: Replace with your Vertex AI Gemini call that returns TEXT ONLY.
    Keep temperature=0.
    For local testing, this deterministic stub picks COPAY col + RETAIL_90 row if present.
    """
    lines = []
    for ln in prompt.splitlines():
        if "|COL|COPAY]" in ln or "|ROW|RETAIL_90]" in ln or "|ROW|MAIL]" in ln:
            idtxt = ln.split("]")[0].split("[",1)[1]
            lines.append(f"[{idtxt}]")
    return "\n".join(lines) or prompt  # last resort just echo (so fallback kicks in)


def run_one_row_example():
    # 1) Load doc graph from your GraphRAG pickle
    doc_graph = DocGraphAdapterFromPickle("output/validation_graph_from_document.pkl")

    # 2) Build candidates once per run
    all_candidates = build_candidates_from_doc_graph(doc_graph)

    # 3) Mapping config (plan codes + section rules)
    cfg = MappingConfig(
        plan_map={"PCCBPPO":"BASIC PLAN","PCEPPPO":"ECONOMY PLAN","PCHDHP":"HDHP PLAN"},
        retail_90_uses_mail=True,
        section_priority=[
            {"if":{"delivery":"SPECIALTY"}, "use_section":"Specialty Member Cost Share"},
            {"if":{"network_in":["GOV90P","GOVCLP"]}, "use_section":"Stepped Member Cost Share for VA"},
            {"if":{"drug_specific":"SX_MST-EES"}, "use_section":"Specialty Member Cost Share"},
            {"else": True, "use_section":"Member Cost Share"},
        ],
    )

    # 4) A sample POST row (replace with your real data row)
    post_row = {
        "POST_XREF_PLAN_CODE":"PCEPPPO",
        "POST_DELIVERY_SYSTEM":"Retail",
        "POST_TIER_NUM":2,
        "POST_DAYS_SUPPLY":90,
        "POST_DRUG_SPECIFIC_COPAY":"NotSX_MST-EES",
        "POST_NETWORK":"STD",
        "POST_COPAY_AMOUNT":"$105.00",
    }

    result = validate_copay_row(post_row, cfg, doc_graph, all_candidates, call_llm)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run_one_row_example()







import networkx as nx
import os
import pickle
import re
from typing import List, Dict, Any

class RulebookGraphBuilderAgent:
    def __init__(self, rulebook_markdown_path: str, output_graph_path: str):
        self.rulebook_markdown_path = rulebook_markdown_path
        self.output_graph_path = output_graph_path
        os.makedirs(os.path.dirname(self.output_graph_path), exist_ok=True)

    def _parse_rulebook_markdown(self, markdown_content: str) -> List[Dict[str, str]]:
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

            if line.startswith('## '):
                current_section = line[3:].strip()
                continue
            elif line.startswith('### '):
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

    def _generate_graph_from_parsed_rules(self, rules: List[Dict[str, Any]]) -> nx.DiGraph:
        """
        Builds a NetworkX directed graph from the structured rule data, including hierarchical relationships.
        """
        G = nx.DiGraph()

        # First pass: Add all nodes with their attributes
        for rule in rules:
            node_name = rule.get("Rule Name").strip()
            if not node_name:
                continue
            G.add_node(node_name, **{k: v for k, v in rule.items() if k != "Rule Name"})
       
        # Add all unique parent nodes to ensure they exist
        all_parents = {rule.get("Parent_Node", "").strip() for rule in rules if "Parent_Node" in rule}
        for parent in all_parents:
            if parent and not G.has_node(parent):
                G.add_node(parent, Node_Type='Parent_Placeholder')
       
        # Second pass: Add edges based on Edge_Target, Parent_Node, and Precondition
        for rule in rules:
            node_name = rule.get("Rule Name").strip()
            parent_node = rule.get("Parent_Node", "").strip()
            edge_target = rule.get("Edge_Target", "").strip()
            edge_type = rule.get("Edge_Type", "Causes").strip()
            precondition = rule.get("Precondition", "").strip()

            if not node_name:
                continue

            # Case 1: Rule has a parent, link it
            if parent_node and not G.has_edge(parent_node, node_name):
                # Use a specific edge attribute for parent-child to signify structure
                G.add_edge(parent_node, node_name, Edge_Type='Child_Of')
                print(f" Added hierarchical edge: {parent_node} → {node_name} (Child_Of)")

            # Case 2: Rule has an edge target, link it
            if edge_target and not G.has_edge(node_name, edge_target):
                G.add_edge(node_name, edge_target, Edge_Type=edge_type)
                print(f"Added logical edge: {node_name} → {edge_target} ({edge_type})")

            # Case 3: Handle specific preconditions as intermediate nodes
            if precondition and not G.has_edge(precondition, node_name):
                 # Add an edge from precondition to the rule node
                if G.has_node(precondition):
                    G.add_edge(precondition, node_name, Edge_Type='Precondition_For')
                    print(f" Added precondition edge: {precondition} → {node_name} (Precondition_For)")
                else:
                    G.add_node(precondition, Node_Type='Precondition_Placeholder')
                    G.add_edge(precondition, node_name, Edge_Type='Precondition_For')
                    print(f"Added precondition edge: {precondition} → {node_name} (Precondition_For)")
       
        # Add a special node to explicitly mark the "Paid→Reject" path start
        if not G.has_node("Paid→Reject"):
            G.add_node("Paid→Reject", Node_Type="Claim_Status_Change")
        if not G.has_edge("Paid→Reject", "Valid Transition Status"):
            G.add_edge("Paid→Reject", "Valid Transition Status", Edge_Type="Causes")

        # Ensure all common outcome and intermediate nodes exist for a clean graph
        for outcome_node in ['Valid_Mismatch', 'Invalid_Mismatch', 'SME_Review', 'Excluded', 'Skipped',
                             'Deeper_Field_Differences', 'Reject_Code_Comparison', 'PA_Local_Message_Check',
                             'PA_Reason_Layer_Comparison', 'Valid Transition Status', 'Reject_Code_Check',
                             'Reject Code Is 75', 'Reject Code Is Not 75', 'Local Message Indicates PA',
                             'PA Reason or Layer Changed', 'PA Reason and Layer Same', 'Missing or Unexpected Data',
                             'Matching Local Messages (Same Reject)', 'Different Local Messages (Same Reject)',
                             'Matching Local Messages (Cross Reject)', 'Different Local Messages (Cross Reject)']:
            if not G.has_node(outcome_node):
                G.add_node(outcome_node, Node_Type='Outcome_Placeholder')
       
        return G

    def build_graph(self) -> nx.DiGraph:
        """
        Orchestrates the building of the Rulebook graph.
        """
        print(f"Building Rulebook Graph from {self.rulebook_markdown_path}...")
        try:
            with open(self.rulebook_markdown_path, 'r') as f:
                rulebook_md = f.read()
           
            parsed_rules = self._parse_rulebook_markdown(rulebook_md)
            print(f"Parsed {len(parsed_rules)} rules from Markdown.")
           
            graph = self._generate_graph_from_parsed_rules(parsed_rules)
           
            with open(self.output_graph_path, "wb") as f:
                pickle.dump(graph, f)
            print(f"Rulebook Graph saved to {self.output_graph_path}")
            return graph
        except FileNotFoundError:
            print(f"Error: Rulebook Markdown file not found at {self.rulebook_markdown_path}")
            return None
        except Exception as e:
            print(f"Error building Rulebook Graph: {e}")
            return None






