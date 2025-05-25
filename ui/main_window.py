"""Okno główne GUI – lista ▸ rysunek ▸ panel edycji."""

from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from tkinter import messagebox

from core.models import Uniterm
from core.repository import UnitermRepository
from core.services import horizontal_to_vertical
from .canvas_widget import UnitermCanvas


class MainWindow(tb.Window):
    """Trzy-kolumnowy układ: lista ▸ canvas ▸ edycja."""

    # ──────────────────────────── inicjalizacja ────────────────────────────
    def __init__(self, repo: UnitermRepository):
        super().__init__(themename="flatly")

        self.repo:    UnitermRepository = repo
        self.cur:     Uniterm | None    = None     # edytowany poziomy
        self.preview: Uniterm | None    = None     # podgląd pionowy

        self._build_ui()
        self._refresh_list()

    # ────────────────────────── budowanie interfejsu ───────────────────────
    def _build_ui(self) -> None:
        # okno
        self.title("Uniterm")
        W, H = 1200, 550
        sx, sy = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{W}x{H}+{(sx-W)//2}+{(sy-H)//2}")
        self.resizable(False, False)

        # główny PanedWindow
        root = tb.PanedWindow(self, orient=HORIZONTAL)
        root.pack(fill=BOTH, expand=True)

        # kolumna 1 – lista
        self._build_nav(root)

        # kolumna 2 – canvas
        self.canvas = UnitermCanvas(root, width=650, height=500)
        root.add(self.canvas, weight=1)

        # kolumna 3 – panel edycji
        self._build_edit(root)

    # ♦ NAVIGATION / lista ──────────────────────────────────────────────────
    def _build_nav(self, parent) -> None:
        nav = tb.Frame(parent, padding=10); parent.add(nav, weight=0)

        tb.Label(nav, text="Lista unitermów",
                 font=("Segoe UI", 12, "bold"))\
          .pack(anchor="w", pady=(0, 15))

        self.lb = tk.Listbox(nav, width=25, font=("Segoe UI", 10))
        self.lb.pack(fill=BOTH, expand=True, pady=(0, 8))
        self.lb.bind("<<ListboxSelect>>", self.on_select)

        for lbl, style, cmd in (
            ("➕ Nowy",   SUCCESS, self.on_new),
            ("💾 Zapisz", PRIMARY, self.on_save),
            ("🗑 Usuń",   DANGER,  self.on_delete),
        ):
            tb.Button(nav, text=lbl, bootstyle=style, command=cmd)\
              .pack(fill=X, pady=2)

    # ♦ EDIT PANEL ─────────────────────────────────────────────────────────
    def _build_edit(self, parent) -> None:
        frm = tb.Frame(parent, padding=10); parent.add(frm, weight=0)
        self.edit: dict[str, tk.Entry] = {}

        # nagłówek
        tb.Label(frm, text="Edycja parametrów",
                 font=("Segoe UI", 12, "bold"))\
          .grid(row=0, column=0, columnspan=2,
                sticky="w", pady=(0, 15))

        # ── NAZWA ───────────────────
        self._add_entry(frm, "Nazwa:", 1, "name")
        frm.grid_rowconfigure(1, pad=15)

        # ── UNITERM #1  (A, B, u) ─────────────────────────────────────────
        tb.Label(frm, text="Uniterm #1",
                 font=("Segoe UI", 10, "bold"),
                 foreground="#3F72AF")\
          .grid(row=2, column=0, columnspan=2,
                sticky="w", pady=(4, 2))

        self._add_entry(frm, "A:",   3, "a")
        self._add_entry(frm, "B:",   4, "b")
        self._add_entry(frm, "u:",   5, "cond")

        # separator graficzny
        tb.Separator(frm, orient=HORIZONTAL)\
          .grid(row=6, column=0, columnspan=2,
                sticky="we", pady=10)

        # ── UNITERM #2  (X, Y, u₂) ────────────────────────────────────────
        tb.Label(frm, text="Uniterm #2",
                 font=("Segoe UI", 10, "bold"),
                 foreground="#3F72AF")\
          .grid(row=7, column=0, columnspan=2,
                sticky="w", pady=(0, 2))

        self._add_entry(frm, "X:",    8,  "x")
        self._add_entry(frm, "Y:",    9,  "y")
        self._add_entry(frm, "u₂:",   10, "cond2")

        # kolumna z Entry rozciąga się
        frm.columnconfigure(1, weight=1)

        # ── Zamiana A / B + przycisk  ────────────────────────────────────
        tb.Label(frm, text="Zamień:", anchor="e", width=8)\
          .grid(row=11, column=0, sticky="e",
                padx=(0, 5), pady=(12, 4))

        self.swap = tk.StringVar(value="A")
        rb_box = tb.Frame(frm)
        rb_box.grid(row=11, column=1, sticky="w", pady=(20, 6))

        for val in ("A", "B"):
            tb.Radiobutton(rb_box, text=val,
                           variable=self.swap, value=val,
                           bootstyle="info-toolbutton",
                           width=3)\
              .pack(side="left", padx=4)       

        # przycisk „Zamiana → V”
        tb.Button(frm, text="🔄 Zamiana → V",
                  bootstyle=WARNING,
                  command=self.on_swap)\
          .grid(row=12, column=0, columnspan=2,
                sticky="we", pady=(18, 0))

    # helper do dodawania pól
    def _add_entry(self, parent, label, row, key) -> None:
        tb.Label(parent, text=label, width=8, anchor="e")\
          .grid(row=row, column=0, sticky="e",
                padx=(0, 5), pady=2)
        ent = tb.Entry(parent)
        ent.grid(row=row, column=1, sticky="we", pady=2)
        self.edit[key] = ent

    # ───────────────────────────  listbox  ────────────────────────────────
    def _refresh_list(self) -> None:
        self.lb.delete(0, "end")
        for name in self.repo.names():
            self.lb.insert("end", name)

    def on_select(self, *_):
        if not (sel := self.lb.curselection()):
            return
        if (u := self.repo.get(self.lb.get(sel[0]))) is None:
            return
        self.cur, self.preview = u, None
        self._fill_panel(u)
        self._redraw()

    # ───────────────────────────  CRUD  ───────────────────────────────────
    def on_new(self):
        self.lb.selection_clear(0, "end")
        self.cur = self.preview = None
        self._clear_panel()
        self.canvas.delete("uniterm")

    def on_save(self):
        u = self._collect_panel()
        if not u.name:
            messagebox.showwarning("Brak nazwy",
                                   "Pole «Nazwa» nie może być puste.")
            return
        self.repo.save(u)
        self.cur, self.preview = u, None
        self._refresh_list()
        self._redraw()
        ToastNotification(title="Zapisano",
                          message=f"Uniterm „{u.name}” został zapisany.",
                          duration=2000, bootstyle=SUCCESS).show_toast()

    def on_delete(self):
        if not self.cur:
            return
        if messagebox.askyesno("Potwierdź",
                               f"Czy na pewno usunąć „{self.cur.name}”?"):
            self.repo.delete(self.cur.name)
            self.on_new()
            self._refresh_list()

    # ───────────────────────  Zamiana poziomej → pionowa  ────────────────
    def on_swap(self):
        base = self._collect_panel()
        if not base.name:
            base.name = "<podgląd>"
        self.cur = base
        self.preview = horizontal_to_vertical(base, on=self.swap.get())
        self._redraw()

    # ───────────────────────────  Canvas  ────────────────────────────────
    def _redraw(self) -> None:
        self.canvas.delete("uniterm")
        if self.cur:
            self.canvas.draw(self.cur, dx=0)
        if self.preview:
            self.canvas.draw(self.preview, dx=350)

    # ───────────────────────────  panel helpery  ─────────────────────────
    def _fill_panel(self, u: Uniterm) -> None:
        self._clear_panel()
        for k, ent in self.edit.items():
            ent.insert(0, getattr(u, k, ""))
        self.swap.set("A")

    def _clear_panel(self) -> None:
        for ent in self.edit.values():
            ent.delete(0, "end")
        self.swap.set("A")

    def _collect_panel(self) -> Uniterm:
        data = {k: ent.get().strip() for k, ent in self.edit.items()}
        return Uniterm(**data)
