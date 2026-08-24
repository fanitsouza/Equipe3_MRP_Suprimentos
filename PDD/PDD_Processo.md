# Semana 08 — Automação do Processo de MRP em Suprimentos

**Disciplina:** Técnicas de Hyperautomation  
**Professor:** Moisés Levy / Dr. Vitor Bremgartner da Frota  
**Alunos:** 
- Fani Tamires de Souza Batista
- Gustavo Martins Luz
- Luã Maury Maquiné da Silva
- Luan Vasconcelos Pinheiro

---

## 1. Identificação do Projeto

- **Equipe:** Equipe 01 (Suprimentos)
- **Processo desenvolvido:** Automação do Processo de MRP em Suprimentos (Geração e Atualização da Master All)
- **Gestor responsável:** Felipe Campelo (Gerente de Sourcing & Suprimentos — LG Electronics)
- **Área demandante:** Sourcing — Planejamento de Materiais e Capacidade de Fornecedores

### 1.1 Integrantes da equipe

| Integrante | Responsabilidade |
| :--- | :--- |
| **Fani Tamires de Souza Batista** | Organização da equipe, modelagem BPMN, regras de negócio, relatório técnico, revisão final e validação geral |
| **Luã Maury Maquiné da Silva** | Manipulação da planilha Master All, organização do documento, Git/GitHub e evidências dos testes |
| **Gustavo Martins Luz** | Extração dos dados de produção N-FP, leitura dos arquivos de estoque e validação dos campos obrigatórios |
| **Luan Vasconcelos Pinheiro** | Desenvolvimento do módulo de integração com o GERP, automação web e orquestração de macros |

---

## 2. Descrição da solução desenvolvida

A solução desenvolvida corresponde ao ecossistema de Hyperautomation voltado para o setor de Sourcing & Suprimentos da LG Electronics do Brasil. O objetivo do módulo é automatizar completamente a rotina diária de planejamento de necessidades de materiais (MRP), integrando 5 fontes de dados corporativas (Plano de Produção N-FP, Saldo Onhand LG, Bill of Materials - BOM no GERP, Delivery Status e Saldo de Estoque de Fornecedores) para gerar e manter atualizada a planilha mestra Master All.

A automação foi estruturada para eliminar tarefas manuais e repetitivas de extração, recorte temporal de calendários (D+13 dias até sábado, expurgo de domingos/feriados, 8 semanas e visão mensal) e exclusão de colunas em Delivery Status. Além disso, a solução orquestra as 4 macros pesadas do Excel em segundo plano com tratamento de exceções e tolerância a timeouts, executando a validação obrigatória de consistência entre a aba BOM e o Summary Master.

O módulo desenvolvido também possui controle de integridade e notificação automatizada no modelo Human-in-the-Loop, liberando 1 FTE em carga horária operacional para que o gestor Felipe Campelo e os analistas de suprimentos foquem em análises táticas, compras estratégicas e negociação de capacidades com fornecedores.

---

## 3. Regras de negócio

Dentre as regras de negócio identificadas no desenvolvimento do processo de MRP em Suprimentos da LG Electronics, foram levantadas:

- Apenas arquivos das 5 fontes homologadas (N-FP, Onhand DX, BOM GERP, Delivery e Fornecedores) podem ser processados.
- O robô deve verificar diariamente às 07:30h a disponibilidade dos novos arquivos matinais.
- A primeira Master All do dia deve ser criada e disponibilizada até as 08:00h com a data corrente.
- O Plano Diário (N-FP) deve cobrir o horizonte D+13 dias úteis, finalizando rigorosamente no segundo sábado subsequente.
- Colunas de datas anteriores ao dia atual devem ser expurgadas da visão diária.
- Todas as colunas referentes a domingos e feriados em Manaus devem ser excluídas (validação: toneladas = 0).
- O Plano Semanal deve iniciar na segunda-feira imediatamente após o último sábado da visão diária e abranger exatamente 8 semanas consecutivas.
- O Plano Mensal deve consolidar os meses subsequentes de planejamento de longo prazo.
- Os dados tratados de produção devem ser colados a partir da 2ª célula na aba PlanPPH para preservar os cabeçalhos fixos da macro.
- Na aba Delivery Status, devem ser excluídas todas as colunas de C (Org) a AV (Notas NO), mantendo intactas as fórmulas de A e B.
- Os dados da planilha de Onhand devem ser copiados integralmente para sua respectiva aba.
- Se houver nova BOM: a ordem de macros deve ser: 1º Update BOM > 2º Formatar Summary Master > 3º Update Onhand > 4º Update Plan.
- Se não houver nova BOM: a ordem de macros deve ser: 1º Update Onhand > 2º Update Plan.
- Trava de integridade: a Data registrada na aba BOM deve ser rigorosamente idêntica à Data da aba Summary Master.
- A aba Delivery Status deve ser atualizada de forma recorrente a cada 20 minutos durante todo o turno operacional (08h às 18h).
- Em caso de erro, divergência de datas ou dados corrompidos, o robô deve isolar a planilha e emitir alerta crítico imediato.

