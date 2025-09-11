# export_graph_tables.py
import os
import pickle
import pandas as pd
import networkx as nx

PICKLE_PATH = "output/graph_from_document.pkl"   # <-- change if needed
OUT_XLSX = os.path.join(os.path.dirname(PICKLE_PATH) or ".", "graph_tables.xlsx")

def main():
    if not os.path.exists(PICKLE_PATH):
        raise FileNotFoundError(f"Graph pickle not found: {PICKLE_PATH}")

    with open(PICKLE_PATH, "rb") as f:
        G: nx.DiGraph = pickle.load(f)

    # Build DataFrames
    nodes_df = pd.DataFrame([{"Node_ID": n, **attrs} for n, attrs in G.nodes(data=True)])
    edges_df = pd.DataFrame([{"Source": u, "Target": v, **attrs} for u, v, attrs in G.edges(data=True)])

    # One Excel file, multiple sheets
    with pd.ExcelWriter(OUT_XLSX, engine="xlsxwriter") as writer:
        nodes_df.to_excel(writer, sheet_name="Nodes", index=False)
        edges_df.to_excel(writer, sheet_name="Edges", index=False)

        # (Optional) quick summary sheet
        summary = pd.DataFrame({
            "Metric": ["#Nodes", "#Edges"],
            "Value": [len(nodes_df), len(edges_df)]
        })
        summary.to_excel(writer, sheet_name="Summary", index=False)

        # (Nice-to-have) autosize columns
        for sheet, df in {"Nodes": nodes_df, "Edges": edges_df, "Summary": summary}.items():
            w = writer.book.worksheets()[-1] if sheet == "Summary" else writer.sheets[sheet]
            for i, col in enumerate(df.columns):
                width = min(60, max(df[col].astype(str).map(len).max(), len(col)) + 2)
                w.set_column(i, i, width)

    print(f"✅ Wrote tables to: {OUT_XLSX}")

if __name__ == "__main__":
    main()