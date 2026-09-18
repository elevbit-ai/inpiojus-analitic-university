# Privacidade e Consentimento / Privacy and Consent

> **PT:** A fiscalização de provas envolve dados pessoais e biométricos. Este
> documento explica o que o InpioJus Analitic University coleta, por quê, e como
> ele foi projetado para respeitar a LGPD (Lei 13.709/2018) e o GDPR.
>
> **EN:** Exam proctoring involves personal and biometric data. This document
> explains what InpioJus Analitic University collects, why, and how it is
> designed to respect Brazil's LGPD (Law 13.709/2018) and the GDPR.

## Princípios / Principles

1. **Consentimento primeiro / Consent first.**
   PT: A fiscalização **não inicia** sem o aluno digitar o termo de consentimento.
   EN: Monitoring **does not start** unless the student types the consent term.

2. **Transparência / Transparency.**
   PT: Um indicador "● GRAVANDO" fica visível o tempo todo. Nada é oculto.
   EN: A "● RECORDING" indicator is visible at all times. Nothing is hidden.

3. **Tempo limitado / Time-bounded.**
   PT: A coleta ocorre **somente durante o tempo da prova** e encerra ao fim.
   EN: Collection happens **only during the exam window** and ends afterwards.

4. **Minimização / Data minimization.**
   - PT: Câmera → **apenas o rosto** (miniaturas recortadas no rosto, nunca o ambiente).
     EN: Camera → **face only** (thumbnails cropped to the face, never the room).
   - PT: Teclado → **metadados** (ritmo, colagens, atalhos) e o **comprimento** do
     texto colado; **nunca** o conteúdo digitado, senhas ou textos fora da prova.
     EN: Keyboard → **metadata** (rhythm, pastes, shortcuts) and the **length** of
     pasted text; **never** the typed content, passwords, or text outside the exam.
   - PT: Mouse → padrão de movimentação e inatividade.
     EN: Mouse → movement and idle patterns.

5. **Dados locais / Local data.**
   PT: Tudo é gravado no computador do aluno, em `~/.inpiojus_university/`. O
   extrato é **entregue pelo próprio aluno** à instituição. O software não envia
   dados para servidores.
   EN: Everything is stored on the student's computer, in
   `~/.inpiojus_university/`. The extract is **handed by the student** to the
   institution. The software does not upload data to any server.

6. **Sem decisão automática / No automated decision.**
   PT: O analisador produz um **indicador de risco** para **apoiar a revisão
   humana**. Ele **não reprova** ninguém. A instituição deve analisar as
   evidências e garantir o **contraditório** ao aluno (LGPD, art. 20).
   EN: The analyzer produces a **risk indicator** to **support human review**. It
   **fails no one**. The institution must review the evidence and grant the
   student the **right to respond** (LGPD, art. 20).

## Direitos do titular / Data-subject rights

PT: O aluno pode inspecionar o extrato (é um `.txt` legível), pedir cópia ou
solicitar a exclusão dos dados locais apagando a pasta `~/.inpiojus_university/`.
Como não há envio a servidores, o aluno mantém controle direto sobre os dados.

EN: The student may inspect the extract (a readable `.txt`), request a copy, or
delete the local data by removing the `~/.inpiojus_university/` folder. Because
nothing is uploaded, the student keeps direct control over the data.

## Responsabilidade da instituição / Institution's responsibility

PT: Cabe à instituição informar previamente o uso da fiscalização, obter base
legal adequada, tratar o extrato com segurança e usá-lo apenas para a finalidade
de integridade da prova.

EN: The institution must inform students in advance, establish a proper legal
basis, secure the extract, and use it solely for exam-integrity purposes.

---
InpioJus Analitic University · Joaquim Pedro de Morais Filho · j360074@hotmail.com
