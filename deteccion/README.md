# README

En este directorio están el modelo best.pt y un conjunto de imágenes para poder hacer predicciones.

COmando a ejecutar para hacer las predcciones

Ejecutar este comando desde el directorio de 'deteccion'

```bash
yolo detect predict \
  model=best.pt \
  source=imgs_rgb \
  imgsz=512 \
  conf=0.30 \
  save=True \
  save_txt=False \
  project=resultados_prediccion \
  name=tile13 \
  exist_ok=True \
  line_thickness=3 \
  show_labels=False \
  show_conf=False
```

### Parámetros del comando de predicción

A continuación se detalla cada parámetro utilizado en el comando de inferencia con YOLO26m:

- **`model`** = `best.pt`  
  Modelo entrenado que se utiliza para realizar las predicciones. Corresponde al mejor peso obtenido durante el entrenamiento.

- **`source`** = `imgs_rgb`  
  Ruta de la carpeta que contiene las imágenes a procesar (en este caso, las imágenes TIFF convertidas a 3 canales RGB).

- **`imgsz`** = `512`  
  Tamaño de entrada de las imágenes durante la inferencia. Las imágenes se redimensionan automáticamente a 512×512 píxeles. Este valor coincide con el utilizado durante el entrenamiento.

- **`conf`** = `0.30`  
  Umbral de confianza mínimo. Solo se dibujarán las cajas de detección cuando el modelo estime una probabilidad igual o superior al 30 % de que el objeto sea un pingüino barbijo.  
  *Recomendación*: bajar a 0.25 para detectar más individuos (mayor sensibilidad) o subir a 0.35–0.40 para reducir falsos positivos.

- **`save`** = `True`  
  Guarda las imágenes resultantes con las cajas de detección dibujadas. Este parámetro es obligatorio si se desea obtener una salida visual.

- **`save_txt`** = `False`  
  Desactiva la generación de archivos `.txt` con las etiquetas en formato YOLO. Se utiliza porque solo se requieren las visualizaciones (cajas).

- **`project`** = `resultados_prediccion`  
  Nombre de la carpeta principal donde se guardarán todos los resultados de la predicción.

- **`name`** = `tile13`  
  Nombre de la subcarpeta dentro de `project` donde se almacenarán los resultados de esta ejecución concreta.

- **`exist_ok`** = `True`  
  Permite sobrescribir la carpeta de resultados si ya existe, evitando errores de ejecución.

- **`line_thickness`** = `3`  
  Grosor de las líneas de las cajas de detección. Un valor mayor hace las cajas más visibles.

- **`show_labels`** = `False`  
  Desactiva la visualización del texto de la clase ("pinguino") encima de cada caja.

- **`show_conf`** = `False`  
  Desactiva la visualización del porcentaje de confianza (por ejemplo, 0.87) junto a cada detección.  
  Con este parámetro activado en `False`, solo se muestra la caja sin ningún texto adicional.