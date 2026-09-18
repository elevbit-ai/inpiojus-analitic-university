"""
Window / focus monitor.
Monitor de janela e foco.

EN: Detects when focus leaves the exam window (tab/app switching). On Windows
    it reads the foreground window title and owning process via the Win32 API
    (ctypes, no external dependency). The exam window is the one focused when
    monitoring starts; any switch to a different window is recorded.

PT: Detecta quando o foco sai da janela da prova (troca de aba/app). No Windows
    lê o título da janela em foco e o processo dono via API Win32 (ctypes, sem
    dependência externa). A janela da prova é a que está em foco no início; toda
    troca para outra janela é registrada.
"""

from __future__ import annotations

import os
import threading
import time

_IS_WIN = os.name == "nt"

if _IS_WIN:
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32
    _kernel32 = ctypes.windll.kernel32
    _PROCESS_QUERY_LIMITED = 0x1000


def _foreground_window() -> tuple[str, str]:
    """Return (title, process_name) of the foreground window."""
    if not _IS_WIN:
        return ("", "")
    hwnd = _user32.GetForegroundWindow()
    if not hwnd:
        return ("", "")
    n = _user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    _user32.GetWindowTextW(hwnd, buf, n + 1)
    titulo = buf.value

    pid = wintypes.DWORD()
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    processo = ""
    h = _kernel32.OpenProcess(_PROCESS_QUERY_LIMITED, False, pid.value)
    if h:
        try:
            tam = wintypes.DWORD(260)
            nome = ctypes.create_unicode_buffer(260)
            if _kernel32.QueryFullProcessImageNameW(h, 0, nome, ctypes.byref(tam)):
                processo = os.path.basename(nome.value)
        finally:
            _kernel32.CloseHandle(h)
    return (titulo, processo)


# Apps that are suspicious to have focused during an exam.
# Apps suspeitos de estar em foco durante a prova.
_SUSPICIOUS = {
    "cmd.exe", "powershell.exe", "pwsh.exe", "windowsterminal.exe",
    "code.exe", "notepad.exe", "notepad++.exe", "wordpad.exe",
    "winword.exe", "telegram.exe", "whatsapp.exe", "discord.exe",
    "slack.exe", "teams.exe", "python.exe", "conhost.exe",
}


class WindowMonitor:
    def __init__(self, session):
        self.s = session
        self._thread = None
        self._baseline_title = ""
        self._baseline_proc = ""
        self._fora = False

    def start(self):
        if not _IS_WIN:
            self.s.add_event("window", "info",
                             "window monitor available only on Windows",
                             {"platform": os.name})
            return
        self._baseline_title, self._baseline_proc = _foreground_window()
        self.s.baseline_window = f"{self._baseline_proc} :: {self._baseline_title}"
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while not self.s.stop.is_set():
            titulo, proc = _foreground_window()
            mesmo = (proc == self._baseline_proc and
                     _similar(titulo, self._baseline_title))
            self.s.focus_on_exam = mesmo
            if not mesmo and not self._fora:
                self._fora = True
                sev = "high" if proc.lower() in _SUSPICIOUS else "medium"
                self.s.add_event("focus_lost", sev,
                                 f"focus -> {proc or 'desconhecido'} :: {titulo[:80]}",
                                 {"process": proc, "title": titulo[:120]})
            elif mesmo and self._fora:
                self._fora = False
                self.s.add_event("focus_regained", "info",
                                 "focus returned to exam window", {})
            self.s.stop.wait(1.0)

    def stop(self):
        pass


def _similar(a: str, b: str) -> bool:
    """Titles of the same page shift as it navigates; compare loosely."""
    if not a or not b:
        return a == b
    a, b = a.lower(), b.lower()
    if a == b:
        return True
    # Same trailing app name (e.g. "... - Google Chrome").
    ta, tb = a.rsplit(" - ", 1)[-1], b.rsplit(" - ", 1)[-1]
    return ta == tb
