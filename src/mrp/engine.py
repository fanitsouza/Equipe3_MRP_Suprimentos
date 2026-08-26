from collections.abc import Iterable

from .exceptions import DadosInvalidosError
from .models import (
    AtualizacaoFornecedor,
    EstoqueMaterial,
    Fornecedor,
    ResultadoMRP,
    Severidade,
    StatusMRP,
)
from .validators import validar_atualizacoes, validar_estoques, validar_fornecedores


def calcular_mrp(
    estoques: Iterable[EstoqueMaterial],
    fornecedores: Iterable[Fornecedor],
    atualizacoes: Iterable[AtualizacaoFornecedor] = (),
) -> list[ResultadoMRP]:
    """Calcula necessidades e bloqueia divergências para decisão humana.

    A necessidade líquida é ``max(demanda + segurança - estoque, 0)``.
    Qualquer atualização que divergir do cadastro do GRP impede a sugestão
    automática de compra somente para o material afetado.
    """
    itens_estoque = validar_estoques(estoques)
    itens_fornecedor = validar_fornecedores(fornecedores)
    itens_atualizacao = validar_atualizacoes(atualizacoes)

    fornecedor_por_material = {item.material: item for item in itens_fornecedor}
    atualizacao_por_material = {item.material: item for item in itens_atualizacao}
    resultados: list[ResultadoMRP] = []

    for item in itens_estoque:
        fornecedor = fornecedor_por_material.get(item.codigo_material)
        if fornecedor is None:
            raise DadosInvalidosError(
                f"Fornecedor não encontrado para o material: {item.codigo_material}"
            )
        if fornecedor.status.casefold() != "ativo":
            raise DadosInvalidosError(
                f"Fornecedor {fornecedor.nome} está inativo para {item.codigo_material}"
            )

        necessidade = max(
            item.demanda_semanal + item.estoque_seguranca - item.estoque_atual,
            0,
        )
        atualizacao = atualizacao_por_material.get(item.codigo_material)

        if atualizacao is not None:
            if atualizacao.fornecedor != fornecedor.nome:
                raise DadosInvalidosError(
                    f"Atualização de {item.codigo_material} pertence a fornecedor diferente"
                )
            if _ha_divergencia(fornecedor, atualizacao):
                resultados.append(
                    ResultadoMRP(
                        material=item.codigo_material,
                        fornecedor=fornecedor.nome,
                        necessidade_calculada=necessidade,
                        quantidade_sugerida=None,
                        capacidade_considerada=atualizacao.capacidade_semanal,
                        prazo_considerado_dias=atualizacao.prazo_dias,
                        status=StatusMRP.AGUARDANDO_VALIDACAO_HUMANA,
                        severidade=Severidade.AVISO,
                        requer_validacao_humana=True,
                        mensagem=(
                            f"Divergência entre GRP e {atualizacao.origem}: capacidade "
                            f"{fornecedor.capacidade_semanal}→{atualizacao.capacidade_semanal}; "
                            f"prazo {fornecedor.prazo_dias}→{atualizacao.prazo_dias} dias. "
                            "Sugestão de compra bloqueada."
                        ),
                    )
                )
                continue

        resultados.append(_resultado_automatico(item, fornecedor, necessidade))

    materiais_estoque = {item.codigo_material for item in itens_estoque}
    atualizacoes_orfas = set(atualizacao_por_material) - materiais_estoque
    if atualizacoes_orfas:
        raise DadosInvalidosError(
            "Atualização sem material no estoque: " + ", ".join(sorted(atualizacoes_orfas))
        )
    return resultados


def _ha_divergencia(fornecedor: Fornecedor, atualizacao: AtualizacaoFornecedor) -> bool:
    return (
        fornecedor.capacidade_semanal != atualizacao.capacidade_semanal
        or fornecedor.prazo_dias != atualizacao.prazo_dias
    )


def _resultado_automatico(
    item: EstoqueMaterial,
    fornecedor: Fornecedor,
    necessidade: int,
) -> ResultadoMRP:
    if necessidade == 0:
        status = StatusMRP.SEM_COMPRA
        mensagem = "Estoque suficiente; compra não necessária."
    elif necessidade > fornecedor.capacidade_semanal:
        status = StatusMRP.CAPACIDADE_INSUFICIENTE
        mensagem = (
            f"Necessidade de {necessidade} excede a capacidade semanal de "
            f"{fornecedor.capacidade_semanal}; requer planejamento complementar."
        )
    else:
        status = StatusMRP.COMPRA_SUGERIDA
        mensagem = "Compra calculada automaticamente."

    return ResultadoMRP(
        material=item.codigo_material,
        fornecedor=fornecedor.nome,
        necessidade_calculada=necessidade,
        quantidade_sugerida=necessidade,
        capacidade_considerada=fornecedor.capacidade_semanal,
        prazo_considerado_dias=fornecedor.prazo_dias,
        status=status,
        severidade=Severidade.INFO,
        requer_validacao_humana=False,
        mensagem=mensagem,
    )

