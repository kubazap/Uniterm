"""Funkcje biznesowe."""

from __future__ import annotations
from .models import Uniterm


def toggle_ab(u: Uniterm) -> None:
    """Zamienia miejscami pola A i B."""
    u.a, u.b = u.b, u.a


def horizontal_to_vertical(u: Uniterm, on: str = "A") -> Uniterm:
    """
    Zwraca uniterm pionowy utworzony na podstawie poziomego.

    Parametr `on` określa, który wiersz (A lub B) zostanie zastąpiony sekwencją.
    """
    v = Uniterm(**u.__dict__)
    v.orientation = "V"
    v.bracket_on = on
    if on == "A":
        v.a = u.seq_csv
    else:
        v.b = u.seq_csv
    return v
