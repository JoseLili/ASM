"""boot/arranque.py – Banner de arranque y diagnóstico
=====================================================

• Muestra un banner Figlet + versión/autor durante `settings.BOOT_BANNER_SECONDS`.
• Ejecuta `boot.diagnostico.run()`; enseña el resultado `settings.DIAG_RESULT_SECONDS`.
• Cambia el estado a ESPERANDO (o PARO si falla) y devuelve el control a main.

Se importa y se llama desde `main.py` **antes** de crear el manejador de eventos:

    from boot import arranque
    estado_mgr = EstadoManager(Estado.DIAGNOSTICO)
    lcd = LCD()
    arranque.run(lcd, estado_mgr)
"""
from __future__ import annotations

import importlib
import logging
import sys
import time
from pathlib import Path
from textwrap import dedent

from config import settings
from config.estados import Estado
from hardware.lcd import LCD
from logica.estado_actual import EstadoManager

_logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# utilidades figlet / fallback
# ---------------------------------------------------------------------------

def _banner(site_name: str) -> str:
    """Genera banner Figlet o usa assets/bienvenida.txt si no hay pyfiglet."""
    try:
        import pyfiglet  # type: ignore

        return pyfiglet.figlet_format(site_name, width=80)
    except Exception:  # pragma: no cover
        ascii_path = settings.BASE_DIR / "assets" / "bienvenida.txt"
        if ascii_path.exists():
            return ascii_path.read_text(encoding="utf-8")
        return f"*** {site_name} ***"


# ---------------------------------------------------------------------------
# función pública
# ---------------------------------------------------------------------------

def run(lcd: LCD, estado_mgr: EstadoManager) -> None:
    """Ejecuta la secuencia de arranque.

    * `lcd` ya inicializado.
    * `estado_mgr` creado con Estado.DIAGNOSTICO.
    """
    site_name = settings.SITE_FILE.read_text(encoding="utf-8").strip() or "SIN_SITIO"

    # 1) Banner en consola
    banner_txt = _banner(site_name)
    print(banner_txt)

    # 2) Mostrar en LCD la cabecera
    lcd.clear()
    lcd.write_string(f"v{settings.VERSION} {settings.AUTHOR}")
    lcd.crlf()
    lcd.write_string(site_name[:16])
    time.sleep(settings.BOOT_BANNER_SECONDS)

    # 3) Diagnóstico
    ok, resumen = _run_diagnostico()
    estado_mgr.set(Estado.DIAGNOSTICO)
    lcd.clear()
    lcd.write_string("DIAGNOSTICO")
    lcd.crlf()
    lcd.write_string("OK" if ok else "FALLO")
    time.sleep(settings.DIAG_RESULT_SECONDS)

    # 4) Estado final
    estado_mgr.set(Estado.ESPERANDO if ok else Estado.PARO)
    lcd.clear()
    lcd.write_string("Esperando evento")
    if not ok:
        _logger.error("Fallo en diagnóstico: %s", resumen)
        sys.exit(1)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _run_diagnostico() -> tuple[bool, str]:
    """Importa dinámicamente boot.diagnostico.run()."""
    try:
        diagnostico = importlib.import_module("boot.diagnostico")
        return diagnostico.run()
    except ModuleNotFoundError:
        _logger.warning("boot/diagnostico.py no encontrado; se omite test HW")
        return True, "Sin diagnóstico"
    except Exception as exc:  # pragma: no cover
        _logger.exception("Error en diagnóstico: %s", exc)
        return False, "Excepción en diagnóstico"
