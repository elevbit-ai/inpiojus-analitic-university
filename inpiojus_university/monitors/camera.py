"""
Camera monitor (face-only).
Monitor de câmera (somente o rosto).

EN: At intervals, grabs a webcam frame and runs OpenCV's YuNet face detector.
    It enforces the "only your face" rule: it confirms exactly one face is
    present, flagging when the face is absent (student left) or when more than
    one face appears (someone is helping). On anomalies it may save a small
    thumbnail CROPPED TO THE FACE only — never the surrounding room — so the
    institution can verify identity without filming the environment.

PT: Em intervalos, captura um quadro da webcam e roda o detector de rosto YuNet
    do OpenCV. Aplica a regra "somente o seu rosto": confirma que há exatamente
    um rosto, sinalizando quando o rosto está ausente (aluno saiu) ou quando há
    mais de um rosto (alguém ajudando). Em anomalias, pode salvar uma miniatura
    RECORTADA APENAS NO ROSTO — nunca o ambiente ao redor — para a instituição
    conferir a identidade sem filmar o local.

The YuNet model (~230 KB) is downloaded once and cached locally.
O modelo YuNet (~230 KB) é baixado uma vez e fica em cache local.
"""

from __future__ import annotations

import threading
import time
import urllib.request
from pathlib import Path

try:
    import cv2
    import numpy as np
    _OK = True
except Exception:
    _OK = False

_MODEL_URL = ("https://github.com/opencv/opencv_zoo/raw/main/models/"
              "face_detection_yunet/face_detection_yunet_2023mar.onnx")
INTERVALO = 8.0        # seconds between checks / segundos entre verificações
SALVAR_A_CADA = 60.0   # save a presence thumbnail at most this often


def _modelo_local() -> Path:
    base = Path.home() / ".inpiojus_university" / "models"
    base.mkdir(parents=True, exist_ok=True)
    return base / "face_detection_yunet_2023mar.onnx"


def _garantir_modelo() -> Path | None:
    caminho = _modelo_local()
    if caminho.exists() and caminho.stat().st_size > 1000:
        return caminho
    try:
        dados = urllib.request.urlopen(_MODEL_URL, timeout=30).read()
        caminho.write_bytes(dados)
        return caminho
    except Exception:
        return None


class CameraMonitor:
    def __init__(self, session, indice: int = 0):
        self.s = session
        self.indice = indice
        self._thread = None
        self._cap = None
        self._detector = None
        self._ultimo_salvo = 0.0
        self._sem_rosto = False
        self._multi = False
        self._fotos_dir = session.dir / "faces"

    def start(self):
        if not _OK:
            self.s.add_event("camera", "warn", self.s.t("cam_unavailable"), {})
            print("  " + self.s.t("cam_unavailable"))
            return
        modelo = _garantir_modelo()
        cap = cv2.VideoCapture(self.indice)
        if not modelo or not cap or not cap.isOpened():
            if cap:
                cap.release()
            self.s.add_event("camera", "warn", self.s.t("cam_unavailable"),
                             {"model": bool(modelo)})
            print("  " + self.s.t("cam_unavailable"))
            self.s.metrics["camera_active"] = False
            return
        self._cap = cap
        self._detector = cv2.FaceDetectorYN_create(str(modelo), "", (320, 320),
                                                    0.7, 0.3, 5000)
        self._fotos_dir.mkdir(parents=True, exist_ok=True)
        self.s.metrics["camera_active"] = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        checagens = presencas = 0
        while not self.s.stop.is_set():
            ok, frame = self._cap.read()
            if ok and frame is not None:
                checagens += 1
                n = self._contar_rostos(frame)
                if n == 1:
                    presencas += 1
                    if not getattr(self, "_ok_flag", False):
                        self._ok_flag = True
                    self._sem_rosto = self._multi = False
                    self._talvez_salvar(frame, "presenca")
                elif n == 0 and not self._sem_rosto:
                    self._sem_rosto = True; self._multi = False
                    self.s.add_event("face_absent", "high", self.s.t("cam_no_face"), {})
                elif n >= 2 and not self._multi:
                    self._multi = True; self._sem_rosto = False
                    self.s.add_event("multi_face", "high",
                                     self.s.t("cam_multi_face"), {"faces": n})
                    self._talvez_salvar(frame, "multi", forcar=True)
            self.s.stop.wait(INTERVALO)
        self.s.metrics["camera_checks"] = checagens
        self.s.metrics["camera_face_ok"] = presencas

    def _contar_rostos(self, frame) -> int:
        h, w = frame.shape[:2]
        self._detector.setInputSize((w, h))
        _, faces = self._detector.detect(frame)
        return 0 if faces is None else len(faces)

    def _talvez_salvar(self, frame, tag: str, forcar: bool = False):
        agora = time.time()
        if not forcar and (agora - self._ultimo_salvo) < SALVAR_A_CADA:
            return
        self._ultimo_salvo = agora
        h, w = frame.shape[:2]
        self._detector.setInputSize((w, h))
        _, faces = self._detector.detect(frame)
        if faces is None or len(faces) == 0:
            return
        # Crop tightly to the (first) face only — never the surroundings.
        x, y, fw, fh = faces[0][:4].astype(int)
        m = int(0.2 * max(fw, fh))
        x0, y0 = max(0, x - m), max(0, y - m)
        x1, y1 = min(w, x + fw + m), min(h, y + fh + m)
        rosto = frame[y0:y1, x0:x1]
        if rosto.size == 0:
            return
        rosto = cv2.resize(rosto, (160, 160))
        marca = time.strftime("%H%M%S")
        nome = self._fotos_dir / f"{tag}_{marca}.jpg"
        cv2.imwrite(str(nome), rosto, [cv2.IMWRITE_JPEG_QUALITY, 82])

    def stop(self):
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
