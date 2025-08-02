"""config/estados.py – Enum de estados globales del sistema
==========================================================

Centraliza la lista *única* de estados válidos.  Mantener aquí asegura que tanto
la lógica, el LCD y el logger hablen el mismo idioma.
"""
from __future__ import annotations

import enum

__all__ = [
    "Estado",
]


# TODO: podrías usar `enum.auto()` para evitar valores explícitos y reducir
#       mantenimiento si el orden cambia.
class Estado(enum.IntEnum):
    """Estados operativos del Sistema de Alerta Sísmica."""

    DIAGNOSTICO = 0  #: Arranque y verificación de hardware
    ESPERANDO = 1    #: Stand‑by normal
    ALERTA = 2       #: Alerta sísmica real
    SIMULACRO = 3    #: Sonido de simulacro
    EVACUACION = 4   #: Evacuación con audio
    PARO = 5         #: Paro de emergencia / fin de audio

    # ------------------------------------------------------------------
    # Ayudas de presentación
    # ------------------------------------------------------------------
    def to_lcd(self) -> str:
        """Texto corto que se muestra en la LCD (2ª línea)."""
        # NOTE: el diccionario se crea en cada llamada; cachear o hacerlo
        #       atributo de clase si se llama con mucha frecuencia.
        mapping: dict["Estado", str] = {
            Estado.DIAGNOSTICO: "Diagnóstico…",
            Estado.ESPERANDO: "Esperando evento",
            Estado.ALERTA: "Alerta sísmica!",
            Estado.SIMULACRO: "Simulacro",
            Estado.EVACUACION: "Evacuación",
            Estado.PARO: "Paro emergencia",
        }
        return mapping.get(self, "")

    def __str__(self) -> str:  # para logs legibles
        return self.name.title()

# SUGERENCIA: Si planeas internacionalizar mensajes, extrae `to_lcd` a
#             un módulo de traducciones y evita strings embebidos aquí.
