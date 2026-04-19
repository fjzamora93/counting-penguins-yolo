## 1. Procesamiento del ortomosaico

### 1.1. Recorte del ortomosaico en teselas

El ortomosaico original (orthomosaic_all_big.tif) se encuentra en formato GeoTIFF con sistema de coordenadas EPSG:4326 (WGS84). Sus dimensiones son 10 195 píxeles de ancho por 11 420 píxeles de alto. Para facilitar el manejo computacional, se dividió la imagen en una cuadrícula de 20 filas por 20 columnas, generando teselas de aproximadamente 500×500 píxeles cada una.

El recorte se realizó con la librería Rasterio, que preserva los metadatos espaciales (transformación afín, sistema de coordenadas y extensión geográfica) en cada submosaico. Para cada tesela se definió una ventana (window) de extracción y se leyó la matriz de píxeles correspondiente.


### 1.2. Filtrado de teselas por calidad de imagen

No todas las teselas resultantes contienen información útil para el entrenamiento. Se aplicaron tres criterios de exclusión:

- Píxeles negros (valor 0 en todos los canales): se descartaron teselas con una proporción >50% de píxeles negros (es decir, donde no hay fotografía).

- Píxeles blancos (valor 255 en todos los canales): se descartaron teselas con una proporción >10% de píxeles blancos (frecuentemente asociados a nubes o nieve sobreexpuesta).

- Píxeles vacíos o sin datos (valor nodata o canal alfa igual a 0): se descartaron teselas con >10% de píxeles sin información.

Este filtro garantiza que el conjunto de datos final contenga únicamente regiones con cobertura útil y evita que el modelo aprenda patrones no deseados asociados a artefactos de adquisición o márgenes sin información.

### 1.3 Conversión de cuatro bandas (RGBA) a imágenes RGB de tres bandas

Como paso final en la preparación de las imágenes para la inferencia, se realizó la conversión de las teselas GeoTIFF de cuatro bandas (RGBA) a imágenes RGB de tres bandas. Esta conversión fue necesaria porque el modelo YOLO26m fue entrenado exclusivamente con imágenes de tres canales, y la presencia del canal alfa generaba un error de incompatibilidad dimensional en la primera capa convolucional (RuntimeError: expected input to have 3 channels, but got 4 channels instead). Mediante un script personalizado en Python basado en la librería rasterio, se extrajeron únicamente las tres primeras bandas (rojo, verde y azul) de cada tesela, preservando la información fotográfica relevante y descartando el canal de transparencia.

Las imágenes resultantes se guardaron en una nueva carpeta (imgs_rgb) manteniendo el nombre original de los archivos. Esta conversión garantizó la compatibilidad completa entre las teselas de entrada y la arquitectura del modelo, permitiendo ejecutar el proceso de predicción sin errores técnicos y asegurando que las detecciones se realizaran sobre representaciones visuales consistentes con las utilizadas durante el entrenamiento.


## 2. Extracción de coordenadas

### 2.1. Extracción de coordenadas y asignación de etiquetas

Se dispone de un archivo CSV (chinstraps_eca56.csv) que contiene las coordenadas geográficas (X, Y) de pingüinos etiquetados manualmente en el ortomosaico original. Para cada tesela generada, se procedió a:

- Filtrar las coordenadas que caen dentro de sus límites espaciales (empleando min_x, max_x, min_y, max_y de cada tesela).

- Asignar etiquetas en formato YOLO (clase, coordenadas relativas del centro de la caja, ancho y alto normalizados). Dado que las coordenadas originales son puntos, se asumió un tamaño de caja fijo apropiado para la especie (o se generó una caja alrededor de cada punto mediante un radio predefinido).