---

## 4. Diagrama BPMN

**Figura 1 — BPMN do Processo: Automação do Processo de MRP em Suprimentos da LG Electronics.**  
*Fonte: Elaborado pela equipe, 2026.*

**Descrição do fluxo:**  
O fluxo BPMN representa a transição completa do processo de Planejamento de Necessidades de Materiais (MRP) da LG Electronics. O processo é disparado pontualmente às 07:30h da manhã pelo gatilho diário do orquestrador RPA, além de contar com um gatilho recorrente a cada 20 minutos para sincronização de entregas. Na Fase 1, bots automatizados em Python (Playwright e IMAP) extraem os dados oficiais no Oracle GERP, diretórios compartilhados e e-mails de fornecedores. Na Fase 2, uma engine matricial baseada na biblioteca Pandas realiza o tratamento e higienização temporal (recorte D+13 dias até sábado, expurgo de domingos/feriados, 8 semanas e exclusão vetorial de colunas C:AV em Delivery) em frações de segundo.

Em seguida, na Fase 3 e 4, os dados tratados são injetados na planilha Master All via openpyxl e o robô executa a cadeia ordenada de macros VBA. Caso haja nova versão de BOM liberada pela engenharia, o robô executa a sequência completa (Update BOM, Formatar Summary Master, Update Onhand e Update Plan). Caso contrário, executa a sequência padrão (Update Onhand e Update Plan). Na Fase 5, um gateway de decisão valida se a data da aba BOM coincide exatamente com a data da aba Summary Master. Sendo consistente, os relatórios de capacidade diários, semanais e mensais são gerados e publicados automaticamente. Na Fase 6, o gestor Felipe Campelo e os analistas atuam no modelo Human-in-the-Loop para tomada de decisões estratégicas de aquisição.

---

## 5. Processo AS-IS

No cenário AS-IS, o setor de Suprimentos realiza manualmente todo o processo de consolidação de dados. O analista precisa acessar individualmente múltiplos sistemas legados (GERP, N-FP, GRP e Outlook), baixar planilhas pesadas e manipulá-las diretamente no Microsoft Excel.

Esse processo depende de intensa ação manual: abrir a Master All do dia anterior e limpar dados antigos; baixar a planilha de Onhand e colar na aba correspondente; baixar o plano bruto do N-FP, filtrar dias úteis até sábado, expurgar manualmente domingos e feriados, recortar 8 semanas e colar na aba PlanPPH a partir da 2ª célula; disparar a macro de Onhand e aguardar 5 minutos de travamento; disparar a macro de Update Plan e aguardar mais 15 minutos; acessar o GERP, baixar o relatório de Delivery Status, apagar manualmente as colunas C a AV e colar os novos dados; checar visualmente se há nova BOM no GERP e, se houver, rodar macros de formatação que travam o computador por até 25 minutos; e, finalmente, comparar visualmente as datas da aba BOM e Summary Master antes de compilar os relatórios para os fornecedores.

- Receber arquivos de estoques e plano de produção por e-mail e sistemas;
- Abrir a planilha Master All do dia anterior e limpar dados antigos;
- Baixar planilha de saldo Onhand LG e colar na aba Onhand;
- Extrair plano bruto do N-FP e formatar colunas manualmente no Excel;
- Filtrar período D+13 dias até sábado e expurgar domingos e feriados;
- Recortar 8 semanas para a visão semanal e consolidar períodos mensais;
- Colar plano formatado na aba PlanPPH a partir da 2ª célula;
- Disparar manualmente macro Update Onhand (espera de 3 a 5 minutos);
- Disparar manualmente macro Update Plan (espera de 12 a 15 minutos);
- Baixar Delivery Status no GERP, apagar colunas C até AV e colar na aba Delivery;
- Verificar manualmente no GERP se houve alteração na lista de materiais (BOM);
- Se houver BOM: rodar Update BOM (1 min) e Formatar Summary Master (25 min);
- Conferir visualmente se a data da aba BOM coincide com a aba Summary Master;
- Compilar relatórios manuais de capacidade e enviar por e-mail aos fornecedores;
- Repetir a atualização da aba Delivery Status a cada 20 minutos ao longo do dia.

No processo AS-IS, a equipe de Suprimentos gasta entre 35 e 50 minutos na criação da primeira planilha da manhã e acumula mais de 12 horas semanais por colaborador apenas em atividades repetitivas. Esse modelo apresenta graves gargalos operacionais: alta vulnerabilidade a erros de digitação e exclusão de colunas, congelamentos constantes do Microsoft Excel devido à sobrecarga de macros VBA e desatualização das notas fiscais entregues na portaria, aumentando o risco de paradas nas linhas de montagem da fábrica de Manaus.

---

## 6. Processo TO-BE

