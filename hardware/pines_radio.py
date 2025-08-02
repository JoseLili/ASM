"""hardware/pines_radio.py – Monitoreo de la señal del radio Midland WR‑120
===========================================================================

El relé del radio es **normalmente abierto (NO)** y se cierra cuando inicia la
alerta.  El pin (GPIO 4) por tanto permanece en **alto** gracias a la resistencia
``pull_up`` y cae a **bajo** al activarse la alarma.

Se expone la clase ``RadioMonitor`` con eventos de *inicio* y *fin* de alerta,
permitiendo a la lógica superior cambiar estado y reproducir audio.
"""
from __future__ import annotations

from typing import Callable, Final

try:
    from gpiozero import Button  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Se requiere gpiozero. Ejecuta 'pip install gpiozero'.") from exc

from config import settings

__all__ = [
    "RadioMonitor",
]


class RadioMonitor:
    """Envuelve el GPIO asociado al relé del Midland.

    Parámetros
    ----------
    on_start : Callable[[], None]
        Callback llamado al *cerrarse* el contacto (flanco descendente → alerta).
    on_end : Callable[[], None] | None, opcional
        Se llama al *abrirse* nuevamente el contacto, si se suministra.
    """

    def __init__(
        self,
        on_start: Callable[[], None],
        *,
        on_end: Callable[[], None] | None = None,
    ) -> None:
        self._btn: Final[Button] = Button(
            pin=settings.GPIO_RADIO,
            pull_up=True,
            bounce_time=settings.DEBOUNCE_TIME,
        )

        # gpiozero.Button dispara "when_pressed" cuando el nivel pasa a LOW si
        # pull_up=True.  Equivale al cierre del relé (inicio de alerta).
        self._btn.when_pressed = lambda _: on_start()

        if on_end is not None:
            # "when_released" → nivel regresa a HIGH (fin de alerta)
            self._btn.when_released = lambda _: on_end()

    # ------------------------------------------------------------------
    # Limpieza
    # ------------------------------------------------------------------
    def close(self) -> None:
        self._btn.close()
