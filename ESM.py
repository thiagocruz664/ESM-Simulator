#    ESM Simulator its a GUI for programing in assmbly of the ESMx16 ISA

#    Copyright © 2025 Cruz Thiago, Ryberg Brian, Meier Jonathan, Hernan Kisiel, Roberto Carballo, Matías Krujoski y Alicia Rendon.

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Controlador principal de ESM Simulator.

El archivo coordina cuatro responsabilidades sin modificar el diseño de los
componentes graficos:

1. Preprocesa el texto del editor y valida su formato.
2. Delega al nucleo LEX/YACC la validacion y ejecucion del programa.
3. Usa traducir_instruccion() como unico punto de conversion entre assembler
   y palabras ESMx16 de 16 bits.
4. Sincroniza la memoria, el acumulador, las flags, el PC y los TRAP con la GUI.

Las funciones se agrupan por secciones y se documentan con sus parametros y
valores de retorno para que el flujo pueda mantenerse sin depender de bloques
de logica incrustados en los callbacks.
"""

import ctypes
import configparser
import os
import platform
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

from GUI_barraMenu import BarraMenu
from GUI_entradaMemoria import EditorTexto, Memoria
from GUI_help import Ayuda
from GUI_info import Informacion
from GUI_salidaEstado import Consola, Variables

version = 20.0
"""
Change log:
    +   Se reestructuro y documento todo el código yacc del programa
    
    +   Se elimino la función nzpeador(), el funcionamiento de la misma fue derivado a la 
        función modificar_acumulador() y se implemento su uso en el parser
    
    +   Se documento todo el codigo GUI_barraMenu.py
    
    +   Se documento todo el codigo GUI_entradaMemoria.py
    
    +   Se documento todo el codigo GUI_salidaEstado.py

    +   Se unificaron traductor_para_st y el traductor Brianesco en la funcion
        traducir_instruccion(), utilizada para ensamblar y desensamblar.

    +   Se reestructuro y documento todo el codigo de ESM.py.

    +   Se implemento HALT como alias exacto de TRAP x25 en el traductor,
        el ensamblado, el desensamblado y la ejecucion.

    +   Se soluciono un problema con lineas erroneas no interpretadas como tal, 
        cargando un valor 0 en la memoria.
        
    +   Se creo una nueva pestaña de ayuda con la documentacion de las 
        instrucciones y ejemplos de codigos de la ESM,
