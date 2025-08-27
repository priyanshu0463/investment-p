import pytest

from market_sim.consensus.block import Block
from market_sim.consensus.keys import KeyManager
from market_sim.consensus.chain import Chain
from market_sim.consensus.sim_driver import run_simple_simulation


def test_block_serialization_and_hash_stability():
    b1 = Block(parent_hash="abc", epoch=1, transactions=[{"x": 1}, {"y": 2}], proposer_id="0")
    b2 = Block(parent_hash="abc", epoch=1, transactions=[{"x": 1}, {"y": 2}], proposer_id="0")
    assert b1.serialize() == b2.serialize()
    assert b1.hash() == b2.hash()


def test_signature_verification_roundtrip():
    km = KeyManager()
    msg = b"hello"
    sig = km.sign(msg)
    assert KeyManager.verify(km.public_key, sig, msg)
    assert not KeyManager.verify(km.public_key, sig, b"tamper")


def test_chain_validation_rules():
    genesis = Block(parent_hash=None, epoch=0, transactions=[], proposer_id="g")
    c = Chain(genesis)
    b1 = Block(parent_hash=genesis.hash(), epoch=1, transactions=[], proposer_id="0")
    assert c.validate_and_add(b1)
    b_bad_parent = Block(parent_hash="deadbeef", epoch=2, transactions=[], proposer_id="0")
    assert not c.validate_and_add(b_bad_parent)
    b_bad_epoch = Block(parent_hash=b1.hash(), epoch=1, transactions=[], proposer_id="0")
    assert not c.validate_and_add(b_bad_epoch)


def test_streamlet_happy_path_small_network():
    logs = run_simple_simulation(num_nodes=4, epochs=8)
    # All nodes must agree on finalized log prefix
    assert all(logs[0] == l for l in logs)
    # Some transactions should be finalized
    assert len(logs[0]) > 0


