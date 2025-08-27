from typing import Dict, List, Tuple

from .broker import MessageBroker
from .keys import PublicKeyRegistry
from .node import ConsensusNode


def run_simple_simulation(num_nodes: int = 4, epochs: int = 10, fail_epoch: int | None = None) -> List[List]:
    broker = MessageBroker()
    registry: PublicKeyRegistry = {}
    nodes: Dict[str, ConsensusNode] = {}

    for i in range(num_nodes):
        node_id = str(i)
        nodes[node_id] = ConsensusNode(node_id=node_id, broker=broker, public_keys=registry, total_nodes=num_nodes)

    # Seed some mempool transactions
    for e in range(1, epochs + 1):
        for i in range(num_nodes):
            nodes[str(i)].mempool.append({"epoch": e, "from": str(i), "val": e * 10 + i})
        # leader proposes
        leader = nodes[str(int(__import__("hashlib").sha256(str(e).encode()).hexdigest(), 16) % num_nodes)]
        if fail_epoch is None or e != fail_epoch:
            leader.propose(e)
        # deliver messages for this epoch
        broker.deliver_all()

    # Drain any remaining network messages
    broker.deliver_all()

    return [nodes[str(i)].finalized_log for i in range(num_nodes)]


def run_for_snapshot(num_nodes: int = 4, epochs: int = 10, fail_epoch: int | None = None) -> Tuple[List[List[str]], Dict[str, str]]:
    broker = MessageBroker()
    registry: PublicKeyRegistry = {}
    nodes: Dict[str, ConsensusNode] = {}

    for i in range(num_nodes):
        node_id = str(i)
        nodes[node_id] = ConsensusNode(node_id=node_id, broker=broker, public_keys=registry, total_nodes=num_nodes)

    for e in range(1, epochs + 1):
        for i in range(num_nodes):
            nodes[str(i)].mempool.append({"epoch": e, "from": str(i), "val": e * 10 + i})
        leader = nodes[str(int(__import__("hashlib").sha256(str(e).encode()).hexdigest(), 16) % num_nodes)]
        if fail_epoch is None or e != fail_epoch:
            leader.propose(e)
        broker.deliver_all()

    broker.deliver_all()

    # Use node 0's view for visualization
    node0 = nodes["0"]
    chains = node0.chains
    labels: Dict[str, str] = {}
    for chain in chains:
        for h in chain:
            b = node0.blocks_by_hash.get(h)
            if b:
                labels[h] = f"E:{b.epoch},L:{b.proposer_id}"
            else:
                labels[h] = h[:6]
    return chains, labels


if __name__ == "__main__":
    logs = run_simple_simulation()
    for i, log in enumerate(logs):
        print(f"Node {i} finalized {len(log)} txs")


