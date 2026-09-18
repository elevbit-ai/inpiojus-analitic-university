"""
Command-line interface (PowerShell / CMD).
Interface de linha de comando (PowerShell / CMD).

    inpiojus-university fiscalizar        inicia a fiscalização de uma prova
    inpiojus-university analisar EXT.txt  analisa um extrato (agente University)
    inpiojus-university demo-extrato      gera um extrato de exemplo p/ teste

Author / Autor: Joaquim Pedro de Morais Filho <j360074@hotmail.com>
"""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, analyzer
from .consent import obter_consentimento
from .i18n import T, escolher_idioma
from .proctor import ProctorSession


def _pergunta(t, chave: str, valor: str | None) -> str:
    if valor:
        return valor
    try:
        return input("  " + t(chave)).strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit("\n" + t("consent_declined"))


def cmd_fiscalizar(args, lang):
    t = T(lang)
    print("╔" + "═" * 58 + "╗")
    print("║  " + f"{t('app_name')}".ljust(56) + "║")
    print("║  " + f"{t('author_line')}".ljust(56) + "║")
    print("╚" + "═" * 58 + "╝")

    aluno = _pergunta(t, "ask_student", args.aluno)
    matricula = _pergunta(t, "ask_id", args.matricula)
    url = _pergunta(t, "ask_exam_url", args.url)
    minutos = args.minutos or _pergunta(t, "ask_minutes", None)
    try:
        minutos = float(minutos)
    except (TypeError, ValueError):
        sys.exit("  minutos inválidos / invalid minutes")

    if not obter_consentimento(lang):
        sys.exit(0)

    sessao = ProctorSession(aluno=aluno, matricula=matricula, url=url,
                            minutos=minutos, lang=lang)
    sessao.executar()


def cmd_analisar(args, lang):
    t = T(lang)
    try:
        resultado = analyzer.analisar(args.extrato)
    except FileNotFoundError:
        sys.exit(f"  {t('an_invalid')} {args.extrato}")
    except Exception as e:
        sys.exit(f"  {t('an_invalid')} {e}")

    if args.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return
    print(analyzer.relatorio(resultado, lang))


def cmd_demo(args, lang):
    """Generate a synthetic (suspicious) extract for testing the analyzer."""
    from .demo import gerar_extrato_demo
    caminho = gerar_extrato_demo(destino=args.saida, cenario=args.cenario, lang=lang)
    print(f"  demo -> {caminho}")


def construir_parser():
    p = argparse.ArgumentParser(
        prog="inpiojus-university",
        description=("InpioJus Analitic University — proctoring de provas online + "
                     "análise de integridade. Por Joaquim Pedro de Morais Filho."),
    )
    p.add_argument("--versao", "--version", action="version",
                   version=f"InpioJus Analitic University v{__version__}")
    p.add_argument("--lang", choices=["pt", "en"], help="idioma / language")
    sub = p.add_subparsers(dest="comando", required=True)

    f = sub.add_parser("fiscalizar", aliases=["proctor"],
                       help="inicia a fiscalização de uma prova / start proctoring")
    f.add_argument("--aluno", "--student")
    f.add_argument("--matricula", "--id")
    f.add_argument("--url")
    f.add_argument("--minutos", "--minutes", type=float)
    f.set_defaults(func=cmd_fiscalizar)

    a = sub.add_parser("analisar", aliases=["analyze"],
                       help="analisa um extrato de prova / analyze an exam extract")
    a.add_argument("extrato", help="arquivo .txt do extrato / extract .txt file")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_analisar)

    d = sub.add_parser("demo-extrato", aliases=["demo"],
                       help="gera um extrato de exemplo / generate a sample extract")
    d.add_argument("--saida", "--out", help="caminho de saída / output path")
    d.add_argument("--cenario", "--scenario",
                   choices=["limpo", "suspeito", "grave"], default="suspeito")
    d.set_defaults(func=cmd_demo)

    return p


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    parser = construir_parser()
    args = parser.parse_args(argv)
    lang = escolher_idioma(getattr(args, "lang", None))
    args.func(args, lang)


if __name__ == "__main__":
    main()
