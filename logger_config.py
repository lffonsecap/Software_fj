"""
logger_config.py
----------------
Configura el archivo de logs donde se registran todos los eventos y errores.

Se usa el módulo estándar 'logging' de Python. El archivo se guarda en
la carpeta 'logs/' junto al proyecto, con el nombre 'software_fj.log'.
"""

import logging          # Módulo estándar para registrar eventos
from pathlib import Path  # Manejo de rutas independiente del sistema operativo

# Carpeta 'logs' ubicada al lado de este archivo
CARPETA_LOGS = Path(__file__).resolve().parent / "logs"
# Ruta completa del archivo de logs
ARCHIVO_LOG = CARPETA_LOGS / "software_fj.log"


def obtener_logger(nombre: str) -> logging.Logger:
    """Devuelve un logger configurado para escribir en el archivo de logs."""
    # Creamos la carpeta si todavía no existe (no falla si ya existe)
    CARPETA_LOGS.mkdir(exist_ok=True)

    # Todos los loggers del sistema cuelgan de "software_fj"
    logger = logging.getLogger(f"software_fj.{nombre}")

    # Configuramos el logger raíz del sistema una sola vez
    raiz = logging.getLogger("software_fj")
    if not raiz.handlers:
        # Registramosdesde nivel debug para no perder ningún evento
        raiz.setLevel(logging.DEBUG)
        # Manejador que escribe en el archivo (modo 'a' = agregar al final)
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
        # Formato: fecha | nivel | módulo | mensaje
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-22s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        manejador.setFormatter(formato)
        raiz.addHandler(manejador)

    return logger
