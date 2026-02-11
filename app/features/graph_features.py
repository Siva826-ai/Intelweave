import pandas as pd
import networkx as nx

def build_contact_graph(df: pd.DataFrame) -> nx.Graph:
    g = nx.Graph()
    for _, r in df.iterrows():
        a, b = str(r.get("a_party")), str(r.get("b_party"))
        if a == "nan" or b == "nan":
            continue
        if g.has_edge(a, b):
            g[a][b]["count"] += 1
        else:
            g.add_edge(a, b, count=1)
    return g

def graph_features(g: nx.Graph, nodes: list[str]) -> pd.DataFrame:
    deg = dict(g.degree())
    bt = nx.betweenness_centrality(g) if g.number_of_nodes() < 5000 else {n: 0.0 for n in g.nodes()}
    out = []
    for n in nodes:
        out.append({
            "node": n,
            "degree": float(deg.get(n, 0)),
            "betweenness": float(bt.get(n, 0.0)),
        })
    return pd.DataFrame(out)
