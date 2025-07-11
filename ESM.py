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

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import ctypes
import platform
import sys
import tempfile
import configparser
from GUI_barraMenu import BarraMenu
from GUI_entradaMemoria import  EditorTexto, Memoria
from GUI_salidaEstado import  Consola, Variables
from GUI_info import Informacion

version = 19.4

"""
Change log:
        Bugs:
    --ST de un TRAPx23 guarda el acumulador correcto, no un 0 como antes
        Features:
    --Hipervinculo en link de la pestaña de about ahora se abre al dar click en el
    --Gmails corregidos
    --Se agrego la variable version
    --Rediseño smooth de memoria
    --Se agrego la crecion de consola.log junto a todos los logs que necesarios del python
"""

primer_inicio = True
s = 0
ab = 0
tib = 0
end = False
ruta_archivo = None
diccionario = None
pc = None
runer2 = False
lang, current_theme, theme = None, None, None
contador_branch = {}

log_file = open("consola.log","w")
def log(msj):
    global log_file
    log_file.write(msj+"\n")

def check_permissions():
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
        
    except Exception as e:
        log(f"Error al verificar permisos (line 82): {e}")
def cargar_bibliotecas_c():
    global lib
    if os.name == "nt":  # Windows
        # Verificar si el intérprete es de 64 bits
        arch = platform.architecture()[0]
        try:
            os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
            lib = ctypes.CDLL("lib.dll") 
        except OSError as e:
            log(f"Error al cargar DLL en Windows: {e}")
    elif os.name == "posix":  # Linux/Mac
        try:
            os.environ["LD_LIBRARY_PATH"] = os.getcwd()
            lib = ctypes.CDLL(os.path.join(os.getcwd(), "lib.so"))
        except OSError as e:
            log(f"Error al cargar SO en Linux/Mac: {e}")
    else:
        log("Sistema operativo no identificado")

    if 'lib' in globals():
        log("Bibliotecas cargadas correctamente.")
    else:
        log("Error al cargar las bibliotecas.")

    lib.assemble.restype = ctypes.c_int
    lib.assemble.argtypes = [ctypes.c_int]
    lib.stepin.restype = ctypes.c_int
    lib.stepin.argtypes = [ctypes.c_int]
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
check_permissions()
print(platform.architecture())
cargar_bibliotecas_c()
config = configparser.ConfigParser()
def configs():
    try:
        config.read('config.ini')
        global lang, current_theme, theme
        lang = config.get('Settings', 'lang', fallback='es')
        current_theme = config.get('Settings', 'current_theme', fallback='dark')
        theme = themes[current_theme]
    except Exception as ex:
        log(f"Error (line 135): {ex}")
def guardar_config():
    try:
        config.set('Settings', 'lang', lang)
        config.set('Settings', 'current_theme', current_theme)
        with open('config.ini', 'w') as configfile: 
            config.write(configfile)
    except Exception as ex:
        log(f"Error (line 143): {ex}")

def es_linea_vacia(linea):
    return not linea.strip()
def eliminar_espacios(linea):
    return linea.strip()
def eliminar_comentarios(linea):
    comentario = linea.find("//")
    if comentario != -1:
        return linea[:comentario]
    return linea
def procesar_linea(linea, archivo_salida):
    linea = eliminar_comentarios(linea)
    segmentos = linea.split(';')
    for segmento in segmentos:
        segmento = eliminar_espacios(segmento)
        if not es_linea_vacia(segmento):
            archivo_salida.write(segmento + '\n')

def preprocesado(direccion_archivo, archivo_salida_path):
    Binario = True
    Hexa = True
    Normal = False
    historial = 0
    e=0
    log(f"ARCHIVO LLEGADO PREPROCESADO: {direccion_archivo}")
    try:
        with open(direccion_archivo, 'r', encoding='utf-8') as archivo_entrada:
            with open(archivo_salida_path, 'w', encoding='utf-8') as archivo_salida:
                for linea in archivo_entrada:

                    linea_a_analizar = linea.replace("\n","")
                    if len(linea_a_analizar)==16 and Binario == True:
                        try:
                            int(linea_a_analizar, 2)
                            Binario = True
                            Hexa = False
                            historial +=1
                        except ValueError:
                            log("FALLE EN BINARIO")
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
                            log("FALLE EN EL HEXA")
                            Hexa = False
                    else:
                        if len(linea_a_analizar)!=0:
                            Hexa=False
                    if Binario == False and Hexa == False and historial == 0:
                        Normal = True

                    log(f"LINEA: {linea.strip()}")
                    procesar_linea(linea, archivo_salida)
                    
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
        log(f"Error (line 216): {ex}")
with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    archivo_salida_path = temp_file.name
with open(archivo_salida_path, 'r', encoding='utf-8') as temp_file:
    contenido = temp_file.read()
    print(contenido)

def nuevo_archivo():
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
        log(f"Error (line 236): {ex}")
