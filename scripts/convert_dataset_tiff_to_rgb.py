#!/usr/bin/env python3
"""
Convierte GeoTIFF con más de 3 bandas (p. ej. RGBA) a RGB de 3 bandas in-place.
YOLO espera tensores [B, 3, H, W]; sin esto aparece:
RuntimeError: ... expected input to have 3 channels, but got 4 channels instead

Uso (desde la raíz del repo):
  python scripts/convert_dataset_tiff_to_rgb.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import rasterio
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
IMAGE_ROOT = ROOT / "datasets" / "penguin_dataset" / "images"
LABELS_ROOT = ROOT / "datasets" / "penguin_dataset" / "labels"


def convert_file(path: Path) -> bool:
    with rasterio.open(path) as src:
        if src.count <= 3:
            return False
        data = src.read()[:3]
        profile = src.profile.copy()
        profile["count"] = 3
    tmp = path.with_name(path.name + ".rgb_tmp")
    try:
        with rasterio.open(tmp, "w", **profile) as dst:
            dst.write(data)
        tmp.replace(path)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    return True


def main() -> int:
    if not IMAGE_ROOT.is_dir():
        print(f"No existe {IMAGE_ROOT}", file=sys.stderr)
        return 1

    tiffs = [
        p
        for split in ("train", "val")
        for p in (IMAGE_ROOT / split).glob("*")
        if p.suffix.lower() in (".tif", ".tiff")
    ]
    if not tiffs:
        print(f"No hay TIFF en {IMAGE_ROOT}/{{train,val}}")
        return 0

    n_changed = 0
    for path in tqdm(tiffs, desc="RGB (3 bandas)"):
        if convert_file(path):
            n_changed += 1
    print(f"Archivos convertidos (4+ → 3 bandas): {n_changed} / {len(tiffs)}")

    # Cachés de ultralytics pueden quedar desalineados si cambian las imágenes
    if LABELS_ROOT.is_dir():
        for cache in LABELS_ROOT.rglob("*.cache"):
            cache.unlink(missing_ok=True)
            print(f"Eliminado caché: {cache.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
