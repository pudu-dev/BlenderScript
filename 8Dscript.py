"""                _     
                  | |
 _ __   _   _   __| | _   _
|  _ \ | | | | / _  || | | |
| |_) || |_| || (_| || |_| |
|  __/  \__ _| \__ _| \__ _|
| |
| | Created, Programmed and Designed by:
|_| @Benjamin Maldonado
    benjaminmaldonadobarrales@gmail.com
    https://pudu-dev.vercel.app/ """


import bpy
import os
import math
import glob
from array import array

#CONFIGURACION
#ajustar maximo de fotogramas por animación
FRAME_COUNT = 8
#decidir el nombre de la carpeta, cambiar nombre por cada ejecución
OUTPUT_FOLDER_NAME = "Y BOT Animations"
#ademas debemos decidir la resolucion mas abajo y ajustar la carpeta donde guardaremos

def create_spritesheet(files_by_direction, directions, frames, output_path,
                       frame_width, frame_height):

    # Crear una imagen con ocho filas y una columna por fotograma
    sheet_width = frame_width * len(frames)
    sheet_height = frame_height * len(directions)

    sheet = bpy.data.images.new(
        name="spritesheet_temp",
        width=sheet_width,
        height=sheet_height,
        alpha=True
    )

    try:
        pixels = array('f', [0.0]) * (
            sheet_width * sheet_height * 4
        )

        for direction_index, (angle, angle_dir) in enumerate(directions):

            files = files_by_direction.get(angle_dir, [])

            for frame_index, filepath in enumerate(files):

                if not filepath or not os.path.isfile(filepath):
                    continue

                source = bpy.data.images.load(
                    filepath,
                    check_existing=False
                )

                try:
                    source_width, source_height = source.size

                    if (
                        source_width != frame_width
                        or source_height != frame_height
                    ):
                        print(
                            f"Advertencia: dimensiones incorrectas: "
                            f"{filepath}"
                        )
                        continue

                    source_pixels = array(
                        'f', [0.0]
                    ) * (frame_width * frame_height * 4)

                    source.pixels.foreach_get(source_pixels)

                    # Mantener el orden de directions, de arriba hacia abajo
                    row = direction_index

                    x_offset = frame_index * frame_width
                    y_offset = ((len(directions) - 1 - row) * frame_height)

                    for y in range(frame_height):

                        source_start = y * frame_width * 4
                        source_end = source_start + frame_width * 4

                        target_start = (
                            ((y_offset + y) * sheet_width + x_offset) * 4
                        )
                        target_end = target_start + frame_width * 4

                        pixels[target_start:target_end] = (
                            source_pixels[source_start:source_end]
                        )

                finally:
                    bpy.data.images.remove(source)

        sheet.pixels.foreach_set(pixels)
        sheet.update()

        sheet.filepath_raw = output_path
        sheet.file_format = 'PNG'
        sheet.save()

    finally:
        bpy.data.images.remove(sheet)


