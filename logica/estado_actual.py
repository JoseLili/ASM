"""logica/estado_actual.py – Gestión thread‑safe del estado global
=================================================================

Almacena el **estado operativo** vigente e informa a los observadores cuando
cambia.  Esto desacopla la lógica de eventos del hardware (Radio, Botones) y de
las salidas (LCD, Logger, Audio).

* Diseño **thread‑safe** con `threading.Lock`, ya que los callbacks de gpiozero
  se ejecutan en hilos.
* Patrón **publish / subscribe** minimalista: otras capas se suscriben para
  recibir notificaciones (`on_state_change(estado_nuevo)`).
"""
from __future__ import annotations

import logging
import threading
from typing import Callable, List

from config.estados import Estado

__all__ = [
    "EstadoManager",
]

_logger = logging.getLogger(__name__)


class EstadoManager:
    """Singleton light‑weight para gestionar el estado activo."""

    def __init__(self, estado_inicial: Estado = Estado.DIAGNOSTICO) -> None:
        self._estado: Estado = estado_inicial
        self._subs: List[Callable[[Estado], None]] = []
        self._lock = threading.Lock()

    # ---------------------------------------------------------------
    # Subscripción
    # ---------------------------------------------------------------
    def subscribe(self, callback: Callable[[Estado], None], *, fire_immediately: bool = False) -> None:
        """Registra un *callback* que se invocará al cambiar el estado.

        Si `fire_immediately` es True, el callback se llama de inmediato con el
        estado vigente.
        """
        with self._lock:
            self._subs.append(callback)
            if fire_immediately:
                callback(self._estado)

    # ---------------------------------------------------------------
    # Acceso y cambio de estado
    # ---------------------------------------------------------------
    @property
    def value(self) -> Estado:  # `estado_manager.value`
        with self._lock:
            return self._estado

    def set(self, nuevo_estado: Estado) -> None:
        """Actualiza el estado y notifica a subscriptores si cambió."""
        with self._lock:
            if nuevo_estado == self._estado:
                return  # sin cambio
            self._estado = nuevo_estado
            subs_copy = self._subs.copy()
        _logger.debug("Estado cambiado a %s", nuevo_estado)
        for callback in subs_copy:
            try:
                callback(nuevo_estado)
            except Exception:  # pragma: no cover
                _logger.exception("Callback de estado falló")
