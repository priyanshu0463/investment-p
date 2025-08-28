## Streamlet Consensus Integration for investment-p

### Why consensus for a market simulation
- **Problem**: Multiple agents (traders, market makers, exchange) must share a single, consistent event history. Without it, state diverges (order book, trades, balances).
- **Solution**: Use State Machine Replication with a blockchain-style, linearly ordered log of transactions. Consensus deterministically orders agent actions into blocks that everyone processes.

### Protocol selection summary
- **Considered**: Dolev-Strong via sequential BB (correct but impractical), Nakamoto PoW (permissionless, probabilistic finality, unnecessary cost), and **Streamlet**.
- **Chosen**: **Streamlet** (permissioned, simple, partially synchronous, deterministic finality via 3-chain rule, designed for pedagogy and implementation).

### What was implemented
- A minimal, self-contained Streamlet-like flow suitable for a simulation:
  - **Propose**: epoch leader proposes a block extending the longest notarized chain.
  - **Vote**: nodes verify and vote if proposal extends their longest notarized chain.
  - **Notarize**: when a block collects ≥ ⌈2n/3⌉ votes, it’s notarized.
  - **Finalize**: any notarized 3-chain with consecutive epochs finalizes the prefix through the middle block; transactions are appended to the node’s finalized log.

### Files added and key changes
- New package: `market_sim/consensus`
  - `__init__.py`: exports primary components.
  - `block.py`: immutable `Block` with stable serialization and hashing.
  - `keys.py`: `KeyManager` for ECDSA keys/sign/verify using `cryptography`.
  - `chain.py`: simple chain helper for validation and tip management.
  - `messages.py`: `Proposal`, `Vote` message dataclasses.
  - `broker.py`: in-memory `MessageBroker` to simulate a network.
  - `node.py`: `ConsensusNode` implementing propose/vote/finalize, notarization tracking, and finalized log.
  - `sim_driver.py`: lightweight driver to run epochs and return logs; supports leader failure in a selected epoch.
  - `viz.py`: optional Graphviz visualization (`render_notarized_chains`) for notarized chains.
  - `render_snapshot.py`: script to generate PNGs of the chain for both happy path and a leader-failure scenario.
- Tests:
  - `market_sim/tests/test_consensus.py`: unit tests for block, signatures, chain rules, and a small happy-path integration.
  - `market_sim/tests/test_consensus_failures.py`: integration test validating progress when a leader fails in one epoch.
- Dependencies:
  - Updated `requirements.txt` to include `cryptography` and `graphviz` (Python package). System Graphviz binary installed via `winget` for PNG output.

### How to run
- Run simulation driver (prints finalized tx counts per node):
```bash
venv\Scripts\python.exe -m market_sim.consensus.sim_driver
```
- Render snapshots (produces `streamlet_snapshot.png` and `streamlet_snapshot_fail5.png`):
```bash
venv\Scripts\python.exe -m market_sim.consensus.render_snapshot
```
If PNGs don’t appear, install Graphviz system binaries and ensure `dot` is on PATH.

### How to run tests
```bash
venv\Scripts\pytest.exe -q
```
All tests currently pass, including integration with the existing market-making test.

### Outcomes and significance
- **Deterministic finality**: Finalized transactions will not be reverted, supporting robust trade settlement semantics.
- **Consistency**: All honest nodes converge on the same finalized log under partial synchrony.
- **Resilience**: Leader failure in a single epoch does not break safety; liveness resumes with the next leader.
- **Observability**: Visual snapshots illustrate forks, notarization, and finalization, aiding debugging and explanation.

### Impact on the overall project
- Establishes a clean consensus layer that can become the canonical ordering service for `market_sim`:
  - Agents submit actions to their local node’s mempool rather than directly mutating shared state.
  - The simulation engine can apply only finalized transactions to the order book and portfolios, eliminating state divergence.
  - The architecture now mirrors realistic distributed exchanges, enabling future experiments with faults, delays, and adversarial behavior.

### Design notes and limitations
- The current network is an in-memory broker suitable for deterministic simulations. It can be extended to model delays/partitions.
- Leader election is a deterministic hash of the epoch to emulate randomness; plug in a stronger RNG/beacon as desired.
- The implementation focuses on clarity over micro-optimizations; production deployments would harden validation, persistence, and signatures transport.

### Next steps (optional enhancements)
- Integrate finalized-log callbacks with the existing simulation engine to drive the order book updates directly from consensus.
- Add adversarial scenarios (e.g., fork attempts, equivocation) to tests and visualizations.
- Persist block and vote data structures for replay/longer runs.
- Extend visualization to color-code proposed/notarized/finalized blocks and highlight finalized prefixes per epoch.

### Final result
- Streamlet-based consensus components are implemented, tested, and demonstrated with visual outputs. The project now has a principled foundation for consistent, deterministic market simulations.


