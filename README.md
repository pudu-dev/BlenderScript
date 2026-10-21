# Blender 8D Sprite Exporter

Script para **Blender** que automatiza la creacion de sprites 2D para videojuegos a partir de modelos 3d con animaciones.

El script renderiza todas las animaciones disponibles desde **ocho direcciones diferentes**:

- Frente
- Frente derecha
- Derecha
- Atrás derecha
- Atrás
- Atrás izquierda
- Izquierda
- Frente izquierda

Para cada animación y dirección, genera imágenes individuales en formato **PNG con transparencia** y crea automáticamente un **spritesheet** con los fotogramas renderizados.

## Características

- Exportación automática de todas las acciones disponibles en Blender.
- Renderizado desde ocho direcciones.
- Cantidad de fotogramas configurable.
- Resolución de render configurable.
- Imágenes PNG con canal alfa.
- Creación de carpetas organizadas por animación y dirección.
- Generación automática de spritesheets.
- Exportación opcional de mapas de normales.
- Restauración de la configuración original de Blender al finalizar.

## Configuración

Antes de ejecutar el script, debes modificar los siguientes valores:

#frames
FRAME_COUNT = 8

#nombre de carpeta a crear
OUTPUT_FOLDER_NAME = "Y BOT Animations"

s.render.resolution_x = 1024
s.render.resolution_y = 1024

#ruta destino de carpeta
render8directions_selected_objects(
    r"C:\Users\MIPC\Desktop\blender\blender assets"
)


si por alguna razon hay algun problema con las direcciones, podemos modificar los valores en:

directions = [
    (180, "Back"),
    (135, "Back Right"),
    (90,  "Right"),
    (45,  "Front Right"),
    (0,   "Front"),
    (315, "Front Left"),
    (270, "Left"),
    (225, "Back Left"),
]


## ProBlenderTip: 
# 1- en blender abrir una pestaña con el modelo principal y otra con las animaciones, anexamos las animaciones de una pestaña al modelo con (archivo-anexar) 

# 2- en planilla de tiempos/ editor de acciones , apretamos A en el modo pose y con S en la linea de tiempo podemos ajustar los fotogramas

