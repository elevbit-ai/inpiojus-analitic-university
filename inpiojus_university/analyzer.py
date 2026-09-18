"""
Integrity analyzer — the "University" agent.
Analisador de integridade — o agente "University".

EN: Reads a proctoring extract and produces an explainable fraud-risk report.
    It weighs individual signals (large pastes, typing bursts, tab switches,
    extra faces, absences) AND temporal correlations that reveal cheating
    workflows — e.g. leaving the exam window and then pasting a long answer, or
    switching away and returning with a machine-like burst. The output is a risk
    indicator to SUPPORT human review, never an automatic verdict.

PT: Lê um extrato de fiscalização e produz um relatório explicável de risco de
    fraude. Pondera sinais individuais (colagens grandes, rajadas de digitação,
    trocas de aba, rostos extras, ausências) E correlações temporais que revelam
    o "modo de operação" da cola — por exemplo, sair da janela da prova e então
    colar uma resposta longa, ou trocar de janela e voltar com uma rajada de
    digitação típica de máquina. A saída é um indicador de risco para APOIAR a
    revisão humana, nunca um veredito automático.
"""

from __future__ import annotations

from . import extract as extract_mod
from .i18n import T

# Individual signal weights (points) / pesos dos sinais individuais.
PESOS = {
    "multi_face": 40,
    "typing_burst": 25,
    "alt_tab": 15,
    "print_screen": 8,
    "win_key": 6,
    "mouse_idle": 5,
    "copy": 2,
    "cut": 2,
}

LIMIAR_MEDIO = 25
LIMIAR_ALTO = 70
JANELA_CORR = 25.0   # seconds for temporal correlation / segundos p/ correlação


def _peso_paste(n: int) -> int:
    if n >= 200:
        return 35
    if n >= 80:
        return 20
    return 8


def _peso_focus(ev: dict) -> int:
    return 20 if ev.get("severity") == "high" else 10


def _peso_absent() -> int:
    return 18


