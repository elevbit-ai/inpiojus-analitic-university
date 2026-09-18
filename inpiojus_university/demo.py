"""
Synthetic extract generator (for testing / examples).
Gerador de extratos sintéticos (para testes / exemplos).

EN: Builds a valid, hash-sealed extract with a chosen cheating scenario, without
    needing a camera or keyboard. Used by the test suite and the website demos.

PT: Constrói um extrato válido e selado por hash com um cenário de fraude
    escolhido, sem precisar de câmera ou teclado. Usado pela suíte de testes e
    pelas demonstrações do site.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from . import __version__, extract as extract_mod


class DemoSession:
    def __init__(self, aluno, matricula, url, minutos, eventos, metrics, lang="pt"):
        self.aluno = aluno
        self.matricula = matricula
        self.url = url
        self.minutos = minutos
        self.lang = lang
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.iniciada_em = datetime.now()
        self.baseline_window = "chrome.exe :: Prova de Direito Constitucional - AVA"
        self.metrics = metrics
        self._eventos = eventos
        self.dir = Path(".")

    def eventos(self):
        return self._eventos

    def contexto_maquina(self):
        return {
            "sistema": "Windows 10",
            "maquina": "PC-ALUNO",
            "python": "3.11",
            "agente": f"InpioJus Analitic University v{__version__}",
        }


def _ev(t, clock, sev, tipo, detalhe, dados=None):
    return {"t": t, "clock": clock, "severity": sev, "type": tipo,
            "detail": detalhe, "data": dados or {}}


CENARIOS = {
    "limpo": {
        "metrics": {"keystrokes": 2100, "paste_events": 0, "mouse_distance_px": 51200,
                    "mouse_moves": 3400, "camera_active": True, "camera_checks": 420,
                    "camera_face_ok": 415},
        "eventos": [
            _ev(120.0, "20:02:00", "info", "focus_regained", "focus returned to exam window"),
            _ev(900.0, "20:15:00", "medium", "mouse_idle", "mouse still for 95s", {"idle_seconds": 95}),
        ],
    },
    "suspeito": {
        "metrics": {"keystrokes": 640, "paste_events": 2, "mouse_distance_px": 18300,
                    "mouse_moves": 900, "camera_active": True, "camera_checks": 300,
                    "camera_face_ok": 268},
        "eventos": [
            _ev(305.0, "20:05:05", "high", "alt_tab", "Alt+Tab (troca de janela)"),
            _ev(298.0, "20:04:58", "high", "focus_lost", "focus -> chrome.exe :: ChatGPT",
                {"process": "chrome.exe", "title": "ChatGPT"}),
            _ev(320.0, "20:05:20", "info", "focus_regained", "focus returned to exam window"),
            _ev(327.0, "20:05:27", "high", "paste", "colagem de 214 caracteres (Ctrl+V)",
                {"clipboard_len": 214}),
            _ev(1180.0, "20:19:40", "medium", "mouse_idle", "mouse still for 140s", {"idle_seconds": 140}),
            _ev(1240.0, "20:20:40", "medium", "paste", "colagem de 96 caracteres (Ctrl+V)",
                {"clipboard_len": 96}),
        ],
    },
    "grave": {
        "metrics": {"keystrokes": 210, "paste_events": 4, "mouse_distance_px": 6100,
                    "mouse_moves": 260, "camera_active": True, "camera_checks": 280,
                    "camera_face_ok": 150},
        "eventos": [
            _ev(140.0, "20:02:20", "high", "multi_face", "mais de um rosto detectado", {"faces": 2}),
            _ev(210.0, "20:03:30", "high", "focus_lost", "focus -> chrome.exe :: ChatGPT",
                {"process": "chrome.exe", "title": "ChatGPT - resposta"}),
            _ev(235.0, "20:03:55", "high", "paste", "colagem de 512 caracteres (Ctrl+V)",
                {"clipboard_len": 512}),
            _ev(240.0, "20:04:00", "high", "typing_burst", "digitação em rajada (~42 teclas/s)",
                {"keys_per_s": 42.0}),
            _ev(600.0, "20:10:00", "high", "face_absent", "rosto ausente do quadro"),
            _ev(660.0, "20:11:00", "high", "alt_tab", "Alt+Tab (troca de janela)"),
            _ev(690.0, "20:11:30", "high", "paste", "colagem de 430 caracteres (Ctrl+V)",
                {"clipboard_len": 430}),
            _ev(900.0, "20:15:00", "high", "multi_face", "mais de um rosto detectado", {"faces": 2}),
            _ev(1500.0, "20:25:00", "high", "print_screen", "Print Screen (captura de tela)"),
        ],
    },
}


def gerar_extrato_demo(destino=None, cenario="suspeito", lang="pt") -> Path:
    conf = CENARIOS.get(cenario, CENARIOS["suspeito"])
    sess = DemoSession(
        aluno="ALUNO DE EXEMPLO / SAMPLE STUDENT",
        matricula="2026-000123",
        url="https://ava.universidade.edu.br/prova/8842",
        minutos=60,
        eventos=list(conf["eventos"]),
        metrics=dict(conf["metrics"]),
        lang=lang,
    )
    caminho = extract_mod.gerar(sess)
    if destino:
        alvo = Path(destino)
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(caminho.read_text(encoding="utf-8"), encoding="utf-8")
        if caminho.resolve() != alvo.resolve():
            caminho.unlink(missing_ok=True)
        return alvo
    return caminho
