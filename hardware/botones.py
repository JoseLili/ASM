"""hardware/botones.py – Manejo de botones físicos con *hold‑time* obligatorio
=============================================================================

Gestiona los tres pulsadores conectados a la Raspberry Pi:
    • Simulacro   (GPIO 17)
    • Evacuación  (GPIO 22)
    • Paro / Reset (GPIO 27)

Cada botón debe mantenerse **pulsado al menos 5 segundos** para confirmar la
acción y evitar disparos accidentales por rebote o contactos sucios.

Se usa la librería **gpiozero** porque simplifica la gestión de *pull‑ups*,
*debounce* y eventos `when_held`.  Si prefieres RPi.GPIO puro, basta reescribir
la clase `ButtonWrapper` conservando la misma API.
"""
from __future__ import annotations

from typing import Callable, Final

try:
    from gpiozero import Button  # type: ignore
except ImportError as exc:  # pragma: no cover – se maneja en pruebas
    raise RuntimeError(
        "La librería gpiozero no está instalada. Ejecute 'pip install gpiozero'."
    ) from exc

from config import settings

__all__ = [
    "BotonController",
]

# ---------------------------------------------------------------------------
# Abstracción interna – deja el hook abierto para *mocking* en pruebas
# ---------------------------------------------------------------------------
class ButtonWrapper(Button):
    """Subclase de gpiozero.Button con parámetros por defecto.

    • `pull_up=True` porque los botones son NO contra GND.
    • `bounce_time` y `hold_time` salen del archivo de configuración.
    """

    def __init__(self, pin: int):
        super().__init__(
            pin=pin,
            pull_up=True,
            bounce_time=settings.DEBOUNCE_TIME,
            hold_time=settings.BUTTON_HOLD_TIME,
            hold_repeat=False,
        )


# ---------------------------------------------------------------------------
# Clase pública
# ---------------------------------------------------------------------------
class BotonController:
    """Administra callbacks para Simulacro, Evacuación y Paro.

    Parámetros
    ----------
    on_simulacro : Callable[[], None]
        Función a invocar tras un *hold* de 5 s en el botón de simulacro.
    on_evacuacion : Callable[[], None]
        Función a invocar tras un *hold* de 5 s en el botón de evacuación.
    on_paro : Callable[[], None]
        Función a invocar tras un *hold* de 5 s en el botón de paro / reset.
    """

    def __init__(
        self,
        on_simulacro: Callable[[], None],
        *,
        on_evacuacion: Callable[[], None],
        on_paro: Callable[[], None],
    ) -> None:
        self._btn_simulacro: Final[ButtonWrapper] = ButtonWrapper(settings.GPIO_SIMULACRO)
        self._btn_evacuacion: Final[ButtonWrapper] = ButtonWrapper(settings.GPIO_EVACUACION)
        self._btn_paro: Final[ButtonWrapper] = ButtonWrapper(settings.GPIO_PARO)

        # Asignar callbacks – se disparan sólo tras hold_time
        self._btn_simulacro.when_held = lambda _: on_simulacro()
        self._btn_evacuacion.when_held = lambda _: on_evacuacion()
        self._btn_paro.when_held = lambda _: on_paro()

    # ------------------------------------------------------------------
    # Métodos utilitarios
    # ------------------------------------------------------------------
    def close(self) -> None:
        """Libera los recursos GPIO (útil en pruebas o apagado limpio)."""
        self._btn_simulacro.close()
        self._btn_evacuacion.close()
        self._btn_paro.close()