- Normalizar las coordenadas para que sean independientes del tamaño de la tesela:
    xcentro=xpıˊxelWtile,ycentro=ypıˊxelHtile,w=wpıˊxelesWtile,h=hpıˊxelesHtile
    xcentro​=Wtile​xpıˊxel​​,ycentro​=Htile​ypıˊxel​​,w=Wtile​wpıˊxeles​​,h=Htile​hpıˊxeles​​

    donde WtileWtile​ y HtileHtile​ son el ancho y alto de la tesela en píxeles.

Los archivos de etiqueta resultantes tienen extensión .txt y siguen el estándar YOLO: cada línea contiene clase x_centro y_centro ancho alto.


### 2.2. Generación de ejemplos negativos

Además de las teselas con pingüinos, se incluyeron teselas sin ninguna anotación (ejemplos negativos) para mejorar la capacidad del modelo de discriminar fondo. Para ello se repitió el proceso de recorte sobre regiones del ortomosaico donde no había coordenadas de pingüinos, y se generaron archivos .txt vacíos asociados a esas imágenes.


### 2.3. Partición en conjuntos de entrenamiento, validación y prueba

El conjunto de teselas etiquetadas se dividió de la siguiente manera:

- Entrenamiento (train): 70 % de las teselas (primeras 7 de cada bloque de 10).

- Validación (val): 20 % (siguientes 2 de cada bloque de 10).

- Prueba (test): 10 % (última de cada bloque de 10).

Esta partición cíclica asegura una distribución homogénea de la variabilidad espacial y de densidad de aves entre los tres conjuntos. Las imágenes y sus archivos .txt correspondientes se copiaron a directorios separados (images/train, labels/train, images/val, labels/val, images/test, labels/test) siguiendo la estructura requerida por YOLOv5 y YOLOv8.


## 3. Entrenamiento del modelo YOLO

Una vez estructurado y particionado el conjunto de datos (carpetas images/ y labels/ con las sub-imágenes de ≈500×500 píxeles y sus correspondientes etiquetas normalizadas en formato YOLO), se procedió al entrenamiento de un modelo de detección de objetos basado en la familia YOLO de Ultralytics.
El comando de entrenamiento utilizado fue el siguiente (ejecutado mediante la interfaz CLI de Ultralytics):

```bash
yolo train model=yolo26s.pt data=datasets/penguin_dataset.yaml epochs=30 imgsz=512 batch=32 device=cpu
```

### 3.1 Detalles de la configuración de entrenamiento

- Modelo preentrenado: Se empleó inicialmente el peso yolo26s.pt y, posteriormente, yolo26m.pt (variante medium del modelo YOLO26, la versión más reciente de Ultralytics en el momento de la experimentación, lanzada en enero de 2026). La variante medium demostró ser más adecuada para la tarea de detección de pingüinos en imágenes aéreas de alta resolución recortadas, gracias a su mayor capacidad de representación de características sin incurrir en un coste computacional excesivo.

- Archivo de configuración del dataset (penguin_dataset.yaml): Este archivo definía la estructura del conjunto de datos siguiendo el estándar de Ultralytics, especificando las rutas a las carpetas de entrenamiento (train) y validación (val), el número de clases (1: pingüino barbijo o chinstrap penguin) y los nombres de las clases.

- Número de épocas (epochs=30): Se entrenó durante 30 épocas completas. Experimentos con un mayor número de épocas no mostraron mejoras significativas en las métricas de validación, por lo que se mantuvo este valor para evitar sobreajuste y optimizar el tiempo de cómputo. Se recomienda en futuras iteraciones activar el parámetro patience para implementar early stopping basado en la pérdida de validación.

- Tamaño de imagen de entrada (imgsz=512): Las sub-imágenes se redimensionaron automáticamente a 512 × 512 píxeles. Esta resolución, inferior al valor predeterminado de 640 × 640, permitió reducir el consumo de memoria y acelerar el proceso de entrenamiento, especialmente relevante al ejecutarse en CPU.

