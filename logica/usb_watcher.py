"""logica/usb_watcher.py – Montaje automático de USB y exportación de logs usando pyudev"""
from __future__ import annotations

import errno
import logging
import subprocess
import threading
import time
from pathlib import Path

import pyudev
import psutil

from config import settings
from hardware.lcd import LCD
from logs import exportador_logs

_logger = logging.getLogger(__name__)

_CHECK_INTERVAL = 5        # segundos entre escaneos fallback
_CONFIRM_SECONDS = 8       # segundos para mostrar confirmación en LCD
_MOUNT_DIR = Path("/mnt/usb")

class USBWatcher(threading.Thread):
    """Hilo que monitorea eventos UDEV para montar USB y exportar logs automáticamente."""
    def __init__(self, lcd: LCD):
        super().__init__(daemon=True, name="USBWatcher")
        self._lcd = lcd
        self._vistos: set[str] = set()
        # Configurar monitor udev para particiones
        self._context = pyudev.Context()
        self._monitor = pyudev.Monitor.from_netlink(self._context)
        self._monitor.filter_by(subsystem='block', device_type='partition')

    def run(self) -> None:
        # Iniciar observador udev
        observer = pyudev.MonitorObserver(self._monitor, callback=self._udev_event)
        observer.start()
        # Poll fallback
        while True:
            self._poll_mounts()
            time.sleep(_CHECK_INTERVAL)

    def _udev_event(self, device: pyudev.Device) -> None:
        """Maneja eventos UDEV de adición y remoción de particiones."""
        action = device.action
        dev_node = device.device_node  # e.g. '/dev/sdb1'
        if action == 'add':
            # Montar y exportar
            self._mount_and_export(dev_node)
        elif action == 'remove':
            # Limpiar vistos y desmontar
            if dev_node in self._vistos:
                self._vistos.remove(dev_node)
            try:
                subprocess.run(['sudo', 'umount', str(_MOUNT_DIR)], check=True)
                _logger.info("Desmontado %s", dev_node)
            except subprocess.CalledProcessError:
                pass

    def _poll_mounts(self) -> None:
        # Detecta montajes manuales en /mnt/usb
        for part in psutil.disk_partitions(all=False):
            if Path(part.mountpoint) == _MOUNT_DIR and part.device not in self._vistos:
                self._mount_and_export(part.device)

    def _mount_and_export(self, dev_node: str) -> None:
        try:
            # Montar
            uid = subprocess.check_output(['id', '-u']).decode().strip()
            gid = subprocess.check_output(['id', '-g']).decode().strip()
            opts = f"uid={uid},gid={gid},umask=002"
            subprocess.run([
                'sudo', 'mount', '-t', 'vfat', dev_node, str(_MOUNT_DIR), '-o', opts
            ], check=True)
            _logger.info("Montado %s en %s", dev_node, _MOUNT_DIR)
            # Exportar logs
            carpeta = exportador_logs.export(_MOUNT_DIR)
            self._vistos.add(dev_node)
            _logger.info("Backup USB escrito en %s", carpeta)
            print(f"[DEBUG] Exported logs to: {carpeta}")
            # Mostrar confirmación en LCD
            site_name = settings.SITE_FILE.read_text(encoding="utf-8").strip() or "SIN_SITIO"
            self._lcd.mostrar_bienvenida(site_name)
            self._lcd.mostrar_estado_texto("BACKUP OK")
            time.sleep(_CONFIRM_SECONDS)
            self._lcd.mostrar_estado_texto("Esperando evento")
        except subprocess.CalledProcessError as e:
            _logger.error("Error al montar o exportar %s: %s", dev_node, e)
        except OSError as e:
            if e.errno == errno.EIO:
                _logger.error("I/O Error al exportar: %s", e)
                self._lcd.mostrar_estado_texto("USB I/O ERROR")
                time.sleep(_CONFIRM_SECONDS)
                self._lcd.mostrar_estado_texto("Esperando evento")
            else:
                _logger.exception("OS Error al exportar logs: %s", e)
        except Exception:
            _logger.exception("Error inesperado en USBWatcher._mount_and_export")
