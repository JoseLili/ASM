"""main.py – Punto de arranque del Sistema de Alerta Sísmica BLTeech V2.23
============================================================================

Arranca el diagnóstico, muestra la bienvenida y lanza el bucle principal
(`ManejadorEventos`).  Pensado para ejecutarse con:

    $ python main.py            # durante pruebas manuales

o bien desde un servicio **systemd** que apunte a este archivo usando el venv.
"""
from __future__ import annotations

import signal
import sys
import time
from contextlib import suppress

from config import settings
from hardware.lcd import LCD
from logs.logger import Logger
from logica.estado_actual import EstadoManager, Estado
from logica.manejador_eventos import ManejadorEventos

# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------

def main() -> None:
    # Instancias principales
    estado_mgr = EstadoManager(Estado.DIAGNOSTICO)
    lcd = LCD()
    logger = Logger()

    # Mostrar bienvenida
    site_name = settings.SITE_FILE.read_text(encoding="utf-8").strip() or "SIN_SITIO"
    lcd.mostrar_bienvenida(site_name)
    time.sleep(1)

    # Pasar a stand‑by
    estado_mgr.set(Estado.ESPERANDO)
    lcd.mostrar_estado(Estado.ESPERANDO)

    manejador = ManejadorEventos(
        estado_mgr=estado_mgr,
        lcd_callback=lcd.mostrar_estado,
        log_callback=logger.registrar,
    )
    manejador.start()

    # ------------------------------------------------------------------
    # Señales para detener ordenadamente
    # ------------------------------------------------------------------
    stop = False

    def _graceful_exit(signum: int, _frame):
        nonlocal stop
        stop = True
        print(f"\n[INFO] Signal {signum} received – shutting down…", file=sys.stderr)
        
    signal.signal(signal.SIGINT, _graceful_exit)   # Ctrl+C
    signal.signal(signal.SIGTERM, _graceful_exit)  # systemd stop

    try:
        while not stop:
            time.sleep(1)
    finally:
        print("[INFO] Stopping ManejadorEventos…", file=sys.stderr)
        with suppress(Exception):
            manejador.stop()
        with suppress(Exception):
            lcd.close()
        print("[INFO] Shutdown complete.")


if __name__ == "__main__":
    main()