- Tamaño de batch (batch): Se observó que tamaños de batch demasiado bajos producían resultados muy deficientes (inestabilidad en el entrenamiento y bajo rendimiento). Por ello, se aumentó progresivamente el valor del batch hasta llegar a 32, que resultó en una convergencia más estable y mejores métricas. Al entrenar en CPU, este batch elevado fue viable, aunque incrementó el tiempo por época.

- Dispositivo de cómputo (device=cpu): Todo el proceso se realizó en CPU debido a las limitaciones de hardware disponibles en el entorno de ejecución. Aunque el entrenamiento en CPU es considerablemente más lento que en GPU, permitió completar los experimentos de forma reproducible.

Adicionalmente, se probó la variante YOLO26l (large), pero no se observó una mejoría sustancial en las métricas de validación (precision, recall, mAP@0.5 y mAP@0.5:0.95) con respecto al modelo medium. Por tanto, se seleccionó YOLO26m como la configuración óptima para este estudio, considerando el balance entre precisión y eficiencia.

El entrenamiento utilizó los hiperparámetros predeterminados de Ultralytics (optimizador SGD con momentum 0.937, data augmentation con mosaico, flips, ajustes HSV, etc.) y se monitorizaron las métricas estándar de detección de objetos, así como las curvas de pérdida y las gráficas generadas automáticamente (F1-curve, PR-curve, confusion matrix).

Esta configuración representa un punto de partida sólido y reproducible para la detección automática de pingüinos barbijo en ortomosaicos UAV. Los pesos finales obtenidos (best.pt) pueden emplearse directamente para inferencia en nuevos tiles o para fine-tuning adicional.


### 3.2 Hiperparámetros por defecto y aumentación de datos

El entrenamiento utilizó los hiperparámetros predeterminados de Ultralytics para YOLO26/YOLOv8, entre los que destacan:

- Optimizador: SGD (Stochastic Gradient Descent) con momentum = 0.937 y tasa de aprendizaje inicial lr0 = 0.01.

- Decaimiento de peso (weight decay) y programación de la tasa de aprendizaje (cosine o linear decay según configuración por defecto).

- Aumento de datos (data augmentation) activado por defecto: mosaico (mosaic), volteo horizontal (fliplr=0.5), ajustes de HSV (hue, saturation, value), traslación, escalado y otras transformaciones que mejoran la robustez del modelo frente a variaciones en iluminación, orientación y escala presentes en imágenes aéreas antárticas.

Durante el entrenamiento se monitorizaron las métricas estándar de detección de objetos:

- Precision y Recall
- mAP@0.5 (mean Average Precision con umbral IoU de 0.5)
- mAP@0.5:0.95 (mAP promedio en diferentes umbrales IoU del 0.5 al 0.95)

Los resultados de estas métricas, junto con las curvas de pérdida (box_loss, cls_loss, dfl_loss) y las gráficas generadas automáticamente por Ultralytics (confusion matrix, F1-curve, PR-curve, etc.), se almacenaron en la carpeta runs/train/ (o similar, según el nombre de la ejecución).


### 3.3 Consideraciones adicionales
El uso de YOLO26s en lugar de versiones anteriores (YOLOv5 o YOLOv8) aprovecha las mejoras arquitectónicas recientes de Ultralytics, como inferencia end-to-end sin NMS en algunas configuraciones, mejor eficiencia y mayor precisión en benchmarks. Entrenar en CPU con imgsz=512 y batch=32 permitió completar el proceso en un tiempo razonable, aunque para experimentos futuros se recomienda migrar a GPU (ej. device=0) para reducir drásticamente el tiempo de entrenamiento y explorar valores más altos de imgsz (640 o superior) y épocas.

Esta configuración representa un punto de partida sólido y reproducible para la detección automática de pingüinos barbijo en ortomosaicos de UAV. Los pesos finales (best.pt y last.pt) generados pueden utilizarse directamente para inferencia en nuevos tiles o para continuar el fine-tuning con más datos o hiperparámetros ajustados.







