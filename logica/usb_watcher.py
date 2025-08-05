"""logica/usb_watcher.py – Detecta memorias USB montadas en /mnt/usb y exporta logs automáticamente."""
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

_CHECK_INTERVAL = 5        # segundos entre escaneos
_CONFIRM_SECONDS = 8       # segundos para mostrar confirmación en LCD
_MOUNT_DIR = Path("/mnt/usb")

class USBWatcher(threading.Thread):
    """Hilo que vigila /mnt/usb y exporta logs cuando detecta un montaje de USB."""
    def __init__(self, lcd: LCD):
        super().__init__(daemon=True, name="USBWatcher")
        self._lcd = lcd
        self._vistos: set[str] = set()

    def run(self) -> None:  # pragma: no cover (loop infinito)
        while True:
            try:
                self._scan()
            except Exception:
                _logger.exception("USBWatcher fallo en _scan")
            time.sleep(_CHECK_INTERVAL)

    def _scan(self) -> None:
        # Solo interesa el punto de montaje fijo /mnt/usb
        for part in psutil.disk_partitions(all=False):
            # ya procesado?
            if part.device in self._vistos:
                continue
            # lectura/escritura
            if 'rw' not in part.opts:
                continue
            # tipos compatibles
            if part.fstype.lower() not in {"vfat", "exfat", "ntfs", "ext4"}:
                continue

            mountpoint = Path(part.mountpoint)
            # solo /mnt/usb
            if mountpoint != _MOUNT_DIR:
                continue

            # asegurar directorio y procesar
            if mountpoint.is_dir():
                self._vistos.add(part.device)
                self._export(mountpoint)

    def _export(self, mountpoint: Path) -> None:
        try:
            carpeta = exportador_logs.export(mountpoint)
            _logger.info("Backup USB escrito en %s", carpeta)
            # mostrar confirmación en LCD
            site_name = settings.SITE_FILE.read_text(encoding="utf-8").strip() or "SIN_SITIO"
            self._lcd.mostrar_bienvenida(site_name)
            self._lcd.mostrar_estado_texto("BACKUP OK")
            time.sleep(_CONFIRM_SECONDS)
            self._lcd.mostrar_estado_texto("Esperando evento")
        except Exception:
            _logger.exception("Error al exportar logs a %s", mountpoint)
