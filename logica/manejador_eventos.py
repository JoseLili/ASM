"""logica/manejador_eventos.py – Núcleo de orquestación
=====================================================

Conecta radio, botones, audio, LCD y logger usando una cola de eventos y un
hilo dedicado.  Tras reproducir cualquier audio, vuelve automáticamente a
`Estado.ESPERANDO`.
"""
from __future__ import annotations

import queue
import threading
import time
from enum import Enum, auto
from typing import Callable, Optional
from datetime import datetime
from config import settings
from config.estados import Estado
from hardware import sonido
from hardware.botones import BotonController
from hardware.pines_radio import RadioMonitor
from logica.estado_actual import EstadoManager

__all__ = [
    "ManejadorEventos",
]


class _Evt(Enum):
    ALERTA = auto()
    SIMULACRO = auto()
    EVACUACION = auto()
    PARO = auto()
    FIN_AUDIO = auto()


class ManejadorEventos:
    """Gestiona transiciones de estado de forma thread‑safe."""

    def __init__(
        self,
        estado_mgr: EstadoManager,
        lcd_callback: Callable[[Estado], None],
        log_callback: Callable[[Estado], None],
    ) -> None:
        self._estado_mgr = estado_mgr
        self._lcd_cb = lcd_callback
        self._log_cb = log_callback

        self._cola: "queue.Queue[_Evt]" = queue.Queue()
        self._run = True
        self._thr = threading.Thread(target=self._loop, daemon=True)

        # Hardware ------------------------------------------------------
        self._botones = BotonController(
            on_simulacro=lambda: self._cola.put(_Evt.SIMULACRO),
            on_evacuacion=lambda: self._cola.put(_Evt.EVACUACION),
            on_paro=lambda: self._cola.put(_Evt.PARO),
        )
        self._radio = RadioMonitor(on_start=lambda: self._cola.put(_Evt.ALERTA))

        # Timer para saber cuándo termina audio
        self._audio_timer: Optional[threading.Timer] = None

    # -----------------------------------------------------------------
    def start(self) -> None:
        self._thr.start()

    def stop(self) -> None:
        self._run = False
        self._cola.put(_Evt.PARO)
        self._thr.join(timeout=2)
        self._botones.close()
        self._radio.close()
        sonido.stop_audio()

    # -----------------------------------------------------------------
    def _loop(self) -> None:
        while self._run:
            try:
                ev = self._cola.get(timeout=0.5)
            except queue.Empty:
                continue

            # ── Log en terminal con timestamp ────────────────────────────
            t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{t}] Botón PRESIONADO: {ev.name}")

            if ev is _Evt.ALERTA:
                self._transitar(Estado.ALERTA, sonido.play_alerta, settings.ALERTA_DURATION)
            elif ev is _Evt.SIMULACRO:
                self._transitar(Estado.SIMULACRO, sonido.play_simulacro, settings.SIMULACRO_DURATION)
            elif ev is _Evt.EVACUACION:
                self._transitar(Estado.EVACUACION, sonido.play_evacuacion, settings.EVACUACION_DURATION)
            elif ev is _Evt.PARO:
                sonido.stop_audio()
                self._cancel_audio_timer()
                self._cambiar_estado(Estado.PARO)
                self._cambiar_estado(Estado.ESPERANDO)
            elif ev is _Evt.FIN_AUDIO:
                self._cambiar_estado(Estado.ESPERANDO)

            self._cola.task_done()

    # -----------------------------------------------------------------
    def _transitar(self, nuevo: Estado, accion_audio: Callable[[], None], dur: int) -> None:
        self._cambiar_estado(nuevo)
        accion_audio()
        self._cancel_audio_timer()
        self._audio_timer = threading.Timer(dur, lambda: self._cola.put(_Evt.FIN_AUDIO))
        self._audio_timer.start()

    def _cambiar_estado(self, estado: Estado) -> None:
        self._estado_mgr.set(estado)
        self._lcd_cb(estado)
        self._log_cb(estado)

    def _cancel_audio_timer(self) -> None:
        if self._audio_timer and self._audio_timer.is_alive():
            self._audio_timer.cancel()
        self._audio_timer = None
