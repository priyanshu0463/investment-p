"""
Streamlet consensus package for the market simulation.

This package provides minimal, readable building blocks to simulate
Streamlet in a permissioned setting:
- Block: immutable transaction container
- KeyManager: ECDSA keys and signatures
- Chain: helper for simple chain validation
- Messages: proposal and vote
- MessageBroker: simple in-memory message passing
- ConsensusNode: propose-vote-finalize lifecycle per Streamlet
"""

from .block import Block
from .keys import KeyManager
from .chain import Chain
from .messages import Proposal, Vote
from .broker import MessageBroker
from .node import ConsensusNode

__all__ = [
    "Block",
    "KeyManager",
    "Chain",
    "Proposal",
    "Vote",
    "MessageBroker",
    "ConsensusNode",
]



