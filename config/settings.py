"""
Configuración central del Sistema de Alerta Sísmica Automatizada V2.23 (BLTeech)
-------------------------------------------------------------------------------
Define **todas** las constantes y rutas que emplean los demás módulos. Modifica
únicamente este archivo para cambiar pines, tiempos o rutas entre despliegues;
así evitamos la propagación de valores mágicos.
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas base
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
ASSETS_DIR: Path = BASE_DIR / "assets" / "sonidos"
LOGS_DIR: Path = BASE_DIR / "logs"
CONFIG_DIR: Path = BASE_DIR / "config"

# Archivos de audio (MP3)
AUDIO_ALERTA: Path = ASSETS_DIR / "alerta_sismica.mp3"
AUDIO_SIMULACRO: Path = ASSETS_DIR / "simulacro.mp3"
AUDIO_EVACUACION: Path = ASSETS_DIR / "evacuacion.mp3"

# Archivo con el nombre del sitio de despliegue (editable sin tocar código)
SITE_FILE: Path = CONFIG_DIR / "sitio.txt"

# Log principal del sistema
LOG_FILE: Path = LOGS_DIR / "eventos.log"

# ---------------------------------------------------------------------------
# GPIO – asignaciones de pines Raspberry Pi 4 B
# ---------------------------------------------------------------------------
GPIO_RADIO: int = 4        # Entrada – Relé Midland WR‑120 (NO, pull‑up)
GPIO_SIMULACRO: int = 17   # Botón de simulacro (NO, pull‑up)
GPIO_EVACUACION: int = 22  # Botón de evacuación (NO, pull‑up)
GPIO_PARO: int = 27        # Botón de paro de emergencia / reset (NO, pull‑up)

# ---------------------------------------------------------------------------
# Pantalla LCD I²C HD44780 + backpack PCF8574
# ---------------------------------------------------------------------------
I2C_BUS: int = 1
LCD_I2C_ADDRESS: int = 0x27
LCD_COLS: int = 16
LCD_ROWS: int = 2

# ---------------------------------------------------------------------------
# Tiempos y umbrales (segundos)
# ---------------------------------------------------------------------------
DEBOUNCE_TIME: float = 0.05       # Antirebote de botones
BUTTON_HOLD_TIME: float = 5.0    # Tiempo que deben mantenerse pulsados los
                                 # botones para activar su rutina (anti‑ruido)

# Duración de cada audio
ALERTA_DURATION: int = 180        # Audio de alerta sísmica (GPIO_RADIO)
SIMULACRO_DURATION: int = 80      # Audio de simulacro
EVACUACION_DURATION: int = 80     # Audio de evacuación

# Tiempo máximo permitido antes de auto‑paro (watchdog) – >= mayor audio + margen
WATCHDOG_TIMEOUT: int = 200       # Cortará cualquier audio que exceda este valor


# ---------------------------------------------------------------------------
# Duracion del mensaje en la pantalla LCD
# ---------------------------------------------------------------------------

BOOT_BANNER_SECONDS = 8      # bienvenida
DIAG_RESULT_SECONDS = 4      # resultado diagnóstico

# ---------------------------------------------------------------------------
# Texto de bienvenida (Figlet o fallback ASCII)
# ---------------------------------------------------------------------------

VERSION: str = "2.23"
AUTHOR: str = "BLTeech"
WELCOME_TEMPLATE: str = (
    "{figlet}\n"  # Se sustituye con banner Figlet generado en runtime
    "Sistema Alerta Sísmica v{version} – {author}"
)

__all__ = [
    # rutas base
    "BASE_DIR",
    "ASSETS_DIR",
    "LOGS_DIR",
    "CONFIG_DIR",
    "AUDIO_ALERTA",
    "AUDIO_SIMULACRO",
    "AUDIO_EVACUACION",
    "SITE_FILE",
    "LOG_FILE",
    # GPIO
    "GPIO_RADIO",
    "GPIO_SIMULACRO",
    "GPIO_EVACUACION",
    "GPIO_PARO",
    # LCD
    "I2C_BUS",
    "LCD_I2C_ADDRESS",
    "LCD_COLS",
    "LCD_ROWS",
    # tiempos
    "DEBOUNCE_TIME",
    "BUTTON_HOLD_TIME",
    "ALERTA_DURATION",
    "SIMULACRO_DURATION",
    "EVACUACION_DURATION",
    "WATCHDOG_TIMEOUT",
    # meta
    "VERSION",
    "AUTHOR",
    "WELCOME_TEMPLATE",
]
