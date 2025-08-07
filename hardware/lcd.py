"""hardware/lcd.py – Control de la pantalla HD44780 16×2 vía I²C (PCF8574)
============================================================================
Envuelve la librería **RPLCD** para que el resto de módulos sólo llame a
`mostrar_estado()` o `mostrar_bienvenida()` sin preocuparse por comandos low‑level.
"""
from __future__ import annotations
from config import settings
import logging
from contextlib import suppress
from typing import Final

try:
    # RPLCD >= 2.0
    from RPLCD.i2c import CharLCD  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "RPLCD no está instalado. Ejecuta 'pip install RPLCD[smbus]'."
    ) from exc

from config import settings
from config.estados import Estado

__all__: Final = ["LCD"]

_logger = logging.getLogger(__name__)


class LCD:
    """Abstracción mínima sobre el display 16×2."""

    def __init__(self) -> None:
        self._lcd = CharLCD(
            i2c_expander="PCF8574",
            address=settings.LCD_I2C_ADDRESS,
            port=settings.I2C_BUS,
            cols=settings.LCD_COLS,
            rows=settings.LCD_ROWS,
            charmap="A02",
            auto_linebreaks=False,
        )
        self.limpiar()

    # ------------------------------------------------------------------
    # Operaciones de alto nivel
    # ------------------------------------------------------------------
    def limpiar(self) -> None:
        with suppress(Exception):
            self._lcd.clear()

    def clear(self) -> None:
        """Alias para limpiar()."""
        self.limpiar()

    def write_string(self, texto: str) -> None:
        """Alias a CharLCD.write_string()."""
        with suppress(Exception):
            self._lcd.write_string(texto)

    def crlf(self) -> None:
        """Alias a CharLCD.crlf()."""
        with suppress(Exception):
            self._lcd.crlf()

    def mostrar_estado_texto(self, texto: str) -> None:
        """Escribe un texto personalizado en la segunda línea de la LCD."""
        try:
            # Sitúa el cursor al inicio de la segunda línea
            self._lcd.cursor_pos = (1, 0)
            # Escribe el texto (recorta o completa al ancho)
            self._lcd.write_string(texto[: settings.LCD_COLS].ljust(settings.LCD_COLS))
        except Exception:
             _logger.exception("Error en mostrar_estado_texto(%r)", texto)
    def mostrar_bienvenida(self, sitio: str) -> None:
        """Muestra la versión, autor y nombre de sitio al arranque."""
        self.limpiar()
        linea1 = f"v{settings.VERSION} {settings.AUTHOR}"[: settings.LCD_COLS]
        linea2 = sitio[: settings.LCD_COLS]
        self._lcd.write_string(linea1.ljust(settings.LCD_COLS))
        self._lcd.crlf()
        self._lcd.write_string(linea2.ljust(settings.LCD_COLS))

    def mostrar_estado(self, estado: Estado) -> None:
        """Actualiza la segunda línea según `Estado.to_lcd()`."""
        texto = estado.to_lcd()
        if not texto:
            return
        # Mantiene la primera línea (bienvenida) intacta y sobreescribe la 2ª
        self._lcd.cursor_pos = (1, 0)
        self._lcd.write_string(texto.ljust(settings.LCD_COLS))

    # ------------------------------------------------------------------
    # Limpieza explícita (opcional)
    # ------------------------------------------------------------------
    def close(self) -> None:
        with suppress(Exception):
            self._lcd.close(clear=True)
