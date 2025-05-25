"""Punkt wejścia aplikacji (GUI)."""

from core.repository import UnitermRepository
from ui.main_window import MainWindow

if __name__ == "__main__":
    repo = UnitermRepository()
    MainWindow(repo).mainloop()