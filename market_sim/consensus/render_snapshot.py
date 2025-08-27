from market_sim.consensus.sim_driver import run_for_snapshot
from market_sim.consensus.viz import render_notarized_chains


def main() -> None:
    # Happy path snapshot
    chains, labels = run_for_snapshot(num_nodes=4, epochs=8)
    render_notarized_chains(chains, labels, outfile="streamlet_snapshot")
    print("Rendered snapshot to streamlet_snapshot.png (if Graphviz is installed)")

    # Leader failure at epoch 5 snapshot
    chains2, labels2 = run_for_snapshot(num_nodes=4, epochs=8, fail_epoch=5)
    render_notarized_chains(chains2, labels2, outfile="streamlet_snapshot_fail5")
    print("Rendered snapshot to streamlet_snapshot_fail5.png (if Graphviz is installed)")


if __name__ == "__main__":
    main()


