# ⚠️ Sistema de Alerta Sísmica Automatizada – V2.25 BLTeech ASM

**Autor:** BLTeech\
📍 **Sitio de despliegue:** configurable en `config/sitio.txt`\
🖥️ **Dispositivo base:** Raspberry Pi 4 Modelo B

---

## 🧾 Descripción general

Este sistema arranca al encender la Pi y ejecuta automáticamente:

1. Activar el entorno virtual Python.
2. Levantar `pigpiod` (daemon GPIO) si no está corriendo.
3. Ejecutar `main.py` para:
   - Monitorear un radio vía GPIO (jack 3.5 mm).
   - Gestionar botones (Simulacro, Evacuación, Paro).
   - Mostrar estados en LCD I²C HD44780 16×2.
   - Reproducir sonidos en loop con parada programada.
   - Registrar eventos en logs rotativos.
   - Exportar logs automáticamente a USB.
   - Manejar apagado limpio (SIGTERM/SIGINT).

Funciona 100 % offline y es robusto para entornos críticos.

---

## ⚙️ Requisitos de hardware

| Componente                          | GPIO / Pin físico           | Notas                         |
| ----------------------------------- | --------------------------- | ----------------------------- |
| **Radio Midland WR-120** (rele NO)  | GPIO 4 / Pin 7              | Pull-up para detectar cierre  |
| **Botón Simulacro**                 | GPIO 17 / Pin 11            | NO → GND                      |
| **Botón Evacuación**                | GPIO 22 / Pin 15            | NO → GND                      |
| **Botón Paro/Emergencia**           | GPIO 27 / Pin 13            | NO → GND                      |
| **LCD HD44780 16×2 + I²C backpack** | SDA (GPIO 2) / SCL (GPIO 3) | I²C addr: `0x27`              |
| **Salida de audio**                 | Jack analógico (hw:0,0)     | Usa `-a hw:0,0` en mpg123/mpv |

---

## 🧰 Dependencias Python

Archivo `requirements.txt`:

```text
colorzero==2.0
gpiozero==2.0.1
pigpio==1.78
psutil==7.0.0
pyfiglet==1.0.3
pygame==2.6.1
pyudev==0.24.3
RPi.GPIO==0.7.1
RPLCD==1.4.0
setuptools==80.9.0
smbus2==0.5.0
```

Instala todo con:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

---

## 🔧 Instalación del sistema

1. **Clona el repositorio**:
   ```bash
   ```

git clone [https://tu-repo/alerta\_sismica\_blt.git](https://tu-repo/alerta_sismica_blt.git) cd alerta\_sismica\_blt

````

2. **Dependencias APT**:
```bash
sudo apt update
sudo apt install -y python3-venv ffmpeg figlet i2c-tools python3-smbus acl
````

3. **Configura I²C** (si hace falta) con `raspi-config` → Interface Options → I2C.

4. **Recodificar sonidos** (si es necesario):

   ```bash
   ```

cd assets/sonidos for f in alerta\_sismica simulacro evacuacion; do ffmpeg -y -i "\$f.mp3" -codec\:a libmp3lame -b\:a 192k "\${f}.mp3" done cd -

````

---

## 🚀 Arranque automático (@reboot Cron)

Creamos un script `start.sh` y lo programamos en crontab de root:

```bash
cat > start.sh << 'EOF'
#!/usr/bin/env bash
# start.sh: activa venv, arranca pigpiod y main.py
exec 1>/dev/null 2>&1
cd /home/blteech/alerta_sismica_blt || exit 1
source venv/bin/activate
if ! pgrep -x pigpiod >/dev/null; then pigpiod; sleep 1; fi
exec python3 main.py
EOF
chmod +x start.sh
sudo crontab -e
# Añade:
@reboot /home/blteech/alerta_sismica_blt/start.sh
````

Al reiniciar, el sistema estará activo sin intervención.

---

## 🔄 Exportación de logs a USB

- **Automático:** detecta y exporta a `/mnt/usb/ALSI_export_YYYYMMDD-HHMMSS`.
- **Manual:**
  ```bash
  sudo mkdir -p /mnt/usb
  sudo mount -t vfat /dev/sdb1 /mnt/usb -o uid=$(id -u),gid=$(id -g),umask=002
  ```

---

## 🔐 Permisos de mantenimiento con ACL

```bash
sudo adduser mantenimiento
sudo chown -R blteech:blteech /home/blteech/alerta_sismica_blt
sudo chmod -R og-rwx /home/blteech/alerta_sismica_blt
sudo setfacl -m u:mantenimiento:x /home/blteech
sudo setfacl -m u:mantenimiento:x /home/blteech/alerta_sismica_blt
sudo setfacl -m u:mantenimiento:x /home/blteech/alerta_sismica_blt/config
sudo setfacl -m u:mantenimiento:rw /home/blteech/alerta_sismica_blt/config/sitio.txt
```

*`mantenimiento`** podrá editar SOLO **`config/sitio.txt`**.*

---

## 🖥️ Banner SSH con FIGLET

```bash
sudo figlet -f slant "BLTeech ASM" | sudo tee /etc/ssh/banner.txt
sudo tee -a /etc/ssh/banner.txt > /dev/null << 'EOF'
© Todos los derechos. BLTeech. Contactanos: https://blteech.com/ | +52 55 4012 6421
EOF
sudo sed -i 's@^#Banner.*@Banner /etc/ssh/banner.txt@' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

Conecta por SSH y verás tu banner ASCII antes del prompt.

---

## 🧪 Mantenimiento y pruebas

- **Ver logs**: añade `>> run.log 2>&1` en `start.sh` y usa `tail -f run.log`.
- **Actualizar dependencias**:
  ```bash
  source venv/bin/activate
  pip install -U -r requirements.txt
  deactivate
  ```
- **Reinicios**: `sudo reboot`.

---