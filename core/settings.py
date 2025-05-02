"""Stałe konfiguracyjne aplikacji."""

DEFAULT_FONT_FAMILY = "Calibri"      
DEFAULT_FONT_SIZE   = 14             

# Parametry połączenia z MySQL 
DB = dict(
    host="localhost",
    user="root",
    password="",
    database="unitermdb",
    autocommit=True,
    pool_name="uniterm_pool",
    pool_size=5,
)
