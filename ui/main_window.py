"""Okno główne."""

from __future__ import annotations
import copy
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
    """Trzy-kolumnowy układ: lista, rysunek, panel edycji."""

    def __init__(self, repo: UnitermRepository):
        super().__init__(themename="flatly")
        self.repo = repo
        self.cur: Uniterm | None = None       
        self.preview: Uniterm | None = None  

        self._build_ui()
        self._refresh_list()

    # ---------- Budowanie UI ----------
    def _build_ui(self):
        self.title("Uniterm")
        width, height = 1200, 500
        self.resizable(False, False)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{width}x{height}+{(sw - width)//2}+{(sh - height)//2}")

        root = tb.PanedWindow(self, orient=HORIZONTAL)
        root.pack(fill=BOTH, expand=True)

        # Kolumna 1 – lista unitermów
        nav = tb.Frame(root, padding=10); root.add(nav, weight=0)
        tb.Label(nav, text="Lista unitermów", font=("Segoe UI", 12, "bold"))\
          .pack(anchor="w", pady=(0, 15))
        self.lb = tk.Listbox(nav, width=25, font=("Segoe UI", 10))
        self.lb.pack(fill=BOTH, expand=True, pady=(0, 8))
        self.lb.bind("<<ListboxSelect>>", self.on_select)

        btn = lambda t, style, cmd: tb.Button(nav, text=t, bootstyle=style,
                                              command=cmd).pack(fill=X, pady=2)
        btn("➕ Nowy",   SUCCESS, self.on_new)
        btn("💾 Zapisz", PRIMARY, self.on_save)
        btn("🗑 Usuń",   DANGER,  self.on_delete)

        # Kolumna 2 – rysunek
        self.canvas = UnitermCanvas(root, width=650, height=500)
        root.add(self.canvas, weight=1)

        # Kolumna 3 – panel edycji
        self._build_edit_panel(root)

    def _build_edit_panel(self, parent):
        frm = tb.Frame(parent, padding=10)
        parent.add(frm, weight=0)
        self.edit = {}

        # ---------- Nagłówek ----------
        tb.Label(frm, text="Edycja parametrów", font=("Segoe UI", 12, "bold"))\
        .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,15))

        self._entry(frm, "Nazwa:",           1, "name", label_width=8)
        self._entry(frm, "A:",               2, "a",    label_width=8)
        self._entry(frm, "B:",               3, "b",    label_width=8)
        self._entry(frm, "u:",               4, "cond", label_width=8)
        self._entry(frm, "Seq (x,y,z):",     5, "seq",  label_width=10)

        frm.columnconfigure(1, weight=1)

        # ---------- Zamień A/B ----------
        tb.Label(frm, text="Zamień:", width=8, anchor="e")\
        .grid(row=6, column=0, sticky="e", padx=(0,5), pady=(10,2))
        self.swap_val = tk.StringVar(value="A")
        swap_frame = tb.Frame(frm)
        swap_frame.grid(row=6, column=1, sticky="w", pady=(10,2))
        for v in ("A","B"):
            tb.Radiobutton(
                swap_frame, text=v, variable=self.swap_val, value=v,
                bootstyle="info-toolbutton", width=3
            ).pack(side="left", padx=2)

        # ---------- Przycisk Zamiana ----------
        tb.Button(
            frm, text="🔄 Zamiana → V",
            bootstyle=WARNING,
            command=self.on_swap
        ).grid(row=7, column=0, columnspan=2, sticky="we", pady=(15,0))


    def _entry(self, parent, text, row, key, label_width=8):
        """Pomocnik: tworzy Label + Entry w jednym wierszu."""
        tb.Label(parent, text=text, width=label_width, anchor="e")\
        .grid(row=row, column=0, sticky="e", padx=(0,5), pady=2)
        ent = tb.Entry(parent)
        ent.grid(row=row, column=1, sticky="we", pady=2)
        self.edit[key] = ent

    # ---------- Obsługa listy ----------
    def _refresh_list(self):
        """Aktualizuje listbox nazwami z bazy."""
        self.lb.delete(0, "end")
        for name in self.repo.names():
            self.lb.insert("end", name)

    def on_select(self, *_):
        """Kliknięcie w liście – ładuj rekord i rysuj."""
        if not (sel := self.lb.curselection()):
            return
        if (u := self.repo.get(self.lb.get(sel[0]))) is None:
            return
        self.cur, self.preview = u, None
        self._populate_panel(u)
        self._redraw()

    # ---------- Przyciski CRUD ----------
    def on_new(self):
        self.lb.selection_clear(0, "end")
        self.cur, self.preview = None, None
        self._clear_panel()
        self.canvas.delete("uniterm")

    def on_save(self):
        u = self._collect_from_panel()
        if not u.name:
            messagebox.showwarning("Brak nazwy", "Pole „Nazwa” nie może być puste.")
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


    def on_swap(self):
        base = self._collect_from_panel()
        if not base.name:                     
            base.name = "<podgląd>"
        self.cur = base
        self.preview = horizontal_to_vertical(
            base, on=self.swap_val.get())
        self._redraw()

    # ---------- Rysunek ----------
    def _redraw(self):
        self.canvas.delete("uniterm")
        if self.cur:
            self.canvas.draw(self.cur, dx=0)
        if self.preview:
            self.canvas.draw(self.preview, dx=350)

    # ---------- Panel edycji ----------
    def _populate_panel(self, u: Uniterm):
        self._clear_panel()
        self.edit["name"].insert(0, u.name)
        self.edit["a"].insert(0, u.a)
        self.edit["b"].insert(0, u.b)
        self.edit["cond"].insert(0, u.cond)
        if u.seq:
            self.edit["seq"].insert(0, ", ".join(u.seq))
        self.swap_val.set("A")

    def _clear_panel(self):
        for ent in self.edit.values():
            ent.delete(0, "end")
        self.swap_val.set("A")

    def _collect_from_panel(self) -> Uniterm:
        seq_list = [s.strip() for s in self.edit["seq"].get().split(",") if s.strip()]
        return Uniterm(
            name=self.edit["name"].get().strip(),
            a=self.edit["a"].get().strip(),
            b=self.edit["b"].get().strip(),
            cond=self.edit["cond"].get().strip(),
            seq=seq_list,
        )