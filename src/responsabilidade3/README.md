# Responsabilidade 3

Esta pasta contem a camada de relatorios, logs, alertas, fallback e circuit breaker.

A Responsabilidade 3 comeca depois que a Responsabilidade 2 ja calculou o MRP. Por isso, esta camada nao calcula:

- necessidade liquida;
- estoque projetado;
- lote de compra;
- fornecedor;
- regras especiais do Fornecedor C.

## Contrato De Entrada

O contrato de entrada e `MRPInputContract`, definido em `input_contract.py`.
`MRPResult` continua disponivel como alias para manter a nomenclatura conceitual
do resultado do Motor MRP.

Campos principais:

- `material`
- `fornecedor`
- `estoque_atual`
- `necessidade`
- `quantidade_comprar`
- `capacidade`
- `prazo_dias`
- `status_validacao`
- `observacao`

O relatorio Excel atual possui as colunas:

- `Fornecedor`
- `Material`
- `Estoque`
- `Necessidade`
- `Capacidade`
- `Prazo_Dias`
- `Status_Validacao`
- `Observacao`

Quando o Motor MRP real existir, a integracao esperada e:

```text
Responsabilidade 2
-> adapter
-> MRPResult
-> Responsabilidade 3
```

Se a saida real do Motor MRP tiver outros nomes ou estrutura, crie ou ajuste apenas um adapter/converter para produzir `MRPResult`.

## Severidade E Logs

Os niveis de severidade sao definidos em `severity.py`:

- `INFO`: operacao normal.
- `WARNING`: falha recuperavel ou fallback utilizado.
- `ERROR`: etapa falhou, mas o fluxo permaneceu controlado.
- `CRITICAL`: falha que impede resultado confiavel ou compromete integridade.

Os logs estruturados sao emitidos como JSON pelo `logging` padrao em `structured_logging.py`.
Campos sensiveis como senha, password, token, cookie, segredo e credenciais sao mascarados.

## Fixtures

`fixtures.py` possui dados ficticios para testar esta responsabilidade sem depender do Motor MRP real:

- geracao do relatorio Excel;
- logs;
- alertas;
- fallback;
- circuit breaker.
