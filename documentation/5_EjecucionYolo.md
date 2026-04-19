## NOTAS DE 2026


Sustituye tu sección de "Yolov8 nano, M, L" por las versiones de 2026. La nomenclatura se mantiene, pero el rendimiento en objetos pequeños (tus pingüinos) es superior:

    YOLO26 Nano (yolo26n.pt): Sustituye al v8n. Es mucho más inteligente detectando formas pequeñas.

    YOLO26 Medium (yolo26m.pt): El equilibrio ideal para drones.

    YOLO26 Large (yolo26l.pt): Máxima precisión para conteos científicos finales.



Si el entrenamiento falla con **«expected input to have 3 channels, but got 4»**, los TIFF del dataset tienen 4 bandas (p. ej. RGBA) y YOLO espera RGB (3). Convierte el dataset ya generado y borra cachés de etiquetas:

```bash
python scripts/convert_dataset_tiff_to_rgb.py
```

Los recortes nuevos que guardes con `utils/img_fun.py` ya se exportan en RGB (3 bandas).

Comando adaptado par ael MODELO MEDIO:

```bash

# EL que se ha usado mar 29 a las 13:33 NANO
yolo train model=yolo26n.pt data=datasets/penguin_dataset.yaml epochs=100 imgsz=640 batch=4 device=cpu


# Modelo medio, prosimo a utilizar: no afina demasiado parobar aumentar el tamaño
yolo train model=yolo26s.pt data=datasets/penguin_dataset.yaml epochs=30 imgsz=512 batch=32 device=cpu





yolo train model=yolo26n.pt data=datasets/penguin_dataset.yaml epochs=100 imgsz=640 batch=4 device=cpu


yolo train model=yolo26m.pt data=./datasets/penguin_dataset.yaml epochs=100 imgsz=1024 batch=-1 device=cpu
```





## DOCUMENTACIÓN 2024

Una vez están clasificados los conjunto de entrenamiento y test, se procede a la ejecución de YOLO. Para ello, se debe seguir los siguientes pasos:

1. Creamos el archivo penguin_dataset.yaml, que tiene la configuración básica.
2. Creamos el sistema de directorios y subdirectorios para el entrenamiento y la validación.


Para empezar comenzamos organizando lso conjunjtos de train y test siguiendo esta estructura (esta estructura debe coincidir con la que definamos en el documento de settings de ultralytics).

```bash
datasets/
├── penguin_dataset.yaml
├── penguin_dataset/
    ├── images/
    │   ├── train/
    │   │   ├── 000001.jpg
    │   │   ├── 000002.jpg
    │   ├── val/
    │   │   ├── 000001.jpg
    │   │   ├── 000002.jpg
    ├── labels/
    |   │   ├── train/
    │   │   ├── 000001.jpg
    │   │   ├── 000002.jpg
    │   ├── val/
    │   │   ├── 000001.jpg
    │   │   ├── 000002.jpg
```

# Instalación de dependencias

Comenzamos instalando las dependencias necesarias para el entrenamiento de Yolov8. Para ello, ejecutamos el siguiente comando:

```bash
pip install ultralytics

# o si queremos actualizar la librería
pip upgrade ultralytics
```


# Comprobación de directorios

Si estamos trabajando con Yolov8, y tras instalar ultralytics, se va a generar un documento settings.json en el siguiente directorio de Ultralytics.

```bash

C:\Users\Administrador.CRISASUSESTUDIO\AppData\Roaming\Ultralytics
    
```

Dentro ese directorio encontraremos información ESENCIAL sobre donde se van a buscar las carpetas y los distintos subconjuntos:

```json
  "datasets_dir": "C:\\Users\\Administrador.CRISASUSESTUDIO\\Desktop\\projects\\CountingPenguins\\datasets",
  "weights_dir": "C:\\Users\\Administrador.CRISASUSESTUDIO\\Desktop\\projects\\CountingPenguins\\weights",
  "runs_dir": "C:\\Users\\Administrador.CRISASUSESTUDIO\\Desktop\\projects\\CountingPenguins\\runs",
```




# yolov8: ejecución de entrenamiento

Existen varios parámetros que hay que tener en cuenta:

- Tamaño del batch. A mayor tamaño, mejor resultado, auqnue será más lento. Para pruebas iniciales comienza por 16, y después sube a 32 y 64.
  
- Tamaño de las imágenes. El tamaño de las imágenes debe ser divisible por 32 (por ejemplo, 512). No es conveniente aumentar las imágenes sin un propósito concreto, ya que esto puede provocar distorsión. Normalmetne lo del tamaño se hace al contrario, es decir, tomar imágenes grandes y reducirlas.. o si la distorisión no va a ser significativa.



Existen varias versiones dle modelo yolov8, cada una con distintas características.  A continuación explicamos algunos

### Yolov8 nano

Es rápido, pero no muy preciso. Viene bien para hacer pruebas rápidas.

```bash
yolo train model=yolov8n.pt data=./datasets/penguin_dataset_windows.yaml epochs=100 imgsz=512 batch=16 device=cpu
```

