"""Integração entre os coletores e o motor de regras do MRP."""

from collections.abc import Mapping
from typing import Any

from src.models.data import NFPRecord, StockRecord, SupplierRecord, SupplierUpdate

from .engine import calcular_mrp
from .exceptions import DadosInvalidosError
from .models import AtualizacaoFornecedor, EstoqueMaterial, Fornecedor, ResultadoMRP


CHAVES_OBRIGATORIAS = {
    "stock",
    "supplier_csv",
    "grp_web",
    "nfp",
    "supplier_update",
}


def calcular_mrp_da_coleta(coleta: Mapping[str, Any]) -> list[ResultadoMRP]:
    """Converte e cruza a saída de ``collect_all`` antes do cálculo."""
    ausentes = CHAVES_OBRIGATORIAS - set(coleta)
    if ausentes:
        raise DadosInvalidosError(
            "Fontes ausentes na coleta: " + ", ".join(sorted(ausentes))
        )

    estoques_origem = _lista_tipificada(coleta["stock"], StockRecord, "stock")
    fornecedores_csv = _lista_tipificada(
        coleta["supplier_csv"], SupplierRecord, "supplier_csv"
    )
    fornecedores_web = _lista_tipificada(
        coleta["grp_web"], SupplierRecord, "grp_web"
    )
    nfp = coleta["nfp"]
    atualizacao = coleta["supplier_update"]
    if not isinstance(nfp, NFPRecord):
        raise DadosInvalidosError("Registro de NFP inválido")
    if not isinstance(atualizacao, SupplierUpdate):
        raise DadosInvalidosError("Atualização de fornecedor inválida")

    _validar_consistencia_grp(fornecedores_csv, fornecedores_web)
    _validar_nfp(nfp, fornecedores_csv)
    _validar_valores_anteriores(atualizacao, fornecedores_csv)

    estoques = [
        EstoqueMaterial(
            codigo_material=item.material,
            estoque_atual=_quantidade_inteira(item.stock, "estoque", item.material),
            demanda_semanal=_quantidade_inteira(
                item.weekly_demand, "demanda semanal", item.material
            ),
            estoque_seguranca=_quantidade_inteira(
                item.safety_stock, "estoque de segurança", item.material
            ),
        )
        for item in estoques_origem
    ]
    fornecedores = [
        Fornecedor(
            nome=item.supplier,
            material=item.material,
            capacidade_semanal=_quantidade_inteira(
                item.capacity, "capacidade", item.material
            ),
            prazo_dias=item.lead_time_days,
            preco_unitario=item.unit_price,
            status=item.status,
        )
        for item in fornecedores_csv
    ]
    atualizacoes = [
        AtualizacaoFornecedor(
            fornecedor=atualizacao.supplier,
            material=atualizacao.material,
            capacidade_semanal=_quantidade_inteira(
                atualizacao.new_capacity, "nova capacidade", atualizacao.material
            ),
            prazo_dias=_inteiro_obrigatorio(
                atualizacao.new_lead_time_days,
                "novo prazo",
                atualizacao.material,
            ),
            origem="e-mail do fornecedor",
        )
    ]
    return calcular_mrp(estoques, fornecedores, atualizacoes)


def _validar_consistencia_grp(
    csv: list[SupplierRecord], web: list[SupplierRecord]
) -> None:
    por_material_csv = {_assinatura(item): item for item in csv}
    por_material_web = {_assinatura(item): item for item in web}
    if por_material_csv.keys() != por_material_web.keys():
        raise DadosInvalidosError("Materiais/fornecedores divergem entre CSV e GRP Web")

    for chave, cadastro in por_material_csv.items():
        web_item = por_material_web[chave]
        if (
            cadastro.capacity != web_item.capacity
            or cadastro.lead_time_days != web_item.lead_time_days
            or cadastro.unit_price != web_item.unit_price
        ):
            raise DadosInvalidosError(
                f"Dados divergem entre CSV e GRP Web para {cadastro.material}"
            )


def _validar_nfp(nfp: NFPRecord, fornecedores: list[SupplierRecord]) -> None:
    fornecedor = next(
        (
            item
            for item in fornecedores
            if item.material == nfp.material and item.supplier == nfp.supplier
        ),
        None,
    )
    if fornecedor is None:
        raise DadosInvalidosError(
            f"NFP {nfp.number} não corresponde ao fornecedor/material cadastrado"
        )
    if nfp.unit_price != fornecedor.unit_price:
        raise DadosInvalidosError(
            f"Preço da NFP {nfp.number} diverge do GRP para {nfp.material}"
        )


def _validar_valores_anteriores(
    atualizacao: SupplierUpdate, fornecedores: list[SupplierRecord]
) -> None:
    fornecedor = next(
        (
            item
            for item in fornecedores
            if item.material == atualizacao.material
            and item.supplier == atualizacao.supplier
        ),
        None,
    )
    if fornecedor is None:
        raise DadosInvalidosError("Atualização recebida de fornecedor não cadastrado")
    if (
        atualizacao.old_capacity != fornecedor.capacity
        or atualizacao.old_lead_time_days != fornecedor.lead_time_days
    ):
        raise DadosInvalidosError(
            f"Valores anteriores do e-mail não correspondem ao GRP para {atualizacao.material}"
        )


def _lista_tipificada(valor: Any, tipo: type, fonte: str) -> list[Any]:
    if not isinstance(valor, list) or not all(isinstance(item, tipo) for item in valor):
        raise DadosInvalidosError(f"Dados inválidos na fonte {fonte}")
    return valor


def _assinatura(item: SupplierRecord) -> tuple[str, str]:
    return item.supplier, item.material


def _quantidade_inteira(valor: Any, campo: str, material: str) -> int:
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        raise DadosInvalidosError(f"{campo} inválido para {material}: {valor!r}")
    if valor < 0 or not float(valor).is_integer():
        raise DadosInvalidosError(
            f"{campo} deve ser uma quantidade inteira não negativa para {material}"
        )
    return int(valor)


def _inteiro_obrigatorio(valor: Any, campo: str, material: str) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
        raise DadosInvalidosError(f"{campo} inválido para {material}: {valor!r}")
    return valor

