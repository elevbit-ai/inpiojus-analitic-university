"""
Keyboard monitor (privacy-preserving).
Monitor de teclado (preserva a privacidade).

EN: Records ONLY integrity-relevant metadata while the exam window is focused:
    typing cadence (timestamps, not characters), paste/copy/cut, Alt+Tab, the
    Windows key, Print Screen, and — on paste — the LENGTH of the clipboard
    text (never its content). It never stores plaintext, passwords, or anything
    typed outside the exam. This is what reveals AI copy-paste without reading
    the student's answers.

PT: Registra SOMENTE metadados relevantes à integridade enquanto a janela da
    prova está em foco: ritmo de digitação (horários, não caracteres),
    colar/copiar/recortar, Alt+Tab, tecla Windows, Print Screen e — ao colar —
    o COMPRIMENTO do texto da área de transferência (nunca o conteúdo). Nunca
    guarda texto, senhas, ou nada digitado fora da prova. É o que revela a
    colagem de IA sem ler as respostas do aluno.
"""

from __future__ import annotations

import os
import threading
import time

try:
    from pynput import keyboard as _kb
    _OK = True
except Exception:
    _OK = False

_IS_WIN = os.name == "nt"

BURST_JANELA = 2.0     # seconds / segundos
BURST_LIMITE = 30      # keystrokes in the window => machine-like burst


def _clipboard_len() -> int:
    """Length (chars) of clipboard unicode text; 0 if empty/unavailable."""
    if not _IS_WIN:
        return 0
    import ctypes
    from ctypes import wintypes

    u32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
    CF_UNICODETEXT = 13
    if not u32.OpenClipboard(0):
        return 0
    try:
        if not u32.IsClipboardFormatAvailable(CF_UNICODETEXT):
            return 0
        h = u32.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return 0
        k32.GlobalLock.restype = ctypes.c_void_p
        ptr = k32.GlobalLock(h)
        if not ptr:
            return 0
        try:
            return int(ctypes.wcslen(ctypes.c_wchar_p(ptr)))
        finally:
            k32.GlobalUnlock(h)
    finally:
        u32.CloseClipboard()


class KeyboardMonitor:
    def __init__(self, session):
        self.s = session
        self._listener = None
        self._ctrl = self._alt = self._shift = False
        self._chars = 0
        self._pastes = 0
        self._recent: list[float] = []
        self._burst_flag = False
        self._lock = threading.Lock()

    def start(self):
        if not _OK:
            self.s.add_event("keyboard", "warn", self.s.t("kbd_unavailable"), {})
            print("  " + self.s.t("kbd_unavailable"))
            return
        self._listener = _kb.Listener(on_press=self._press, on_release=self._release)
        self._listener.start()

    # -- modifier bookkeeping --
    def _is(self, key, nomes):
        return any(getattr(_kb.Key, n, None) == key for n in nomes)

    def _release(self, key):
        if self._is(key, ("ctrl", "ctrl_l", "ctrl_r")):
            self._ctrl = False
        elif self._is(key, ("alt", "alt_l", "alt_r", "alt_gr")):
            self._alt = False
        elif self._is(key, ("shift", "shift_l", "shift_r")):
            self._shift = False

    def _press(self, key):
        agora = time.time()
        no_exame = getattr(self.s, "focus_on_exam", True)

        if self._is(key, ("ctrl", "ctrl_l", "ctrl_r")):
            self._ctrl = True; return
        if self._is(key, ("alt", "alt_l", "alt_r", "alt_gr")):
            self._alt = True; return
        if self._is(key, ("shift", "shift_l", "shift_r")):
            self._shift = True; return

        # Special / shortcut keys — always recorded.
        if self._is(key, ("tab",)) and self._alt:
            self.s.add_event("alt_tab", "high", "Alt+Tab (troca de janela)", {}); return
        if self._is(key, ("cmd", "cmd_l", "cmd_r")):
            self.s.add_event("win_key", "medium", "Windows key pressed", {}); return
        if self._is(key, ("print_screen",)):
            self.s.add_event("print_screen", "high", "Print Screen (captura de tela)", {}); return

        letra = getattr(key, "char", None)
        if self._ctrl and letra in ("v", "V"):
            n = _clipboard_len()
            self._pastes += 1
            sev = "high" if n >= 80 else "medium"
            self.s.add_event("paste", sev,
                             f"colagem de {n} caracteres (Ctrl+V)",
                             {"clipboard_len": n}); return
        if self._ctrl and letra in ("c", "C"):
            self.s.add_event("copy", "info", "Ctrl+C", {}); return
        if self._ctrl and letra in ("x", "X"):
            self.s.add_event("cut", "info", "Ctrl+X", {}); return

        # Ordinary typing — cadence + burst only, no characters stored.
        if no_exame:
            with self._lock:
                self._chars += 1
                self._recent.append(agora)
                corte = agora - BURST_JANELA
                self._recent = [t for t in self._recent if t >= corte]
                if len(self._recent) >= BURST_LIMITE and not self._burst_flag:
                    self._burst_flag = True
                    taxa = len(self._recent) / BURST_JANELA
                    self.s.add_event("typing_burst", "high",
                                     f"digitação em rajada (~{taxa:.0f} teclas/s)",
                                     {"keys_per_s": round(taxa, 1)})
                elif len(self._recent) < BURST_LIMITE // 2:
                    self._burst_flag = False

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
        self.s.metrics["keystrokes"] = self._chars
        self.s.metrics["paste_events"] = self._pastes
