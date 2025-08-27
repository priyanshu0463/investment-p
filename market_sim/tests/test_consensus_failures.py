from market_sim.consensus.sim_driver import run_simple_simulation


def test_leader_failure_skips_epoch_but_progress_continues():
    logs_without_failure = run_simple_simulation(num_nodes=4, epochs=8, fail_epoch=None)
    logs_with_failure = run_simple_simulation(num_nodes=4, epochs=8, fail_epoch=5)

    # All nodes must agree in each run
    assert all(logs_without_failure[0] == l for l in logs_without_failure)
    assert all(logs_with_failure[0] == l for l in logs_with_failure)

    # With a failed leader in epoch 5, finalized tx count should be less or equal
    assert len(logs_with_failure[0]) <= len(logs_without_failure[0])


