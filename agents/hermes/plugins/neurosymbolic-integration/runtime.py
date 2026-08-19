"""Estado acotado por turno para coordinar hooks y herramienta oficial."""

from __future__ import annotations

import hashlib
import threading
import uuid
from collections import OrderedDict
from typing import Any, Dict, Optional


class NeurosymbolicRuntime:
    """Correlaciona detección, tool call y transformación de salida."""

    def __init__(self, max_entries: int = 128):
        self._lock = threading.RLock()
        self._max_entries = max_entries
        self._active_by_turn: "OrderedDict[str, str]" = OrderedDict()
        self._requests: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()

    @staticmethod
    def turn_keys(**kwargs) -> list[str]:
        keys = []
        for field in ("turn_id", "session_id", "task_id"):
            value = kwargs.get(field)
            if value is not None and str(value) and str(value) not in keys:
                keys.append(str(value))
        return keys or ["one-shot"]

    def _trim(self) -> None:
        while len(self._requests) > self._max_entries:
            request_id, _ = self._requests.popitem(last=False)
            for key, active in list(self._active_by_turn.items()):
                if active == request_id:
                    self._active_by_turn.pop(key, None)
        while len(self._active_by_turn) > self._max_entries:
            self._active_by_turn.popitem(last=False)

    def begin(self, query: str, **kwargs) -> str:
        keys = self.turn_keys(**kwargs)
        key = keys[0]
        request_id = uuid.uuid4().hex
        with self._lock:
            for active_key in keys:
                self._active_by_turn[active_key] = request_id
            self._requests[request_id] = {
                "query": query,
                "query_hash": hashlib.sha256(query.encode("utf-8")).hexdigest(),
                "turn_key": key,
                "status": "pending",
                "contract": None,
            }
            self._trim()
        return request_id

    def clear_turn(self, **kwargs) -> None:
        with self._lock:
            for key in self.turn_keys(**kwargs):
                self._active_by_turn.pop(key, None)

    def query_for(self, request_id: str) -> Optional[str]:
        with self._lock:
            request = self._requests.get(request_id)
            return str(request["query"]) if request else None

    def completed_contract(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            request = self._requests.get(request_id)
            if not request or request.get("status") != "completed":
                return None
            contract = request.get("contract")
            return dict(contract) if isinstance(contract, dict) else None

    def complete(
        self,
        request_id: str,
        contract: Dict[str, Any],
        **kwargs,
    ) -> None:
        keys = self.turn_keys(**kwargs)
        key = keys[0]
        with self._lock:
            request = self._requests.setdefault(
                request_id,
                {
                    "query": "",
                    "query_hash": "",
                    "turn_key": key,
                },
            )
            request["status"] = "completed"
            request["contract"] = dict(contract)
            for active_key in keys:
                self._active_by_turn[active_key] = request_id
            original_key = request.get("turn_key")
            if original_key:
                self._active_by_turn[str(original_key)] = request_id
            self._trim()

    def result_for_turn(self, **kwargs) -> Optional[Dict[str, Any]]:
        with self._lock:
            request_id = next(
                (
                    self._active_by_turn.get(key)
                    for key in self.turn_keys(**kwargs)
                    if self._active_by_turn.get(key)
                ),
                None,
            )
            if not request_id:
                return None
            request = self._requests.get(request_id)
            if not request:
                return None
            return {
                "request_id": request_id,
                "status": request.get("status"),
                "contract": request.get("contract"),
            }

    def consume_turn(self, **kwargs) -> Optional[Dict[str, Any]]:
        with self._lock:
            request_id = next(
                (
                    self._active_by_turn.get(key)
                    for key in self.turn_keys(**kwargs)
                    if self._active_by_turn.get(key)
                ),
                None,
            )
            if not request_id:
                return None
            for key, active in list(self._active_by_turn.items()):
                if active == request_id:
                    self._active_by_turn.pop(key, None)
            request = self._requests.get(request_id)
            return dict(request) if request else None
