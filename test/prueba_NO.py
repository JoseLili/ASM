#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Prueba de contacto NO del Midland WR-120
#  - Tip (rojo)  → GPIO 17
#  - Sleeve (negro) → GND
#
# Opcional: LED en GPIO 18 para confirmar visualmente.

from gpiozero import Button, LED
from signal import pause
from datetime import datetime

ALERTA_PIN = 17         # Entrada desde el relé
LED_PIN    = 18         # Salida opcional (LED o buzzer)

alerta = Button(ALERTA_PIN, pull_up=True, bounce_time=0.05)
led    = LED(LED_PIN)

def on_alert():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] ¡Alerta recibida!")
    led.blink(on_time=0.2, off_time=0.2, n=10, background=True)

alerta.when_released = on_alert

print("Esperando alerta… presiona Self-Test en la radio o puentea Tip↔Sleeve.")
pause()        # Mantiene vivo el script
