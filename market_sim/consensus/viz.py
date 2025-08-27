from typing import Dict, List

try:
    from graphviz import Digraph
except Exception:  # pragma: no cover - optional dependency at runtime
    Digraph = None  # type: ignore


def render_notarized_chains(chains: List[List[str]], label_by_hash: Dict[str, str], outfile: str = "chains") -> None:
    if Digraph is None:
        return
    dot = Digraph(comment="Streamlet Notarized Chains")
    seen = set()
    for chain in chains:
        for i, h in enumerate(chain):
            if h not in seen:
                dot.node(h, label_by_hash.get(h, h[:6]))
                seen.add(h)
            if i > 0:
                dot.edge(chain[i - 1], h)
    try:
        dot.render(outfile, format="png", cleanup=True)
    except Exception:
        # Gracefully skip if Graphviz system binaries are unavailable
        pass


