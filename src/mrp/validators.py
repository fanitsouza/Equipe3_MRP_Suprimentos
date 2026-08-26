from collections.abc import Iterable

from .exceptions import DadosInvalidosError
from .models import AtualizacaoFornecedor, EstoqueMaterial, Fornecedor


def validar_estoques(estoques: Iterable[EstoqueMaterial]) -> list[EstoqueMaterial]:
    itens = list(estoques)
    _validar_lista_nao_vazia(itens, "estoque")
    vistos: set[str] = set()
    for item in itens:
        _validar_texto(item.codigo_material, "codigo_material")
        _validar_inteiro_nao_negativo(item.estoque_atual, "estoque_atual", item.codigo_material)
        _validar_inteiro_nao_negativo(item.demanda_semanal, "demanda_semanal", item.codigo_material)
        _validar_inteiro_nao_negativo(item.estoque_seguranca, "estoque_seguranca", item.codigo_material)
        if item.codigo_material in vistos:
            raise DadosInvalidosError(f"Material duplicado no estoque: {item.codigo_material}")
        vistos.add(item.codigo_material)
    return itens


def validar_fornecedores(fornecedores: Iterable[Fornecedor]) -> list[Fornecedor]:
    itens = list(fornecedores)
    _validar_lista_nao_vazia(itens, "fornecedores")
    vistos: set[str] = set()
    for item in itens:
        _validar_texto(item.nome, "fornecedor")
        _validar_texto(item.material, "material")
        _validar_inteiro_nao_negativo(item.capacidade_semanal, "capacidade_semanal", item.material)
        _validar_inteiro_nao_negativo(item.prazo_dias, "prazo_dias", item.material)
        if not isinstance(item.preco_unitario, (int, float)) or isinstance(item.preco_unitario, bool) or item.preco_unitario < 0:
            raise DadosInvalidosError(f"preco_unitario inválido para {item.material}: {item.preco_unitario!r}")
        if item.material in vistos:
            raise DadosInvalidosError(f"Mais de um fornecedor principal para o material: {item.material}")
        vistos.add(item.material)
    return itens


def validar_atualizacoes(
    atualizacoes: Iterable[AtualizacaoFornecedor],
) -> list[AtualizacaoFornecedor]:
    itens = list(atualizacoes)
    vistos: set[str] = set()
    for item in itens:
        _validar_texto(item.fornecedor, "fornecedor")
        _validar_texto(item.material, "material")
        _validar_inteiro_nao_negativo(item.capacidade_semanal, "capacidade_semanal", item.material)
        _validar_inteiro_nao_negativo(item.prazo_dias, "prazo_dias", item.material)
        if item.material in vistos:
            raise DadosInvalidosError(f"Mais de uma atualização para o material: {item.material}")
        vistos.add(item.material)
    return itens


def _validar_lista_nao_vazia(itens: list[object], nome: str) -> None:
    if not itens:
        raise DadosInvalidosError(f"A lista de {nome} não pode estar vazia")


def _validar_texto(valor: str, campo: str) -> None:
    if not isinstance(valor, str) or not valor.strip():
        raise DadosInvalidosError(f"{campo} deve ser um texto não vazio")


def _validar_inteiro_nao_negativo(valor: int, campo: str, material: str) -> None:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
        raise DadosInvalidosError(f"{campo} inválido para {material}: {valor!r}")

