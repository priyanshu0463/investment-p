from collections import deque
from typing import Deque, Dict, List, Tuple, Any


class MessageBroker:
    def __init__(self) -> None:
        self._subscribers: Dict[str, Any] = {}
        self._queue: Deque[Tuple[str, Any]] = deque()

    def register(self, node_id: str, handler) -> None:
        self._subscribers[node_id] = handler

    def broadcast(self, message: Any) -> None:
        for node_id in self._subscribers.keys():
            self._queue.append((node_id, message))

    def send(self, node_id: str, message: Any) -> None:
        self._queue.append((node_id, message))

    def deliver_all(self) -> None:
        while self._queue:
            node_id, message = self._queue.popleft()
            handler = self._subscribers.get(node_id)
            if handler is not None:
                handler(message)



