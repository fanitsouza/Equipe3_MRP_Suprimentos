from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class StockRecord:
    material: str
    stock: float
    weekly_demand: float
    safety_stock: float


@dataclass(frozen=True)
class SupplierRecord:
    supplier: str
    material: str
    capacity: float
    lead_time_days: int
    unit_price: float
    status: str


@dataclass(frozen=True)
class NFPRecord:
    number: str
    supplier: str
    material: str
    quantity: float
    issue_date: date
    unit_price: float


@dataclass(frozen=True)
class SupplierUpdate:
    supplier: str
    material: str
    old_capacity: Optional[float]
    new_capacity: Optional[float]
    old_lead_time_days: Optional[int]
    new_lead_time_days: Optional[int]
    reason: str
