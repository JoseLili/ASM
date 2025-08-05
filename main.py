"""main.py – Punto de arranque del Sistema de Alerta Sísmica BLTeech V2.23
============================================================================

Arranca el diagnóstico, muestra la bienvenida y lanza el bucle principal
(`ManejadorEventos`).  Pensado para ejecutarse con:

    $ python main.py            # durante pruebas manuales

o bien desde un servicio **systemd** que apunte a este archivo usando el venv.
"""
from __future__ import annotations

from gpiozero import Device
from gpiozero.pins.pigpio import PiGPIOFactory
Device.pin_factory = PiGPIOFactory()

import signal
import sys
import time
from contextlib import suppress

from config import settings
from hardware.lcd import LCD
from logs.logger import Logger
from logica.estado_actual import EstadoManager, Estado
from logica.manejador_eventos import ManejadorEventos
from logica.usb_watcher import USBWatcher

# ---------------------------------------------------------------------------
# Inicialización
# ---------------------------------------------------------------------------

def main() -> None:
    # Instancias principales
    estado_mgr = EstadoManager(Estado.DIAGNOSTICO)
    lcd = LCD()
    logger = Logger()
    
    # ── 1) Splash inicial ──────────────────────────────────────────────
    site_name = settings.SITE_FILE.read_text(encoding="utf-8").strip() or "SIN_SITIO"
    # muestra versión/aut​or + “Bienvenido”
    lcd.mostrar_bienvenida("Bienvenido")
    time.sleep(settings.BOOT_BANNER_SECONDS)

    # ── 2) Pantalla estática de “sitio” y estado inicial ─────────────
    lcd.limpiar()
    # Línea 1: Sitio: Coyuya
    line1 = f"Sitio: {site_name}"[: settings.LCD_COLS]
    lcd.write_string(line1.ljust(settings.LCD_COLS))
    lcd.crlf()
    # Línea 2: Esperando evento...
    line2 = f"{Estado.ESPERANDO.to_lcd()}..."[: settings.LCD_COLS]
    lcd.write_string(line2.ljust(settings.LCD_COLS))

    # Aviso interno / log inicial
    estado_mgr.set(Estado.ESPERANDO)

    manejador = ManejadorEventos(
        estado_mgr=estado_mgr,
        lcd_callback=lcd.mostrar_estado,
        log_callback=logger.registrar,
    )
    manejador.start()


    # ── Lanzar el USBWatcher para exportar logs al insertar USB ─────────
    usb_watcher = USBWatcher(lcd)
    usb_watcher.start()
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
