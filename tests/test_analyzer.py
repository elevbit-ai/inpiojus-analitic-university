"""
Tests / Testes — analyzer, extract round-trip and tamper detection.
Execute:  python -m unittest discover tests
"""

import tempfile
import unittest
from pathlib import Path

from inpiojus_university import analyzer, extract
from inpiojus_university.demo import gerar_extrato_demo


class TesteExtrato(unittest.TestCase):
    def _gerar(self, cenario):
        d = Path(tempfile.mkdtemp())
        return gerar_extrato_demo(destino=d / f"{cenario}.txt", cenario=cenario)

    def test_round_trip_e_integridade(self):
        p = self._gerar("suspeito")
        dados = extract.ler(p)
        self.assertTrue(dados["integridade"])
        self.assertEqual(dados["sessao"]["matricula"], "2026-000123")
        self.assertTrue(any(e["type"] == "paste" for e in dados["eventos"]))

    def test_deteccao_de_adulteracao(self):
        p = self._gerar("grave")
        texto = p.read_text(encoding="utf-8").replace("512 caracteres", "999 caracteres")
        p.write_text(texto, encoding="utf-8")
        dados = extract.ler(p)
        self.assertFalse(dados["integridade"])


class TesteAnalisador(unittest.TestCase):
    def _analise(self, cenario):
        d = Path(tempfile.mkdtemp())
        p = gerar_extrato_demo(destino=d / f"{cenario}.txt", cenario=cenario)
        return analyzer.analisar(str(p))

    def test_cenario_limpo_e_baixo(self):
        r = self._analise("limpo")
        self.assertEqual(r["nivel"], "low")
        self.assertEqual(r["achados"], [])

    def test_cenario_grave_e_alto(self):
        r = self._analise("grave")
        self.assertEqual(r["nivel"], "high")
        categorias = {a["categoria"] for a in r["achados"]}
        self.assertIn("colagem/paste", categorias)
        self.assertIn("camera", categorias)
        self.assertIn("padrão/pattern", categorias)  # correlação temporal

    def test_correlacao_saida_entao_colagem(self):
        r = self._analise("grave")
        padroes = [a for a in r["achados"] if a["categoria"] == "padrão/pattern"]
        self.assertTrue(padroes, "deveria detectar o padrão saída->colagem")

    def test_adulteracao_forca_alto_risco(self):
        d = Path(tempfile.mkdtemp())
        p = gerar_extrato_demo(destino=d / "g.txt", cenario="grave")
        texto = p.read_text(encoding="utf-8").replace("Print Screen", "Alterado")
        p.write_text(texto, encoding="utf-8")
        r = analyzer.analisar(str(p))
        self.assertEqual(r["nivel"], "high")
        self.assertFalse(r["integridade"])

    def test_relatorio_bilingue(self):
        r = self._analise("suspeito")
        self.assertIn("RISCO DE FRAUDE", analyzer.relatorio(r, "pt"))
        self.assertIn("FRAUD RISK", analyzer.relatorio(r, "en"))
        self.assertIn("Joaquim Pedro de Morais Filho", analyzer.relatorio(r, "pt"))


if __name__ == "__main__":
    unittest.main()
