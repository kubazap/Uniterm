"""Encje domenowe."""

from __future__ import annotations
from dataclasses import dataclass
from .settings import DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE


@dataclass
class Uniterm:
    """Reprezentuje pojedynczy uniterm."""
    # główne pola
    id:          int | None = None
    name:        str = ""
    description: str = ""

    a:    str = ""
    b:    str = ""
    cond: str = ""           

    x:   str = ""            
    y:   str = ""            
    cond2:  str = ""            

    orientation: str = "H"   # 'H' lub 'V'
    bracket_on:  str = "A"   # 'A' lub 'B'

    # wygląd rysunku
    font_family: str = DEFAULT_FONT_FAMILY
    font_size:   int = DEFAULT_FONT_SIZE

    @property
    def seq(self) -> list[str]:
        """Zwraca listę [X, Y, u₂] bez pustych elementów."""
        return [s for s in (self.x, self.y, self.cond2) if s]

    @classmethod
    def from_row(cls, row: dict) -> "Uniterm":
        return cls(**row)
