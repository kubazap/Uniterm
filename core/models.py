"""Encje domenowe."""

from __future__ import annotations
from dataclasses import dataclass, field
from .settings import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE


@dataclass
class Uniterm:
    """Reprezentuje pojedynczy uniterm wraz z danymi pomocniczymi."""
    id:          int | None = None
    name:        str = ""
    description: str = ""
    a:           str = ""
    b:           str = ""
    cond:        str = ""
    orientation: str = "H"           
    seq:         list[str] = field(default_factory=list)
    bracket_on:  str = "A"          
    font_family: str = DEFAULT_FONT_FAMILY
    font_size:   int = DEFAULT_FONT_SIZE

    @property
    def seq_csv(self) -> str:
        """Sekwencja w formie tekstu z separatorem."""
        return "; ".join(self.seq)

    @classmethod
    def from_row(cls, row: dict) -> "Uniterm":
        """Buduje obiekt na podstawie wyniku kwerendy."""
        seq_txt = row.pop("seq_str", "") or ""
        u = cls(**row)
        if seq_txt:
            u.seq = [s.strip() for s in seq_txt.split(";")]
        return u