### Yolov8 M

Es más lento, pero más preciso. Viene bien para hacer pruebas siguientes al anterior.

```bash
yolo train model=yolov8m.pt data=./datasets/penguin_dataset.yaml epochs=100 imgsz=512 batch=32 device=cpu

```

### Yolov8 L

Es el más lento, pero el más preciso. Viene bien para hacer pruebas finales.

```bash
yolo train model=yolov8l.pt data=./datasets/penguin_dataset.yaml epochs=100 imgsz=512 batch=64 device=cpu
```



## Carpetas weights y runs

1. weights_dir: Aquí se guardan los pesos entrenados del modelo. Al ejecutar un entrenamiento, el modelo guardará los pesos del mejor modelo (por defecto, al final de cada época).

2. runs_dir: Esta carpeta almacena los resultados de las ejecuciones, como las métricas, los gráficos y otros registros del entrenamiento. Además, guarda un subdirectorio para cada ejecución con un identificador único (por ejemplo, exp seguido de un número).

Para asegurarse de que después de cada entreanmiento los resultados son completamente nuevos, es posible borrar el contenido de estas carpetas manualmetne sin problemas, o ejecutando estos comandos:

```bash
rm -r C:\Users\Administrador.CRISASUSESTUDIO\Desktop\projects\CountingPenguins\weights\*
rm -r C:\Users\Administrador.CRISASUSESTUDIO\Desktop\projects\CountingPenguins\runs\*
```

## Realizar nuevas predicciones

Para realizar nuevas predicciones, se puede ejecutar el siguiente comando:

datasets/penguin_dataset/images/train

```bash
yolo detect predict model=runs/detect/train2/weights/best.pt source=./test/img

# Para guardar las métricas

yolo detect predict model=runs/train4/weights/best.pt source=./datasets/test save_txt=True

yolo detect predict model=runs/detect/train2/weights/best.pt source=./test/img save_txt=True

```
# Realización de test

Comenzamos editando nuestro archivo yaml para indicar donde se van a alejar nuestros TEST.

Creamos la carpeta de test y seguimos la misma estructura para las etiquetas -funciona igual que con train y con val.

Una vez hecho esto, podemos ejecutar el siguiente comando:


```bash	
$ yolo val model=runs/detect/train2/weights/best.pt data=./datasets/penguin_dataset_windows.yaml
```

Si quieres parametrizar el umbral de confianza o el iou, puedes parametrizarlo asi:

```bash
yolo val model=runs/detect/train2/weights/best.pt data=./datasets/penguin_dataset_windows.yaml conf=0.5 iou=0.51

```

El umbral de confianza afecta tanto a falsos positivos como a falsos negativos, pero en mayor medida a los falsos negativos cuando ajustas un umbral alto de confianza.

Bajar el umbral de confianza reducirá los falsos negativos (es decir, el fondo dejará de verse como un pingüino), pero al mismo tiempo aumentará los falsos positivos. Dado este caso, este escenario puede ser deseable, ya que manualmente luego es posible corregir los falsos positivos desmarcándolos. Sin embargo, volver a marcar un pingüino que no fue marcado la primera vez, es más complicado.

# Posibles fallos del modelo

Rebajar el nivel de confianza. Si el nivel de confianza es muy alto, no reportará resultados, así que puede ser bueno rebajarlo.

- Procura mantener el iou por encima del 51%. El iou se refiere a los pinguinos que están justo en los bordes. Necesitamos que haya más de un 51% de pingüino para que lo detecte.
  
```bash
yolo detect predict model=runs/train4/weights/best.pt source=./test/img conf=0.5 iou=0.51 save=True save_txt=True

```




- model=runs/detect/train/weights/best.pt: Esta es la ruta al modelo entrenado, específicamente el mejor modelo guardado (best.pt), que está en la carpeta de runs/detect/train/weights. Si tienes otro archivo de pesos que deseas usar, reemplaza la ruta.

- source=./test_images: Especifica la carpeta donde están las imágenes que quieres probar. En este caso, las imágenes están en ./test_images. Si están en otro lugar, solo cambia la ruta.

### Visualización de los resultados: 
Después de ejecutar el comando, YOLOv8 generará las predicciones y las almacenará en una subcarpeta dentro de runs/detect/predict/. Los resultados incluyen las imágenes con las predicciones y las cajas delimitadoras (bounding boxes).

### Ver los resultados: 
Los resultados estarán en la carpeta de salida que se crea automáticamente, como runs/detect/predict/exp, donde exp será un número de experimento (si es la primera vez que ejecutas este comando).




**VERSIONES ANTIGUAS -NO USAR**
````bash
python train.py --img 640 --batch 16 --epochs 100 --data ../data/penguin_dataset.yaml --weights yolov5s.pt --name penguin_detection

//YOLOV7
python train.py --img 640 --batch 16 --epochs 100 --data ../data/penguin_dataset.yaml --cfg cfg/training/yolov7.yaml --weights 'yolov7.pt' --device cpu

````