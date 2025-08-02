"""logs/logger.py – Registro de eventos del Sistema de Alerta Sísmica
======================================================================

Registra cada transición de estado en un archivo rotativo diario
(`logs/eventos.log`). La línea tiene formato CSV sencillo:

ISO_DATETIME, NOMBRE_SITIO, ESTADO, DETALLE_OPCIONAL

Ejemplo:
```
2025-08-01T19:32:10, LAB_FÍSICA, ALERTA, 
```
"""
from __future__ import annotations

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from config import settings
from config.estados import Estado

__all__: Final = ["Logger"]


class Logger:
    """Inicializa `logging` y ofrece `registrar()` como API plana."""

    def __init__(self) -> None:
        # Asegurar carpeta de logs
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        self._log_path: Path = settings.LOG_FILE
        self._site: str = self._leer_nombre_sitio()

        # Configura logger stdlib (nivel INFO) + manejador rotativo diario (7 días)
        self._logger = logging.getLogger("alerta.logger")
        self._logger.setLevel(logging.INFO)

        handler = logging.handlers.TimedRotatingFileHandler(
            self._log_path, when="midnight", backupCount=7, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s,%(message)s", "%Y-%m-%dT%H:%M:%S"))
        self._logger.addHandler(handler)

        # También a consola en DEBUG opcional
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        self._logger.addHandler(stream)

    # ------------------------------------------------------------------
    def registrar(self, estado: Estado, detalle: str | None = "") -> None:
        """Escribe una línea de log con hora UTC, sitio y estado."""
        linea = f"{self._site},{estado.name},{detalle or ''}"
        self._logger.info(linea)

    # ------------------------------------------------------------------
    @staticmethod
    def _leer_nombre_sitio() -> str:
        try:
            return settings.SITE_FILE.read_text(encoding="utf-8").strip() or "SIN_SITIO"
        except FileNotFoundError:
            return "SIN_SITIO"
