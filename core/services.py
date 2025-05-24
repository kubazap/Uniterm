"""Funkcje biznesowe związane z przekształcaniem unitermów."""

from __future__ import annotations
from .models import Uniterm


def toggle_ab(u: Uniterm) -> None:
    """Zamienia miejscami pola A i B (na obiekcie przekazanym w argumencie)."""
    u.a, u.b = u.b, u.a


# ──────────────────────────────────────────────────────────────────────────────
#  Zamiana unitermu poziomego na pionowy
# ──────────────────────────────────────────────────────────────────────────────
def horizontal_to_vertical(u: Uniterm, on: str = "A") -> Uniterm:
    """
    Zwraca **NOWY** obiekt `Uniterm` w orientacji „V”.

    Parametr
    --------
    on : str
        Litera „A” lub „B” – wskazuje, który z dwóch członów nagłówka
        (A lub B) ma zostać **zastąpiony sekwencją**.

    Zasady
    ------
    1. W nagłówku pionowego rysunku pokazujemy **TYLKO pierwszy element**
       sekwencji (`u.seq[0]`).  
    2. Pozostałe elementy sekwencji rysujemy pionowo pod klamrą.  
    3. Pełną listę `seq` zachowujemy w nowym obiekcie – potrzebuje jej
       warstwa rysująca.
    """
    v = Uniterm(**u.__dict__)          # płytka kopia wszystkich pól
    v.orientation = "V"
    v.bracket_on  = on.upper()

    first_seq = u.seq[0] if u.seq else ""

    if v.bracket_on == "A":
        v.a = first_seq
    else:
        v.b = first_seq

    v.seq = u.seq[:]                   # zachowujemy CAŁĄ listę
    return v
