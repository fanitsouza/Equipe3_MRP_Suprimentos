# Projeto LG Electronics — Automação do Processo de MRP em Suprimentos (Master All)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![BPMN 2.0](https://img.shields.io/badge/BPMN-2.0%20Standard-orange.svg)](https://www.omg.org/spec/BPMN/2.0/)
[![Documentation](https://img.shields.io/badge/docs-PDD%20%26%20Mapeamento-green.svg)](docs/)
[![Status](https://img.shields.io/badge/status-Homologado-success.svg)]()

> **Atividade Dirigida em Equipe — Mapeamento de Processos, BPMN e Construção do PDD**  
> **Empresa:** LG Electronics do Brasil (Manaus / AM)  
> **Área:** Sourcing & Suprimentos — Planejamento de Materiais e Capacidade de Fornecedores  
> **Gestor do Processo:** Felipe Campelo (Gerente de Sourcing & Suprimentos)  
> **Disciplina:** Técnicas de Hyperautomation — Turma T02 (2026)  
> **Docentes:** Prof. Me. Moisés dos Santos Lévy e Dr. Vitor Bremgartner da Frota

---

## 👥 Equipe de Desenvolvimento (Equipe 01 - Suprimentos)

| Integrante | Papel / Responsabilidades |
| :--- | :--- |
| **Fani Tamires de Souza Batista** | Organização da equipe, modelagem BPMN, regras de negócio, relatório técnico, revisão final e validação geral |
| **Luã Maury Maquiné da Silva** | Manipulação da planilha Master All, organização do documento, Git/GitHub e evidências dos testes |
| **Gustavo Martins Luz** | Extração dos dados de produção N-FP, leitura dos arquivos de estoque e validação dos campos obrigatórios |
| **Luan Vasconcelos Pinheiro** | Desenvolvimento do módulo de integração com o GERP, automação web e orquestração de macros |

---

## 📌 Visão Geral do Projeto

Este repositório contém o ecossistema completo de engenharia de processos, automação RPA e documentação técnica (PDD e Mapeamento) para a automação do **MRP (Material Requirements Planning)** do setor de Suprimentos da fábrica da **LG Electronics em Manaus**.

### O Desafio Corporativo
Diariamente, a equipe de suprimentos gasta cerca de 50 minutos na abertura matinal e mais de 12 horas semanais manipulando manualmente 5 fontes distintas de dados (Plano N-FP, Onhand LG, BOM GERP, Delivery Status e Estoques de Fornecedores) para atualizar a planilha mestra **Master All**. O processo envolvia cálculos manuais de calendários (D+13, exclusão de domingos/feriados, 8 semanas), exclusão de colunas em Delivery (C:AV) e execução sequencial de 4 macros VBA pesadas que frequentemente congelavam os computadores da equipe.

### A Solução Implementada
A solução de Hyperautomation desenvolvida em Python realiza:
1. **Extração Autônoma:** Conexão ao Oracle GERP via Playwright e monitoramento de e-mails/repositórios.
2. **Higienização Matricial com Pandas:** Aplicação instantânea das regras de D+13 dias até sábado, expurgo de domingos/feriados em Manaus, 8 semanas e exclusão de colunas em frações de segundo.
3. **Injeção Segura e Orquestração VBA:** Alimentação estruturada via `openpyxl` e execução monitorada das macros com tratamento de timeout.
4. **Trava de Integridade Automática:** Validação cruzada `Data BOM == Data Summary Master`.
5. **Atualização Recorrente de Entregas:** Sincronização da aba Delivery Status a cada 20 minutos com as notas da portaria.
6. **Human-in-the-Loop:** Liberação de **1 FTE** para tomada de decisão estratégica pelo gestor Felipe Campelo e analistas de compras.

---

## 📂 Estrutura do Repositório

```text
Projeto LG MRP Suprimentos/
├── docs/
│   ├── BPMN/
│   │   ├── processo_AS-IS.drawio     # Modelo XML BPMN 2.0 do processo manual
│   │   ├── processo_AS-IS.svg        # Diagrama vetorial AS-IS
│   │   ├── processo_TO-BE.drawio     # Modelo XML BPMN 2.0 do processo automatizado
│   │   └── processo_TO-BE.svg        # Diagrama vetorial TO-BE
│   ├── PDD/
│   │   ├── PDD_Processo.docx         # PDD no padrão Semana 08 (Microsoft Word)
│   │   ├── PDD_Processo.pdf          # PDD compilado em PDF pronto para entrega
│   │   └── PDD_Processo.md           # PDD em formato Markdown
│   └── mapeamento/
│       └── Mapeamento_Detalhado_Processo.md  # Entradas, regras, RACI e métricas
├── evidencias/
│   └── FLUXO DA AUTOMAÇÃO - TO-BE.png        # Arquitetura conceitual em 6 fases
├── update_all.py                     # Script mestre de geração e validação
└── README.md                         # Documentação principal do repositório
```

---

## 📊 Comparativo de Resultados (AS-IS vs. TO-BE)

| Métrica de Desempenho | Cenário AS-IS (Manual) | Cenário TO-BE (Automatizado) | Ganho Obtido |
| :--- | :---: | :---: | :---: |
| **Tempo de Geração (1ª Master All)** | 35 a 50 minutos | **&lt; 5 minutos** | **-90% Lead Time** |
| **Esforço Operacional Humano** | 12h semanais / analista | **&lt; 30 min / dia** | **1 FTE Liberado** |
| **Frequência de Atualização Delivery** | Manual e esporádica | **A cada 20 minutos** | **Tempo Real** |
| **Taxa de Erro de Recorte / Digitação** | ~15% a 20% | **&lt; 0.1%** | **Precisão Total** |
| **Segurança Operacional da Fábrica** | Risco de ruptura de estoque | **Totalmente blindada** | **Estabilidade** |

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem & Processamento:** Python 3.10+, Pandas, OpenPyXL, PyWin32
- **Automação Web & E-mail:** Playwright, IMAPClient, BotCity
- **Modelagem de Processos:** Draw.io (BPMN 2.0 Standard Stencils)
- **Versionamento & GitFlow:** Git, GitHub
- **Documentação:** Microsoft Word (.docx), Google Chrome Headless (.pdf), Markdown (.md)

---

## 🚀 Como Executar o Projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/lg-suprimentos-t02/projeto-mrp-masterall.git
   ```
2. Instale as dependências:
   ```bash
   pip install pandas openpyxl python-docx pytest playwright
   ```
3. Recompilar e validar toda a documentação e diagramas:
   ```bash
   python update_all.py
   ```