def abrir_archivo():
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
            log(f"Achivo abierto {ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
            log("Error", f"No se pudo abrir el archivo: {e}")
            error(100)
def escrivir_archivo():
    global ruta_archivo
    if ruta_archivo:
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as file:
                contenido = file.read()
                editor.code_editor.delete(1.0, tk.END)
                editor.code_editor.insert(tk.END, contenido)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
            log("Error", f"No se pudo escrivir el archivo: {e}")
            error(100)     
def guardar_archivo(event=None):
    try:
        menu.frame_close()
    except:
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
def guardar_como(event=None):
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
def guardar_archivo_binario():
    menu.frame_close()
    if(memoria.ensamblado):
        ruta=ruta_archivo
        name=os.path.splitext(ruta)[0] + ".bin"
        # f = open(name, "w")
        # dicccinario[pc]=(etiqueta,linea,binario,hexa)
        try:
            with open(name, "w") as archivo:
                for valor in diccionario.values():
                    if len(valor) > 2 and valor[2]:
                        archivo.write(valor[2] + "\n") 
                mostrar_mensaje(f"Archivo guardado '{os.path.basename(name)}'")
                log(f"Archivo guardado {archivo}")
        except Exception as ex:
            mostrar_mensaje(f"No se pudo guardar el archivo: {ex}")
            log(f"No se pudo guardar el archivo binario: {ex}")
    else:
        error(220)
        log(f"Error en el guardar_archivo_binario {220}")

    
    #nombre del archivo os.path.basename(archivo)
def guardar_archivo_hexadecimal():
    menu.frame_close()
    if(memoria.ensamblado):
        ruta=ruta_archivo
        name=os.path.splitext(ruta)[0] + ".hex"
        try:
            with open(name, "w") as archivo:
                for valor in diccionario.values():
                    if len(valor) > 3 and valor[3]:
                        archivo.write(valor[3] + "\n")
                mostrar_mensaje(f"Archivo guardado '{os.path.basename(name)}'")
                log(f"Archivo guardado {archivo}")
        except Exception as ex:
            mostrar_mensaje(f"No se pudo guardar el archivo: {ex}")
            log(f"No se pudo guardar el archivo hexadecimal: {ex}")
    else:
        error(220)
        log(f"Error en el guardar_archivo_hexadecimal {220}")

def mostrar_mensaje(mensaje, duracion=1000):
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

def offset_numericos(offset12,binary):
    if offset12>=0:
        num_bin = format(offset12, f'0{12}b')
    else:
        num_bin = format((1 << 12) + offset12, f'0{12}b')
    binario = binary+num_bin
    return binario
def offset_direccion(dir_objetivo,binary,pc):
    log(f"PC actual {pc}")
    flag = False
    if(dir_objetivo - (pc+1) > 2047 or dir_objetivo - (pc+1) < -2048):
        if(65536-(dir_objetivo-(pc+1)) > 2048 and (dir_objetivo-(pc+1))+65536 > 2047):
            s=319
            return s
    if(65536-(dir_objetivo-(pc+1))<=2048):
        offset12 = -(65536-(dir_objetivo-(pc+1)))
        num_bin = format((1 << 12)+offset12,f'0{12}b')
        flag=True
    elif((dir_objetivo-(pc+1))+65536 <= 2047):
        offset12 = (dir_objetivo-(pc+1))+65536
        num_bin = format(offset12, f'0{12}b')
        flag=True
    if(not flag):
        offset12 = dir_objetivo - (pc +1)
        if offset12>=0:
            num_bin = format(offset12, f'0{12}b')
        else:
            num_bin = format((1 << 12) + offset12, f'0{12}b')

    binario = binary+num_bin
    return binario

def traductor_para_st(decimal,direccion_towrite):
    if decimal >= 0:
        binario = format(decimal,f'0{16}b')
    else:
        binario = format((1 << 16) + decimal, f'0{16}b')

    match binario[0:4]:
        case "0101": #NOTB
            return "NOTB"
        case "0100": #NOTA
            if binario[4] == "0":
                PCoffset = int(binario[5:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR NOTA #5
                if(offset>65536):
                    offset = offset - 65536
                return f"NOTA x{format(offset,f'04x')}"
            if binario[4] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                if(offset<0):
                    offset = 65536 + offset 
                return f"NOTA x{format(offset,f'04x')}"

        case "0001": #ADD imm12
            if binario[4] == "0":
                imm12 = int(binario[5:],2)
                return f"ADD #{imm12}"
            else:
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                imm12 = decimal_invertido + 1
                return f"ADD #{-imm12}"

        case "0000": #ADD PCoffset12
            if binario[4] == "0":
                PCoffset = int(binario[5:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR
                if(offset>65536):
                    print("MAYOR")
                    offset = offset - 65536
                return f"ADD x{format(offset,f'04x')}"
            if binario[4] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                if(offset<0):
                    offset = 65536 + offset 
                return f"ADD x{format(offset,f'04x')}"
        
        case "0010": #AND PCoffse12:
            if binario[4] == "0":
                PCoffset = int(binario[5:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR
                if(offset>65536):
                    offset = offset - 65536
                return f"AND x{format(offset,f'04x')}"
            if binario[4] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                if(offset<0):
                    offset = 65536 + offset 
                return f"AND x{format(offset,f'04x')}"

        case "0011": #AND imm12
            if binario[4] == "0":
                imm12 = int(binario[5:],2)
                return f"AND #{imm12}"
            else:
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                imm12 = decimal_invertido + 1
                return f"AND #{-imm12}"

        case "0110": #LD PCoffset12
            if binario[4] == "0":
                PCoffset = int(binario[5:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR
                if(offset>65536):
                    offset = offset - 65536
                return f"LD x{format(offset,f'04x')}"
            if binario[4] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                if(offset<0):
                    offset = 65536 + offset 
                return f"LD x{format(offset,f'04x')}"

        case "0111": #ST PCoffset12
            if binario[4] == "0":
                PCoffset = int(binario[5:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR
                if(offset>65536):
                    offset = offset - 65536
                return f"ST x{format(offset,f'04x')}"
            if binario[4] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[5:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                if(offset<0):
                    offset = 65536 + offset 
                return f"ST x{format(offset,f'04x')}"

        case "1000": #BR con N=0
            n = ""
            if binario[4] == "1":
                z = "z"
            else:
                z = ""
            if binario[5] == "1":
                p = "p"
            else:
                p = ""
            if binario[6] == "0":
                PCoffset = int(binario[7:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR
                if(offset>65536):
                    offset = offset - 65536
                return f"BR {n}{z}{p} x{format(offset,f'04x')}"
            if binario[6] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[7:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                if(offset<0):
                    offset = 65536 + offset 
                return f"BR {n}{z}{p} x{format(offset,f'04x')}"

        case "1001": #BR con N=1
            n = "n"
            if binario[4] == "1":
                z = "z"
            else:
                z = ""
            if binario[5] == "1":
                p = "p"
            else:
                p = ""
            if binario[6] == "0":
                PCoffset = int(binario[7:],2)
                offset=direccion_towrite + (PCoffset+1) ###CHEKEAR CON EL INVERSOR
                return f"BR {n}{z}{p} x{format(offset,f'04x')}"
            if binario[6] == "1":
                invertido = ''.join('1' if bit == '0' else '0' for bit in binario[7:])
                decimal_invertido = int(invertido, 2)
                PCoffset = decimal_invertido + 1
                offset = (direccion_towrite + 1) - (PCoffset) ###CHEKEAR CON EL INVERSOR
                return f"BR {n}{z}{p} x{format(offset,f'04x')}"
    return None

errores_lang = {
    "es": {
        100: "Error 100: No se pudo abrir el archivo",
        200: "Error 200: La cantidad de instrucciones usando el orig dado sobrepaso la capacidad de la memoria",
        210: "Error 210: El PC intento acceder a una posición fuera del rango de la memoria",
        211: "Error 211: La posicion de memoria salio fuera del rango de la memoria",
        212: "Error 212: El número ingresado está fuera del rango permitido.",
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
        310: "Error 310: Se esperaba una direccion X21 o X23",
        311: "Error 311: Se esperaba un valor hexadecimal valido",
        312: "Error 312: Los valores numericos deben empezar con '#'",
        313: "Error 313: Los valores numéricos deben estar en el rango permitido de -2048 a 2047.",
        314: "Error 314: No hay etiquetas que coincidan",
        315: "Error 315: Caracter invalido",
        316: "Error 316: No se encontro el final del codigo (.END)",
        317: "Error 317: No se encontro la direccion inicial de memoria (.ORIG)",
        318: "Error 318: La instrucción BR esperaba un offset de hasta 9bits (-511 a 512)",
        319: "Error 319: La instrucción esperaba un offset de hasta 12bits (-2048 a 2047)",
        320: "Error 320: Caracter invalido"
    },
    "en": {
        100: "Error 100: Could not open the file",
        200: "Error 200: The number of instructions using the given .ORIG exceeded memory capacity",
        210: "Error 210: The PC attempted to access a position outside the memory range",
        211: "Error 211: The memory position went out of the memory range",
        212: "Error 212: The number entered is out of the allowed range.",
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
        310: "Error 310: An X21 or X23 address was expected",
        311: "Error 311: A valid hexadecimal value was expected",
        312: "Error 312: Numeric values must start with '#'",
        313: "Error 313: Numeric values must be in the allowed range of -2048 to 2047.",
        314: "Error 314: No matching labels found",
        315: "Error 315: Invalid character",
        316: "Error 316: The end of the code (.END) was not found",
        317: "Error 317: The initial memory address (.ORIG) was not found",
        318: "Error 318: The BR instruction expected an offset of up to 9 bits (-512 to 511)",
        319: "Error 319: The instruction expected an offset of up to 12 bits (-2048 to 2047)",
        320: "Error 320: Invalid character"
    }
}
def error(e):
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
                    consola.print(f"PC (x{format(pc,f'04x')}) => {errores[e]}") #este es coso1
                else:
                    consola.print(f"PC (x{format(pc,f'04x')}) => {errores[e]}")
                    s=4
            else:
                consola.print(errores[e])
        if e != 1:
            reset()
        else:
            end = True

def consola_capture():
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
def capture_char(event):
    global tib, ab
    
    while tib == 1:
        teclas_especiales = {"Return", "KP_Enter"}  
        char = event.char
        
        
        if event.keysym in teclas_especiales:
            char = '\r'  
        
    
        teclas_ignorar = {
            "Shift_L", "Shift_R", "Control_L", "Control_R", 
            "Alt_L", "Alt_R", "Caps_Lock", "Meta", "ISO_Level3_Shift"
        }
        
       
        if event.keysym in teclas_ignorar or (event.state & 0x00000004):  
            return
        
        if char is None or (not char.isprintable() and char != '\r'):
            error(320)
            return
        
        if not (char.isalnum() or char in ['_', '-'] or char == '\r'):  
            error(320)
            return
        
      
        if char.isprintable() or char == '\r':
            if ab == 0:
                consola.consola.delete("insert -1 chars", "insert")  # Elimina carácter anterior
                display_char = ' ' if char == '\r' else char
                consola.print(display_char) 
                ab = 1
            
            tib = 0
            lib.bandera_check()
            c_int_value = ctypes.c_int(ord(char))
            lib.modificar_acumulador(c_int_value)
            break
    
    consola.consola.config(state=tk.DISABLED)
    consola.consola.unbind("<Key>")
    
    
    c_origen = (ctypes.c_int).in_dll(lib, "origen")
    c_pc = (ctypes.c_int).in_dll(lib, "pc")
    pc = c_pc.value
    c_acumulador = (ctypes.c_int).in_dll(lib, "acumulador")
    acumulador = c_acumulador.value
    c_status = (ctypes.c_char_p).in_dll(lib, "ALUFlags")
    status = c_status.value.decode("utf-8")
    
    try:
        if diccionario[hex(pc)][1].split(" ")[0].replace("\n", "") == "ST":
            imm12 = diccionario[hex(pc)][1].split(" ")[1].replace("\n", "")
            if imm12[0] == "#":  # CASO DE NÚMERO DIRECTO
                borrar = int(imm12[1:]) + 1
            elif imm12[0] == 'x':  # CASO DE DIRECCIÓN DE MEMORIA
                dir_objetivo_borrar = int(imm12[1:], 16)
                borrar = dir_objetivo_borrar - pc
            else:  # CASO DE ETIQUETA
                etiqueta_siono = True
                imm12 = imm12.replace("\n", "")
                c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                borrar = dir_etiq_int - pc
                remplazar_etiqueta = diccionario[hex(pc + borrar)][0]
            
            acum_hexa = format(ord(char), '04x').upper()
            acum_bin = format(ord(char), '0{16}b')
            if pc + borrar < 0:
                dir = 65536 + (pc + borrar)
                log(f"RULETA {dir}")
            else:
                dir = pc + borrar
                log(f"NO RULETA {dir}")
            
            instrucsão = traductor_para_st(acumulador, pc + borrar)
            if instrucsão is not None:
                instrucsão += "\0"
                c_string_st = ctypes.c_char_p(instrucsão.encode('utf-8'))
                lib.reemplazar_linea_st(c_string_st, dir)
            else:
                instrucsão = f"#{acumulador}"
                c_string_st = ctypes.c_char_p(instrucsão.encode('utf-8'))
                lib.reemplazar_linea_st(c_string_st, dir)
            
            if etiqueta_siono:
                tupla_remplazo = (remplazar_etiqueta, f"{instrucsão}", f"{acum_bin}", f"{acum_hexa}")
            else:
                tupla_remplazo = (None, f"{instrucsão}", f"{acum_bin}", f"{acum_hexa}")
            diccionario[hex(dir)] = tupla_remplazo
            log(f"LO QUE GUARDE {diccionario[hex(dir)]}")
    except Exception as ex:
        log(f"Error (line 715): {ex}")
    
    try:
        data_view.actualizar(acumulador, status, format(pc, '04x'))
        memoria.mapear_memoria(diccionario, c_origen.value, pc)
    except Exception as ex:
        log(f"Error (line 720): {ex}")
    
    try:
        global runer
        if runer == 1:
            runer = 0
            run()
    except Exception as ex:
        log(f"Error (line 727): {ex}")
    
    tib = 1
    
def assembly():
    try:
        os.remove("input.tmp")
        os.remove(temp_file_path)
        log("Archivo temporal borrado")
    except Exception as ex:
        log(f"Error (line 735): {ex}")

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
        log(f"Error (line 748): {ex}")
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, "input.tmp")
        with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
            pass
        log(f"TEMP DIR: {temp_dir}\n TEMP PATH: {temp_file_path}")
    except Exception as ex:
        log(f"Error (line 757): {ex}")
    
    e = preprocesado(ruta_archivo,temp_file_path)
    dir = 12288
    lista=[]
    try:
        if e >= 0:
            error(e)
            log(f"Error en el assembly {e}")
        else:
            with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
                if e == -2:
                    for linea in temp_file:
                        lista.append(traductor_para_st(int(linea,2),dir))
                        dir+=1
                elif e == -16:
                    for linea in temp_file:
                        lineabin = format(int(linea, 16), '016b')
                        log(f"{lineabin}")
                        lista.append(traductor_para_st(int(lineabin,2),dir))
                        dir+=1
                lista.append(".END")
                
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                for linea in lista:
                    log(f"{linea}")
                    temp_file.write(f"{linea}\n")
        
        temp_line_dir = tempfile.gettempdir()
        temp_line_path = os.path.join(temp_line_dir, "line.tmp")

        c_line_path = ctypes.c_char_p(temp_line_path.encode('utf-8'))
        c_temp_file_path = ctypes.c_char_p(temp_file_path.encode('utf-8'))

        log("Se creo y se paso al yacc el archivo temporal")
    except Exception as ex:
        log(f"Error (line 793): {ex}")

    if len(lista)==0:
        log("Codigo en assembly")
        e = lib.assemble(10,c_temp_file_path,c_line_path)
    else:
        log("Codigo en hexa/binario")
        e = lib.assemble(1,c_temp_file_path,c_line_path)
    log(f"Codigo error del yacc {e}")
    
    log("ESTE ES EL ARCHIVO TEMPORAL")
    with open(temp_file_path, 'r', encoding='utf-8') as temp_file:
        contenido = temp_file.read()
        log(contenido)

    ##DICCIONARIO
    global diccionario, pc, s #Report 15
    diccionario = {}
    c_origen = (ctypes.c_int).in_dll(lib, "origen")
    pc = c_origen.value
    
    if(c_origen.value>65535 or pc<0):
        error(211)
        log(f"Error en el origen assembly {e}")
    if e<0:
        pc = 12288
    memoria.ensamblado = True
    log(f"Origen: {c_origen}\n PC {pc}")
    try:
        while(True):
            s = 1
            linea = lib.get_line(pc).decode('utf-8')
            if (linea != ".END\n"):
                if lib.get_etiq(pc) != None:
                    etiqueta = lib.get_etiq(pc).decode('utf-8')
                    linea = linea.replace(etiqueta,"")
                    linea = linea.replace(" ","",1)
                else:
                    etiqueta = None

                ###TRADUCTOR BRIANESCO
                log(f"ESTA LINEA LLEGO: {linea} desde el PC {pc}")
                flag_br_dict = 0
                instruc = linea.split(" ")[0]
                instruc = instruc.replace("\n","")
                if instruc.startswith("BR") and instruc != "BR":
                    flag_br_dict = 1
                    flags = instruc.split("BR")[1]
                    instruc = "BR"
                match instruc:
                    case "ADD":
                        imm12 = linea.split(" ")[1]

                        if imm12[0] == "#": ##CASO DE NUMERO DIRECTO
                            binario = "0001"
                            binario = offset_numericos(int(imm12[1:]),binario)

                        elif imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA
                            binario = "0000"
                            dir_objetivo = int(imm12[1:],16)
                            binario = offset_direccion(dir_objetivo,binario,pc)

                            if(dir_objetivo- pc > 2047 or dir_objetivo - pc < -2048):
                                if(65536-(dir_objetivo-(pc+1)) > 2048 and (dir_objetivo-(pc+1))+65535 > 2047):
                                    e= 319
                            
                        else:   ##CASO DE ETIQUETA
                            binario = "0000"
                            imm12 = imm12.replace("\n","")                        
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            binario = offset_direccion(dir_etiq_int,binario,pc)
                    case "AND":
                        imm12 = linea.split(" ")[1]
                        if imm12[0] == "#": ##CASO DE NUMERO DIRECTO
                            binario = "0011"
                            binario = offset_numericos(int(imm12[1:]),binario)

                        elif imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA
                            binario = "0010"
                            dir_objetivo = int(imm12[1:],16)
                            binario = offset_direccion(dir_objetivo,binario,pc)

                            if(dir_objetivo- pc > 2047 or dir_objetivo - pc < -2048):
                                if(65536-(dir_objetivo-(pc+1)) > 2048 and (dir_objetivo-(pc+1))+65535 > 2047):
                                    e= 319
                            
                        else:   ##CASO DE ETIQUETA
                            binario = "0010"
                            imm12 = imm12.replace("\n","")                        
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            binario = offset_direccion(dir_etiq_int,binario,pc)
                    case "NOTA":
                        imm12 = linea.split(" ")[1]

                        if imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA
                            binario = "0100"
                            dir_objetivo = int(imm12[1:],16)
                            binario = offset_direccion(dir_objetivo,binario,pc)
                            
                            if(dir_objetivo- pc > 2047 or dir_objetivo - pc < -2048):
                                if(65536-(dir_objetivo-(pc+1)) > 2048 and (dir_objetivo-(pc+1))+65535 > 2047):
                                    e= 319
                            
                        else:   ##CASO DE ETIQUETA
                            binario = "0100"
                            imm12 = imm12.replace("\n","")                        
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            binario = offset_direccion(dir_etiq_int,binario,pc)
                    case "NOTB":
                        binario = "0101000000000000"
                        hexa = "5000"
                    case "LD":
                        imm12 = linea.split(" ")[1]

                        if imm12[0] == "#": ##CASO DE NUMERO DIRECTO
                            binario = "0110"
                            binario = offset_numericos(int(imm12[1:]),binario)

                        elif imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA
                            binario = "0110"
                            dir_objetivo = int(imm12[1:],16)
                            binario = offset_direccion(dir_objetivo,binario,pc)

                            if(dir_objetivo- pc > 2047 or dir_objetivo - pc < -2048):
                                if(65536-(dir_objetivo-(pc+1)) > 2048 and (dir_objetivo-(pc+1))+65535 > 2047):
                                    e= 319
    
                        else:   ##CASO DE ETIQUETA
                            binario = "0110"
                            imm12 = imm12.replace("\n","")                        
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            binario = offset_direccion(dir_etiq_int,binario,pc)
                    case "ST":
                        imm12 = linea.split(" ")[1]

                        if imm12[0] == "#": ##CASO DE NUMERO DIRECTO
                            binario = "0111"
                            binario = offset_numericos(int(imm12[1:]),binario)

                        elif imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA
                            binario = "0111"
                            dir_objetivo = int(imm12[1:],16)
                            binario = offset_direccion(dir_objetivo,binario,pc)

                            if(dir_objetivo- pc > 2047 or dir_objetivo - pc < -2048):
                                if(65536-(dir_objetivo-(pc+1)) > 2048 and (dir_objetivo-(pc+1))+65535 > 2047):
                                    e= 319
    
                        else:   ##CASO DE ETIQUETA
                            binario = "0111"
                            imm12 = imm12.replace("\n","")                        
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            if dir_etiq_int == -1:
                                error(314)
                            binario = offset_direccion(dir_etiq_int,binario,pc)
                        ##HAY QUE AÑADIR EL TEMA DE BORRAR INSTRUCCIONES EN EL DICCIO CUANDO ENTRE ST, NO ES ACA
                    case "BR":
                        
                        if flag_br_dict == 0:
                            imm12 = linea.split(" ")[2]
                            flags = linea.split(" ")[1]
                        else:
                            imm12 = linea.split(" ")[1]

                        binario = "100"
                        if "n" in flags:
                            binario = binario + "1"
                        else:
                            binario = binario + "0"
                        if "z" in flags:
                            binario = binario + "1"
                        else:
                            binario = binario + "0"
                        if "p" in flags:
                            binario = binario + "1"
                        else:
                            binario = binario + "0"
                        
                        if imm12[0] == '#': ##CASO DE NUMERO DIRECTO FUNCIONANDO!!!
                            offset9 = int(imm12[1:])

                            #SI EL OFFSET NUMERICO NO DA
                            if offset9>511 or offset9<-512:
                                e=318

                            else:
                                if offset9>=0:
                                    num_bin = format(offset9, f'0{10}b')
                                else:
                                    num_bin = format((1 << 10) + offset9, f'0{10}b')
                                binario = binario+num_bin

                        elif imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA FUNCIONANDO!!!
                            dir_salt = int(imm12[1:],16)

                            if(dir_salt - (pc+1) > 511 or dir_salt - (pc+1) < -512):
                                if(65536-(dir_salt-pc+1) > 512 and (dir_salt-pc+1)+65535 > 511):
                                    e= 318
                                else:
                                    if(65536-(dir_salt-pc+1)<=512):
                                        log(f"Direccion{dir_salt}|||pc{pc+1}")
                                        offset9 = -(65536-(dir_salt-(pc+1)))
                                        log(f"EL OFFSET9 es {offset9}")
                                        num_bin = format((1 << 10)+offset9,f'0{10}b')
                                        log(f"EL NUM_BIN es {num_bin}")
                                    elif((dir_salt-(pc+1))+65536 <= 511):
                                        log(f"Direccion{dir_salt}|||pc{pc+1}")
                                        offset9 = (dir_salt-(pc+1))+65536
                                        num_bin = format(offset9, f'0{10}b')
                                        log(f"EL NUM_BIN es {num_bin}")
                            else:               
                                offset9 = dir_salt - (pc+1)
                                if offset9>=0:
                                    num_bin = format(offset9, f'0{10}b')
                                else:
                                    num_bin = format((1 << 10) + offset9, f'0{10}b')

                            binario = binario+num_bin
                        
                        else:   ##CASO DE ETIQUETA FUNCIONANDO!!!
                            imm12 = imm12.replace("\n","")                        
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            ###ERROR QUE LA ETIQUETA ESTE MAS LEJOS QUE EL PCoffset9
                            if(dir_etiq_int - (pc+1) > 511 or dir_etiq_int - (pc+1) < -512):
                                if(65536-(dir_etiq_int-(pc+1)) > 512 and (dir_etiq_int-(pc+1))+65535 > 511):
                                    e= 318
                                else:
                                    if(65536-(dir_etiq_int-(pc+1))<=512):
                                        log(f"Direccion{dir_etiq_int}|||pc{pc+1}")
                                        offset9 = -(65536-(dir_etiq_int-(pc+1)))
                                        log(f"EL OFFSET9 es {offset9}")
                                        num_bin = format((1 << 10)+offset9,f'0{10}b')
                                        log(f"EL NUM_BIN es {num_bin}")
                                    elif((dir_etiq_int-(pc+1))+65536 <= 511):
                                        log(f"Direccion{dir_etiq_int}|||pc{pc+1}")
                                        offset9 = (dir_etiq_int-(pc+1))+65536
                                        num_bin = format(offset9, f'0{10}b')
                                        log(f"EL NUM_BIN es {num_bin}")
                            else:               
                                offset9 = dir_etiq_int - (pc+1)
                                if offset9>=0:
                                    num_bin = format(offset9, f'0{10}b')
                                else:
                                    num_bin = format((1 << 10) + offset9, f'0{10}b')            
                            
                            binario = binario+num_bin

                    case ".FILL":
                        imm12 = linea.split(" ")[1]
                        if imm12[0] == "#": ##CASO DE NUMERO DIRECTO
                            filling = imm12[1:].replace("\n","")
                            filling = int(filling)
                            if filling >= 0:
                                num_bin = format(filling, f'0{16}b')
                            else:
                                num_bin = format((1 << 16) + filling, f'0{16}b')
                            binario = num_bin
                            
                    case "TRAP":
                        imm12 = linea.split(" ")[1].replace("\n","")
                        binario = "111"
                        if imm12 == "x21":
                            binario = binario + "0000000100001"
                        elif imm12 == "x23":
                            binario = binario + "0000000100011"                 
                    case _:
                        binario = "0000000000000000"
                if(binario!=319):
                    try:
                        log(f"Este es el binario que estoy intentando traducir: {binario}")
                        decimal = int(binario, 2)
                    except:
                        dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)

                        if(dir_etiq_int==-1):
                            e=314
                            error(e)
                            log(f"Error en el assembly {e}")
                            break
                else:
                    break
                
                try:
                    hexa = format(decimal,f'04x').upper()
                    dupla = (etiqueta,linea,binario,hexa)
                    diccionario[hex(pc)] = dupla
                    valor_numerico_ins = int(binario,2)
                    log(f"Datos: {dupla} | Nose que era esto: {valor_numerico_ins}")
                    lib.modificar_matriz_dato(valor_numerico_ins,pc)

                    pc += 1
                    if (pc>65535):pc=0

                    if e!=0 and e!=1:
                        break
                except Exception as ex:
                    log(f"Error (line 1092): {ex}")
            else:
                break
        
        memoria.mapear_memoria(diccionario,c_origen.value,c_origen.value)
        memoria.diccionario_memoria = diccionario
    except Exception as ex:
        log(f"Error (line 1099): {ex}")
    
    if(e==0):
        if s!=4:
            if(lang=="es"):
                consola.print("¡Código ensamblado exitosamente!")
            elif(lang=="en"):
                consola.print("¡Assembly successful!")
        global ab
        ab = 1
        memoria.ab_memoria = 1
        c_acumulador = (ctypes.c_int).in_dll(lib, "acumulador")
        c_acumulador = c_acumulador.value
        c_status = (ctypes.c_char_p).in_dll(lib, "ALUFlags")
        c_status = c_status.value
        c_pc = (ctypes.c_int).in_dll(lib, "pc")
        c_pc = c_pc.value
        data_view.actualizar(c_acumulador,c_status,format(c_pc,'04x'))
        log(f"PC: {c_pc}    Acumulador: {c_acumulador}    ALUFlags: {c_status}")
    else:
        error(e)
        log(f"Error en el assembly {e}")
def stepin():
    global lang,ab,tib,contador_branch, runer2
    iteracionesMaximas = 200
    for branch_run in contador_branch:
        if contador_branch[branch_run] > iteracionesMaximas:
            runer2 = False
            consola.print(f"SE DETECTO UN POSIBLE BUCLE INFINITO EN LA DIRECCION {hex(branch_run)}, DETENIENDO EJECUCION")
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
                c_acumulador = (ctypes.c_int).in_dll(lib, "acumulador")
                acumulador = c_acumulador.value
                c_pc = (ctypes.c_int).in_dll(lib, "pc")
                pc = c_pc.value
                if (pc>65535):pc=0
                c_status = (ctypes.c_char_p).in_dll(lib, "ALUFlags")
                status = c_status.value.decode("utf-8")
                log(f"PC ACTUAL: {pc}   |   ACUMULADOR: {acumulador}    |   STATUS:{status}")
                log(f"TIB:   {c_tib}   {tib}")
                etiqueta_siono = False
                try:
                    if(diccionario[hex(pc)][1].split(" ")[0].replace("\n","")=="ST"):
                        imm12 = diccionario[hex(pc)][1].split(" ")[1].replace("\n","")
                        if imm12[0] == "#": ##CASO DE NUMERO DIRECTO
                            borrar = int(imm12[1:])+1
                        elif imm12[0] == 'x': ##CASO DE DIRECCION DE MEMORIA
                            dir_objetivo_borrar = int(imm12[1:],16)
                            borrar = dir_objetivo_borrar - (pc)
                        else:   ##CASO DE ETIQUETA
                            etiqueta_siono = True
                            imm12 = imm12.replace("\n","")                      
                            c_string = ctypes.c_char_p(imm12.encode('utf-8'))
                            dir_etiq_int = lib.buscarDireccionEtiqueta(c_string)
                            borrar = dir_etiq_int - (pc)
                            remplazar_etiqueta = diccionario[hex(pc+borrar)][0]
                        c_acumulador = (ctypes.c_int).in_dll(lib, "acumulador")
                        acumulador = c_acumulador.value
                        if acumulador >= 0:
                            acum_bin = format(acumulador,f'0{16}b')
                            acum_hexa = format(acumulador,f'04x').upper()
                        else:
                            acum_bin = format((1 << 16) + acumulador, f'0{16}b')
                            acum_hexa = format((1<<16) + acumulador,f'04x').upper()

                        if pc+borrar < 0:
                            dir = 65536 + (pc+borrar)
                            log(f"RULETA {dir}")
                        else:
                            dir = pc +borrar
                            log(f"NO RULETA {dir}")
                        instrucsão = traductor_para_st(acumulador,dir)
                        if instrucsão != None:
                            instrucsão = instrucsão + "\0"
                            c_string_st = ctypes.c_char_p(instrucsão.encode('utf-8'))
                            lib.reemplazar_linea_st(c_string_st,dir)
                        else:
                            instrucsão = f"#{acumulador}"
                            c_string_st = ctypes.c_char_p(instrucsão.encode('utf-8'))
                            lib.reemplazar_linea_st(c_string_st,dir)
                        if etiqueta_siono:
                            tupla_remplazo = (remplazar_etiqueta,f"{instrucsão}",f"{acum_bin}",f"{acum_hexa}")
                        else:
                            tupla_remplazo = (None,f"{instrucsão}",f"{acum_bin}",f"{acum_hexa}")
                        diccionario[hex(dir)] = tupla_remplazo
                        log(f"LO QUE GUARDE {diccionario[hex(dir)]}")
                except Exception as ex:
                    log(f"Error (SE QUISO DETECTAR UN ST): {ex}")
                try:
                    if(diccionario[hex(pc)][1].split(" ")[0].replace("\n","")=="BR"):     
                        if pc not in contador_branch:
                            contador_branch[pc] = 1           
                        else:
                            contador_branch[pc] += 1
                        
                except Exception as ex:
                    log(f"ERROR (SE QUISO DETECTAR UN BR): {ex}")
                if(tib==1):
                    consola_capture()
                    c_status = (ctypes.c_char_p).in_dll(lib, "ALUFlags")
                elif(tob==1):
                    if (lang=="es"):
                        c_acumulador = (ctypes.c_int).in_dll(lib, "acumulador")
                        acumulador = c_acumulador.value
                        consola.print(f"{chr(acumulador)}",tob)
                        log(f"Carácter de salida --> {chr(acumulador)}")
                    elif (lang=="en"):
                        c_acumulador = (ctypes.c_int).in_dll(lib, "acumulador")
                        acumulador = c_acumulador.value
                        consola.print(f"{chr(acumulador)}",tob)
                        log(f"Carácter de salida --> {chr(acumulador)}")
                    consola.tib = 0
                    tib = 0
                    lib.bandera_check()
                    c_origen = (ctypes.c_int).in_dll(lib, "origen")
                    memoria.mapear_memoria(diccionario,c_origen.value,pc)
                else:
                    c_origen = (ctypes.c_int).in_dll(lib, "origen")
                    data_view.actualizar(acumulador,status,format(pc,'04x'))
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
        log(f"Error (line 1224): {ex}")
def run():
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
        log(f"Error (line 1244): {ex}")
def reset():
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
def toggle_mode():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()
    guardar_config()
def apply_theme():
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
        log(f"Error (line 1320): {ex}")

def español():
    menu.frame_close()
    global lang
    lang = "es"
    log(f"Lenguaje: {lang}")
    cambiar_lenguaje(lang)
    mostrar_mensaje("Español")
def english():
    menu.frame_close()
    global lang
    lang = "en"
    log(f"Lenguaje: {lang}")
    cambiar_lenguaje(lang)
    mostrar_mensaje("English")
def cambiar_lenguaje(lang):
    guardar_config()
    menu.lenguaje(lang)
    memoria.lenguaje(lang)
    editor.lenguaje(lang)
    data_view.lenguaje(lang)
    consola.lenguaje(lang,errores_lang)
def about():
    try:
        about_window = Informacion(ventana,lang,current_theme)
        about_window.tema()
        about_window.limpiar()
        about_window.lenguaje()
    except Exception as ex:
        log(f"Error (line 1350): {ex}")

ventana = tk.Tk()
ventana.title(f"ESM Simulator {version}")
ventana.geometry("800x600")
ventana.minsize(1140,680)
ventana.resizable(True, True)
ventana.grid_rowconfigure(1, weight=1)
ventana.grid_columnconfigure(1, weight=1)

configs()

canvas = tk.Canvas(ventana, bg=themes[current_theme]["bg"])
canvas.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew")
main_frame = tk.Frame(canvas, bg=themes[current_theme]["bg"])
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
canvas_window = canvas.create_window((0, 0), window=main_frame,anchor="nw")

def configure_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))
def configure_canvas_window(event=None):
    canvas_width = canvas.winfo_width()
    canvas.itemconfig(canvas_window, width=canvas_width)
main_frame.bind('<Configure>', configure_scroll_region)
canvas.bind('<Configure>', configure_canvas_window)

zoom_factor = 1.0
min_zoom = 1.0
max_zoom = 3.0
def apply_zoom(scale, event=None):
    global zoom_factor
    if scale * zoom_factor > max_zoom:
        return
    if scale * zoom_factor < min_zoom:
        reset_zoom()
        return
    if event:
        mouse_x = canvas.canvasx(event.x)
        mouse_y = canvas.canvasy(event.y)
    else:
        mouse_x = canvas.winfo_width() / 2
        mouse_y = canvas.winfo_height() / 2
    canvas.scale("all", mouse_x, mouse_y, scale, scale)
    zoom_factor *= scale
    canvas.configure(scrollregion=canvas.bbox("all"))
def zoom_in(event=None): apply_zoom(1.1, event)
def zoom_out(event=None): apply_zoom(0.9, event)
def reset_zoom(event=None):
    global zoom_factor
    scale = 1.0 / zoom_factor
    apply_zoom(scale)
    zoom_factor = 1.0
canvas.bind("<Control-MouseWheel>", lambda e: zoom_in(e) if e.delta > 0 else zoom_out(e))
ventana.bind("<Control-plus>", zoom_in)
ventana.bind("<Control-minus>", zoom_out)
ventana.bind("<Control-0>", reset_zoom)

menu = BarraMenu(main_frame, lang, theme, nuevo_archivo, abrir_archivo, guardar_archivo, guardar_como, assembly, run, stepin, reset, toggle_mode, español, english, about, guardar_archivo_binario, guardar_archivo_hexadecimal)
editor = EditorTexto(main_frame,guardar_archivo,escrivir_archivo,mostrar_mensaje)
consola = Consola(main_frame,lang)
memoria = Memoria(main_frame,diccionario,pc,ab,theme)
data_view = Variables(main_frame)

ventana.bind('<Control-z>', editor.deshacer)
ventana.bind('<Control-y>', editor.rehacer)
if not primer_inicio:
    ventana.bind('<Control-s>', guardar_archivo())
else:
    primer_inicio = False

cambiar_lenguaje(lang)
apply_theme()

ventana.mainloop()

