"""logs/exportador_logs.py – Exporta registros + diagnóstico a un directorio.

Uso CLI (desde la Pi):
    python -m logs.exportador_logs /media/usb

Uso programático:
    from logs import exportador_logs
    ruta = exportador_logs.export("/media/usb")
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from config import settings

LOG_DIR: Path = settings.BASE_DIR / "logs"
DIAG_PATTERN = "diagnostico_*.txt"


def _collect_logs() -> List[Path]:
    """Devuelve la lista de archivos .log (rotativos) ordenados por fecha."""
    return sorted(LOG_DIR.glob("*.log"))


def _latest_diagnostico() -> Path | None:
    archivos = sorted((LOG_DIR / "diagnosticos").glob(DIAG_PATTERN))
    return archivos[-1] if archivos else None


def export(dest_dir: str | Path) -> Path:
    """Copia los .log y el último diagnóstico al *dest_dir*.

    Crea una carpeta tipo `ALSI_export_YYYYMMDD-HHMMSS` y devuelve su ruta.
    """
    dest_path = Path(dest_dir).expanduser().resolve()
    if not dest_path.is_dir():
        raise FileNotFoundError(dest_path)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    export_folder = dest_path / f"ALSI_export_{ts}"
    export_folder.mkdir(exist_ok=True)

    # Copiar logs
    for log_file in _collect_logs():
        shutil.copy2(log_file, export_folder / log_file.name)

    # Copiar diagnóstico más reciente
    diag = _latest_diagnostico()
    if diag is not None:
        shutil.copy2(diag, export_folder / diag.name)

    return export_folder


if __name__ == "__main__":
    import argparse, sys, textwrap

    parser = argparse.ArgumentParser(
        description="Exporta logs y diagnóstico a un directorio (USB).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """Ejemplo:
              python -m logs.exportador_logs /media/usb
            """,
        ),
    )
    parser.add_argument("dest", help="Ruta destino (ej. /media/usb)")
    args = parser.parse_args()

    try:
        destino = export(args.dest)
    except Exception as exc:  # pragma: no cover
        print("Error:", exc)
        sys.exit(1)
    print("Logs exportados en", destino)
