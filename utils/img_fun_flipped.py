
import os
import pandas as pd
from tqdm import tqdm  
import rasterio
from typing import Tuple
from rasterio.windows import Window
import numpy as np

from utils.img_fun import ensure_rgb_channels

# Funciones para el procesamiento de imágenes
def hello():
    print("Hello, world!")



def get_img_info(img_path: str) -> dict:
    """
    Abre una imagen con rasteiro y devuelve un diccionario con toda la información clave sobre la imagen.

    Args:
    - full_image_path: el path completo de la imagen.
    """
    img_dict = {}

    with rasterio.open(img_path) as src:
        transform = src.transform  # Transformación de coordenadas (Affine)
        
        # Coordenadas de las esquinas
        top_left = (transform.c, transform.f)  # Esquina superior izquierda
        top_right = (transform * (src.width, 0))  # Esquina superior derecha
        bottom_left = (transform * (0, src.height))  # Esquina inferior izquierda
        bottom_right = (transform * (src.width, src.height))  # Esquina inferior derecha
        
        # Dimensiones de la imagen
        width, height = src.width, src.height

        # Sistema de referencia espacial (CRS)
        crs = src.crs
        
        print("Metadata:")
        print("---------")
        for key, value in src.profile.items():
            print(f"{key}: {value}")
        
        print("\nCoordenadas de las esquinas de la imagen:")
        print("TOP LEFT:", top_left)
        print("BOTTOM RIGHT:", bottom_right)

        # Creación del diccionario
        img_dict['metadata'] = src.meta
        img_dict['top_left'] = top_left
        img_dict['top_right'] = top_right
        img_dict['bottom_left'] = bottom_left
        img_dict['bottom_right'] = bottom_right
        img_dict['width'] = width
        img_dict['height'] = height
        img_dict['crs'] = crs

        for key, value in src.profile.items():
            img_dict[key] = value

    return img_dict



def crop_tile_into_subrecortes_flipped(
        tiff_file: str,
        output_dir: str,
        num_tile: int,
        coords_csv: str = './coords/yolo_coords.csv',
        rows: int = 10,
        cols: int = 10,
        is_negative: bool = False
) -> None:
    """
    Recorta una imagen grande del ortmosoaico en subrecortes de aproximadamente 500x500 píxeles,
    guardando solo los recortes que contienen al menos una coordenada del archivo CSV.

    Args:
    - tiff_file: str - Ruta al archivo TIFF que se desea recortar.
    - output_dir: str - Directorio donde se guardarán los subrecortes.
    - num_tile: int - Número de tile que se está procesando.
    - coords_csv: str - Ruta al archivo CSV con las coordenadas (class, x_center, y_center, width, height).
    - rows: int - Número de filas en las que se dividirá la imagen (por defecto 20).
    - cols: int - Número de columnas en las que se dividirá la imagen (por defecto 20).
    """
    # Leer coordenadas del archivo CSV
    # Leer coordenadas con pandas
    coords_df = pd.read_csv(coords_csv, header=None, names=["class", "x_center", "y_center", "width", "height"])
    coords_df["x_center"] = pd.to_numeric(coords_df["x_center"], errors="coerce")
    coords_df["y_center"] = pd.to_numeric(coords_df["y_center"], errors="coerce")

    # Eliminar filas con valores no numéricos
    coords_df = coords_df.dropna(subset=["x_center", "y_center"])
    # Obtener información de la imagen
    with rasterio.open(tiff_file) as src:
        WIDTH = src.width
        HEIGHT = src.height
        transform = src.transform  # Transformación geográfica de la imagen

    # Definir el tamaño de cada subrecorte
    tile_width = WIDTH // cols
    tile_height = HEIGHT // rows

    with rasterio.open(tiff_file) as src:
        for i in range(rows):
            for j in range(cols):
                # Calcular las coordenadas del recorte
                left = j * tile_width
                upper = i * tile_height
                right = left + tile_width
                lower = upper + tile_height

                # Transformar los píxeles del recorte a coordenadas geográficas
                top_left_coords = rasterio.transform.xy(transform, upper, left, offset="ul")
                bottom_right_coords = rasterio.transform.xy(transform, lower, right, offset="lr")

                min_x, max_y = top_left_coords
                max_x, min_y = bottom_right_coords

                # Filtrar coordenadas dentro del recorte
                filtered_coords = coords_df[
                    (coords_df["x_center"] >= min_x) & (coords_df["x_center"] <= max_x) &
                    (coords_df["y_center"] >= min_y) & (coords_df["y_center"] <= max_y)
                ]

             
                # Crear ventana de recorte
                window = Window(left, upper, tile_width, tile_height)
                cropped_image = src.read(window=window)

                # Guardar el recorte
                cropped_meta = src.meta.copy()
                cropped_meta.update({
                    "height": tile_height,
                    "width": tile_width,
                    "transform": rasterio.windows.transform(window, src.transform)
                })

                if is_negative:
                    if filtered_coords.empty:
                        print("Coordenadas vacías... guardando")
                        filename = f"negative_{i * cols + j + 1}.tiff"
                        output_path = f"{output_dir}/{filename}"
                        cropped_image, cropped_meta = ensure_rgb_channels(cropped_image, cropped_meta)
                        with rasterio.open(output_path, 'w', **cropped_meta) as dst:
                            dst.write(cropped_image)
                else:
                    # Solo guardar si hay coordenadas
                    if filtered_coords.empty:
                        continue  # No guardar imágenes sin coordenadas si no queremos negativos
                    filename = f"{num_tile}_{i * cols + j + 1}.tiff"
                    output_path = f"{output_dir}/{filename}"
                    cropped_image, cropped_meta = ensure_rgb_channels(cropped_image, cropped_meta)
                    with rasterio.open(output_path, 'w', **cropped_meta) as dst:
                        dst.write(cropped_image)
                
