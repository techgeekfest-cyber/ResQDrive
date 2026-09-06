"""WebSocket connection manager for real-time broadcast to all clients."""
import asyncio
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("resqdrive.ws")


def _json_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)


class ConnectionManager:
    """Tracks active WebSocket clients and broadcasts JSON messages."""

    def __init__(self):
        self.active = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket):
        await websocket.accept()
        async with self._lock:
            self.active.add(websocket)
        logger.info("WS client connected (total=%d)", len(self.active))

    async def disconnect(self, websocket):
        async with self._lock:
            self.active.discard(websocket)
        logger.info("WS client disconnected (total=%d)", len(self.active))

    @property
    def count(self):
        return len(self.active)

    async def broadcast(self, message):
        """Send a dict message to every connected client (best-effort)."""
        if not self.active:
            return
        payload = json.dumps(message, default=_json_default)
        dead = []
        # snapshot to avoid mutation during iteration
        for ws in list(self.active):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self.active.discard(ws)


manager = ConnectionManager()
