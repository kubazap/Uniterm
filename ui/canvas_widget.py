"""Interfejs graficzny do rysowania unitermów."""

from __future__ import annotations
from tkinter import Canvas, font
from core.models import Uniterm

# Stałe graficzne
SEP      = ";"           # separator tekstowy
GRID_CLR = "#f3f3f3"     # kolor linii siatki
LINE_CLR = "#3F72AF"     # kolor klamer
LABEL_H  = 60            # wysokość paska opisów


class UnitermCanvas(Canvas):
    """Canvas z siatką w tle i metodą renderującą Uniterm."""

    def __init__(self, master, grid: int = 14, **kw):
        super().__init__(master, bg="white", **kw)
        self.grid = grid
        self.bind("<Configure>", lambda _e: self._draw_grid())

    # ---------- Rysowanie tła ----------
    def _draw_grid(self) -> None:
        """Rysuje punktową siatkę oraz biały pasek na etykiety."""
        self.delete("grid")
        w, h, g = self.winfo_width(), self.winfo_height(), self.grid
        dash = (1, 3)
        for x in range(0, w, g):
            self.create_line(x, 0, x, h, fill=GRID_CLR, dash=dash, tags="grid")
        for y in range(0, h, g):
            self.create_line(0, y, w, y, fill=GRID_CLR, dash=dash, tags="grid")
        self.create_rectangle(0, h - LABEL_H, w, h, outline="", tags="grid")

    # ---------- Klamry ----------
    def _h_bracket(self, x1, x2, y) -> None:
        half = 6
        self.create_line(x1, y, x2, y, fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x1, y - half, x1, y + half, fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x2, y - half, x2, y + half, fill=LINE_CLR, width=2, tags="uniterm")

    def _v_bracket(self, x, y1, y2) -> None:
        seg = 10
        self.create_line(x, y1 - 8, x, y2, fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x - 6, y1 - 8, x + seg, y1 - 8, fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x - 6, y2, x + seg, y2, fill=LINE_CLR, width=2, tags="uniterm")

    def _bracket_over(self, text_id, pad: int = 4) -> None:
        """Rysuje klamrę nad tekstem o id `text_id`."""
        x1, y1, x2, _ = self.bbox(text_id)
        self._h_bracket(x1 - pad, x2 + pad, y1 - 2)

    # ---------- Rysowanie unitermu ----------
    def draw(self, u: Uniterm | None, dx: int = 0) -> None:
        """Czyści poprzedni rysunek i renderuje `u` z przesunięciem `dx`."""
        if u is None:
            return

        fnt = font.Font(family=u.font_family, size=u.font_size, weight="bold")
        h = self.winfo_height()

        if u.orientation == "H":
            # --- Poziomy uniterm ---
            y0 = 95
            txt = f"{u.a}{SEP} {u.b}{SEP} {u.cond}"
            text_w = fnt.measure(txt)
            x0 = 80 + dx
            self._h_bracket(x0 - 8, x0 + text_w + 16, y0)
            self.create_text(x0 + 3, y0 + 15, text=txt, anchor="w",
                             font=fnt, tags="uniterm")
            self._label(h, x0 + (text_w + 16) / 2, "Pozioma", fnt)
        else:
            # --- Pionowy uniterm ---
            lines, idx = self._vertical_lines(u)
            step, start_y = 42, 80
            tx, bx = dx, dx - 20          
            extra = 10                    

            for i, t in enumerate(lines):
                y = start_y + i * step + (extra if i == idx else 0)
                tid = self.create_text(tx, y, text=t, anchor="w",
                                       font=fnt, tags="uniterm")
                if i == idx:
                    self._bracket_over(tid, pad=6)

            y1 = start_y - 25 + extra
            y2 = start_y + (len(lines) - 1) * step + 25
            self._v_bracket(bx, y1, y2)

            max_w = max(fnt.measure(t) for t in lines)
            self._label(h, tx + max_w / 2, "Pionowa", fnt)

    @staticmethod
    def _vertical_lines(u: Uniterm):
        """Zwraca listę wierszy oraz indeks wiersza z klamrą."""
        if u.bracket_on == "A":
            return [u.seq_csv, SEP, u.b, SEP, u.cond], 0
        return [u.a, SEP, u.seq_csv, SEP, u.cond], 2

    def _label(self, h, x, text, fnt):
        """Rysuje podpis pod rysunkiem."""
        self.create_text(
            x, h - LABEL_H / 2 - 3,
            text=text,
            fill=LINE_CLR,
            font=(fnt.actual("family"), fnt.actual("size") - 2),
            tags="uniterm",
        )