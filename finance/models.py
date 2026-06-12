from dataclasses import dataclass
from typing import Optional, List

DEFAULT_CATEGORIES: List[str] = [
    "餐饮",
    "交通",
    "购物",
    "娱乐",
    "居住",
    "其他",
]


@dataclass
class Category:
    id: Optional[int]
    name: str


@dataclass
class Record:
    id: Optional[int]
    amount: float
    category_id: int
    record_date: str  # YYYY-MM-DD
    note: Optional[str] = None
    created_at: Optional[str] = None
    category_name: Optional[str] = None  # runtime-only, not stored in DB
