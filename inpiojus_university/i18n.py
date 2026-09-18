"""
Bilingual strings (Portuguese / English).
Textos bilíngues (Português / Inglês).

The language is chosen by --lang, the INPIOJUS_LANG environment variable,
or auto-detected from the operating system (default: pt).
"""

from __future__ import annotations

import locale
import os

STRINGS = {
    # ---- generic / genérico ----
    "app_name": {"pt": "InpioJus Analitic University", "en": "InpioJus Analitic University"},
    "author_line": {
        "pt": "por Joaquim Pedro de Morais Filho",
        "en": "by Joaquim Pedro de Morais Filho",
    },
    "tool_support": {
        "pt": "Ferramenta de apoio à integridade acadêmica — não emite veredito automático.",
        "en": "Academic-integrity support tool — it does not issue an automatic verdict.",
    },

    # ---- consent / consentimento ----
    "consent_title": {
        "pt": "TERMO DE CONSENTIMENTO E AVISO DE PRIVACIDADE",
        "en": "CONSENT FORM AND PRIVACY NOTICE",
    },
    "consent_body": {
        "pt": (
            "Ao iniciar, você autoriza que o InpioJus Analitic University\n"
            "monitore a sua prova online SOMENTE durante o tempo do exame:\n\n"
            "  • Câmera: registra APENAS o seu rosto, em intervalos, para\n"
            "    confirmar presença e detectar terceiros. Nada do ambiente\n"
            "    ao redor precisa ser filmado — mantenha só o rosto no quadro.\n"
            "  • Teclado: registra METADADOS (ritmo de digitação, colagens,\n"
            "    teclas de atalho), e não senhas ou textos fora da prova.\n"
            "  • Mouse: registra o padrão de movimentação e inatividade.\n"
            "  • Janela: verifica se apenas a aba/janela da prova está em foco.\n\n"
            "Os dados ficam no SEU computador, em um extrato local, e são\n"
            "entregues por você à instituição. A fiscalização encerra ao fim\n"
            "do tempo. Você pode cancelar a qualquer momento (a prova pode ser\n"
            "invalidada pela instituição, conforme o regulamento dela)."
        ),
        "en": (
            "By starting, you authorize InpioJus Analitic University to monitor\n"
            "your online exam ONLY during the exam window:\n\n"
            "  • Camera: records ONLY your face, at intervals, to confirm\n"
            "    presence and detect other people. The surroundings need not be\n"
            "    filmed — keep only your face in frame.\n"
            "  • Keyboard: records METADATA (typing rhythm, paste events,\n"
            "    shortcuts), not passwords or text outside the exam.\n"
            "  • Mouse: records movement and idle patterns.\n"
            "  • Window: checks that only the exam tab/window is focused.\n\n"
            "Data stays on YOUR computer, in a local extract, and is handed by\n"
            "you to the institution. Monitoring ends when time is up. You may\n"
            "cancel at any moment (the institution may void the exam under its\n"
            "own rules)."
        ),
    },
    "consent_prompt": {
        "pt": "Digite ACEITO para consentir e iniciar, ou qualquer outra coisa para cancelar: ",
        "en": "Type ACCEPT to consent and start, or anything else to cancel: ",
    },
    "consent_word": {"pt": "ACEITO", "en": "ACCEPT"},
    "consent_declined": {
        "pt": "Consentimento não concedido. A fiscalização não foi iniciada.",
        "en": "Consent not granted. Monitoring was not started.",
    },

    # ---- session / sessão ----
    "ask_student": {"pt": "Nome do aluno: ", "en": "Student name: "},
    "ask_id": {"pt": "Matrícula/ID: ", "en": "Enrollment/ID: "},
    "ask_exam_url": {"pt": "URL da prova: ", "en": "Exam URL: "},
    "ask_minutes": {"pt": "Duração da prova (minutos): ", "en": "Exam duration (minutes): "},
    "session_started": {
        "pt": "Fiscalização iniciada. Mantenha apenas a aba da prova aberta.",
        "en": "Monitoring started. Keep only the exam tab open.",
    },
    "recording_indicator": {
        "pt": "● GRAVANDO — prova sob fiscalização",
        "en": "● RECORDING — exam under monitoring",
    },
    "time_left": {"pt": "Tempo restante", "en": "Time left"},
    "session_finished": {
        "pt": "Prova encerrada. Gerando extrato...",
        "en": "Exam finished. Generating extract...",
    },
    "extract_saved": {"pt": "Extrato salvo em:", "en": "Extract saved to:"},
    "send_to_faculty": {
        "pt": "Envie este arquivo à sua instituição, conforme as instruções dela.",
        "en": "Send this file to your institution, following their instructions.",
    },
    "press_finish": {
        "pt": "Pressione Ctrl+C para encerrar a prova antes do tempo.",
        "en": "Press Ctrl+C to end the exam before time is up.",
    },

    # ---- monitors / monitores ----
    "cam_unavailable": {
        "pt": "[câmera] indisponível — monitoramento de vídeo desativado nesta sessão.",
        "en": "[camera] unavailable — video monitoring disabled for this session.",
    },
    "cam_no_face": {"pt": "rosto ausente do quadro", "en": "face absent from frame"},
    "cam_multi_face": {"pt": "mais de um rosto detectado", "en": "more than one face detected"},
    "kbd_unavailable": {
        "pt": "[teclado] captura indisponível (instale 'pynput').",
        "en": "[keyboard] capture unavailable (install 'pynput').",
    },
    "focus_lost": {"pt": "foco saiu da janela da prova", "en": "focus left the exam window"},

    # ---- analyzer / analisador ----
    "an_title": {"pt": "ANÁLISE DE INTEGRIDADE DA PROVA", "en": "EXAM INTEGRITY ANALYSIS"},
    "an_risk": {"pt": "RISCO DE FRAUDE", "en": "FRAUD RISK"},
    "an_low": {"pt": "BAIXO", "en": "LOW"},
    "an_medium": {"pt": "MÉDIO", "en": "MEDIUM"},
    "an_high": {"pt": "ALTO", "en": "HIGH"},
    "an_score": {"pt": "Pontuação", "en": "Score"},
    "an_findings": {"pt": "INDÍCIOS ENCONTRADOS", "en": "FINDINGS"},
    "an_none": {"pt": "Nenhum indício relevante de fraude foi encontrado.",
                "en": "No relevant signs of fraud were found."},
    "an_conclusion": {"pt": "CONCLUSÃO", "en": "CONCLUSION"},
    "an_disclaimer": {
        "pt": ("Este relatório é um indicador de risco para APOIAR a revisão humana. "
               "Não constitui prova nem decisão automática. A instituição deve analisar "
               "as evidências e ouvir o aluno antes de qualquer medida."),
        "en": ("This report is a risk indicator to SUPPORT human review. It is not proof "
               "nor an automatic decision. The institution must review the evidence and "
               "hear the student before any measure is taken."),
    },
    "an_invalid": {"pt": "Extrato inválido ou ilegível:", "en": "Invalid or unreadable extract:"},
    "an_integrity_ok": {"pt": "Integridade do extrato: OK (hash confere).",
                        "en": "Extract integrity: OK (hash matches)."},
    "an_integrity_fail": {
        "pt": "ATENÇÃO: o extrato foi ALTERADO após a geração (hash não confere).",
        "en": "WARNING: the extract was MODIFIED after generation (hash mismatch).",
    },
}


def escolher_idioma(preferido: str | None = None) -> str:
    """Resolve the active language / resolve o idioma ativo."""
    if preferido in ("pt", "en"):
        return preferido
    env = os.environ.get("INPIOJUS_LANG", "").lower()[:2]
    if env in ("pt", "en"):
        return env
    try:
        loc = (locale.getdefaultlocale()[0] or "").lower()
    except Exception:
        loc = ""
    return "en" if loc.startswith("en") else "pt"


class T:
    """Tiny translator / tradutor mínimo."""

    def __init__(self, lang: str):
        self.lang = lang if lang in ("pt", "en") else "pt"

    def __call__(self, chave: str) -> str:
        entrada = STRINGS.get(chave)
        if not entrada:
            return chave
        return entrada.get(self.lang, entrada.get("pt", chave))
