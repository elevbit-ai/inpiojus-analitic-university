"""
Mouse monitor.
Monitor de mouse.

EN: Tracks pointer movement and idle periods. Long stretches with no movement
    while typing continues, or perfectly repetitive movement, are recorded as
    signals for later analysis. Uses 'pynput' when available; degrades quietly.

PT: Acompanha a movimentação do ponteiro e os períodos de inatividade. Longos
    trechos sem movimento enquanto a digitação continua, ou movimentos
    perfeitamente repetitivos, são registrados como sinais para a análise.
    Usa 'pynput' quando disponível; degrada silenciosamente.
"""

from __future__ import annotations

import math
import threading
import time

try:
    from pynput import mouse as _mouse
    _OK = True
except Exception:
    _OK = False

IDLE_LIMITE = 90.0  # seconds of stillness that count as "idle" / segundos parado


class MouseMonitor:
    def __init__(self, session):
        self.s = session
        self._listener = None
        self._watcher = None
        self._last_pos = None
        self._last_move = time.time()
        self._dist_total = 0.0
        self._moves = 0
        self._idle_flagged = False
        self._lock = threading.Lock()

    def start(self):
        if not _OK:
            self.s.add_event("mouse", "info", "pynput unavailable — mouse monitor off", {})
            return
        self._last_move = time.time()
        self._listener = _mouse.Listener(on_move=self._on_move, on_click=self._on_click)
        self._listener.start()
        self._watcher = threading.Thread(target=self._loop, daemon=True)
        self._watcher.start()

    def _on_move(self, x, y):
        with self._lock:
            agora = time.time()
            if self._last_pos is not None:
                dx, dy = x - self._last_pos[0], y - self._last_pos[1]
                self._dist_total += math.hypot(dx, dy)
            self._last_pos = (x, y)
            self._moves += 1
            self._last_move = agora
            if self._idle_flagged:
                self._idle_flagged = False

    def _on_click(self, x, y, button, pressed):
        if pressed:
            with self._lock:
                self._last_move = time.time()

    def _loop(self):
        while not self.s.stop.is_set():
            with self._lock:
                parado = time.time() - self._last_move
                if parado >= IDLE_LIMITE and not self._idle_flagged:
                    self._idle_flagged = True
                    self.s.add_event(
                        "mouse_idle", "medium",
                        f"mouse still for {int(parado)}s",
                        {"idle_seconds": int(parado)},
                    )
            self.s.stop.wait(5.0)

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
        with self._lock:
            self.s.metrics["mouse_distance_px"] = int(self._dist_total)
            self.s.metrics["mouse_moves"] = self._moves
