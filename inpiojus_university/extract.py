"""
Exam extract writer and reader.
Escritor e leitor do extrato da prova.

EN: Produces a human-readable, machine-parseable .txt extract with the session
    metadata, metrics and full event timeline, sealed with a SHA-256 hash so
    the analyzer can detect any tampering after generation.

PT: Produz um extrato .txt legível por humanos e por máquina, com os metadados
    da sessão, as métricas e a linha do tempo completa de eventos, selado com um
    hash SHA-256 para o analisador detectar qualquer adulteração posterior.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

SEP = "=" * 66
MARCA_HASH = "hash_sha256:"


def _linha_evento(ev: dict) -> str:
    detalhe = str(ev.get("detail", "")).replace("|", "/").strip()
    dados = json.dumps(ev.get("data", {}), ensure_ascii=False, separators=(",", ":"))
    return (f"{ev['t']} | {ev['clock']} | {ev['severity']} | "
            f"{ev['type']} | {detalhe} | {dados}")


def gerar(session) -> Path:
    ctx = session.contexto_maquina()
    eventos = session.eventos()
    L: list[str] = []
    L.append(SEP)
    L.append(" INPIOJUS ANALITIC UNIVERSITY")
    L.append(" EXTRATO DE FISCALIZAÇÃO DE PROVA / EXAM PROCTORING EXTRACT")
    L.append(f" {ctx['agente']} — por Joaquim Pedro de Morais Filho")
    L.append(SEP)
    L.append("")

    L.append("[SESSAO / SESSION]")
    L.append(f"session_id: {session.session_id}")
    L.append(f"aluno / student: {session.aluno}")
    L.append(f"matricula / id: {session.matricula}")
    L.append(f"url_prova / exam_url: {session.url}")
    L.append(f"inicio / start: {session.iniciada_em.strftime('%Y-%m-%d %H:%M:%S')}")
    L.append(f"fim / end: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    L.append(f"duracao_prevista_min / planned_minutes: {session.minutos:g}")
    L.append(f"janela_prova / exam_window: {session.baseline_window}")
    L.append("")

    L.append("[MAQUINA / MACHINE]")
    L.append(f"sistema / system: {ctx['sistema']}")
    L.append(f"maquina / host: {ctx['maquina']}")
    L.append(f"python: {ctx['python']}")
    L.append("")

    L.append("[CONSENTIMENTO / CONSENT]")
    L.append("consentido / consented: SIM / YES")
    L.append(f"registrado_em / recorded_at: {session.iniciada_em.strftime('%Y-%m-%d %H:%M:%S')}")
    L.append("termos_versao / terms_version: 1.0")
    L.append("")

    m = session.metrics
    L.append("[METRICAS / METRICS]")
    L.append(f"keystrokes: {m.get('keystrokes', 0)}")
    L.append(f"paste_events: {m.get('paste_events', 0)}")
    L.append(f"mouse_distance_px: {m.get('mouse_distance_px', 0)}")
    L.append(f"mouse_moves: {m.get('mouse_moves', 0)}")
    L.append(f"camera_active: {str(m.get('camera_active', False)).lower()}")
    L.append(f"camera_checks: {m.get('camera_checks', 0)}")
    L.append(f"camera_face_ok: {m.get('camera_face_ok', 0)}")
    L.append(f"total_eventos / total_events: {len(eventos)}")
    L.append("")

    L.append("[EVENTOS / EVENTS]")
    L.append("# t_seg | relogio | severidade | tipo | detalhe | dados_json")
    for ev in eventos:
        L.append(_linha_evento(ev))
    L.append("")

    corpo = "\n".join(L)
    h = hashlib.sha256(corpo.encode("utf-8")).hexdigest()
    corpo += "\n[INTEGRIDADE / INTEGRITY]\n"
    corpo += ("# O hash cobre todo o conteudo acima. Qualquer alteracao o invalida.\n"
              "# The hash covers everything above. Any change invalidates it.\n")
    corpo += f"{MARCA_HASH} {h}\n"

    caminho = session.dir / f"extrato_{session.session_id}.txt"
    caminho.write_text(corpo, encoding="utf-8")
    return caminho


# ----------------------------------------------------------------------
def ler(caminho: str | Path) -> dict:
    """Parse an extract file / lê e interpreta um arquivo de extrato."""
    texto = Path(caminho).read_text(encoding="utf-8")
    linhas = texto.splitlines()

    # Integrity check.
    hash_gravado = None
    corte = None
    for i, l in enumerate(linhas):
        if l.startswith(MARCA_HASH):
            hash_gravado = l.split(":", 1)[1].strip()
        if l.strip() == "[INTEGRIDADE / INTEGRITY]":
            corte = i
    integridade = None
    if hash_gravado is not None and corte is not None:
        corpo = "\n".join(linhas[:corte])
        # remove a trailing blank line kept before the section
        if corpo.endswith("\n"):
            corpo = corpo[:-1]
        recomputado = hashlib.sha256((corpo + "\n").encode("utf-8")).hexdigest()
        integridade = (recomputado == hash_gravado)

    sessao: dict = {}
    metricas: dict = {}
    eventos: list[dict] = []
    secao = None
    for l in linhas:
        s = l.strip()
        if s.startswith("[") and s.endswith("]"):
            secao = s
            continue
        if not s or s.startswith("#"):
            continue
        if secao == "[SESSAO / SESSION]" and ":" in l:
            k, v = l.split(":", 1)
            sessao[k.split(" / ")[0].strip()] = v.strip()
        elif secao == "[METRICAS / METRICS]" and ":" in l:
            k, v = l.split(":", 1)
            metricas[k.split(" / ")[0].strip()] = v.strip()
        elif secao == "[EVENTOS / EVENTS]" and "|" in l:
            partes = [p.strip() for p in l.split("|")]
            if len(partes) >= 6:
                try:
                    dados = json.loads(partes[5])
                except Exception:
                    dados = {}
                eventos.append({
                    "t": float(partes[0]) if partes[0].replace(".", "").isdigit() else 0.0,
                    "clock": partes[1],
                    "severity": partes[2],
                    "type": partes[3],
                    "detail": partes[4],
                    "data": dados,
                })

    return {
        "sessao": sessao,
        "metricas": metricas,
        "eventos": eventos,
        "integridade": integridade,
    }
