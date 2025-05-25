"""Warstwa dostępu do danych."""

from __future__ import annotations
import contextlib
from mysql.connector import pooling
from .models import Uniterm
from .settings import DB


class UnitermRepository:
    """DAO z pulą połączeń."""

    # ────────────────────────────────────────────────────────────────
    #  Konstruktor  +  pomocnicze
    # ────────────────────────────────────────────────────────────────
    def __init__(self, **override_cfg):
        cfg = DB | override_cfg
        self.pool = pooling.MySQLConnectionPool(**cfg)

    def _conn(self):
        """Zwraca połączenie z puli."""
        return self.pool.get_connection()

    # ────────────────────────────────────────────────────────────────
    #  SELECT  lista nazw
    # ────────────────────────────────────────────────────────────────
    def names(self) -> list[str]:
        """Alfabetycznie posortowana lista nazw unitermów."""
        sql = "SELECT name FROM uniterms ORDER BY name"
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor()
            try:
                cur.execute(sql)
                return [row[0] for row in cur.fetchall()]
            finally:
                cur.close()

    # ────────────────────────────────────────────────────────────────
    #  SELECT  pojedynczy rekord
    # ────────────────────────────────────────────────────────────────
    def get(self, name: str) -> Uniterm | None:
        sql = "SELECT * FROM uniterms WHERE name=%s"
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor(dictionary=True)
            try:
                cur.execute(sql, (name,))
                row = cur.fetchone()
                return Uniterm.from_row(row) if row else None
            finally:
                cur.close()

    # ────────────────────────────────────────────────────────────────
    #  INSERT / UPDATE (UPSERT)
    # ────────────────────────────────────────────────────────────────
    def save(self, u: Uniterm) -> None:
        sql = """
        INSERT INTO uniterms
          (name, description, a, b, cond,
           x, y, cond2, orientation, bracket_on)
        VALUES
          (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          description = VALUES(description),
          a           = VALUES(a),
          b           = VALUES(b),
          cond        = VALUES(cond),
          x           = VALUES(x),
          y           = VALUES(y),
          cond2       = VALUES(cond2),
          orientation = VALUES(orientation),
          bracket_on  = VALUES(bracket_on)
        """
        vals = (
            u.name, u.description, u.a, u.b, u.cond,
            u.x, u.y, u.cond2,
            u.orientation, u.bracket_on,
        )
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor()
            try:
                cur.execute(sql, vals)
                cnx.commit()
            finally:
                cur.close()

    # ────────────────────────────────────────────────────────────────
    #  DELETE
    # ────────────────────────────────────────────────────────────────
    def delete(self, name: str) -> None:
        sql = "DELETE FROM uniterms WHERE name=%s"
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor()
            try:
                cur.execute(sql, (name,))
                cnx.commit()
            finally:
                cur.close()
