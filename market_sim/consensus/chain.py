from typing import List

from .block import Block


class Chain:
    def __init__(self, genesis_block: Block) -> None:
        self.blocks: List[Block] = [genesis_block]

    def tip(self) -> Block:
        return self.blocks[-1]

    def validate_and_add(self, block: Block) -> bool:
        if block.parent_hash != self.tip().hash():
            return False
        if block.epoch <= self.tip().epoch:
            return False
        self.blocks.append(block)
        return True



