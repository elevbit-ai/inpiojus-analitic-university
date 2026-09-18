"""
Proctoring session orchestrator.
Orquestrador da sessão de fiscalização.

EN: Starts the monitors, runs the exam timer, collects the event timeline and
    metrics, and produces the signed extract at the end. All data stays local.

PT: Inicia os monitores, controla o cronômetro da prova, reúne a linha do tempo
    de eventos e as métricas, e gera o extrato assinado ao final. Todos os dados
    permanecem locais.
"""

from __future__ import annotations

import platform
import threading
import time
from datetime import datetime
from pathlib import Path

from . import __version__
from .i18n import T
from .monitors.camera import CameraMonitor
from .monitors.keyboard import KeyboardMonitor
from .monitors.mouse import MouseMonitor
from .monitors.window import WindowMonitor
from . import extract as extract_mod


def _base_sessions() -> Path:
    d = Path.home() / ".inpiojus_university" / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


class ProctorSession:
    def __init__(self, *, aluno: str, matricula: str, url: str,
                 minutos: float, lang: str = "pt"):
        self.aluno = aluno
        self.matricula = matricula
        self.url = url
        self.minutos = float(minutos)
        self.lang = lang
        self.t = T(lang)

        self.stop = threading.Event()
        self.focus_on_exam = True
        self.baseline_window = ""
        self._eventos: list[dict] = []
        self._lock = threading.Lock()
        self.metrics: dict = {}

        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.iniciada_em = datetime.now()
        self.t0 = time.time()
        self.dir = _base_sessions() / marca
        self.dir.mkdir(parents=True, exist_ok=True)
        self.session_id = marca

    # ------------------------------------------------------------------
    def add_event(self, tipo: str, severidade: str, detalhe: str, dados: dict):
        with self._lock:
            self._eventos.append({
                "t": round(time.time() - self.t0, 1),
                "clock": datetime.now().strftime("%H:%M:%S"),
                "type": tipo,
                "severity": severidade,
                "detail": detalhe,
                "data": dados or {},
            })

    def eventos(self) -> list[dict]:
        with self._lock:
            return list(self._eventos)

    # ------------------------------------------------------------------
    def executar(self) -> Path:
        monitores = [
            WindowMonitor(self),
            KeyboardMonitor(self),
            MouseMonitor(self),
            CameraMonitor(self),
        ]
        for m in monitores:
            m.start()

        print("\n  " + self.t("session_started"))
        print("  " + self.t("recording_indicator"))
        print("  " + self.t("press_finish") + "\n")

        fim = self.t0 + self.minutos * 60
        try:
            while not self.stop.is_set():
                restante = fim - time.time()
                if restante <= 0:
                    break
                mm, ss = divmod(int(restante), 60)
                hh, mm = divmod(mm, 60)
                print(f"\r  {self.t('recording_indicator')}   "
                      f"{self.t('time_left')}: {hh:02d}:{mm:02d}:{ss:02d}   ",
                      end="", flush=True)
                self.stop.wait(1.0)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop.set()

        print("\n\n  " + self.t("session_finished"))
        for m in monitores:
            m.stop()
        time.sleep(0.4)

        caminho = extract_mod.gerar(self)
        print("  " + self.t("extract_saved") + " " + str(caminho))
        print("  " + self.t("send_to_faculty"))
        return caminho

    # ------------------------------------------------------------------
    def contexto_maquina(self) -> dict:
        return {
            "sistema": f"{platform.system()} {platform.release()}",
            "maquina": platform.node(),
            "python": platform.python_version(),
            "agente": f"InpioJus Analitic University v{__version__}",
        }