No cenário TO-BE, a solução de Hyperautomation assume a execução de ponta a ponta das etapas operacionais e repetitivas de Suprimentos. O orquestrador dispara automaticamente a rotina às 07:30h da manhã, coleta os 5 arquivos de entrada, realiza o processamento matricial com Pandas em segundos, injeta os dados estruturados na planilha Master All, gerencia o disparo assíncrono das macros VBA, valida a integridade das bases e publica os relatórios diários, semanais e mensais de capacidade por fornecedor.

Esse fluxo atende plenamente ao desafio corporativo da LG Electronics, garantindo automação determinística, precisão matemática nos saldos de estoques, atualização contínua de entregas a cada 20 minutos e atuação do time no modelo Human-in-the-Loop.

- Orquestrador dispara rotina diária pontualmente às 07:30h;
- Bot Web Playwright extrai BOM atualizada e Delivery Status diretamente no Oracle GERP;
- Monitor de e-mail e leitor de arquivos capturam saldos de fornecedores, N-FP e Onhand LG;
- Engine Python / Pandas realiza filtros vetoriais de data (D+13 dias até sábado);
- Expurgo instantâneo e determinístico de domingos e feriados da planta de Manaus;
- Segmentação automatizada de 8 semanas de planejamento e períodos mensais subsequentes;
- Exclusão vetorizada das colunas C a AV na aba Delivery Status, preservando fórmulas A e B;
- Injeção estruturada dos dados na planilha Master All via openpyxl;
- Orquestração automática das macros VBA conforme precedência de negócio;
- Validação de integridade automática entre a data da aba BOM e da aba Summary Master;
- Geração autônoma de relatórios de capacidade por fornecedor (Diário, Semanal e Mensal);
- Atualização recorrente da aba Delivery Status a cada 20 minutos durante o turno fabril;
- Disparo de notificações estruturadas e alertas para revisão estratégica da equipe.

---

## 7. Tecnologias utilizadas

As tecnologias e ferramentas selecionadas para o desenvolvimento da automação foram:

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python 3.10+** | Linguagem principal utilizada para o desenvolvimento de todo o ecossistema de automação |
| **pandas** | Manipulação matricial de alto desempenho, filtros temporais e higienização vetorial de dados |
| **openpyxl / pywin32** | Injeção estruturada de dados na planilha Master All e despacho assíncrono de macros VBA |
| **Playwright / BotCity** | Automação de interface web para login seguro e extração de relatórios no Oracle GERP |
| **pathlib & shutil** | Gestão determinística de caminhos, diretórios de trabalho e arquivamento de logs |
| **pytest / unittest** | Execução de suíte de testes unitários e de integração para validação de regras de negócio |
| **Draw.io** | Modelagem e documentação técnica dos diagramas de fluxo em notação BPMN 2.0 |
| **Git / GitHub / GitFlow** | Versionamento de código, controle de branches e colaboração em equipe |
| **VS Code** | Ambiente de desenvolvimento integrado para escrita de código e testes |

A equipe optou por estruturar a solução combinando a velocidade de processamento do Pandas com a confiabilidade da automação web via Playwright. Essa abordagem modular permite processar mais de 15.000 linhas de dados em menos de 2 segundos, eliminando a dependência de digitação manual e garantindo perfeita integração com os sistemas corporativos legados da LG Electronics.

---

## 8. Evidências dos testes realizados

Nesta etapa, foram realizados testes rigorosos para validar o funcionamento do processo de automação de MRP. Os testes verificaram se os 5 arquivos de entrada foram localizados e extraídos corretamente, se a higienização temporal (D+13 dias até sábado, expurgo de domingos/feriados e 8 semanas) foi aplicada com exatidão, se a exclusão de colunas em Delivery preservou as fórmulas originais, se a injeção na planilha Master All ocorreu a partir da 2ª célula e se a trava de integridade entre BOM e Summary Master bloqueou com sucesso eventuais divergências.

- **Figura 2** — Estrutura de fases da automação e fluxo de dados TO-BE.
- **Figura 3** — Execução da automação em Python e processamento com Pandas no terminal.
- **Figura 4** — Planilha Master All do dia atualizada e validada pelo robô RPA.
- **Figura 5** — Relatórios de capacidade por fornecedor gerados automaticamente.
- **Figura 6** — Suíte de testes automatizados e validações de integridade executadas com sucesso.

---

## 9. Conclusão

A atividade permitiu consolidar com excelência o projeto de Hyperautomation para o processo de MRP em Suprimentos da LG Electronics. A solução desenvolvida automatiza etapas críticas que antes eram manuais e exaustivas, como a coleta de 5 bases dispersas, higienização de matrizes temporais, manipulação do Excel, execução de macros e conferência visual de integridade.

O projeto proporciona resultados altamente expressivos: liberação de 1 FTE em horas de trabalho operacional, redução projetada de 90% nos erros de digitação e recorte temporal, redução no tempo de geração da 1ª Master All de 50 minutos para menos de 6 minutos e mitigação completa dos riscos de parada de fábrica por rupturas de estoque. Com isso, o setor de Suprimentos passa a operar com dados em tempo real, conferindo maior agilidade, confiabilidade e inteligência estratégica à cadeia de suprimentos da LG em Manaus.