def analisar(caminho: str) -> dict:
    dados = extract_mod.ler(caminho)
    eventos = dados["eventos"]
    metricas = dados["metricas"]
    integridade = dados["integridade"]

    achados: list[dict] = []
    score = 0

    def _mm(seg: float) -> str:
        m, s = divmod(int(seg), 60)
        return f"{m:02d}:{s:02d}"

    # ---- integrity gate / porta de integridade ----
    if integridade is False:
        return {
            "sessao": dados["sessao"],
            "metricas": metricas,
            "integridade": False,
            "score": 100,
            "nivel": "high",
            "achados": [{
                "peso": 100, "categoria": "integridade/integrity",
                "resumo_pt": "O extrato foi ALTERADO após a geração (hash não confere). "
                             "O conteúdo não é confiável.",
                "resumo_en": "The extract was MODIFIED after generation (hash mismatch). "
                             "The content cannot be trusted.",
                "evidencia": [],
            }],
        }

    # ---- individual signals / sinais individuais ----
    contagem: dict[str, int] = {}
    paste_total_chars = 0
    for ev in eventos:
        tipo = ev["type"]
        contagem[tipo] = contagem.get(tipo, 0) + 1
        if tipo == "paste":
            n = int(ev["data"].get("clipboard_len", 0))
            paste_total_chars += n
            score += _peso_paste(n)
        elif tipo == "focus_lost":
            score += _peso_focus(ev)
        elif tipo == "face_absent":
            score += _peso_absent()
        else:
            score += PESOS.get(tipo, 0)

    def _evid(tipo):
        return [f"{_mm(e['t'])} ({e['clock']}) — {e['detail']}"
                for e in eventos if e["type"] == tipo]

    if contagem.get("multi_face"):
        achados.append({
            "peso": 40 * contagem["multi_face"], "categoria": "camera",
            "resumo_pt": f"Mais de um rosto detectado pela câmera "
                         f"({contagem['multi_face']}x) — possível presença de terceiro.",
            "resumo_en": f"More than one face detected by the camera "
                         f"({contagem['multi_face']}x) — a third person may be present.",
            "evidencia": _evid("multi_face")[:6],
        })
    if contagem.get("paste"):
        achados.append({
            "peso": sum(_peso_paste(int(e['data'].get('clipboard_len', 0)))
                        for e in eventos if e["type"] == "paste"),
            "categoria": "colagem/paste",
            "resumo_pt": f"{contagem['paste']} colagem(ns) (Ctrl+V), somando "
                         f"{paste_total_chars} caracteres — indício de resposta trazida "
                         f"de fora (ex.: IA ou anotações).",
            "resumo_en": f"{contagem['paste']} paste(s) (Ctrl+V), totaling "
                         f"{paste_total_chars} characters — a sign of answers brought from "
                         f"outside (e.g. AI or notes).",
            "evidencia": _evid("paste")[:6],
        })
    if contagem.get("typing_burst"):
        achados.append({
            "peso": 25 * contagem["typing_burst"], "categoria": "digitação/typing",
            "resumo_pt": f"Digitação em rajada ({contagem['typing_burst']}x) com "
                         f"velocidade típica de máquina/auto-digitador.",
            "resumo_en": f"Machine-like typing bursts ({contagem['typing_burst']}x), "
                         f"consistent with an auto-typer.",
            "evidencia": _evid("typing_burst")[:6],
        })
    trocas = contagem.get("focus_lost", 0) + contagem.get("alt_tab", 0)
    if trocas:
        achados.append({
            "peso": sum(_peso_focus(e) for e in eventos if e["type"] == "focus_lost")
                    + 15 * contagem.get("alt_tab", 0),
            "categoria": "foco/focus",
            "resumo_pt": f"O foco saiu da janela da prova {trocas}x (troca de aba/app), "
                         f"quando a regra exige manter apenas a prova aberta.",
            "resumo_en": f"Focus left the exam window {trocas}x (tab/app switch), while the "
                         f"rule requires keeping only the exam open.",
            "evidencia": (_evid("focus_lost") + _evid("alt_tab"))[:6],
        })
    if contagem.get("face_absent"):
        achados.append({
            "peso": 18 * contagem["face_absent"], "categoria": "camera",
            "resumo_pt": f"Rosto ausente do quadro {contagem['face_absent']}x — o aluno "
                         f"pode ter saído do enquadramento.",
            "resumo_en": f"Face absent from frame {contagem['face_absent']}x — the student "
                         f"may have left the frame.",
            "evidencia": _evid("face_absent")[:6],
        })
    if contagem.get("print_screen"):
        achados.append({
            "peso": 8 * contagem["print_screen"], "categoria": "captura/screenshot",
            "resumo_pt": f"Print Screen acionado {contagem['print_screen']}x.",
            "resumo_en": f"Print Screen used {contagem['print_screen']}x.",
            "evidencia": _evid("print_screen")[:4],
        })

    # ---- temporal correlations / correlações temporais ----
    saidas = [e for e in eventos if e["type"] in ("focus_lost", "alt_tab",
                                                  "face_absent", "mouse_idle")]
    pastes = [e for e in eventos if e["type"] == "paste"]
    bursts = [e for e in eventos if e["type"] == "typing_burst"]

    corr_paste = []
    for p in pastes:
        for s in saidas:
            if 0 <= (p["t"] - s["t"]) <= JANELA_CORR:
                corr_paste.append((s, p))
                break
    if corr_paste:
        score += 25 * len(corr_paste)
        achados.append({
            "peso": 25 * len(corr_paste), "categoria": "padrão/pattern",
            "resumo_pt": f"Padrão de cola detectado {len(corr_paste)}x: o aluno afastou-se "
                         f"da prova (troca de janela, ausência ou inatividade) e, logo em "
                         f"seguida, COLOU uma resposta — sequência típica de consulta a "
                         f"fonte externa (IA, site, anotações).",
            "resumo_en": f"Cheating pattern detected {len(corr_paste)}x: the student moved "
                         f"away from the exam (window switch, absence or idle) and, right "
                         f"after, PASTED an answer — a sequence typical of consulting an "
                         f"external source (AI, website, notes).",
            "evidencia": [f"{_mm(s['t'])} {s['type']} -> {_mm(p['t'])} paste "
                          f"({p['data'].get('clipboard_len', '?')} chars)"
                          for s, p in corr_paste[:6]],
        })

    corr_burst = []
    for b in bursts:
        for s in saidas:
            if 0 <= (b["t"] - s["t"]) <= 15.0:
                corr_burst.append((s, b))
                break
    if corr_burst:
        score += 20 * len(corr_burst)
        achados.append({
            "peso": 20 * len(corr_burst), "categoria": "padrão/pattern",
            "resumo_pt": f"O aluno trocou de janela e retornou digitando em rajada "
                         f"{len(corr_burst)}x — consistente com copiar de fora e transcrever.",
            "resumo_en": f"The student switched windows and returned typing in a burst "
                         f"{len(corr_burst)}x — consistent with copying from elsewhere.",
            "evidencia": [f"{_mm(s['t'])} {s['type']} -> {_mm(b['t'])} burst"
                          for s, b in corr_burst[:6]],
        })

    # ---- paste-dominant answer / resposta majoritariamente colada ----
    try:
        teclas = int(metricas.get("keystrokes", 0))
    except ValueError:
        teclas = 0
    if paste_total_chars > 400 and paste_total_chars > max(teclas, 1) * 2:
        score += 20
        achados.append({
            "peso": 20, "categoria": "colagem/paste",
            "resumo_pt": f"O volume colado ({paste_total_chars} caracteres) supera em muito "
                         f"o que foi digitado ({teclas} teclas): grande parte da resposta "
                         f"não foi escrita pelo aluno no momento da prova.",
            "resumo_en": f"Pasted volume ({paste_total_chars} chars) far exceeds what was "
                         f"typed ({teclas} keys): much of the answer was not written by the "
                         f"student during the exam.",
            "evidencia": [],
        })

    # ---- camera limitation caveat / ressalva de câmera ----
    caveats = []
    if str(metricas.get("camera_active", "false")).lower() != "true":
        caveats.append({
            "pt": "A câmera não esteve ativa nesta sessão — a presença e a ausência de "
                  "terceiros não puderam ser verificadas por vídeo.",
            "en": "The camera was not active in this session — presence and the absence of "
                  "third parties could not be verified by video.",
        })

    nivel = "low"
    if score > LIMIAR_ALTO:
        nivel = "high"
    elif score >= LIMIAR_MEDIO:
        nivel = "medium"

    achados.sort(key=lambda a: a["peso"], reverse=True)
    return {
        "sessao": dados["sessao"],
        "metricas": metricas,
        "integridade": integridade,
        "score": score,
        "nivel": nivel,
        "achados": achados,
        "caveats": caveats,
    }