def render8directions_selected_objects(path):

    # Preparar la ruta de salida
    path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)

    output_folder = os.path.join(path, OUTPUT_FOLDER_NAME)
    os.makedirs(output_folder, exist_ok=True)

    # Obtener los objetos seleccionados
    selected_list = list(bpy.context.selected_objects)

    if not selected_list:
        print("Error: no hay objetos seleccionados.")
        return

    # El objeto activo debe ser el armature
    o = bpy.context.view_layer.objects.active

    if o is None:
        print("Error: no hay un objeto activo.")
        return

    if o not in selected_list:
        print("Error: el objeto activo debe estar seleccionado.")
        return

    if o.type != 'ARMATURE':
        print(
            "Advertencia: el objeto activo no es un Armature. "
            "Se continuará con el objeto seleccionado."
        )

    if o.animation_data is None:
        o.animation_data_create()

    # Guardar la configuración original
    s = bpy.context.scene

    original_frame = s.frame_current
    original_frame_start = s.frame_start
    original_frame_end = s.frame_end

    original_resolution_x = s.render.resolution_x
    original_resolution_y = s.render.resolution_y
    original_resolution_percentage = s.render.resolution_percentage

    original_filepath = s.render.filepath
    original_file_format = s.render.image_settings.file_format
    original_color_mode = s.render.image_settings.color_mode
    original_film_transparent = s.render.film_transparent

    original_rotation = o.rotation_euler.copy()
    original_action = o.animation_data.action

    # Blender 5.1: el compositor utiliza compositing_node_group
    node_tree = s.compositing_node_group

    normal_output = None
    normal_item = None
    original_node_settings = None

    # Buscar opcionalmente el nodo de salida de normales
    if node_tree:
        for node in node_tree.nodes:

            if node.type != 'OUTPUT_FILE':
                continue

            node_description = (
                f"{node.label} {node.name}"
            ).lower()

            if 'normal' not in node_description:
                continue

            if len(node.file_output_items) == 0:
                continue

            normal_output = node
            normal_item = node.file_output_items[0]

            original_node_settings = (
                normal_output.directory,
                normal_output.file_name,
                normal_item.name
            )

            break

    if normal_output:
        print(
            "Nodo de normales encontrado: "
            f"{normal_output.name}"
        )
    else:
        print(
            "No se encontró un nodo de salida de normales. "
            "Se exportarán solamente los spritesheets de color."
        )

    try:
        # Configuración del render / cambiamos la RESOLUCION AQUI
        s.render.resolution_x = 1024
        s.render.resolution_y = 1024
        s.render.resolution_percentage = 100

        # PNG con transparencia
        s.render.image_settings.file_format = 'PNG'
        s.render.image_settings.color_mode = 'RGBA'
        s.render.film_transparent = True

        # Ocho direcciones
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

        # Obtener todas las acciones disponibles
        actions = list(bpy.data.actions)

        if not actions:
            print("No se encontraron acciones en Blender.")
            return

        # Exportar cada acción
        for a in actions:

            print(f"\nExportando animación: {a.name}")

            # Asignar la acción al armature
            o.animation_data.action = a

            # Obtener el rango de fotogramas
            frame_start = math.floor(a.frame_range[0])
            frame_end = math.ceil(a.frame_range[1])

            #cuenta el total de fotogramas y los divide uniformemente para obtener el numero de frames deseados desde inicio a final de la animacion
            total_frames = frame_end - frame_start + 1
            frame_count = min(FRAME_COUNT, total_frames)

            if frame_count == 1:
                frames = [frame_start]
            else:
                frames = [
                    round(
                        frame_start
                        + index * (frame_end - frame_start) / (frame_count - 1)
                    )
                    for index in range(frame_count)
                ]

            if not frames:
                print(f"Se omite la acción vacía: {a.name}")
                continue

            s.frame_start = frame_start
            s.frame_end = frame_end

            # Crear una carpeta por animación
            action_folder = os.path.join(output_folder, a.name)
            os.makedirs(action_folder, exist_ok=True)

            direction_files = {}
            normal_files = {}

            # Recorrer las ocho direcciones
            for angle, angle_dir in directions:

                animation_folder = os.path.join(
                    action_folder,
                    angle_dir
                )
                os.makedirs(animation_folder, exist_ok=True)

                direction_files[angle_dir] = []

                normal_folder = None

                if normal_output:
                    normal_folder = os.path.join(
                        action_folder,
                        f"{angle_dir}_Normals"
                    )
                    os.makedirs(normal_folder, exist_ok=True)

                    normal_files[angle_dir] = []

                # Rotar el armature con la cámara fija
                o.rotation_euler[2] = (
                    original_rotation[2] + math.radians(angle)
                )

                # Renderizar cada fotograma
                for i in frames:

                    s.frame_set(i)

                    filename = (
                        f"{a.name}_{angle_dir}_{i:03d}.png"
                    )

                    filepath = os.path.join(
                        animation_folder,
                        filename
                    )

                    s.render.filepath = filepath

                    normal_prefix = None

                    if normal_output:

                        # Blender 5.1 utiliza directory y file_name
                        normal_prefix = os.path.join(
                            normal_folder,
                            f"{a.name}_{angle_dir}_{i:03d}"
                        )

                        # Eliminar archivos anteriores con este prefijo
                        for old_file in glob.glob(
                            normal_prefix + "*"
                        ):
                            if os.path.isfile(old_file):
                                os.remove(old_file)

                        normal_output.directory = normal_folder
                        normal_output.file_name = (
                            f"{a.name}_{angle_dir}_{i:03d}_normal"
                        )

                    # Renderizar color y ejecutar el compositor
                    bpy.ops.render.render(write_still=True)

                    direction_files[angle_dir].append(filepath)

                    # Comprobar si se creó un archivo de normales
                    if normal_output and normal_prefix:

                        candidates = [
                            f for f in glob.glob(normal_prefix + "*")
                            if os.path.isfile(f)
                        ]

                        if candidates:
                            normal_path = max(
                                candidates,
                                key=os.path.getmtime
                            )
                            normal_files[angle_dir].append(normal_path)
                        else:
                            normal_files[angle_dir].append(None)

                print(
                    f"Dirección {angle_dir}: "
                    f"{len(frames)} fotogramas."
                )

            # Crear spritesheet de color
            create_spritesheet(
                direction_files,
                directions,
                frames,
                os.path.join(
                    action_folder,
                    "spritesheet.png"
                ),
                s.render.resolution_x,
                s.render.resolution_y
            )

            print(
                f"Spritesheet de color creado: {a.name}"
            )

            # Crear spritesheet de normales solo si hay archivos
            has_normals = (
                normal_output is not None
                and any(
                    filepath
                    for files in normal_files.values()
                    for filepath in files
                )
            )

            if has_normals:

                create_spritesheet(
                    normal_files,
                    directions,
                    frames,
                    os.path.join(
                        action_folder,
                        "spritesheetnormals.png"
                    ),
                    s.render.resolution_x,
                    s.render.resolution_y
                )

                print(
                    f"Spritesheet de normales creado: {a.name}"
                )

            else:
                print(
                    f"No se generaron normales para {a.name}. "
                    "Se omite spritesheetnormals.png."
                )

    finally:
        # Restaurar la rotación y la acción originales
        o.rotation_euler = original_rotation
        o.animation_data.action = original_action

        # Restaurar el nodo de salida de normales
        if normal_output and original_node_settings:

            (
                original_directory,
                original_file_name,
                original_item_name
            ) = original_node_settings

            normal_output.directory = original_directory
            normal_output.file_name = original_file_name
            normal_item.name = original_item_name

        # Restaurar el fotograma y el rango originales
        s.frame_set(original_frame)

        s.frame_start = original_frame_start
        s.frame_end = original_frame_end

        # Restaurar la configuración de render
        s.render.resolution_x = original_resolution_x
        s.render.resolution_y = original_resolution_y
        s.render.resolution_percentage = original_resolution_percentage

        s.render.filepath = original_filepath
        s.render.image_settings.file_format = original_file_format
        s.render.image_settings.color_mode = original_color_mode
        s.render.film_transparent = original_film_transparent

    print("\nExportación de todas las animaciones finalizada.")


# Ruta de salida: ajustar carpeta de salida
render8directions_selected_objects(
    r"C:\Users\MIPC\Desktop\blender\blender assets"
)


"""                _     
                  | |
 _ __   _   _   __| | _   _
|  _ \ | | | | / _  || | | |
| |_) || |_| || (_| || |_| |
|  __/  \__ _| \__ _| \__ _|
| |
| | Creado, Programado y Diseñado por:
|_| @Benjamin Maldonado
    benjaminmaldonadobarrales@gmail.com
    https://pudu-dev.vercel.app/
"""