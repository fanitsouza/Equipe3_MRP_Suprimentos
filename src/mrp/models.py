from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severidade(str, Enum):
    INFO = "INFO"
    AVISO = "AVISO"
    ERRO = "ERRO"
    CRITICO = "CRÍTICO"


class StatusMRP(str, Enum):
    SEM_COMPRA = "SEM_COMPRA"
    COMPRA_SUGERIDA = "COMPRA_SUGERIDA"
    CAPACIDADE_INSUFICIENTE = "CAPACIDADE_INSUFICIENTE"
    AGUARDANDO_VALIDACAO_HUMANA = "AGUARDANDO_VALIDACAO_HUMANA"


@dataclass(frozen=True)
class EstoqueMaterial:
    codigo_material: str
    estoque_atual: int
    demanda_semanal: int
    estoque_seguranca: int


@dataclass(frozen=True)
class Fornecedor:
    nome: str
    material: str
    capacidade_semanal: int
    prazo_dias: int
    preco_unitario: float
    status: str = "Ativo"


@dataclass(frozen=True)
class AtualizacaoFornecedor:
    fornecedor: str
    material: str
    capacidade_semanal: int
    prazo_dias: int
    origem: str = "e-mail"


@dataclass(frozen=True)
class ResultadoMRP:
    material: str
    fornecedor: str
    necessidade_calculada: int
    quantidade_sugerida: Optional[int]
    capacidade_considerada: int
    prazo_considerado_dias: int
    status: StatusMRP
    severidade: Severidade
    requer_validacao_humana: bool
    mensagem: str