# ----------------------------------------------------------------------
def relatorio(resultado: dict, lang: str = "pt") -> str:
    t = T(lang)
    sep = "─" * 64
    L: list[str] = []
    L.append("╔" + "═" * 62 + "╗")
    L.append("║  " + t("app_name").ljust(60) + "║")
    L.append("║  " + t("an_title").ljust(60) + "║")
    L.append("╚" + "═" * 62 + "╝")

    s = resultado["sessao"]
    L.append("")
    L.append(f"  {'Aluno / Student':<22}: {s.get('aluno', '-')}")
    L.append(f"  {'Matrícula / ID':<22}: {s.get('matricula', '-')}")
    L.append(f"  {'URL da prova / Exam':<22}: {s.get('url_prova', '-')}")
    L.append(f"  {'Início / Start':<22}: {s.get('inicio', '-')}")

    if resultado.get("integridade") is True:
        L.append("  " + t("an_integrity_ok"))
    elif resultado.get("integridade") is False:
        L.append("  " + t("an_integrity_fail"))

    nivel = resultado["nivel"]
    rotulo = {"low": t("an_low"), "medium": t("an_medium"), "high": t("an_high")}[nivel]
    barra = {"low": "▂▁▁", "medium": "▂▅▁", "high": "▂▅█"}[nivel]
    L.append("")
    L.append(f"\n  {t('an_risk')}: {barra}  {rotulo}   "
             f"({t('an_score')}: {resultado['score']})")
    L.append(sep)

    L.append("\n  " + t("an_findings"))
    L.append(sep)
    if not resultado["achados"]:
        L.append("  " + t("an_none"))
    for a in resultado["achados"]:
        resumo = a["resumo_pt"] if lang == "pt" else a["resumo_en"]
        L.append(f"  ▸ [+{a['peso']}] {resumo}")
        for ev in a.get("evidencia", []):
            L.append(f"        · {ev}")

    for c in resultado.get("caveats", []):
        L.append(f"\n  ⚠ {c[lang]}")

    L.append("\n  " + t("an_conclusion"))
    L.append(sep)
    concl = {
        "low": {"pt": "Baixo risco: os sinais coletados não indicam fraude relevante. "
                      "Recomenda-se apenas o arquivamento do extrato.",
                "en": "Low risk: the collected signals do not indicate relevant fraud. "
                      "Archiving the extract is recommended."},
        "medium": {"pt": "Risco médio: há sinais que merecem revisão humana. Recomenda-se "
                         "analisar as evidências e, se necessário, ouvir o aluno.",
                   "en": "Medium risk: there are signals that warrant human review. Review "
                         "the evidence and, if needed, hear the student."},
        "high": {"pt": "Alto risco: múltiplos sinais consistentes com uso de fontes externas "
                       "(como IA) ou auxílio de terceiros. Encaminhe para revisão formal, "
                       "com contraditório do aluno.",
                 "en": "High risk: multiple signals consistent with external sources (such "
                       "as AI) or third-party help. Refer for formal review, granting the "
                       "student the right to respond."},
    }[nivel][lang]
    L.append("  " + concl)

    L.append("\n  " + t("an_disclaimer"))
    L.append("\n" + sep)
    L.append("  " + t("app_name") + " · " + t("author_line"))
    L.append(sep)
    return "\n".join(L)
