"""Logika biznesowa."""

from __future__ import annotations
from .models import Uniterm


def toggle_ab(u: Uniterm) -> None:
    """In-place zamiana A ↔ B."""
    u.a, u.b = u.b, u.a


# ──────────────────────────────────────────────────────────────
#  Generowanie wersji pionowej
# ──────────────────────────────────────────────────────────────
def horizontal_to_vertical(u: Uniterm, on: str = "A") -> Uniterm:
    """
    Zwraca obiekt w orientacji pionowej.
    • `on="A"` – X trafia na miejsce A,
    • `on="B"` – X trafia na miejsce B,
    natomiast Y i u₂ pojawiają się pod klamrą w pionie.
    """
    v = Uniterm(**u.__dict__)          
    v.orientation = "V"
    v.bracket_on  = on.upper()

    first = u.x                         
    if v.bracket_on == "A":
        v.a = first
    else:
        v.b = first
    return v
