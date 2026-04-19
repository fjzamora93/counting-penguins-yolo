#!/usr/bin/env python3
"""
Convierte GeoTIFF con 4 bandas (RGBA) a RGB de 3 bandas.
Adaptado para tu carpeta: deteccion/imgs/
"""

from pathlib import Path
import rasterio
from tqdm import tqdm

# ==================== CONFIGURACIÓN ====================
# Directorio base del script (deteccion/)
BASE_DIR = Path(__file__).resolve().parent

# Ruta donde están tus imágenes TIFF (4 canales)
IMAGE_DIR = BASE_DIR / "imgs"

# Carpeta donde se guardarán las versiones RGB (3 canales)
OUTPUT_DIR = BASE_DIR / "imgs_rgb"

# ======================================================

def convert_file(input_path: Path, output_path: Path) -> bool:
    """Convierte un TIFF de 4+ bandas a 3 bandas RGB."""
    with rasterio.open(input_path) as src:
        if src.count <= 3:
            print(f"{input_path.name} ya tiene 3 o menos bandas → se omite")
            return False
        
        # Leemos solo las primeras 3 bandas (RGB)
        data = src.read([1, 2, 3])   # bandas 1,2,3 (índice empieza en 1)
        
        # Copiamos el perfil y lo modificamos a 3 bandas
        profile = src.profile.copy()
        profile["count"] = 3
        # Opcional: indicar que es RGB (mejora compatibilidad)
        profile["photometric"] = "RGB"
        
        # Guardamos en archivo temporal y luego reemplazamos
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")
        try:
            with rasterio.open(tmp, "w", **profile) as dst:
                dst.write(data)
            tmp.replace(output_path)
            return True
        except Exception as e:
            if tmp.exists():
                tmp.unlink()
            print(f"Error al convertir {input_path.name}: {e}")
            return False


def main():
    if not IMAGE_DIR.exists():
        print(f"Error: No se encuentra la carpeta {IMAGE_DIR}")
        return 1

    # Creamos la carpeta de salida
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Buscamos todos los .tif y .tiff
    tiffs = list(IMAGE_DIR.glob("*.tif")) + list(IMAGE_DIR.glob("*.tiff"))
    
    if not tiffs:
        print(f"No se encontraron archivos .tif/.tiff en {IMAGE_DIR}")
        return 0

    print(f"Se encontraron {len(tiffs)} archivos TIFF en imgs/")
    n_changed = 0

    for path in tqdm(tiffs, desc="Convirtiendo a RGB (3 bandas)"):
        output_path = OUTPUT_DIR / path.name
        if convert_file(path, output_path):
            n_changed += 1

    print(f"\n¡Conversión terminada!")
    print(f"Archivos convertidos (4 → 3 bandas): {n_changed} / {len(tiffs)}")
    print(f"Las nuevas imágenes RGB están en: {OUTPUT_DIR.resolve()}")
    print("\nAhora puedes ejecutar la predicción con:")
    print(f'   yolo detect predict model=best.pt source=imgs_rgb imgsz=512 conf=0.30 save=True save_txt=True project=resultados_prediccion name=tile13 exist_ok=True')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())