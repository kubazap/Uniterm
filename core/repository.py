"""Warstwa dostępu do danych."""

from __future__ import annotations
import contextlib
from mysql.connector import pooling
from .models import Uniterm
from .settings import DB


class UnitermRepository:
    """DAO korzystający z puli połączeń MySQLConnector."""

    def __init__(self, **override_cfg):
        self.pool = pooling.MySQLConnectionPool(**(DB | override_cfg))

    def _conn(self):
        """Nowe połączenie z puli."""
        return self.pool.get_connection()

    def names(self) -> list[str]:
        """Zwraca listę wszystkich nazw unitermów posortowaną alfabetycznie."""
        sql = "SELECT name FROM uniterms ORDER BY name"
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor()
            try:
                cur.execute(sql)
                rows = cur.fetchall()
                return [r[0] for r in rows]
            finally:
                cur.close()

    def get(self, name: str) -> Uniterm | None:
        """Pobiera jeden rekord po nazwie; zwraca None, gdy brak."""
        sql = "SELECT * FROM uniterms WHERE name=%s"
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor(dictionary=True)
            try:
                cur.execute(sql, (name,))
                row = cur.fetchone()
                return Uniterm.from_row(row) if row else None
            finally:
                cur.close()

    def save(self, u: Uniterm) -> None:
        """Wstawia lub aktualizuje rekord (ON DUPLICATE KEY)."""
        sql = """
        INSERT INTO uniterms
          (name,description,a,b,cond,orientation,seq_str,bracket_on)
        VALUES
          (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
          description=VALUES(description),
          a=VALUES(a), b=VALUES(b), cond=VALUES(cond),
          orientation=VALUES(orientation),
          seq_str=VALUES(seq_str), bracket_on=VALUES(bracket_on)
        """
        vals = (
            u.name, u.description, u.a, u.b, u.cond,
            u.orientation, u.seq_csv, u.bracket_on,
        )
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor()
            try:
                cur.execute(sql, vals)
                cnx.commit()
            finally:
                cur.close()

    def delete(self, name: str) -> None:
        """Usuwa rekord o podanej nazwie."""
        sql = "DELETE FROM uniterms WHERE name=%s"
        with contextlib.closing(self._conn()) as cnx:
            cur = cnx.cursor()
            try:
                cur.execute(sql, (name,))
                cnx.commit()
            finally:
                cur.close()
