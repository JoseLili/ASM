"""hardware/sonido.py – Reproducción de audio en bucle con corte por duración
============================================================================

Provee la clase ``AudioPlayer`` encargada de reproducir un archivo MP3 en bucle
(loop infinito) y detenerlo exactamente a los *N* segundos que marque la
configuración.  El corte se logra mediante un *timer* que termina el proceso
externo.

Ventajas del enfoque:
* **Flexibilidad**: basta cambiar un valor en ``config/settings.py`` para alterar
  la duración, sin editar los archivos de audio.
* **Baja dependencia**: usa reproductores CLI comunes (``mpg123`` ó ``mpv``).
* **Seguridad**: el *timer* evita que el sonido quede enganchado si algo falla.

Si ningún reproductor compatible está disponible, la clase lanza
``RuntimeError``.
"""
from __future__ import annotations

import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from config import settings

__all__ = [
    "AudioPlayer",
]


class AudioPlayer:
    """Gestiona la reproducción de un sonido en *loop* con parada programada."""

    _SUPPORTED_PLAYERS = [
        "mpg123",  # ‐q --loop -1 file.mp3
        "mpv",     # --no-video --loop-file=inf file.mp3
    ]

    def __init__(self) -> None:
        self._player_cmd: str = self._find_player()
        self._proc: Optional[subprocess.Popen] = None
        self._timer: Optional[threading.Timer] = None

    # ---------------------------------------------------------------------
    # API pública
    # ---------------------------------------------------------------------
    def play(self, file_path: Path, duration: int) -> None:
        """Reproduce *file_path* en loop y lo detiene tras *duration* segundos.

        Si ya hay un audio sonando, se detiene primero.
        """
        if not file_path.exists():
            raise FileNotFoundError(file_path)

        self.stop()

        cmd = self._build_command(file_path)
        self._proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Timer para detener
        self._timer = threading.Timer(duration, self.stop)
        self._timer.start()

    def stop(self) -> None:
        """Detiene la reproducción actual (si hay)."""
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None

    # ------------------------------------------------------------------
    # Interno
    # ------------------------------------------------------------------
    @classmethod
    def _find_player(cls) -> str:
        """Devuelve el binario de reproductor disponible o lanza error."""
        for candidate in cls._SUPPORTED_PLAYERS:
            if shutil.which(candidate):
                return candidate
        raise RuntimeError("No se encontró un reproductor CLI compatible (mpg123 o mpv)")

    def _build_command(self, file_path: Path) -> list[str]:
        """Arma la lista de argumentos según el reproductor seleccionado."""
        if self._player_cmd == "mpg123":
            return [self._player_cmd, "-q", "--loop", "-1", str(file_path)]
        if self._player_cmd == "mpv":
            return [
                self._player_cmd,
                "--no-video",
                "--quiet",
                "--loop-file=inf",
                str(file_path),
            ]
        # No debería llegar aquí
        raise RuntimeError("Reproductor no soportado")


# ---------------------------------------------------------------------------
# Instancia global y *helpers* de conveniencia (opcional)
# ---------------------------------------------------------------------------
_player = AudioPlayer()


def play_alerta() -> None:  # 180 s
    """Reproduce la alerta sísmica real por ``settings.ALERTA_DURATION`` segundos."""
    _player.play(settings.AUDIO_ALERTA, settings.ALERTA_DURATION)


def play_simulacro() -> None:  # 80 s
    """Reproduce el sonido de simulacro por ``settings.SIMULACRO_DURATION`` segundos."""
    _player.play(settings.AUDIO_SIMULACRO, settings.SIMULACRO_DURATION)


def play_evacuacion() -> None:  # 80 s
    """Reproduce el sonido de evacuación por ``settings.EVACUACION_DURATION`` segundos."""
    _player.play(settings.AUDIO_EVACUACION, settings.EVACUACION_DURATION)


def stop_audio() -> None:
    """Detiene cualquier reproducción en curso."""
    _player.stop()
