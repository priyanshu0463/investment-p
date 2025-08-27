from dataclasses import dataclass
from typing import Optional


@dataclass
class Proposal:
    sender_id: str
    epoch: int
    block_hash: str
    block_bytes: bytes
    signature: bytes


@dataclass
class Vote:
    sender_id: str
    epoch: int
    block_hash: str
    signature: bytes
    block_bytes: bytes
    for_leader_id: Optional[str] = None


