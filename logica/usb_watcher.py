"""logica/usb_watcher.py – Detecta memorias USB y exporta logs automáticamente."""
from __future__ import annotations

import logging
import threading
import time
from pathlib import Path

import psutil

from config import settings
from hardware.lcd import LCD
from logs import exportador_logs

_logger = logging.getLogger(__name__)

_CHECK_INTERVAL = 5  # segundos
_CONFIRM_SECONDS = 8  # mensaje en LCD

class USBWatcher(threading.Thread):
    def __init__(self, lcd: LCD):
        super().__init__(daemon=True, name="USBWatcher")
        self._lcd = lcd
        self._vistos: set[str] = set()

    # ---------------------------------------------------------
    def run(self) -> None:  # pragma: no cover (hilo while True)
        while True:
            try:
                self._scan()
            except Exception:
                _logger.exception("USBWatcher fallo en _scan")
            time.sleep(_CHECK_INTERVAL)

    # ---------------------------------------------------------
    def _scan(self) -> None:
        for part in psutil.disk_partitions(all=False):
            if part.device in self._vistos:
                continue
            if not part.opts.startswith("rw"):
                continue  # solo destinos de escritura
            if part.fstype.lower() not in {"vfat", "exfat", "ntfs", "ext4"}:
                continue

            mountpoint = Path(part.mountpoint)
            if mountpoint.is_dir():
                self._vistos.add(part.device)
                self._export(mountpoint)

    # ---------------------------------------------------------
    def _export(self, mountpoint: Path) -> None:
        try:
            carpeta = exportador_logs.export(mountpoint)
            _logger.info("Backup USB escrito en %s", carpeta)
            self._lcd.mostrar_bienvenida(settings.SITE_NAME)
            self._lcd.mostrar_estado_texto("BACKUP OK")
            time.sleep(_CONFIRM_SECONDS)
            self._lcd.mostrar_estado_texto("Esperando evento")
        except Exception:
            _logger.exception("Error al exportar logs a %s", mountpoint)
