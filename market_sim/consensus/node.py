import hashlib
from math import ceil
from typing import Any, Dict, List, Optional, Set

from .block import Block
from .broker import MessageBroker
from .chain import Chain
from .keys import KeyManager, PublicKeyRegistry
from .messages import Proposal, Vote


class ConsensusNode:
    def __init__(
        self,
        node_id: str,
        broker: MessageBroker,
        public_keys: PublicKeyRegistry,
        total_nodes: int,
    ) -> None:
        self.node_id = node_id
        self.key_manager = KeyManager()
        self.public_keys: PublicKeyRegistry = public_keys
        self.public_keys[node_id] = self.key_manager.public_key
        self.broker = broker
        self.total_nodes = total_nodes

        self.blocks_by_hash: Dict[str, Block] = {}
        self.votes_by_block: Dict[str, Set[str]] = {}
        self.notarized_blocks: Set[str] = set()
        self.chains: List[List[str]] = []
        self.finalized_log: List[Any] = []
        self.mempool: List[Any] = []
        self.voted_in_epoch: Set[int] = set()

        self.genesis = Block(parent_hash=None, epoch=0, transactions=[], proposer_id="genesis")
        self.blocks_by_hash[self.genesis.hash()] = self.genesis
        self.notarized_blocks.add(self.genesis.hash())
        self.chains = [[self.genesis.hash()]]

        self.broker.register(self.node_id, self._on_message)

    def _on_message(self, message: Any) -> None:
        if isinstance(message, Proposal):
            self.on_receive_proposal(message)
        elif isinstance(message, Vote):
            self.on_receive_vote(message)

    def expected_leader_for_epoch(self, epoch: int) -> str:
        return str(int(hashlib.sha256(str(epoch).encode()).hexdigest(), 16) % self.total_nodes)

    def longest_notarized_chains(self) -> List[List[str]]:
        notarized_set = set(self.notarized_blocks)
        candidates: List[List[str]] = []
        max_len = 0
        for chain in self.chains:
            if all(h in notarized_set for h in chain):
                if len(chain) > max_len:
                    candidates = [chain]
                    max_len = len(chain)
                elif len(chain) == max_len:
                    candidates.append(chain)
        return candidates or [[self.genesis.hash()]]

    def propose(self, epoch: int) -> None:
        if self.expected_leader_for_epoch(epoch) != self.node_id:
            return
        parent_chain = self.longest_notarized_chains()[0]
        parent_hash = parent_chain[-1]
        block = Block(parent_hash=parent_hash, epoch=epoch, transactions=list(self.mempool), proposer_id=self.node_id)
        block_hash = block.hash()
        self.blocks_by_hash[block_hash] = block
        signature = self.key_manager.sign(block.serialize())
        proposal = Proposal(
            sender_id=self.node_id,
            epoch=epoch,
            block_hash=block_hash,
            block_bytes=block.serialize(),
            signature=signature,
        )
        self.broker.broadcast(proposal)

    def on_receive_proposal(self, proposal: Proposal) -> None:
        if self.expected_leader_for_epoch(proposal.epoch) != proposal.sender_id:
            return
        leader_pk = self.public_keys.get(proposal.sender_id)
        if leader_pk is None:
            return
        if not KeyManager.verify(leader_pk, proposal.signature, proposal.block_bytes):
            return
        # Reconstruct and store block from bytes if not present
        block_hash = proposal.block_hash
        if block_hash not in self.blocks_by_hash:
            parsed = self._parse_block_bytes(proposal.block_bytes)
            if parsed is None:
                return
            block = Block(
                parent_hash=parsed["parent_hash"],
                epoch=int(parsed["epoch"]),
                transactions=parsed.get("transactions", []),
                proposer_id=parsed.get("proposer_id", proposal.sender_id),
            )
            if block.hash() != block_hash:
                return
            self.blocks_by_hash[block_hash] = block
        # Allow one vote per epoch
        if proposal.epoch in self.voted_in_epoch:
            return
        # Simplified rule: vote if parent is tip of any longest notarized chain
        parent_ok = False
        for chain in self.longest_notarized_chains():
            if chain[-1] == self._extract_parent_hash_from_block_bytes(proposal.block_bytes):
                parent_ok = True
                break
        if not parent_ok:
            return
        sig = self.key_manager.sign(proposal.block_bytes)
        vote = Vote(sender_id=self.node_id, epoch=proposal.epoch, block_hash=proposal.block_hash, signature=sig, block_bytes=proposal.block_bytes, for_leader_id=proposal.sender_id)
        self.voted_in_epoch.add(proposal.epoch)
        self.broker.broadcast(vote)

    def on_receive_vote(self, vote: Vote) -> None:
        voter_pk = self.public_keys.get(vote.sender_id)
        if voter_pk is None:
            return
        # Verify signature against the block bytes
        if not KeyManager.verify(voter_pk, vote.signature, vote.block_bytes):
            return
        votes = self.votes_by_block.setdefault(vote.block_hash, set())
        if vote.sender_id in votes:
            return
        votes.add(vote.sender_id)
        threshold = ceil((2 * self.total_nodes) / 3)
        if len(votes) >= threshold:
            self.notarized_blocks.add(vote.block_hash)
            self._extend_chains_with_notarized(vote.block_hash)
            self.check_finalization()

    def _extend_chains_with_notarized(self, block_hash: str) -> None:
        # Attach block to any chain whose tip matches the parent
        parent = self._parent_of(block_hash)
        if parent is None:
            return
        new_chains: List[List[str]] = []
        extended = False
        for chain in self.chains:
            if chain[-1] == parent:
                new_chain = chain + [block_hash]
                new_chains.append(new_chain)
                extended = True
            else:
                new_chains.append(chain)
        if not extended:
            # Start a new branch if parent unknown in our chains
            new_chains.append([parent, block_hash])
        self.chains = self._dedupe_longest(new_chains)

    def _dedupe_longest(self, chains: List[List[str]]) -> List[List[str]]:
        by_tip: Dict[str, List[str]] = {}
        for c in chains:
            tip = c[-1]
            if tip not in by_tip or len(c) > len(by_tip[tip]):
                by_tip[tip] = c
        return list(by_tip.values())

    def check_finalization(self) -> None:
        # Find any notarized chain with three consecutive epochs and finalize up to the middle
        notarized = set(self.notarized_blocks)
        for chain in self.chains:
            # Need block objects to check epochs; skip if any missing
            epochs: List[int] = []
            ok = True
            for h in chain:
                b = self.blocks_by_hash.get(h)
                if not b:
                    ok = False
                    break
                epochs.append(b.epoch)
            if not ok or len(chain) < 3:
                continue
            for i in range(len(chain) - 2):
                h1, h2, h3 = chain[i], chain[i + 1], chain[i + 2]
                if h1 in notarized and h2 in notarized and h3 in notarized:
                    e1, e2, e3 = epochs[i], epochs[i + 1], epochs[i + 2]
                    if e2 == e1 + 1 and e3 == e2 + 1:
                        middle_block = self.blocks_by_hash[h2]
                        for tx in middle_block.transactions:
                            self.finalized_log.append(tx)

    def _extract_parent_hash_from_block_bytes(self, block_bytes: bytes) -> Optional[str]:
        # Minimal JSON extraction without importing json to keep dependencies local here
        try:
            import json  # local import

            data = json.loads(block_bytes)
            return data.get("parent_hash")
        except Exception:
            return None

    def _parse_block_bytes(self, block_bytes: bytes) -> Optional[dict]:
        try:
            import json

            return json.loads(block_bytes)
        except Exception:
            return None

    def _parent_of(self, block_hash: str) -> Optional[str]:
        block = self.blocks_by_hash.get(block_hash)
        if block is not None:
            return block.parent_hash
        return None


