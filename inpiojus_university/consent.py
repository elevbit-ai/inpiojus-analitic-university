"""
Informed consent gate.
Porta de consentimento informado.

EN: Monitoring MUST NOT start without explicit, informed consent. This module
    shows the privacy notice and requires the student to type the consent word.

PT: A fiscalização NÃO PODE começar sem consentimento explícito e informado.
    Este módulo mostra o aviso de privacidade e exige que o aluno digite a
    palavra de consentimento.
"""

from __future__ import annotations

from .i18n import T


def obter_consentimento(lang: str = "pt", entrada=input) -> bool:
    t = T(lang)
    print("\n" + "═" * 66)
    print("  " + t("consent_title"))
    print("═" * 66)
    print(t("consent_body"))
    print("\n  " + t("tool_support"))
    print("─" * 66)
    try:
        resposta = entrada("  " + t("consent_prompt")).strip().upper()
    except (EOFError, KeyboardInterrupt):
        print("\n  " + t("consent_declined"))
        return False
    if resposta == t("consent_word").upper():
        return True
    print("  " + t("consent_declined"))
    return False
