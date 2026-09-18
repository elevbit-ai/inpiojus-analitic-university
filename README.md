<div align="center">

# 🎓 InpioJus Analitic University

**Proctoring inteligente de provas online + análise de integridade.**
**Intelligent online-exam proctoring + integrity analysis.**

Consentido · Transparente · 100% local · Bilíngue (PT/EN)
Consent-based · Transparent · 100% local · Bilingual (PT/EN)

por / by **Joaquim Pedro de Morais Filho**

[Site](https://elevbit-ai.github.io/inpiojus-analitic-university/) ·
[Instalação / Install](#-instalação--installation) ·
[Como funciona / How it works](#-como-funciona--how-it-works) ·
[Privacidade / Privacy](PRIVACY.md)

</div>

---

## PT — Visão geral

Muitas provas hoje são feitas em casa, e a tentação de **colar ou usar
inteligência artificial** compromete a lisura da avaliação e a reputação dos
diplomas. O **InpioJus Analitic University** ajuda a instituição a preservar a
integridade das provas online com **dois agentes** que trabalham juntos:

1. **Agente de Fiscalização** (roda no computador do aluno, com **consentimento**):
   ao logar na prova, o aluno informa a **URL da prova** ao agente, aceita o termo
   e a fiscalização roda **somente durante o tempo do exame**. Ele acompanha:
   - **Câmera** — confirma a presença e detecta terceiros, filmando **apenas o rosto**;
   - **Teclado** — registra **ritmo, colagens (Ctrl+V) e atalhos** (sem senhas nem texto);
   - **Mouse** — padrão de movimentação e inatividade;
   - **Janela** — verifica que **apenas a aba da prova** está em foco.

   Ao final, gera um **extrato `.txt` assinado** (com hash anti-adulteração) que o
   aluno **envia para a faculdade**.

2. **Agente University (Analisador)** (roda na instituição): **lê o extrato** e,
   de forma inteligente, estima o **risco de fraude** — inclusive correlacionando
   padrões como *"saiu da prova e logo colou uma resposta"*, típico de consulta a
   IA ou a terceiros. Produz um **indicador de risco (BAIXO/MÉDIO/ALTO)** com as
   evidências, para **apoiar a revisão humana** — nunca um veredito automático.

## EN — Overview

Many exams today are taken at home, and the temptation to **cheat or use AI**
undermines assessment and the value of degrees. **InpioJus Analitic University**
helps institutions preserve online-exam integrity with **two cooperating agents**:

1. **Proctoring Agent** (runs on the student's computer, **with consent**): after
   logging into the exam, the student gives the agent the **exam URL**, accepts the
   terms, and monitoring runs **only during the exam window**, tracking the
   **camera (face only), keyboard metadata, mouse, and the active window**. It then
   produces a **signed `.txt` extract** (tamper-proof hash) that the student
   **sends to the university**.

2. **University Agent (Analyzer)** (runs at the institution): **reads the extract**
   and intelligently estimates the **fraud risk**, correlating patterns such as
   *"left the exam then pasted an answer"* — typical of consulting AI or third
   parties. It outputs a **risk indicator (LOW/MEDIUM/HIGH)** with evidence, to
   **support human review** — never an automatic verdict.

> ⚖️ **Importância / Why it matters:** avaliações íntegras protegem o mérito dos
> alunos honestos e a credibilidade da instituição. Integrity protects honest
> students' merit and the institution's credibility.

## 🔒 Privacidade / Privacy

- **Consentimento obrigatório** antes de iniciar / **mandatory consent** first.
- **Câmera só do rosto** / **face-only camera**; recortes no rosto, nunca o ambiente.
- **Sem plaintext, sem senhas** / **no plaintext, no passwords** — apenas metadados.
- **Dados locais**, entregues pelo aluno / **local data**, handed over by the student.
- **Sem decisão automática** / **no automated decision** (LGPD art. 20 · GDPR).

Detalhes completos em / full details in **[PRIVACY.md](PRIVACY.md)**.

## 🚀 Instalação / Installation

PowerShell (uma linha / one line — requer Python 3.9+):

```powershell
irm https://elevbit-ai.github.io/inpiojus-analitic-university/install.ps1 | iex
```

Manual (Windows / Linux / macOS):

```powershell
git clone https://github.com/elevbit-ai/inpiojus-analitic-university.git
cd inpiojus-analitic-university
pip install -r requirements.txt
python -m inpiojus_university --versao
```

## 🖥️ Uso / Usage — PowerShell & CMD

**Aluno / Student** (fiscalização da prova / exam proctoring):

```powershell
inpiojus-university fiscalizar
# ou com dados prontos / or with arguments:
inpiojus-university fiscalizar --aluno "Ana Souza" --matricula 2026-000123 --url "https://ava.faculdade.edu/prova/8842" --minutos 60
```

**Instituição / Institution** (análise / analysis):

```powershell
inpiojus-university analisar extrato_da_prova.txt
inpiojus-university --lang en analisar exam_extract.txt
inpiojus-university analisar extrato.txt --json
```

**Idioma / Language:** `--lang pt` ou `--lang en` (ou variável `INPIOJUS_LANG`).

## 🧪 Exemplos / Examples

O repositório inclui extratos de exemplo em [`examples/`](examples/):

```powershell
inpiojus-university analisar examples\extrato_exemplo.txt        # risco alto / high risk
inpiojus-university analisar examples\extrato_exemplo_limpo.txt  # risco baixo / low risk
```

Gere seus próprios extratos de teste / generate your own test extracts:

```powershell
inpiojus-university demo-extrato --cenario grave --saida teste.txt
```

## 🧠 Como funciona / How it works

| Sinal / Signal | Peso / Weight | O que revela / What it reveals |
|---|---|---|
| Colagem grande (Ctrl+V) / large paste | alto/high | resposta trazida de fora (IA, notas) / answer from outside |
| Saída → colagem / leave → paste | alto/high | consulta a fonte externa / consulting an external source |
| Rajada de digitação / typing burst | alto/high | auto-digitador / auto-typer |
| Troca de aba / tab switch | médio-alto | não manteve só a prova / did not keep only the exam |
| 2+ rostos / 2+ faces | alto/high | terceiro presente / third person present |
| Rosto ausente / face absent | médio/medium | saiu do enquadramento / left the frame |
| Hash inválido / hash mismatch | crítico/critical | extrato adulterado / extract tampered |

## 🧾 Testes / Tests

```powershell
python -m unittest discover tests
```

## 📜 Autoria e licença / Authorship & license

**Joaquim Pedro de Morais Filho** · 📧 j360074@hotmail.com · 📱 +55 85 99125-3990
Licença / License [MIT](LICENSE) · [AUTHORS.md](AUTHORS.md)

> ⚠️ Ferramenta de **apoio** à integridade acadêmica. O resultado é um indicador
> de risco para revisão humana, sujeito ao contraditório do aluno — **não** é
> prova nem decisão automática. A **support** tool: the output is a risk
> indicator for human review, subject to the student's right to respond — **not**
> proof nor an automatic decision.
