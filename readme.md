# ⚠️ Sistema de Alerta Sísmica Automatizada – V2.23

**Proyecto desarrollado por [BLTeech]**  
📍 **Sitio de despliegue:** CDMX1  
🖥️ **Dispositivo base:** Raspberry Pi 4 Modelo B

---

## 🧾 Descripción general

Este sistema opera de forma autónoma desde el arranque de la Raspberry Pi. Su función es monitorear entradas físicas provenientes de un radio de alerta sísmica o botones dedicados para registrar eventos, reproducir sonidos y mostrar mensajes en una pantalla LCD.

Es ideal para instalaciones donde se requiera un sistema local de alerta confiable, visual y sonoro sin depender de internet ni servicios externos.

---

## ⚙️ Funcionalidades principales

- 🛰️ **Monitoreo continuo** del radio Midland WR-120 vía jack 3.5mm (contacto NO)
- 🔊 **Reproducción automática de sonidos** según el tipo de evento (alerta, simulacro, evacuación)
- 🖥️ **Pantalla LCD** que muestra el estado del sistema en tiempo real
- 🛑 **Botón de paro de emergencia** que detiene el audio activo
- 🧪 **Diagnóstico automático** de componentes al iniciar
- 🗃️ **Registro de eventos** en archivos de log
- 📤 **Exportación manual de logs** en formato `.txt`
- 🔁 **Ejecución automática** al encender la Raspberry Pi (systemd)

---

## 🔌 Asignación de pines

| Componente                                                  | GPIO / Pin físico                                                 |Notas                                                         |
|-------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| **Radio Midland WR-120** (relé NO – contacto Tip⇆Sleeve)    | **GPIO 4** / Pin 7                                                |Entrada con `pull_up=True` → detecta *cierre* iniciar la alerta
|-------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| Sleeve (GND)                                                | Pin 6                                                             | Común con la Pi
|-------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| **Botón Simulacro**                                         | **GPIO 17** / Pin 11                                              | Momento NO → GND (pin 14)
|-------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| **Botón Evacuación**                                        | **GPIO 22** / Pin 15                                              | NO → GND (pin 9)
|-------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| **Botón Reset / Paro**                                      | **GPIO 27** / Pin 13                                              | NO → GND (pin 9)
|-------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------|
| **LCD HD44780 16×2 + I²C backpack (PCF8574)**               | SDA (GPIO 2) / Pin 3 SCL (GPIO 3) / Pin 5 VCC (5V) / Pin 2<br>GND / Pin 9 | Dirección I²C confirmada: `0x27`

## 🖥️ Mensajes mostrados al iniciar
Alerta Sísmica V2.23
Creado por BLTeech
Sitio: CDMX1
Despliegue listo
Diagnóstico: OK


---

## 🔄 Estados del sistema

| Estado               | Activador                          | Acción del sistema                                                        |
|----------------------|-------------------------------------|---------------------------------------------------------------------------|
| `Esperando evento`   | Estado inicial                      | LCD en espera, escucha señales                                            |
| `Alerta sísmica`     | Jack de radio (GPIO 4)              | Reproduce sonido, LCD cambia, registra log                                |
| `Simulacro`          | Botón físico (GPIO 17)              | Reproduce sonido de simulacro, LCD cambia, registra log                   |
| `Evacuación`         | Botón físico (GPIO 22)              | No reproduce audio, LCD cambia, registra log                              |
| `Paro de emergencia` | Botón (GPIO 27) o watchdog interno  | Detiene audio y vuelve a “Esperando evento”                               |
| `Diagnóstico`        | Automático al arrancar              | Verifica LCD, pines, sonidos, etc. y determina si el sistema puede iniciar |

---

## 🧰 Dependencias (Python)

- `gpiozero`
- `RPi.GPIO`
- `RPLCD`
- `smbus2`
- `pygame` *(o `playsound` como alternativa)*
- `logging`, `datetime`, `os`

---

## 🛠️ Ejecución automática (`systemd`)

El sistema se configura para ejecutarse al encender la Raspberry Pi mediante un servicio de `systemd`.

**Archivo:** `/etc/systemd/system/alsi.service`  
**Comando para activarlo:**

```bash
sudo systemctl enable alsi.service


gpiozero
RPi.GPIO
RPLCD
smbus2
pygame
psutil
pyfiglet
pigpio


para arreglar el GPIO instalamos https://github.com/joan2937/pigpio

ffmpeg -y -i assets/sonidos/evacuacion.mp3 \
  -codec:a libmp3lame -b:a 192k assets/sonidos/evacuacion_std.mp3

ffmpeg -y -i assets/sonidos/simulacro.mp3 \
  -codec:a libmp3lame -b:a 192k assets/sonidos/simulacro_std.mp3

ffmpeg -y -i assets/sonidos/alerta_sismica.mp3 \
  -codec:a libmp3lame -b:a 192k assets/sonidos/alerta_sismica_std.mp3

