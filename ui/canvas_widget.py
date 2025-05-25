"""Interfejs graficzny do rysowania unitermów."""
from __future__ import annotations
from tkinter import Canvas, font
from core.models import Uniterm

# ── stałe graficzne ──────────────────────────────────────────────────────────
SEP     = "     ;     "   # separator w nagłówku poziomym
SEP_V   = ";"             # separator w pionowej kolumnie
GRID_CLR = "#f3f3f3"
LINE_CLR = "#3F72AF"
LABEL_H  = 60


class UnitermCanvas(Canvas):
    """Canvas z siatką w tle i metodą draw(Uniterm, dx)."""

    # ───────────────────────── grid ───────────────────────────
    def __init__(self, master, grid: int = 14, **kw):
        super().__init__(master, bg="white", **kw)
        self.grid = grid
        self.bind("<Configure>", lambda _e: self._draw_grid())

    def _draw_grid(self) -> None:
        self.delete("grid")
        w, h, g = self.winfo_width(), self.winfo_height(), self.grid
        dash = (1, 3)
        for x in range(0, w, g):
            self.create_line(x, 0, x, h, fill=GRID_CLR,
                             dash=dash, tags="grid")
        for y in range(0, h, g):
            self.create_line(0, y, w, y, fill=GRID_CLR,
                             dash=dash, tags="grid")
        self.create_rectangle(0, h - LABEL_H, w, h,
                              outline="", tags="grid")

    # ───────────────────────── klamry ───────────────────────────────────────
    def _h_bracket(self, x1: int, x2: int, y: int) -> None:
        half = 6
        self.create_line(x1-20, y, x2, y,
                         fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x1-20, y-half, x1-20, y+half,
                         fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x2, y-half, x2, y+half,
                         fill=LINE_CLR, width=2, tags="uniterm")

    def _v_bracket(self, x: int, y1: int, y2: int) -> None:
        seg = 8
        self.create_line(x,   y1-8, x,   y2,
                         fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x-6, y1-8, x+seg, y1-8,
                         fill=LINE_CLR, width=2, tags="uniterm")
        self.create_line(x-6, y2,    x+seg, y2,
                         fill=LINE_CLR, width=2, tags="uniterm")

    def _bracket_over(self, text_id: int, pad: int = 4) -> None:
        x1, y1, x2, _ = self.bbox(text_id)
        self._h_bracket(x1 - pad, x2 + pad + 20, y1 - 8)

    # ─────────────────────── podpis pod rysunkiem ───────────────────
    def _label(self, h: int, x_center: float, text: str, fnt) -> None:
        self.create_text(
            x_center, h - LABEL_H/2 - 3,
            text=text,
            fill=LINE_CLR,
            font=(fnt.actual("family"), fnt.actual("size") - 2),
            tags="uniterm",
        )

    # ───────────────────────── rysowanie całości ─────────────────────
    def draw(self, u: Uniterm | None, dx: int = 0) -> None:
        """Renderuje przekazany `Uniterm`.  `dx` – dodatkowe przesunięcie X."""
        if u is None:
            return

        fnt = font.Font(family=u.font_family,
                        size=u.font_size,
                        weight="bold")
        h_canvas = self.winfo_height()

        # ═════════════════════════════════════════════════════════════
        # 1) POSTAĆ POZIOMA
        # ═════════════════════════════════════════════════════════════
        if u.orientation == "H":
            y0   = 95
            text = f"{u.a}{SEP} {u.b}{SEP} {u.cond}"
            w    = fnt.measure(text)
            x0   = 80 + dx

            self._h_bracket(x0+12, x0 + w + 16, y0)
            self.create_text(x0 + 3, y0 + 20,
                             text=text,
                             anchor="w",
                             font=fnt,
                             tags="uniterm")
            self._label(h_canvas, x0 + (w + 16)/2, "Pozioma", fnt)
            return      # ⬅ rysowanie zakończone

        # ═════════════════════════════════════════════════════════════
        # 2) POSTAĆ PIONOWA  (u.orientation == 'V')
        #    Używamy pól: x, y, cond2
        # ═════════════════════════════════════════════════════════════
        seq_all = [s for s in (u.x, u.y, u.cond2) if s]
        if not seq_all:
            seq_all = ["—"]

        first_elem = seq_all[0]
        rest_elems = seq_all[1:]

        # 2.1 Nagłówek
        if u.bracket_on.upper() == "A":
            heading = f"{first_elem} {SEP} {u.b} {SEP} {u.cond}"
            prefix  = ""                       
        else:
            heading = f"{u.a} {SEP} {first_elem} {SEP} {u.cond}"
            prefix  = f"{u.a} {SEP} "

        start_x  = dx + 45
        start_y  = 117
        tid = self.create_text(start_x, start_y,
                               text=heading,
                               anchor="w",
                               font=fnt,
                               tags="uniterm")
        self._bracket_over(tid, pad=6)

        # 2.2 pionowa kolumna pozostałych elementów (jeśli są)
        seq_lines: list[str] = []
        for item in rest_elems:
            seq_lines.extend([SEP_V, item]) 

        if seq_lines:
            seq_x  = start_x + fnt.measure(prefix)
            seq_y0 = start_y + 42
            step   = 42

            for i, t in enumerate(seq_lines):
                self.create_text(seq_x, seq_y0 + i * step,
                                 text=t,
                                 anchor="w",
                                 font=fnt,
                                 tags="uniterm")

            # pionowa klamra tylko przy kolumnie sekwencji
            y1 = seq_y0 - 6
            y2 = seq_y0 + (len(seq_lines)-1)*step + 6
            self._v_bracket(seq_x - 14, y1 - 36, y2 + 8)

        # podpis
        max_w = max(fnt.measure(s) for s in [heading] + seq_lines) or 1
        self._label(h_canvas, start_x + max_w/2, "Pionowa", fnt)
