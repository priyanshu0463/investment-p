import hashlib
import json
from dataclasses import dataclass
from typing import List, Any, Optional


def _stable_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class Block:
    parent_hash: Optional[str]
    epoch: int
    transactions: List[Any]
    proposer_id: str

    def serialize(self) -> bytes:
        payload = {
            "parent_hash": self.parent_hash,
            "epoch": self.epoch,
            "transactions": self.transactions,
            "proposer_id": self.proposer_id,
        }
        return _stable_json(payload)

    def hash(self) -> str:
        return hashlib.sha256(self.serialize()).hexdigest()