"""
# Constantes de la arquitectura ESMx16 y de la traduccion de instrucciones.
TAMANO_MEMORIA = 1 << 16
MASCARA_PALABRA = TAMANO_MEMORIA - 1
DIRECCION_CARGA_BINARIA = 0x3000
MODO_ENSAMBLAR = "ensamblar"
MODO_DESENSAMBLAR = "desensamblar"
PREFIJO_FILL_INTERNO = "ETIQUETAINTERNAFILL"
MAX_ITERACIONES_BRANCH = 200

# Estado compartido por los callbacks de Tkinter y la biblioteca nativa.
primer_inicio = True
s = 0
ab = 0
tib = 0
end = False
ruta_archivo = None
diccionario = None
pc = None
runer2 = False
runer = 0
lang, current_theme, theme = None, None, None
contador_branch = {}
lib = None
ventana = None
menu = None
editor = None
consola = None
memoria = None
data_view = None
zoom_value = 100

# ---------------------------------------------------------------------------
# Diagnostico, configuracion y comunicacion con la biblioteca nativa
# ---------------------------------------------------------------------------

log_file = open("consola.log", "w", encoding="utf-8")


def log(msj: str) -> None:
    """
    Registra un mensaje de diagnostico en el archivo consola.log.

    Parametros:
        msj (str): Texto que se desea agregar al registro de ejecucion.
    """
    global log_file
    log_file.write(str(msj) + "\n")
    log_file.flush()


def check_permissions() -> None:
    """
    Comprueba los permisos basicos del proceso y registra la informacion
    disponible para facilitar el diagnostico de problemas de inicio.

    Parametros:
        No recibe parametros.
    """
    try:
        # Verificar si es administrador en Windows
        if os.name == 'nt':  # Windows
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            log(f"¿Es administrador?: {'Sí' if is_admin else 'No'}")
            
            # Obtener usuario actual
            username = os.getenv('USERNAME')
            log(f"Usuario actual: {username}")
            
            # Verificar permisos de escritura en temp
            temp_dir = os.getenv('TEMP')
            can_write = os.access(temp_dir, os.W_OK)
            log(f"¿Puede escribir en {temp_dir}?: {'Sí' if can_write else 'No'}")
            
        else:  # Linux/Unix
            # Obtener uid y gid
            uid = os.getuid()
            gid = os.getgid()
            log(f"UID: {uid}, GID: {gid}")
            
            # Verificar si es root
            is_root = os.geteuid() == 0
            log(f"¿Es root?: {'Sí' if is_root else 'No'}")
            
            # Verificar permisos de escritura en /tmp
            can_write = os.access('/tmp', os.W_OK)
            log(f"¿Puede escribir en /tmp?: {'Sí' if can_write else 'No'}")
        
        # Verificar directorio actual
        current_dir = os.getcwd()
        log(f"Directorio actual: {current_dir}")
        log(f"¿Puede escribir en directorio actual?: {'Sí' if os.access(current_dir, os.W_OK) else 'No'}")
        
        # Verificar permisos del ejecutable de Python
        python_exe = sys.executable
        log(f"Ejecutable de Python: {python_exe}")
    except OSError as e:
        log(f"Error al verificar permisos: {e}")


def cargar_bibliotecas_c() -> int:
    """
    Carga la biblioteca nativa correspondiente al sistema operativo y
    configura las firmas ctypes de todas las funciones utilizadas por Python.

    Parametros:
        No recibe parametros.

    Retorna:
        int: 1 si la biblioteca se cargo correctamente y 0 si ocurrio un error.
    """
    global lib
    if os.name == "nt":  # Windows
        # Verificar si el intérprete es de 64 bits
        arch = platform.architecture()[0]
        try:
            os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
            lib = ctypes.CDLL("lib.dll") 
        except OSError as e:
            log(f"Error al cargar DLL en Windows: {e}")
            return 0
    elif os.name == "posix":  # Linux/Mac
        try:
            os.environ["LD_LIBRARY_PATH"] = os.getcwd()
            lib = ctypes.CDLL(os.path.join(os.getcwd(), "lib.so"))
        except OSError as e:
            log(f"Error al cargar SO en Linux/Mac: {e}")
            return 0
    else:
        log("Sistema operativo no identificado")
        return 0

    if 'lib' in globals():
        log("Bibliotecas cargadas correctamente.")
    else:
        log("Error al cargar las bibliotecas.")
        return 0
    
    lib.assemble.restype = ctypes.c_int
    lib.assemble.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
    lib.stepin.restype = ctypes.c_int
    lib.stepin.argtypes = [ctypes.c_int, ctypes.c_char_p]
    lib.bandera_check.restype = None
    lib.modificar_acumulador.restype = None
    lib.modificar_acumulador.argtypes = [ctypes.c_int]
    lib.reset.restype = None
    lib.get_line.restype = ctypes.c_char_p
    lib.get_line.argtypes = [ctypes.c_int]
    lib.get_etiq.restype = ctypes.c_char_p
    lib.get_etiq.argtypes = [ctypes.c_int]
    lib.buscarDireccionEtiqueta.restype = ctypes.c_int
    lib.buscarDireccionEtiqueta.argtypes = [ctypes.c_char_p]
    lib.modificar_matriz_dato.restype = None    
    lib.modificar_matriz_dato.argtypes = [ctypes.c_int,ctypes.c_int]
    lib.leer_memoria.restype = ctypes.c_uint
    lib.leer_memoria.argtypes = [ctypes.c_int]
    lib.escribir_memoria.restype = None
    lib.escribir_memoria.argtypes = [ctypes.c_int, ctypes.c_int]
    lib.reemplazar_linea_st.restype = None
    lib.reemplazar_linea_st.argtypes = [ctypes.c_char_p, ctypes.c_int]
    return 1


config = configparser.ConfigParser()


def configs() -> None:
    """
    Lee el idioma y el tema guardados en config.ini, aplicando valores
    predeterminados cuando la configuracion no existe.

    Parametros:
        No recibe parametros.
    """
    try:
        config.read('config.ini')
        global lang, current_theme, theme
        lang = config.get('Settings', 'lang', fallback='es')
        current_theme = config.get('Settings', 'current_theme', fallback='dark')
        theme = themes[current_theme]
    except Exception as ex:
        log(f"Error al leer la configuracion: {ex}")


def guardar_config() -> None:
    """
    Guarda en config.ini el idioma y el tema actualmente seleccionados.

    Parametros:
        No recibe parametros.
    """
    try:
        config.set('Settings', 'lang', lang)
        config.set('Settings', 'current_theme', current_theme)
        with open('config.ini', 'w') as configfile: 
            config.write(configfile)
    except Exception as ex:
        log(f"Error al guardar la configuracion: {ex}")


# ---------------------------------------------------------------------------
# Preprocesamiento y validacion del codigo fuente
# ---------------------------------------------------------------------------


def es_linea_vacia(linea: str) -> bool:
    """
    Determina si una linea carece de contenido significativo.

    Parametros:
        linea (str): Linea de texto que se desea analizar.

    Retorna:
        bool: True cuando la linea esta vacia o contiene solo espacios.
    """
    return not linea.strip()


def eliminar_espacios(linea: str) -> str:
    """
    Elimina los espacios ubicados al comienzo y al final de una linea.

    Parametros:
        linea (str): Linea cuyo espaciado exterior se desea normalizar.

    Retorna:
        str: Linea sin espacios exteriores.
    """
    return linea.strip()


def eliminar_comentarios(linea: str) -> str:
    """
    Quita de una linea el comentario iniciado por una doble barra.

    Parametros:
        linea (str): Linea de codigo assembler que se desea procesar.

    Retorna:
        str: Fragmento anterior al comentario o la linea original.
    """
    comentario = linea.find("//")
    if comentario != -1:
        return linea[:comentario]
    return linea


def validar_separacion_instruccion_operando(segmento: str) -> int:
    """
    Comprueba que las instrucciones y directivas que reciben operandos no los
    tengan pegados al nombre de la operacion. De este modo ``ADD #-2`` es
    valido, mientras que ``ADD#-2`` se rechaza antes de llegar al traductor.

    La comprobacion tambien contempla instrucciones con etiqueta de linea,
    ramas compactas y las directivas que reciben un valor.

    Parametros:
        segmento (str): Sentencia assembler sin comentarios que se validara.

    Retorna:
        int: 0 cuando la separacion es valida o 321 cuando falta el espacio.
    """
    operaciones = ("ADD", "AND", "NOTA", "LD", "ST", "TRAP")

    for token in segmento.split():
        for operacion in operaciones:
            if (
                len(token) > len(operacion)
                and token.startswith(operacion)
                and token[len(operacion)] in {"#", "x"}
            ):
                return 321

        if token.startswith("BR") and any(
            caracter in token[2:] for caracter in ("#", "x")
        ):
            return 321

        if token.startswith(".ORIGx") or token.startswith(".FILL#"):
            return 321

    return 0


def quitar_etiqueta_de_linea(linea: str, etiqueta: str | None) -> str:
    """
    Quita unicamente la etiqueta ubicada al inicio de una linea, sin alterar
    las letras que forman parte de la instruccion o de sus operandos.

    Parametros:
        linea (str): Linea assembler que puede comenzar con una etiqueta.
        etiqueta (str | None): Etiqueta asociada a la direccion de memoria.

    Retorna:
        str: Linea sin la etiqueta inicial cuando esta coincide.
    """
    if not etiqueta:
        return linea

    texto = linea.lstrip()
    if not texto.startswith(etiqueta):
        return linea

    resto = texto[len(etiqueta):]
    if resto and not resto[0].isspace():
        return linea
    return resto.lstrip()


def debe_diferir_reflejo_trap(
    run_en_curso: bool, palabra_siguiente: int
) -> bool:
    """
    Indica si la entrada de TRAP x23 debe mostrarse recien en el TRAP x21
    siguiente para evitar que Run refleje dos veces el mismo caracter.

    Parametros:
        run_en_curso (bool): Indica si se esta ejecutando el modo continuo.
        palabra_siguiente (int): Palabra almacenada en la siguiente direccion.

    Retorna:
        bool: True cuando el reflejo debe diferirse hasta TRAP x21.
    """
    # Se conserva la mascara literal para que esta funcion pura pueda probarse
    # de manera aislada, sin depender del estado global del modulo.
    return bool(run_en_curso) and (palabra_siguiente & 0xFFFF) == 0xE021


def preparar_fill_sin_etiqueta(segmento: str, indice: int) -> tuple[str, int]:
    """
    Agrega una etiqueta tecnica a un .FILL sin etiqueta para mantener la
    compatibilidad con el parser nativo. La etiqueta no se muestra en la GUI.

    Parametros:
        segmento (str): Segmento de codigo que puede contener un .FILL.
        indice (int): Numero correlativo usado para generar una etiqueta unica.

    Retorna:
        tuple[str, int]: Segmento normalizado y siguiente indice disponible.
    """
    tokens = segmento.split()
    if tokens and tokens[0] == ".FILL":
        return f"{PREFIJO_FILL_INTERNO}{indice} {segmento}", indice + 1
    return segmento, indice


def encontrar_etiqueta_no_definida(lineas) -> str | None:
    """
    Busca referencias simbolicas que no poseen una declaracion en el codigo,
    sin rechazar etiquetas validas definidas en lineas posteriores.

    Parametros:
        lineas (Iterable[str]): Lineas preprocesadas que se desean validar.

    Retorna:
        str | None: Primera etiqueta no definida o None si todas existen.
    """
    operaciones = {
        "ADD", "AND", "NOTA", "NOTB", "LD", "ST", "TRAP", "HALT"
    }
    directivas = {".ORIG", ".END", ".FILL", ".BLKW"}
    etiquetas = set()
    instrucciones = []

    for linea in lineas:
        texto = linea.split("//", 1)[0]
        for segmento in texto.split(";"):
            tokens = segmento.split()
            if not tokens:
                continue

            primero = tokens[0]
            es_operacion = primero in operaciones or primero.startswith("BR")
            if primero not in directivas and not es_operacion:
                etiquetas.add(primero)
                tokens = tokens[1:]

            if tokens:
                instrucciones.append(tokens)

    for tokens in instrucciones:
        operacion = tokens[0]
        operando = None
        if operacion in {"ADD", "AND", "NOTA", "LD", "ST"}:
            if len(tokens) > 1:
                operando = tokens[1]
        elif operacion == "BR":
            if len(tokens) > 2:
                operando = tokens[2]
        elif operacion.startswith("BR"):
            if len(tokens) > 1:
                operando = tokens[1]

        if (
            operando
            and not operando.startswith(("#", "x"))
            and operando not in etiquetas
        ):
            return operando

    return None


def procesar_linea(linea: str, archivo_salida, contador_fill: int = 0) -> int:
    """
    Elimina comentarios, separa instrucciones por punto y coma y escribe cada
    segmento valido en el archivo temporal de ensamblado.

    Parametros:
        linea (str): Linea original leida desde el archivo fuente.
        archivo_salida (TextIO): Archivo temporal donde se escriben segmentos.
        contador_fill (int): Correlativo para los .FILL que no tienen etiqueta.

    Retorna:
        int: Valor actualizado del contador de .FILL internos.
    """
    linea = eliminar_comentarios(linea)
    segmentos = linea.split(';')
    for segmento in segmentos:
        segmento = eliminar_espacios(segmento)
        if not es_linea_vacia(segmento):
            segmento, contador_fill = preparar_fill_sin_etiqueta(
                segmento, contador_fill
            )
            archivo_salida.write(segmento + '\n')
    return contador_fill

def preprocesado(direccion_archivo: str, archivo_salida_path: str) -> int:
    """
    Normaliza el archivo fuente y determina si contiene assembler, palabras
    binarias o palabras hexadecimales.

    Parametros:
        direccion_archivo (str): Ruta del archivo fuente seleccionado.
        archivo_salida_path (str): Ruta del archivo temporal normalizado.

    Retorna:
        int: 0 para assembler, -2 para binario, -16 para hexadecimal o 221
        cuando se mezclaron formatos incompatibles.
    """
    Binario = True
    Hexa = True
    Normal = False
    historial = 0
    contador_fill = 0
    e=0
    log(f"ARCHIVO LLEGADO PREPROCESADO: {direccion_archivo}")
    try:
        with open(direccion_archivo, 'r', encoding='utf-8') as archivo_entrada:
            with open(archivo_salida_path, 'w', encoding='utf-8') as archivo_salida:
                for linea in archivo_entrada:

                    linea_sin_comentarios = eliminar_comentarios(linea)
                    for segmento in linea_sin_comentarios.split(";"):
                        error_separacion = (
                            validar_separacion_instruccion_operando(segmento)
                        )
                        if error_separacion != 0:
                            return error_separacion

                    linea_a_analizar = linea.replace("\n","")
                    if len(linea_a_analizar)==16 and Binario == True:
                        try:
                            int(linea_a_analizar, 2)
                            Binario = True
                            Hexa = False
                            historial +=1
                        except ValueError:
                            log("La linea no coincide con el formato binario")
                            Binario = False
                    else:
                        if len(linea_a_analizar)!=0:
                            Binario = False
                    if len(linea_a_analizar)==4 and Hexa == True:
                        try:
                            int(linea_a_analizar, 16)
                            Hexa = True
                            Binario = False
                            historial +=1
                        except ValueError:
                            log("La linea no coincide con el formato hexadecimal")
                            Hexa = False
                    else:
                        if len(linea_a_analizar)!=0:
                            Hexa=False
                    if Binario == False and Hexa == False and historial == 0:
                        Normal = True

                    log(f"LINEA: {linea.strip()}")
                    contador_fill = procesar_linea(
                        linea, archivo_salida, contador_fill
                    )
                    
        log(f"Binario = {Binario}, Hexa = {Hexa}, Normal = {Normal}\n")
        if Binario == True and Hexa == False and Normal == False:
            e=-2
        elif Binario == False and Hexa == True and Normal == False:
            e=-16
        elif Binario == False and Hexa == False and Normal == True:
            pass
        else:
            e=221
        return e
    except Exception as ex:
        log(f"Error durante el preprocesado: {ex}")
# El archivo se crea una sola vez y se reutiliza como salida del preprocesado.
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    archivo_salida_path = temp_file.name
with open(archivo_salida_path, 'r', encoding='utf-8') as temp_file:
    contenido = temp_file.read()
    print(contenido)

# ---------------------------------------------------------------------------
# Gestion de archivos y mensajes de la interfaz
# ---------------------------------------------------------------------------


def nuevo_archivo() -> None:
    """
    Limpia el editor y prepara un documento nuevo sin ruta de guardado.

    Parametros:
        No recibe parametros.
    """
    menu.frame_close()
    global ruta_archivo
    try:
        log("Archivo nuevo")
        ruta_archivo = None
        editor.code_editor.delete(1.0, tk.END)
        if lang == "es":
            editor.code_title.config(text="sin_nombre.txt")
        if lang =="en":
            editor.code_title.config(text="untitled.txt")
        menu.frame_close()
    except Exception as ex:
        log(f"Error al crear un archivo nuevo: {ex}")
def abrir_archivo() -> None:
    """
    Abre el selector de archivos y carga en el editor el archivo de texto
    elegido por el usuario.

    Parametros:
        No recibe parametros.
    """
    menu.frame_close()
    editor.archivo=True
    archivo = filedialog.askopenfilename(
        title="Abrir archivo",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if archivo:
        try:
            with open(archivo, "r", encoding="utf-8") as file:
                contenido = file.read()
                editor.code_editor.delete(1.0, tk.END)
                editor.code_editor.insert(tk.END, contenido.rstrip("\n"))
                editor.code_editor.edit_reset() 
                editor.code_title.config(text=os.path.basename(archivo))
                global ruta_archivo
                ruta_archivo = archivo
                editor.archivo = False
            log(f"Archivo abierto {ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
            log(f"No se pudo abrir el archivo: {e}")
            error(100)
def escrivir_archivo() -> None:
    """
    Recarga en el editor el contenido de la ruta actualmente seleccionada.
    Se conserva el nombre historico porque otros componentes lo reciben como
    callback.

    Parametros:
        No recibe parametros.
    """
    global ruta_archivo
    if ruta_archivo:
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as file:
                contenido = file.read()
                editor.code_editor.delete(1.0, tk.END)
                editor.code_editor.insert(tk.END, contenido)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
            log(f"No se pudo recargar el archivo: {e}")
            error(100)     
def guardar_archivo(event=None) -> None:
    """
    Guarda el contenido actual del editor o deriva la operacion a Guardar como
    cuando el documento todavia no posee una ruta.

    Parametros:
        event (tk.Event | None): Evento de teclado opcional enviado por Tkinter.
    """
    try:
        menu.frame_close()
    except Exception:
        pass
    if ruta_archivo:
        try:
            with open(ruta_archivo, "w", encoding="utf-8") as file:
                contenido = editor.code_editor.get(1.0, tk.END)
                file.write(contenido)
                log(f"Archivo guardado {ruta_archivo}")
                if lang == "es":
                    mostrar_mensaje("Archivo guardado exitosamente.")
                elif lang == "en":
                    mostrar_mensaje("File saved successfully.")
        except Exception as e:
            if lang == "es":
                mostrar_mensaje(f"No se pudo guardar el archivo: {e}")
            elif lang == "en":
                mostrar_mensaje(f"Could not save the file: {e}")
            log(f"No se pudo guardar el archivo: {e}")
    else:
        guardar_como()
def guardar_como(event=None) -> None:
    """
    Solicita una nueva ruta, guarda el contenido del editor y actualiza el
    titulo mostrado por la interfaz.

    Parametros:
        event (tk.Event | None): Evento de teclado opcional enviado por Tkinter.
    """
    menu.frame_close()
    archivo = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if archivo:
        try:
            with open(archivo, "w", encoding="utf-8") as file:
                contenido = editor.code_editor.get(1.0, tk.END)
                file.write(contenido)
                global ruta_archivo
                ruta_archivo = archivo
                editor.code_editor.delete(1.0, tk.END)
                editor.code_editor.insert(tk.END, contenido)
                editor.code_editor.edit_reset() 
                editor.code_title.config(text=os.path.basename(archivo))
                log(f"Archivo guardado {ruta_archivo}")
                if lang == "es":
                    mostrar_mensaje("Archivo guardado exitosamente.")
                elif lang == "en":
                    mostrar_mensaje("File saved successfully.")
        except Exception as e:
            if lang == "es":
                mostrar_mensaje(f"No se pudo guardar el archivo: {e}")
            elif lang == "en":
                mostrar_mensaje(f"Could not save the file: {e}")
            log(f"No se pudo guardar como el archivo: {e}")


def separar_segmentos_codigo_fuente(codigo_fuente: str) -> list[str]:
    """
    Obtiene las sentencias significativas del codigo escrito en el editor,
    eliminando comentarios y separando las instrucciones unidas por punto y
    coma. Esta funcion no consulta ni modifica la memoria de ejecucion.

    Parametros:
        codigo_fuente (str): Texto assembler, binario o hexadecimal que se
        desea preparar para su exportacion.

    Retorna:
        list[str]: Sentencias del programa en el orden en que fueron escritas.
    """
    segmentos = []
    for linea in codigo_fuente.splitlines():
        linea = eliminar_comentarios(linea)
        for segmento in linea.split(";"):
            segmento = eliminar_espacios(segmento)
            if not es_linea_vacia(segmento):
                segmentos.append(segmento)
    return segmentos


def es_operacion_o_directiva(token: str) -> bool:
    """
    Indica si un token corresponde a una instruccion o directiva de ESMx16 y,
    por lo tanto, no debe interpretarse como una etiqueta de linea.

    Parametros:
        token (str): Primer elemento de una sentencia del codigo fuente.

    Retorna:
        bool: True si el token es una operacion o una directiva conocida.
    """
    operaciones = {
        "ADD", "AND", "NOTA", "NOTB", "LD", "ST", "TRAP", "HALT"
    }
    directivas = {".ORIG", ".END", ".FILL", ".BLKW"}
    return token in operaciones or token in directivas or token.startswith("BR")


def analizar_codigo_assembler_para_exportacion(
    segmentos: list[str],
) -> tuple[list[tuple[int, str]], dict[str, int]]:
    """
    Realiza las dos tareas previas a traducir el codigo fuente: calcula la
    direccion de cada etiqueta y asocia cada sentencia que ocupa memoria con
    su direccion. Las directivas .ORIG y .END no generan palabras de salida.

    Parametros:
        segmentos (list[str]): Sentencias assembler normalizadas y ordenadas.

    Retorna:
        tuple[list[tuple[int, str]], dict[str, int]]: Celdas del programa como
        pares direccion-sentencia y tabla local de etiquetas.

    Lanza:
        ValueError: Si falta .ORIG o su direccion no posee un formato valido.
    """
    celdas = []
    etiquetas = {}
    direccion = None

    for segmento in segmentos:
        tokens = segmento.split()
        if not tokens:
            continue

        if tokens[0] == ".ORIG":
            if len(tokens) != 2 or not tokens[1].startswith("x"):
                raise ValueError("La directiva .ORIG debe indicar una direccion hexadecimal.")
            direccion = int(tokens[1][1:], 16)
            if not 0 <= direccion < TAMANO_MEMORIA:
                raise ValueError("La direccion de .ORIG esta fuera del rango de memoria.")
            continue

        if tokens[0] == ".END":
            break

        if direccion is None:
            raise ValueError("El codigo assembler debe comenzar con la directiva .ORIG.")

        if not es_operacion_o_directiva(tokens[0]):
            etiqueta = tokens.pop(0)
            etiquetas[etiqueta] = direccion
            if not tokens:
                continue

        if tokens[0] == ".END":
            break

        celdas.append((direccion, " ".join(tokens)))
        direccion = (direccion + 1) & MASCARA_PALABRA

    return celdas, etiquetas


def generar_palabras_desde_codigo_fuente(codigo_fuente: str) -> tuple[int, ...]:
    """
    Genera las palabras originales del programa exclusivamente desde el texto
    del editor. No lee ``diccionario`` ni la memoria nativa, por lo que una
    escritura ST ejecutada previamente no puede alterar la exportacion.

    Las entradas binarias y hexadecimales se conservan directamente. Para
    assembler se calculan las etiquetas en una primera pasada y se utiliza el
    traductor unico en una segunda pasada. Cada .BLKW produce cero y cada
    .FILL conserva el valor declarado en el codigo.

    Parametros:
        codigo_fuente (str): Contenido actual del editor de codigo.

    Retorna:
        tuple[int, ...]: Palabras de 16 bits en el orden del programa.

    Lanza:
        ValueError: Si el codigo esta vacio o contiene una sentencia que no se
        puede traducir correctamente.
    """
    segmentos = separar_segmentos_codigo_fuente(codigo_fuente)
    if not segmentos:
        raise ValueError("No hay codigo para exportar.")

    for segmento in segmentos:
        if validar_separacion_instruccion_operando(segmento) == 321:
            raise ValueError(
                "La instruccion y su operando deben estar separados por "
                f"un espacio: '{segmento}'."
            )

    if all(len(linea) == 16 and set(linea) <= {"0", "1"} for linea in segmentos):
        return tuple(int(linea, 2) for linea in segmentos)

    digitos_hexadecimales = set("0123456789abcdefABCDEF")
    if all(
        len(linea) == 4 and set(linea) <= digitos_hexadecimales
        for linea in segmentos
    ):
        return tuple(int(linea, 16) for linea in segmentos)

    celdas, etiquetas = analizar_codigo_assembler_para_exportacion(segmentos)
    palabras = []
    for direccion, sentencia in celdas:
        binario = traducir_instruccion(
            sentencia,
            direccion,
            MODO_ENSAMBLAR,
            etiquetas=etiquetas,
        )
        if not isinstance(binario, str) or len(binario) != 16:
            raise ValueError(
                f"No se pudo traducir la sentencia '{sentencia}' "
                f"(codigo {binario})."
            )
        palabras.append(int(binario, 2) & MASCARA_PALABRA)
    return tuple(palabras)


def formatear_palabras_para_exportacion(
    palabras: tuple[int, ...], formato: str
) -> tuple[str, ...]:
    """
    Convierte palabras ESMx16 al formato textual seleccionado.

    Parametros:
        palabras (tuple[int, ...]): Palabras originales obtenidas del codigo.
        formato (str): Formato de salida, "binario" o "hexadecimal".

    Retorna:
        tuple[str, ...]: Lineas listas para escribir en el archivo de salida.

    Lanza:
        ValueError: Si el formato solicitado no es valido.
    """
    if formato == "binario":
        return tuple(format(palabra, "016b") for palabra in palabras)
    if formato == "hexadecimal":
        return tuple(format(palabra, "04X") for palabra in palabras)
    raise ValueError(f"Formato de exportacion no valido: {formato}")


def guardar_archivo_maquina(formato: str) -> None:
    """
    Guarda el programa en binario o hexadecimal reconstruyendolo desde el
    codigo escrito. La memoria de ejecucion y el diccionario visual no se usan
    como origen de los datos exportados.

    Parametros:
        formato (str): Formato de salida, "binario" o "hexadecimal".
    """
    menu.frame_close()
    if not memoria.ensamblado:
        error(220)
        log(f"Error en guardar_archivo_maquina {220}")
        return

    extension = ".bin" if formato == "binario" else ".hex"
    nombre = os.path.splitext(ruta_archivo)[0] + extension
    try:
        codigo_fuente = editor.code_editor.get("1.0", "end-1c")
        palabras = generar_palabras_desde_codigo_fuente(codigo_fuente)
        lineas = formatear_palabras_para_exportacion(palabras, formato)
        with open(nombre, "w", encoding="utf-8") as archivo:
            for linea in lineas:
                archivo.write(linea + "\n")
        mostrar_mensaje(f"Archivo guardado '{os.path.basename(nombre)}'")
        log(f"Archivo guardado {nombre} desde el codigo fuente")
    except Exception as ex:
        mostrar_mensaje(f"No se pudo guardar el archivo: {ex}")
        log(f"No se pudo guardar el archivo {formato}: {ex}")


def guardar_archivo_binario() -> None:
    """
    Exporta las palabras del ultimo ensamblado a un archivo con extension .bin.

    Parametros:
        No recibe parametros.
    """
    guardar_archivo_maquina("binario")


def guardar_archivo_hexadecimal() -> None:
    """
    Exporta las palabras del ultimo ensamblado a un archivo con extension .hex.

    Parametros:
        No recibe parametros.
    """
    guardar_archivo_maquina("hexadecimal")

def mostrar_mensaje(mensaje: str, duracion: int = 1000) -> None:
    """
    Muestra una notificacion temporal sobre el editor usando el tema activo.

    Parametros:
        mensaje (str): Texto que se desea mostrar al usuario.
        duracion (int): Tiempo de visualizacion expresado en milisegundos.
    """
    theme = themes[current_theme]
    ventana_mensaje = tk.Toplevel() 
    ventana_mensaje.overrideredirect(1) # Elimina la barra de título 

    ventana_width = editor.code_editor.winfo_width()
    ventana_height = editor.code_editor.winfo_height()
    ventana_x = editor.code_editor.winfo_x()
    ventana_y = editor.code_editor.winfo_y()
    x = ventana_x + (ventana_width // 2)
    y = ventana_y + (ventana_height // 2)

    ventana_mensaje.geometry("+{}+{}".format(x, y)) # Posiciona la ventana 
    tk.Label(ventana_mensaje, text=mensaje, bg=theme["menu_bg"], fg=theme["menu_fg"], padx=10, pady=5).pack() 
    ventana_mensaje.after(duracion, ventana_mensaje.destroy) # Cierra la ventana después de 'duracion' milisegundos

# ---------------------------------------------------------------------------
# Traductor unico ESMx16
# ---------------------------------------------------------------------------


def offset_numericos(offset12: int, binary: str) -> str:
    """
    Codifica un desplazamiento numerico de 12 bits en complemento a dos y lo
    concatena al codigo de operacion recibido.

    Parametros:
        offset12 (int): Desplazamiento numerico validado por el ensamblador.
        binary (str): Codigo de operacion de cuatro bits.

    Retorna:
        str: Palabra binaria de 16 bits formada por opcode y desplazamiento.
    """
    num_bin = format(offset12 & 0xFFF, "012b")
    return binary + num_bin


def offset_direccion(dir_objetivo: int, binary: str, pc_actual: int) -> str | int:
    """
    Calcula un desplazamiento relativo al PC de 12 bits, considerando el
    retorno circular de la memoria entre xFFFF y x0000.

    Parametros:
        dir_objetivo (int): Direccion absoluta a la que debe apuntar la palabra.
        binary (str): Codigo de operacion de cuatro bits.
        pc_actual (int): Direccion donde se almacenara la instruccion.

    Retorna:
        str | int: Palabra binaria resultante o el codigo de error 319 cuando
        el destino queda fuera del rango representable.
    """
    log(f"PC actual {pc_actual}")
    desplazamiento = (dir_objetivo - (pc_actual + 1)) & MASCARA_PALABRA
    if desplazamiento & 0x8000:
        desplazamiento -= TAMANO_MEMORIA
    if not -2048 <= desplazamiento <= 2047:
        return 319
    return binary + format(desplazamiento & 0xFFF, "012b")


def _direccion_de_etiqueta(
    etiqueta: str, etiquetas: dict[str, int] | None = None
) -> int:
    """
    Consulta en la biblioteca nativa la direccion asociada a una etiqueta.

    Parametros:
        etiqueta (str): Nombre simbolico que se desea resolver.
        etiquetas (dict[str, int] | None): Tabla local opcional utilizada para
        traducir el codigo fuente sin consultar la memoria ni el nucleo.

    Retorna:
        int: Direccion de memoria o -1 cuando la etiqueta no existe.
    """
    if etiquetas is not None:
        return etiquetas.get(etiqueta, -1)

    etiqueta_c = ctypes.c_char_p(etiqueta.encode("utf-8"))
    return lib.buscarDireccionEtiqueta(etiqueta_c)


def _destino_desde_offset(bits_offset: str, direccion: int) -> int:
    """
    Reconstruye una direccion absoluta a partir de un offset relativo al PC.

    Parametros:
        bits_offset (str): Desplazamiento binario en complemento a dos.
        direccion (int): Direccion de la palabra que contiene el offset.

    Retorna:
        int: Direccion absoluta normalizada al rango de 16 bits.
    """
    desplazamiento = int(bits_offset, 2)
    if bits_offset[0] == "1":
        desplazamiento -= 1 << len(bits_offset)
    return (direccion + 1 + desplazamiento) & MASCARA_PALABRA


def _offset_branch(dir_objetivo: int, pc_actual: int) -> str | int:
    """
    Calcula el desplazamiento relativo de 10 bits utilizado por BR.

    Parametros:
        dir_objetivo (int): Direccion absoluta de destino del salto.
        pc_actual (int): Direccion donde se almacenara la instruccion BR.

    Retorna:
        str | int: Offset binario de 10 bits o el codigo de error 318.
    """
    desplazamiento = (dir_objetivo - (pc_actual + 1)) & MASCARA_PALABRA
    if desplazamiento & 0x8000:
        desplazamiento -= TAMANO_MEMORIA
    if not -512 <= desplazamiento <= 511:
        return 318
    return format(desplazamiento & 0x3FF, "010b")


def traducir_instruccion(
    contenido: str | int,
    direccion: int,
    modo: str,
    etiquetas: dict[str, int] | None = None,
) -> str | int | None:
    """
    Traduce instrucciones ESMx16 en ambos sentidos mediante una unica API.
    En modo ensamblar convierte una linea assembler en una palabra binaria;
    en modo desensamblar convierte una palabra de 16 bits en texto assembler.

    Parametros:
        contenido (str | int): Linea assembler o valor numerico de 16 bits.
        direccion (int): Direccion de memoria de la instruccion traducida.
        modo (str): MODO_ENSAMBLAR o MODO_DESENSAMBLAR.
        etiquetas (dict[str, int] | None): Tabla local opcional para resolver
        simbolos directamente desde el codigo fuente durante la exportacion.

    Retorna:
        str | int | None: Traduccion resultante, codigo de error 212, 310, 314,
        318 o 319, o None cuando una palabra representa un dato no traducible.
    """
    if modo == MODO_DESENSAMBLAR:
        binario = format(int(contenido) & MASCARA_PALABRA, "016b")
        opcode = binario[:4]

        if opcode == "0101":
            return "NOTB"
        if opcode == "0100":
            destino = _destino_desde_offset(binario[4:], direccion)
            return f"NOTA x{destino:04x}"
        if opcode == "0001":
            inmediato = int(binario[4:], 2)
            if binario[4] == "1":
                inmediato -= 1 << 12
            return f"ADD #{inmediato}"
        if opcode == "0000":
            destino = _destino_desde_offset(binario[4:], direccion)
            return f"ADD x{destino:04x}"
        if opcode == "0010":
            destino = _destino_desde_offset(binario[4:], direccion)
            return f"AND x{destino:04x}"
        if opcode == "0011":
            inmediato = int(binario[4:], 2)
            if binario[4] == "1":
                inmediato -= 1 << 12
            return f"AND #{inmediato}"
        if opcode == "0110":
            destino = _destino_desde_offset(binario[4:], direccion)
            return f"LD x{destino:04x}"
        if opcode == "0111":
            destino = _destino_desde_offset(binario[4:], direccion)
            return f"ST x{destino:04x}"
        if opcode in {"1000", "1001"}:
            flags = (
                ("n" if binario[3] == "1" else "")
                + ("z" if binario[4] == "1" else "")
                + ("p" if binario[5] == "1" else "")
            )
            destino = _destino_desde_offset(binario[6:], direccion)
            return f"BR {flags} x{destino:04x}"
        if opcode == "1110":
            vector_trap = int(binario[3:], 2)
            return {
                0x21: "TRAP x21" or "OUT",
                0x23: "TRAP x23" or "IN",
                0x25: "TRAP x25" or "HALT",
            }.get(vector_trap)
        return None

    if modo != MODO_ENSAMBLAR:
        raise ValueError(f"Modo de traduccion no valido: {modo}")

    texto = str(contenido).strip()
    if validar_separacion_instruccion_operando(texto) == 321:
        return 321

    tokens = texto.split()
    if not tokens:
        return "0000000000000000"

    instruccion = tokens[0]
    flags = ""
    if instruccion.startswith("BR") and instruccion != "BR":
        flags = instruccion[2:]
        instruccion = "BR"

    if instruccion in {"ADD", "AND", "NOTA", "LD", "ST"}:
        operando = tokens[1]
        opcodes_direccion = {
            "ADD": "0000",
            "AND": "0010",
            "NOTA": "0100",
            "LD": "0110",
            "ST": "0111",
        }
        opcodes_inmediato = {"ADD": "0001", "AND": "0011"}

        if operando.startswith("#"):
            opcode = opcodes_inmediato.get(
                instruccion, opcodes_direccion[instruccion]
            )
            return offset_numericos(int(operando[1:]), opcode)

        if operando.startswith("x"):
            dir_objetivo = int(operando[1:], 16)
        else:
            dir_objetivo = _direccion_de_etiqueta(operando, etiquetas)
            if dir_objetivo == -1:
                return 314
        return offset_direccion(
            dir_objetivo, opcodes_direccion[instruccion], direccion
        )

    if instruccion == "NOTB":
        return "0101000000000000"

    if instruccion == "HALT":
        # HALT no posee una codificacion propia: es el alias de TRAP x25.
        return "1110000000100101"

    if instruccion == "BR":
        if not flags:
            flags = tokens[1]
            operando = tokens[2]
        else:
            operando = tokens[1]

        prefijo = (
            "100"
            + ("1" if "n" in flags else "0")
            + ("1" if "z" in flags else "0")
            + ("1" if "p" in flags else "0")
        )
        if operando.startswith("#"):
            desplazamiento = int(operando[1:])
            if not -512 <= desplazamiento <= 511:
                return 318
            return prefijo + format(desplazamiento & 0x3FF, "010b")
        if operando.startswith("x"):
            dir_objetivo = int(operando[1:], 16)
        else:
            dir_objetivo = _direccion_de_etiqueta(operando, etiquetas)
            if dir_objetivo == -1:
                return 314
        offset = _offset_branch(dir_objetivo, direccion)
        return offset if offset == 318 else prefijo + offset

    if instruccion == ".FILL":
        valor = int(tokens[1][1:])
        if not -32768 <= valor <= 32767:
            return 212
        return format(valor & MASCARA_PALABRA, "016b")

    if instruccion == ".BLKW":
        # Una reserva siempre se representa como cero al exportar el codigo,
        # aunque durante la ejecucion ST haya escrito otro valor en su celda.
        return "0000000000000000"

    if instruccion == "TRAP":
        return {
            "x21": "1110000000100001",
            "x23": "1110000000100011",
            "x25": "1110000000100101",
        }.get(tokens[1], 310)

    # Una sentencia assembler desconocida nunca debe convertirse
    # silenciosamente en una palabra cero: debe detener el ensamblado.
    return 315


def convertir_a_entero_con_signo(valor: int) -> int:
    """
    Interpreta los 16 bits menos significativos de un valor como complemento
    a dos.

    Parametros:
        valor (int): Valor entero recibido desde el nucleo o la memoria.

    Retorna:
        int: Valor equivalente dentro del rango -32768 a 32767.
    """
    palabra = valor & MASCARA_PALABRA
    return palabra - TAMANO_MEMORIA if palabra & 0x8000 else palabra


def leer_estado_nucleo() -> tuple[int, int, str]:
    """
    Lee en una sola operacion logica el acumulador, el PC y las flags ALU de
    la biblioteca nativa.

    Parametros:
        No recibe parametros.

    Retorna:
        tuple[int, int, str]: Acumulador, PC normalizado y flags decodificadas.
    """
    acumulador = ctypes.c_int.in_dll(lib, "acumulador").value
    pc_actual = ctypes.c_int.in_dll(lib, "pc").value & MASCARA_PALABRA
    flags = ctypes.c_char_p.in_dll(lib, "ALUFlags").value.decode("utf-8")
    return acumulador, pc_actual, flags


def reflejar_ultima_escritura_st() -> None:
    """
    Sincroniza el diccionario visual con la ultima palabra escrita por ST. La
    direccion y el valor se leen directamente del nucleo para no volver a
    calcular el destino a partir del texto assembler.

    Parametros:
        No recibe parametros.
    """
    hubo_escritura = ctypes.c_int.in_dll(
        lib, "hubo_escritura_memoria"
    ).value
    if not hubo_escritura:
        return

    direccion_escrita = ctypes.c_int.in_dll(
        lib, "ultima_direccion_escrita"
    ).value
    palabra = lib.leer_memoria(direccion_escrita) & MASCARA_PALABRA
    instruccion = traducir_instruccion(
        palabra, direccion_escrita, MODO_DESENSAMBLAR
    )
    if instruccion is None:
        instruccion = f"#{convertir_a_entero_con_signo(palabra)}"

    etiqueta = diccionario.get(hex(direccion_escrita), (None,))[0]
    diccionario[hex(direccion_escrita)] = (
        etiqueta,
        instruccion,
        format(palabra, "016b"),
        format(palabra, "04X"),
    )
    lib.reemplazar_linea_st(instruccion.encode("utf-8"), direccion_escrita)
    log(
        f"MEMORIA ACTUALIZADA {hex(direccion_escrita)}: "
        f"{diccionario[hex(direccion_escrita)]}"
    )


def registrar_ejecucion_branch(pc_actual: int) -> None:
    """
    Incrementa el contador de una direccion cuando la siguiente instruccion
    registrada es BR, permitiendo detectar posibles bucles infinitos.

    Parametros:
        pc_actual (int): Valor actual del contador de programa.
    """
    try:
        instruccion = diccionario[hex(pc_actual)][1].split()[0]
        if instruccion == "BR" or instruccion.startswith("BR"):
            contador_branch[pc_actual] = contador_branch.get(pc_actual, 0) + 1
    except Exception as ex:
        log(f"ERROR (SE QUISO DETECTAR UN BR): {ex}")


def reflejar_st_pendiente_tras_entrada(
    pc_actual: int, acumulador: int
) -> None:
    """
    Actualiza los metadatos visuales cuando la instruccion posterior a una
    entrada TRAP es ST. La escritura real continua a cargo del nucleo.

    Parametros:
        pc_actual (int): Direccion de la instruccion que sigue al TRAP x23.
        acumulador (int): Caracter ingresado y almacenado en el acumulador.
    """
    try:
        tokens = diccionario[hex(pc_actual)][1].split()
        if not tokens or tokens[0] != "ST":
            return

        operando = tokens[1]
        if operando.startswith("#"):
            direccion_destino = pc_actual + 1 + int(operando[1:])
        elif operando.startswith("x"):
            direccion_destino = int(operando[1:], 16)
        else:
            direccion_destino = _direccion_de_etiqueta(operando)
        direccion_destino &= MASCARA_PALABRA

        palabra = acumulador & MASCARA_PALABRA
        instruccion = traducir_instruccion(
            palabra, direccion_destino, MODO_DESENSAMBLAR
        )
        if instruccion is None:
            instruccion = f"#{convertir_a_entero_con_signo(palabra)}"

        etiqueta = diccionario.get(hex(direccion_destino), (None,))[0]
        diccionario[hex(direccion_destino)] = (
            etiqueta,
            instruccion,
            format(palabra, "016b"),
            format(palabra, "04X"),
        )
        lib.reemplazar_linea_st(
            instruccion.encode("utf-8"), direccion_destino
        )
        log(
            f"MEMORIA PREPARADA {hex(direccion_destino)}: "
            f"{diccionario[hex(direccion_destino)]}"
        )
    except Exception as ex:
        log(f"Error al preparar el reflejo de ST tras una entrada: {ex}")

# ---------------------------------------------------------------------------
# Errores y entrada/salida mediante TRAP
# ---------------------------------------------------------------------------

errores_lang = {
    "es": {
        100: "Error 100: No se pudo abrir el archivo",
        200: "Error 200: La cantidad de instrucciones usando el orig dado sobrepaso la capacidad de la memoria",
        210: "Error 210: El PC intento acceder a una posición fuera del rango de la memoria",
        211: "Error 211: La posicion de memoria salio fuera del rango de la memoria",
        212: "Error 212: El valor de .FILL debe estar entre -32768 y 32767.",
        213: "Error 213: Se sobrepaso el limite numerico permitido en el registro",
        220: "Error 220: No hay código ensamblado",
        221: "Error 221: Inconsistencia en el código ensamblado (Se mezclo binario con hexadecimal o ensamblador)",
        0: "",
        1: "Deteniendo programa…",
        "char_output": "{}",
        "char_input": "Ingrese un carácter --> {}",
        "success": "¡Código ensamblado exitosamente!",
        "stop": "Deteniendo programa…",
        300: "Error 300: Se esperaba un valor numerico o una direccion",
        301: "Error 301: La instrucción NOTB no recibe argumentos",
        302: "Error 302: Las flags estan mal",
        303: "Error 303: Se esperaba una direccion",
        310: "Error 310: Se esperaba una direccion X21, X23 o X25",
        311: "Error 311: Se esperaba un valor hexadecimal valido",
        312: "Error 312: Los valores numericos deben empezar con '#'",
        313: "Error 313: Los valores numéricos deben estar en el rango permitido de -2048 a 2047.",
        314: "Error 314: No hay etiquetas que coincidan",
        315: "Error 315: Caracter invalido",
        316: "Error 316: No se encontro el final del codigo (.END)",
        317: "Error 317: No se encontro la direccion inicial de memoria (.ORIG)",
        318: "Error 318: La instrucción BR esperaba un offset de hasta 9bits (-511 a 512)",
        319: "Error 319: La instrucción esperaba un offset de hasta 12bits (-2048 a 2047)",
        320: "Error 320: Caracter invalido",
        321: "Error 321: La instrucción y su operando deben estar separados por un espacio"
    },
    "en": {
        100: "Error 100: Could not open the file",
        200: "Error 200: The number of instructions using the given .ORIG exceeded memory capacity",
        210: "Error 210: The PC attempted to access a position outside the memory range",
        211: "Error 211: The memory position went out of the memory range",
        212: "Error 212: The .FILL value must be between -32768 and 32767.",
        213: "Error 213: The numeric limit allowed in the register was exceeded",
        220: "Error 220: No assembled code found",
        221: "Error 221: Inconsistency in the assembled code (Binary, hexadecimal or assembler was mixed)",
        0: "",
        1: "Halting program…",
        "char_output": "{}",
        "char_input": "Input a character --> {}",
        "success": "¡Assembly successful!",
        "stop": "Halting program…",
        300: "Error 300: A numeric value or address was expected",
        301: "Error 301: The NOTB instruction does not take arguments",
        302: "Error 302: The flags are incorrect",
        303: "Error 303: An address was expected",
        310: "Error 310: An X21, X23 or X25 address was expected",
        311: "Error 311: A valid hexadecimal value was expected",
        312: "Error 312: Numeric values must start with '#'",
        313: "Error 313: Numeric values must be in the allowed range of -2048 to 2047.",
        314: "Error 314: No matching labels found",
        315: "Error 315: Invalid character",
        316: "Error 316: The end of the code (.END) was not found",
        317: "Error 317: The initial memory address (.ORIG) was not found",
        318: "Error 318: The BR instruction expected an offset of up to 9 bits (-512 to 511)",
        319: "Error 319: The instruction expected an offset of up to 12 bits (-2048 to 2047)",
        320: "Error 320: Invalid character",
        321: "Error 321: The instruction and its operand must be separated by a space"
    }
}
def error(e: int) -> None:
    """
    Muestra un codigo de error en el idioma activo y restablece el simulador
    cuando el codigo representa una falla de ensamblado o ejecucion.

    Parametros:
        e (int): Codigo numerico devuelto por el preprocesador o el nucleo.
    """
    global end, pc, s
    if e != 0 and not end:
        errores = errores_lang[lang]
        if e == 1:
            consola.print(errores[e])
        else:
            if pc:
                if s == 0:
                    c_pc = (ctypes.c_int).in_dll(lib, "pc")
                    pc = c_pc.value
                    consola.print(f"PC (x{format(pc,f'04x')}) => {errores[e]}")
                else:
                    consola.print(f"PC (x{format(pc,f'04x')}) => {errores[e]}")
                    s=4
            else:
                consola.print(errores[e])
        if e != 1:
            reset()
        else:
            end = True

def consola_capture() -> None:
    """
    Habilita la consola para que TRAP x23 capture un unico caracter del teclado.

    Parametros:
        No recibe parametros.
    """
    global lang
    global ab
    ab = 0
    consola.consola.config(state=tk.NORMAL)
    if(lang=="es"):
        consola.consola.insert(tk.END,"Ingrese un carácter --> ")
    elif(lang=="en"):
        consola.consola.insert(tk.END,"Input a character --> ")

    consola.consola.bind("<Key>", capture_char)
    consola.consola.focus()
def capture_char(event) -> str:
    """
    Valida el caracter ingresado para TRAP x23, lo carga en el acumulador,
    actualiza las vistas y reanuda Run cuando corresponde.

    Parametros:
        event (tk.Event): Evento de teclado generado sobre la consola.

    Retorna:
        str: La cadena "break" para impedir el procesamiento normal de Tkinter.
    """
    global tib, ab, runer

    if tib != 1:
        return "break"

    teclas_especiales = {"Return", "KP_Enter"}
    teclas_ignorar = {
        "Shift_L", "Shift_R", "Control_L", "Control_R",
        "Alt_L", "Alt_R", "Caps_Lock", "Meta", "ISO_Level3_Shift"
    }
    char = '\r' if event.keysym in teclas_especiales else event.char

    if event.keysym in teclas_ignorar or (event.state & 0x00000004):
        return "break"
    if char is None or (not char.isprintable() and char != '\r'):
        error(320)
        return "break"
    if not (char.isalnum() or char in ['_', '-'] or char == '\r'):
        error(320)
        return "break"

    # Cuando Run encuentra TRAP x23 seguido de TRAP x23, la entrada no se
    # refleja en el primer trap. El segundo trap muestra el caracter una sola
    # vez, evitando el eco duplicado que se producia en la ejecucion continua.
    pc_despues_de_entrada = ctypes.c_int.in_dll(lib, "pc").value
    palabra_siguiente = lib.leer_memoria(pc_despues_de_entrada)
    diferir_reflejo = debe_diferir_reflejo_trap(runer == 1, palabra_siguiente)

    if ab == 0:
        if not diferir_reflejo:
            display_char = ' ' if char == '\r' else char
            consola.print(display_char)
        ab = 1

    tib = 0
    lib.bandera_check()
    lib.modificar_acumulador(ctypes.c_int(ord(char)))
    
    consola.consola.config(state=tk.DISABLED)
    consola.consola.unbind("<Key>")
    
    
    c_origen = ctypes.c_int.in_dll(lib, "origen")
    acumulador, pc, status = leer_estado_nucleo()
    reflejar_st_pendiente_tras_entrada(pc, acumulador)
    acum_signed = convertir_a_entero_con_signo(acumulador)
    
    try:
        data_view.actualizar(acum_signed, status, format(pc, '04x'))
        memoria.mapear_memoria(diccionario, c_origen.value, pc)
    except Exception as ex:
        log(f"Error al actualizar la vista tras la entrada: {ex}")
    
    try:
        if runer == 1:
            runer = 0
            run()
    except Exception as ex:
        log(f"Error al reanudar Run tras la entrada: {ex}")
    
    return "break"
    
# ---------------------------------------------------------------------------
# Ensamblado y ejecucion
# ---------------------------------------------------------------------------


def assembly() -> None:
    """
    Guarda y preprocesa el codigo del editor, solicita al nucleo su ensamblado
    y construye el diccionario que alimenta la vista de memoria.

    Todas las conversiones entre texto assembler y palabras de 16 bits se
    realizan mediante traducir_instruccion().

    Parametros:
        No recibe parametros.
    """
    try:
        os.remove("input.tmp")
        os.remove(temp_file_path)
        log("Archivo temporal borrado")
    except Exception as ex:
        log(f"No se pudieron eliminar temporales anteriores: {ex}")

    try:
        if editor.code_title.cget("text") == "untitled.txt":
            guardar_como()
        if editor.code_title.cget("text") == "untitled.txt":
            error(100)
            return
        reset()
        global lang
        guardar_archivo()
        log(f"{ruta_archivo}")
    except Exception as ex:
        log(f"Error al preparar el archivo para ensamblar: {ex}")
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, "input.tmp")
        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            pass
        log(f"TEMP DIR: {temp_dir}\n TEMP PATH: {temp_file_path}")
    except Exception as ex:
        log(f"Error al crear el archivo temporal de entrada: {ex}")
    
    e = preprocesado(ruta_archivo, temp_file_path)
    direccion_traduccion = DIRECCION_CARGA_BINARIA
    lineas_traducidas = []
    try:
        if e == 0:
            with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
                etiqueta_faltante = encontrar_etiqueta_no_definida(temp_file)
            if etiqueta_faltante is not None:
                e = 314
                log(f"Etiqueta no definida: {etiqueta_faltante}")
        elif e < 0:
            with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
                if e == -2:
                    for linea in temp_file:
                        lineas_traducidas.append(
                            traducir_instruccion(
                                int(linea, 2),
                                direccion_traduccion,
                                MODO_DESENSAMBLAR,
                            )
                        )
                        direccion_traduccion += 1
                elif e == -16:
                    for linea in temp_file:
                        lineabin = format(int(linea, 16), '016b')
                        log(f"{lineabin}")
                        lineas_traducidas.append(
                            traducir_instruccion(
                                int(lineabin, 2),
                                direccion_traduccion,
                                MODO_DESENSAMBLAR,
                            )
                        )
                        direccion_traduccion += 1
                lineas_traducidas.append(".END")
                
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                for linea in lineas_traducidas:
                    log(f"{linea}")
                    temp_file.write(f"{linea}\n")
        
        temp_line_dir = tempfile.gettempdir()
        temp_line_path = os.path.join(temp_line_dir, "line.tmp")

        c_line_path = ctypes.c_char_p(temp_line_path.encode('utf-8'))
        c_temp_file_path = ctypes.c_char_p(temp_file_path.encode('utf-8'))

        log("Se creo y se paso al yacc el archivo temporal")
    except Exception as ex:
        log(f"Error al preparar la llamada al nucleo: {ex}")

    if e == 0 and not lineas_traducidas:
        log("Codigo en assembly")
        e = lib.assemble(10,c_temp_file_path,c_line_path)
    elif e in (-2, -16) and lineas_traducidas:
        log("Codigo en hexa/binario")
        e = lib.assemble(1,c_temp_file_path,c_line_path)
    log(f"Codigo error del yacc {e}")

    if e != 0:
        error(e)
        log(f"Error en el assembly {e}")
        return
    
    log("ESTE ES EL ARCHIVO TEMPORAL")
    with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
        contenido = temp_file.read()
        log(contenido)

    # Construye el diccionario utilizado por la representacion de memoria.
    global diccionario, pc, s
    diccionario = {}
    c_origen = (ctypes.c_int).in_dll(lib, "origen")
    pc = c_origen.value
    
    if c_origen.value >= TAMANO_MEMORIA or pc < 0:
        error(211)
        log(f"Error en el origen assembly {e}")
    if e<0:
        pc = DIRECCION_CARGA_BINARIA
    memoria.ensamblado = True
    log(f"Origen: {c_origen}\n PC {pc}")
    try:
        while(True):
            s = 1
            linea = lib.get_line(pc).decode('utf-8')
            if (linea != ".END\n"):
                if lib.get_etiq(pc) != None:
                    etiqueta = lib.get_etiq(pc).decode('utf-8')
                    linea = quitar_etiqueta_de_linea(linea, etiqueta)
                    if etiqueta.startswith(PREFIJO_FILL_INTERNO):
                        etiqueta = None
                else:
                    etiqueta = None

                # Toda conversion assembler -> palabra pasa por el traductor
                # unico. Ya no existe logica de traduccion dentro de assembly().
                log(f"ESTA LINEA LLEGO: {linea} desde el PC {pc}")
                binario = traducir_instruccion(linea, pc, MODO_ENSAMBLAR)
                if isinstance(binario, int):
                    e = binario
                    log(f"Error de traduccion {e} para la linea: {linea}")
                    break

                log(
                    "Este es el binario que estoy intentando traducir: "
                    f"{binario}"
                )
                decimal = int(binario, 2)
                
                try:
                    hexa = format(decimal,f'04x').upper()
                    dupla = (etiqueta,linea,binario,hexa)
                    diccionario[hex(pc)] = dupla
                    valor_numerico_ins = int(binario,2)
                    log(f"Celda traducida: {dupla} | Palabra: {valor_numerico_ins}")
                    lib.modificar_matriz_dato(valor_numerico_ins,pc)

                    pc = (pc + 1) & MASCARA_PALABRA

                    if e!=0 and e!=1:
                        break
                except Exception as ex:
                    log(f"Error al registrar una celda traducida: {ex}")
            else:
                break
        
        memoria.mapear_memoria(diccionario,c_origen.value,c_origen.value)
        memoria.diccionario_memoria = diccionario
    except Exception as ex:
        log(f"Error al construir el diccionario de memoria: {ex}")
    
    if(e==0):
        if s!=4:
            if(lang=="es"):
                consola.print("¡Código ensamblado exitosamente!")
            elif(lang=="en"):
                consola.print("¡Assembly successful!")
        global ab
        ab = 1
        memoria.ab_memoria = 1
        c_acumulador = ctypes.c_int.in_dll(lib, "acumulador").value
        acum_signed = convertir_a_entero_con_signo(c_acumulador)
        c_status = (ctypes.c_char_p).in_dll(lib, "ALUFlags")
        c_status = c_status.value
        c_pc = (ctypes.c_int).in_dll(lib, "pc")
        c_pc = c_pc.value
        data_view.actualizar(acum_signed,c_status,format(c_pc,'04x'))
        log(f"PC: {c_pc}    Acumulador: {c_acumulador}    ALUFlags: {c_status}")
    else:
        error(e)
        log(f"Error en el assembly {e}")
def stepin() -> None:
    """
    Ejecuta una instruccion en el nucleo, procesa los TRAP, refleja escrituras
    de memoria y actualiza acumulador, flags, PC y breakpoints en la interfaz.

    Parametros:
        No recibe parametros.
    """
    global lang,ab,tib,contador_branch, runer2
    branch_excedido = next(
        (
            direccion
            for direccion, cantidad in contador_branch.items()
            if cantidad > MAX_ITERACIONES_BRANCH
        ),
        None,
    )
    if branch_excedido is not None:
        runer2 = False
        consola.print(
            "SE DETECTO UN POSIBLE BUCLE INFINITO EN LA DIRECCION "
            f"{hex(branch_excedido)}, DETENIENDO EJECUCION"
        )
        contador_branch.clear()
    try:
        if(ab==1):
            global s
            temp_line_dir = tempfile.gettempdir()
            temp_line_path = os.path.join(temp_line_dir, "line.tmp")
            c_line_path = ctypes.c_char_p(temp_line_path.encode('utf-8'))
            log("Archivo temporal en YACC check")
            s = lib.stepin(1,c_line_path)
            log(f"Error:{s}")
            if(s==0):
                c_tib = (ctypes.c_int).in_dll(lib, "banderaParaTrapDeEntrada")
                c_tob = (ctypes.c_int).in_dll(lib, "banderaParaTrapDeSalida")
                global tib, tob
                tib = c_tib.value
                tob = c_tob.value
                acumulador, pc, status = leer_estado_nucleo()
                log(f"PC ACTUAL: {pc}   |   ACUMULADOR: {acumulador}    |   STATUS:{status}")
                log(f"TIB:   {c_tib}   {tib}")

                # El nucleo informa directamente si ST escribio memoria. La
                # sincronizacion completa queda encapsulada en una funcion.
                try:
                    reflejar_ultima_escritura_st()
                except Exception as ex:
                    log(f"Error al reflejar una escritura ST: {ex}")
                registrar_ejecucion_branch(pc)
                if(tib==1):
                    consola_capture()
                elif(tob==1):
                    if (lang=="es"):
                        consola.print(f"{chr(acumulador)}",tob)
                        log(f"Carácter de salida --> {chr(acumulador)}")
                    elif (lang=="en"):
                        consola.print(f"{chr(acumulador)}",tob)
                        log(f"Carácter de salida --> {chr(acumulador)}")
                    consola.tib = 0
                    tib = 0
                    lib.bandera_check()
                    c_origen = (ctypes.c_int).in_dll(lib, "origen")
                    memoria.mapear_memoria(diccionario,c_origen.value,pc)
                else:
                    c_origen = (ctypes.c_int).in_dll(lib, "origen")
                    acum_signed = convertir_a_entero_con_signo(acumulador)
                    data_view.actualizar(acum_signed,status,format(pc,'04x'))
                    if pc in memoria.breakpoints:
                        runer2 = False
                        log(f"BREAKPOINT {runer2}")
                    memoria.mapear_memoria(diccionario,c_origen.value,pc)
            else:
                error(s)
                log(f"Error en el stepin {s}")
        else:
            if(tib!=1):
                error(220)
                log(f"Error en el stepin {s}")
    except Exception as ex:
        log(f"Error durante Step In: {ex}")
def run() -> None:
    """
    Ejecuta instrucciones de forma continua hasta finalizar, encontrar un
    breakpoint, solicitar una entrada o detectar un posible bucle infinito.

    Parametros:
        No recibe parametros.
    """
    global lang,s,ab,tib,runer2
    runer2 = True
    try:
        if(ab==1):
            stepin()
            error(s)
            log(f"Error en el run {s}")
            while(s==0 and tib!=1 and runer2):
                stepin()
            if(tib==1):
                global runer
                runer = 1
            if (s==0 and tib==0 and runer2):
                run()
        else:
            if(tib!=1):
                error(220)
    except Exception as ex:
        log(f"Error durante Run: {ex}")
def reset() -> None:
    """
    Restablece el nucleo, limpia las vistas y reinicia las banderas de control
    utilizadas por el ensamblado y la ejecucion.

    Parametros:
        No recibe parametros.
    """
    lib.reset()
    data_view.limpiar()
    memoria.limpiar()
    consola.limpiar
    global tib, tob, ab, beb, cll, c, tpc, end
    end = False
    tib = 0
    tob = 0
    ab = 0
    beb = 0
    cll = 0
    c = 0
    tpc = 0

# ---------------------------------------------------------------------------
# Temas, idioma y ventanas auxiliares
# ---------------------------------------------------------------------------

themes = {
    "light": {
    "bg": "#FAFAFA",                # Fondo de la ventana (más cálido y menos brillante)
    "fg": "#1E1E1E",                # Texto principal (negro suave para mejor lectura)
    "button_bg": "#E4E4E4",         # Fondo de los botones (gris claro con más contraste)
    "button_fg": "#1E1E1E",         # Texto de los botones
    "button_active_bg": "#CCCCCC",  # Fondo de botones al hacer clic (más oscuro para feedback visual)
    "entry_bg": "#FFFFFF",          # Fondo de las entradas de texto (blanco puro para claridad)
    "entry_fg": "#1E1E1E",          # Texto de las entradas de texto
    "scroll_bg": "#E4E4E4",         # Fondo de las barras de desplazamiento (gris claro)
    "scroll_fg": "#B0B0B0",         # Color del control de la barra de desplazamiento (gris medio)
    "scroll_active": "#909090",     # Color del control de la barra de desplazamiento al hacer clic
    "menu_bg": "#F5F5F5",           # Fondo de la barra de menú (gris suave)
    "menu_fg": "#1E1E1E",           # Texto del menú
    "menu_active_bg": "#D6D6D6",    # Fondo del menú al pasar el cursor (un poco más oscuro)
    "menu_active_fg": "#000000"     # Texto del menú al pasar el cursor (negro puro para contraste)
    },
    "dark": {
    "bg": "#1C1C1C",                # Fondo de la ventana (negro suave para menor fatiga visual)
    "fg": "#EAEAEA",                # Texto principal (gris claro para evitar contraste extremo)
    "button_bg": "#323232",         # Fondo de los botones (gris oscuro pero diferenciado del fondo)
    "button_fg": "#EAEAEA",         # Texto de los botones
    "button_active_bg": "#505050",  # Fondo de botones al hacer clic (gris más claro)
    "entry_bg": "#2A2A2A",          # Fondo de las entradas de texto (oscuro pero no negro absoluto)
    "entry_fg": "#EAEAEA",          # Texto de las entradas de texto
    "scroll_bg": "#323232",         # Fondo de las barras de desplazamiento (gris oscuro)
    "scroll_fg": "#606060",         # Color del control de la barra de desplazamiento
    "scroll_active": "#787878",     # Color del control de la barra de desplazamiento al hacer clic
    "menu_bg": "#252525",           # Fondo de la barra de menú (un poco más claro que el fondo principal)
    "menu_fg": "#EAEAEA",           # Texto del menú
    "menu_active_bg": "#3A3A3A",    # Fondo del menú al pasar el cursor (gris medio para resaltar)
    "menu_active_fg": "#FFFFFF"     # Texto del menú al pasar el cursor (blanco puro para resaltar)
    }
}
def toggle_mode() -> None:
    """
    Alterna entre los temas claro y oscuro, aplica el resultado y lo guarda.

    Parametros:
        No recibe parametros.
    """
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()
    guardar_config()
def apply_theme() -> None:
    """
    Aplica el tema grafico seleccionado a la ventana y a todos los componentes
    principales sin modificar su distribucion ni su comportamiento.

    Parametros:
        No recibe parametros.
    """
    try:
        menu.frame_close()
        theme = themes[current_theme]
        ventana.configure(bg=theme["bg"])
        menu.tema(theme)
        editor.tema(theme)
        consola.tema(theme)
        memoria.tema(theme)
        data_view.tema(theme)
        if current_theme == "dark":
            if lang == "es":
                mostrar_mensaje("Modo oscuro")
            else:
                mostrar_mensaje("Dark mode")
        else:
            if lang == "es":
                mostrar_mensaje("Modo claro")
            else:
                mostrar_mensaje("Light mode")
    except Exception as ex:
        log(f"Error al aplicar el tema: {ex}")

def español() -> None:
    """
    Selecciona el español como idioma activo y actualiza toda la interfaz.

    Parametros:
        No recibe parametros.
    """
    menu.frame_close()
    global lang
    lang = "es"
    log(f"Lenguaje: {lang}")
    cambiar_lenguaje(lang)
    mostrar_mensaje("Español")
def english() -> None:
    """
    Selecciona el ingles como idioma activo y actualiza toda la interfaz.

    Parametros:
        No recibe parametros.
    """
    menu.frame_close()
    global lang
    lang = "en"
    log(f"Lenguaje: {lang}")
    cambiar_lenguaje(lang)
    mostrar_mensaje("English")
def cambiar_lenguaje(lang: str) -> None:
    """
    Propaga el idioma seleccionado a todos los componentes de la interfaz.

    Parametros:
        lang (str): Codigo del idioma que se desea aplicar, "es" o "en".
    """
    guardar_config()
    menu.lenguaje(lang)
    memoria.lenguaje(lang)
    editor.lenguaje(lang)
    data_view.lenguaje(lang)
    consola.lenguaje(lang,errores_lang)
def about() -> None:
    """
    Abre la ventana de Informacion utilizando el idioma y el tema activos.

    Parametros:
        No recibe parametros.
    """
    try:
        about_window = Informacion(ventana,lang,current_theme)
        about_window.tema()
        about_window.limpiar()
        about_window.lenguaje()
    except Exception as ex:
        log(f"Error al abrir Informacion: {ex}")

def ayuda() -> None:
    """
    Abre la ventana de Ayuda utilizando el idioma y el tema activos.

    Parametros:
        No recibe parametros.
    """
    try:
        menu.frame_close()
        help_window = Ayuda(ventana, lang, current_theme)
        help_window.tema()
    except Exception as ex:
        log(f"Error al abrir la ayuda: {ex}")

def ajustar_zoom(valor: int | float) -> None:
    """
    Limita y aplica el nivel de zoom a los componentes que muestran contenido.

    Parametros:
        valor (int | float): Porcentaje solicitado, limitado entre 100 y 200.
    """
    if valor < 100:
        valor = 100
    if valor > 200:
        valor = 200
    global zoom_value
    zoom_value = int(valor)
    editor.ajustar_zoom(zoom_value)
    consola.ajustar_zoom(zoom_value)
    memoria.ajustar_zoom(zoom_value)
    data_view.ajustar_zoom(zoom_value)
    menu.zoom_slider.set(zoom_value)
    log(f"Zoom ajustado a: {zoom_value}%")

# ---------------------------------------------------------------------------
# Inicializacion de la aplicacion
# ---------------------------------------------------------------------------


def iniciar_aplicacion() -> None:
    """
    Carga el nucleo nativo, crea los componentes de la interfaz, conecta sus
    callbacks y pone en marcha el bucle principal de Tkinter.

    La configuracion geometrica y el orden de construccion son los mismos que
    utilizaba la version anterior, por lo que no se modifica el diseño grafico.

    Parametros:
        No recibe parametros.
    """
    global ventana, menu, editor, consola, memoria, data_view
    global zoom_value, primer_inicio

    check_permissions()
    print(platform.architecture())
    cargar_bibliotecas_c()

    ventana = tk.Tk()
    ventana.title(f"ESM Simulator {version}")
    ventana.geometry("800x600")
    ventana.minsize(1140, 680)
    ventana.resizable(True, True)
    ventana.grid_rowconfigure(1, weight=1)
    ventana.grid_columnconfigure(1, weight=1)

    zoom_value = 100
    menu = BarraMenu(
        ventana,
        lang,
        theme,
        zoom_value,
        nuevo_archivo,
        abrir_archivo,
        guardar_archivo,
        guardar_como,
        assembly,
        run,
        stepin,
        reset,
        toggle_mode,
        español,
        english,
        ayuda,
        about,
        guardar_archivo_binario,
        guardar_archivo_hexadecimal,
        ajustar_zoom,
    )
    editor = EditorTexto(
        ventana, guardar_archivo, escrivir_archivo, mostrar_mensaje
    )
    consola = Consola(ventana, lang)
    memoria = Memoria(ventana, diccionario, pc, ab, theme)
    data_view = Variables(ventana)

    ventana.bind(
        "<Control-plus>", lambda event: ajustar_zoom(zoom_value + 10)
    )
    ventana.bind(
        "<Control-minus>", lambda event: ajustar_zoom(zoom_value - 10)
    )
    ventana.bind("<Control-z>", editor.deshacer)
    ventana.bind("<Control-y>", editor.rehacer)
    if not primer_inicio:
        ventana.bind("<Control-s>", guardar_archivo())
    else:
        primer_inicio = False

    configs()
    cambiar_lenguaje(lang)
    apply_theme()
    ajustar_zoom(zoom_value)
    ventana.mainloop()


if __name__ == "__main__":
    iniciar_aplicacion()
