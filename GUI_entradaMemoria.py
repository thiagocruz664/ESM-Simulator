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

class EditorTexto:
    """
    Esta clase implementa el editor de texto de la aplicación,
    proporcionando un área para escribir y editar código fuente.
    Incluye funcionalidades para deshacer, rehacer y detectar
    cambios en el contenido del editor.
    """
    def __init__(self,ventana,guardar,abrir,mensaje):
        """
        Inicializa el editor de texto de la aplicación

        Crea el área de edición de código, la barra de desplazamiento
        vertical y registra los atajos de teclado para guardar,
        deshacer, rehacer y detectar modificaciones en el documento

        Parametros
        ----------
        ventana : Tk
            Ventana principal de la aplicación
        guardar : function
            Función encargada de guardar el archivo actual
        abrir : function
            Función utilizada para recargar el contenido del archivo
        mensaje : function
            Función encargada de mostrar mensajes al usuario
        """
        self.ventana = ventana
        self.guardar = guardar
        self.abrir = abrir
        self.archivo = False
        self.mensaje = mensaje
        self.frame_principal = tk.Frame(self.ventana)
        self.frame_principal.grid(row=1,column=0,padx=0,pady=0,sticky="nw")
        self.code_title = tk.Label(self.frame_principal,text="untitled.txt")
        self.code_title.grid(row=0,column=0,padx=15,pady=5,sticky="nw")
        self.code_editor = tk.Text(self.frame_principal,width=80, undo=True)
        self.code_editor.grid(row=1,column=0,sticky="nsew",padx=5,pady=5)
        self.scrollbar = tk.Scrollbar(self.frame_principal, command=self.code_editor.yview)
        self.scrollbar.grid(row=1, column=1, sticky="ns")  # Posicionamos la scrollbar a la derecha
        self.code_editor.config(yscrollcommand=self.scrollbar.set)
        self.frame_principal.grid_rowconfigure(1, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(1, weight=0)

        self.code_editor.bind('<Control-s>', self.guardar)
        self.code_editor.bind('<Control-z>', self.deshacer)
        self.code_editor.bind('<Control-y>', self.rehacer)
        self.code_editor.bind('<<Modified>>', self.on_modified)
        
    #===============================================================================================
    #======================================= RENDER Y DISEÑO =======================================
    def ajustar_zoom(self, zoom_value: float):
        """
        Modifica el tamaño de la fuente del editor

        Actualiza el tamaño de letra del editor y del título,
        ajustando además el ancho del área de edición para mantener
        una visualización adecuada

        Parametros
        ----------
        zoom_value : float
            Porcentaje de zoom seleccionado por el usuario
        """
        font_size = int(zoom_value * 0.10)
        self.code_editor.configure(font=("Arial", font_size))
        self.code_title.config(font=("Arial", font_size))
        # Ajusta el ancho para compensar el tamaño de fuente
        self.code_editor.config(width=int(800/font_size))
    def tema(self,theme: dict):
        """
        Aplica el tema gráfico al editor de texto

        Actualiza los colores del editor, la barra de desplazamiento,
        el título y el cursor de escritura

        Parametros
        ----------
        theme : dict
            Diccionario con la configuración visual del tema
        """
        self.frame_principal.configure(bg=theme["bg"])
        self.code_title.configure(bg=theme["bg"],fg=theme["fg"])
        self.code_editor.configure(bg=theme["entry_bg"],fg=theme["entry_fg"],
                                   highlightbackground=theme["menu_bg"],
                                   highlightcolor=theme["menu_bg"],
                                   insertbackground=theme["menu_fg"])
        self.scrollbar.configure(bg=theme["scroll_bg"],troughcolor=theme["scroll_fg"],
                                 activebackground=theme["scroll_active"],
                                 highlightbackground=theme["menu_bg"],
                                 highlightcolor=theme["menu_bg"])
    def lenguaje(self,lang: str):
        """
        Actualiza el idioma mostrado en el título del editor

        Parametros
        ----------
        lang : str
            Idioma que se aplicará a la interfaz ("es" o "en")
        """
        if lang == "es":
            self.code_title.config(text="sin_nombre.txt")
        if lang =="en":
            self.code_title.config(text="untitled.txt")
    #===================================== FIN RENDER Y DISEÑO =====================================
    #===============================================================================================

    #===============================================================================================
    #====================================== ATAJOS DE TECLADO ======================================
    def on_modified(self, _event=None):
        """
        Gestiona el evento de modificación del editor

        Inserta un punto de separación en el historial de cambios y
        restablece el indicador de modificación cuando el documento
        no proviene de un archivo abierto

        Parametros
        ----------
        _event : tkinter.Event, opcional
            Evento de modificación generado por Tkinter
        """
        if not self.archivo:
            self.code_editor.edit_separator()
            self.code_editor.edit_modified(False)
    def deshacer(self, _event=None):
        """
        Deshace la última modificación realizada en el editor

        Si no existen acciones para deshacer, restaura el contenido
        actual mediante la función de apertura del archivo

        Parametros
        ----------
        _event : tkinter.Event, opcional
            Evento generado por el atajo de teclado
        """
        self.mensaje("Ctrl + Z")
        try:
            self.code_editor.edit_undo()
        except tk.TclError:
            self.abrir()
    def rehacer(self, _event=None):
        """
        Rehace la última operación deshecha en el editor

        Parametros
        ----------
        _event : tkinter.Event, opcional
            Evento generado por el atajo de teclado
        """
        self.mensaje("Ctrl + Y")
        try:
            self.code_editor.edit_redo()
        except tk.TclError:
            pass  # Ignorar el error si no hay nada que rehacer
    #==================================== FIN ATAJOS DE TECLADO ====================================
    #===============================================================================================

class Memoria:
    """
    Esta clase implementa el renderizado de la memoria
    principal del programa
    """
    def __init__(self,ventana,dicc,pc,ab,theme):
        """
        Inicializa el visor de memoria de la aplicación

        Crea la interfaz gráfica utilizada para representar el contenido
        de la memoria principal, incluyendo las direcciones, los datos
        almacenados, los controles de navegación, la búsqueda de
        direcciones y la administración de breakpoints

        Parametros
        ----------
        ventana : Tk
            Ventana principal de la aplicación
        dicc : dict
            Diccionario que contiene el contenido de la memoria
        pc : int
            Valor inicial del contador de programa
        ab : int
            Indica si la edición de breakpoints está habilitada
        theme : dict
            Diccionario con la configuración visual del tema
        """
        self.ventana = ventana
        self.diccionario_memoria = dicc
        self.pc_memoria = pc
        self.ab_memoria = ab
        self.theme = theme
        self.ensamblado = False
        self.frame_memory = tk.Frame(self.ventana)
        self.frame_memory.grid(row=1,column=1,padx=0,pady=0,sticky="nswe")
        self.memoria_title = tk.Label(self.frame_memory,text="Memoria:")
        self.memoria_title.grid(row=0,column=0,padx=15,pady=5,sticky="ns",columnspan=2)
        self.render_memory = {} #espacios de meomoria que estan en pantalla
        self.punto_de_apoyo = 0
        self.range_memory = 20
        for i in range(self.range_memory):
            entry = []
            entry0 = tk.Button(self.frame_memory,
                               text=f"  ◽ x{format(12288+i,'04x')}",
                               font=("Arial", 8),
                               borderwidth=0,
                               relief="flat",
                               highlightthickness=0,
                               command=lambda i=i: self.breakpoint(i))
            entry0.grid(row=i+1,column=0,padx=0,pady=0,sticky="nswe")
            entry.append(entry0)
            for f in range(4):
                entry1 = tk.Entry(self.frame_memory,
                                  state=tk.DISABLED,
                                  borderwidth=1,
                                  relief="flat",
                                  highlightthickness=0,
                                  font=("Arial", 8))
                entry1.grid(row=i + 1, column=f+1, sticky="nswe")
                entry.append(entry1)
                if f == 1 or f == 2:
                    self.frame_memory.grid_columnconfigure(f+1,weight=1,minsize=100)
                else:
                    self.frame_memory.grid_columnconfigure(f+1,weight=3,minsize=50)
            self.render_memory[i] = entry
            self.frame_memory.grid_rowconfigure(i+1, weight=1)
        self.frame_memory.grid_columnconfigure(0,weight=0,minsize=100)
        self.memory_spaces = {} #memoria completa

        self.frame_funciones = tk.Frame(self.frame_memory)
        self.frame_funciones.grid(row=21,column=2,padx=0,pady=0,sticky="nswe",columnspan=3)
        self.rowup = tk.Button(self.frame_funciones,
                               text="▲",
                               borderwidth=0,
                               relief="flat",
                               highlightthickness=0,
                               font=("Arial", 8),
                               command=self.up)
        self.rowup.grid(row=21,column=4,padx=0,pady=0,sticky="e")
        self.rowdown = tk.Button(self.frame_funciones,
                                 text="▼",
                                 borderwidth=0,
                                 relief="flat",
                                 highlightthickness=0,
                                 font=("Arial", 8),
                                 command=self.down)
        self.rowdown.grid(row=21,column=5,padx=0,pady=0,sticky="w")
        self.pc_search = tk.Entry(self.frame_funciones,
                                  state=tk.NORMAL,
                                  highlightthickness=0,
                                  font=("Arial", 8),
                                  width=8)
        self.pc_search.grid(row=21,column=3,padx=0,pady=0,sticky="w")
        self.x_search = tk.Label(self.frame_funciones,text="x",font=("Arial", 8))
        self.x_search.grid(row=21,column=2,padx=0,pady=0,sticky="e")
        self.search = tk.Button(self.frame_funciones,
                                text="🔍",
                                borderwidth=0,
                                relief="flat",
                                highlightthickness=0,
                                font=("Arial", 8),
                                command=self.buscar)
        self.search.grid(row=21,column=1,padx=0,pady=0,sticky="e")
        self.seguimiento = True
        self.seguimiento_button = tk.Button(self.frame_funciones,
                                            text="🔴",
                                            borderwidth=0,
                                            relief="flat",
                                            highlightthickness=0,
                                            font=("Arial", 8),
                                            command=self.seguir)
        self.seguimiento_button.grid(row=21,column=0,padx=0,pady=0,sticky="w")

        self.frame_memory.bind("<Enter>", self.on_frame)
        self.frame_memory.bind("<Leave>", self.not_on_frame)
        entry1.bind("<Enter>", self.on_frame)
        entry1.bind("<Leave>", self.not_on_frame)
        entry0.bind("<Enter>", self.on_frame)
        entry0.bind("<Leave>", self.not_on_frame)
        self.frame_memory.bind_all("<MouseWheel>", self._on_mousewheel)
        self.frame_memory.bind_all("<Button-4>", self._on_mousewheel)
        self.frame_memory.bind_all("<Button-5>", self._on_mousewheel)
        self.on_frame_siono = False

        self.breakpoints = []
        
    #===============================================================================================
    #======================================= RENDER Y DISEÑO =======================================
    def tema(self,theme: dict):
        """
        Aplica el tema gráfico al visor de memoria

        Actualiza los colores de todos los componentes que forman
        la vista de memoria y refresca su contenido cuando existe
        un programa ensamblado

        Parametros
        ----------
        theme : dict
            Diccionario con la configuración visual del tema
        """
        self.theme = theme
        self.frame_memory.configure(bg=theme["bg"])
        self.memoria_title.configure(bg=theme["bg"], fg=theme["fg"])
        self.frame_funciones.configure(bg=theme["bg"])
        self.rowup.configure(bg=theme["bg"], fg=theme["fg"],
                             activebackground=theme["menu_active_bg"],
                             activeforeground=theme["menu_active_fg"])
        self.rowdown.configure(bg=theme["bg"], fg=theme["fg"],
                               activebackground=theme["menu_active_bg"],
                               activeforeground=theme["menu_active_fg"])
        self.pc_search.configure(bg=theme["entry_bg"], fg=theme["entry_fg"],
                                 highlightbackground=theme["menu_bg"],
                                 highlightcolor=theme["menu_bg"],
                                 insertbackground=theme["menu_fg"])
        self.x_search.configure(bg=theme["bg"],fg=theme["fg"])
        self.search.configure(bg=theme["bg"], fg=theme["fg"],
                              activebackground=theme["menu_active_bg"],
                              activeforeground=theme["menu_active_fg"])
        self.seguimiento_button.configure(bg=theme["bg"], fg=theme["fg"],
                                          activebackground=theme["menu_active_bg"],
                                          activeforeground=theme["menu_active_fg"])
        for i in range(20):
            linea = self.render_memory[i]
            c=0
            for entry in linea:
                if c==0:
                    entry.configure(bg=theme["bg"], fg=theme["fg"],
                                    activebackground=theme["menu_active_bg"],
                                    activeforeground=theme["menu_active_fg"])
                    c=c+1
                else:
                    if i%2==0:
                        entry.configure(disabledbackground=theme["entry_bg"],
                                        disabledforeground=theme["entry_fg"],
                                        highlightbackground=theme["menu_bg"],
                                        highlightcolor=theme["menu_bg"])
                    else:
                        entry.configure(disabledbackground=theme["menu_bg"],
                                        disabledforeground=theme["menu_fg"],
                                        highlightbackground=theme["menu_bg"],
                                        highlightcolor=theme["menu_bg"])
        if self.ensamblado:
            self.mapear_memoria(self.diccionario_memoria,
                                self.punto_de_apoyo,
                                self.punto_de_apoyo,
                                False)
    def lenguaje(self,lang: str):
        """
        Actualiza el idioma mostrado en el visor de memoria

        Parametros
        ----------
        lang : str
            Idioma que se aplicará a la interfaz ("es" o "en")
        """
        if lang == "es":
            self.memoria_title.config(text="Memoria:")
        if lang =="en":
            self.memoria_title.config(text="Memory:")
    def ajustar_zoom(self, value: float):
        """
        Modifica el tamaño de fuente de los componentes del visor
        de memoria segun el zoom seleccionado por el usuario

        Parametros
        ----------
        value : float
            Porcentaje de zoom seleccionado por el usuario
        """
        for i in range(20):
            for j in range(5):
                self.render_memory[i][j].config(font=("Arial", int(value * 0.08)))
        self.memoria_title.config(font=("Arial",int(value*0.10)))
    #===================================== FIN RENDER Y DISEÑO =====================================
    #===============================================================================================
    
    #===============================================================================================
    #============================= METODOS DE DESPLAZAMIENTO DE MEMORIA ============================
    def on_frame(self, _event):
        """
        Indica que el cursor del mouse se encuentra sobre el visor
        de memoria

        Parametros
        ----------
        _event : tkinter.Event
            Evento generado al ingresar al área del visor
        """
        self.on_frame_siono = True
    def not_on_frame(self, _event):
        """
        Indica que el cursor del mouse no se encuentra sobre el 
        visor de memoria

        Parametros
        ----------
        _event : tkinter.Event
            Evento generado al ingresar al área del visor
        """
        self.on_frame_siono = False
    def _on_mousewheel(self, event):
        """
        Gestiona el desplazamiento mediante la rueda del mouse

        Parametros
        ----------
        event : tkinter.Event
            Evento generado por la rueda del mouse
        """
        if self.on_frame_siono:
            if event.num == 4 or event.delta > 0:
                self.up()
            elif event.num == 5 or event.delta < 0:
                self.down()
    def up(self):
        """
        Desplaza la visualización de la memoria una posición hacia
        direcciones inferiores
        """
        self.punto_de_apoyo = self.punto_de_apoyo - 1
        if self.punto_de_apoyo<0:
            self.punto_de_apoyo = 65536 + self.punto_de_apoyo
        self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.pc_memoria,False)
    def down(self):
        """
        Desplaza la visualización de la memoria una posición hacia
        direcciones superiores
        """
        self.punto_de_apoyo = self.punto_de_apoyo + 1
        if self.punto_de_apoyo>=65535:
            self.punto_de_apoyo = self.punto_de_apoyo - 65536
        self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.pc_memoria,False)
    def buscar(self):
        """
        Ubica la vista de memoria en la dirección hexadecimal
        ingresada por el usuario
        """
        try:
            direccion = int(self.pc_search.get(),16)
            self.punto_de_apoyo = direccion
            self.mapear_memoria(self.diccionario_memoria,direccion,self.pc_memoria,False)
        except ValueError:
            pass
    def seguir(self):
        """
        Activa o desactiva el seguimiento automático del contador
        de programa durante la ejecución
        """
        if self.seguimiento:
            self.seguimiento = False
            self.seguimiento_button.config(text="⭕")
        else:
            self.seguimiento = True
            self.seguimiento_button.config(text="🔴")
    #========================== FIN METODOS DE DESPLAZAMIENTO DE MEMORIA ===========================
    #===============================================================================================
    
    #===============================================================================================
    #================================== METODOS DE MAPEO DE MEMORIA ================================
    def mapear_memoria(self,diccionario: dict,origen: int,
                       pc_act: int,bandera_stepin_llamado=True):
        """
        Actualiza la representación gráfica de la memoria

        Sincroniza el contenido mostrado en pantalla con el estado
        actual de la memoria, resaltando la posición del contador
        de programa y los breakpoints definidos. Cuando el modo de
        seguimiento está habilitado, ajusta automáticamente la
        ventana visible para mantener el contador de programa dentro
        del área mostrada

        Parametros
        ----------
        diccionario : dict
            Diccionario que contiene el contenido completo de la memoria
        origen : int
            Dirección base desde la cual comenzará la visualización
        pc_act : int
            Valor actual del contador de programa
        bandera_stepin_llamado : bool, optional
            Indica si el método fue invocado desde la ejecución del
            simulador o mediante un desplazamiento manual
        """
        if bandera_stepin_llamado:
            self.pc_memoria = pc_act
            if self.seguimiento:
                if pc_act == origen:
                    self.punto_de_apoyo = origen
                if pc_act - self.punto_de_apoyo == 20:
                    self.punto_de_apoyo = self.punto_de_apoyo + 1
                if pc_act - self.punto_de_apoyo < 0:
                    self.punto_de_apoyo = pc_act
                if pc_act - self.punto_de_apoyo > 20:
                    self.punto_de_apoyo = pc_act
                if pc_act -self.punto_de_apoyo < 20 and pc_act - self.punto_de_apoyo > 0:
                    pass
        else:
            pass
        diferencial = 0
        for i in range(self.range_memory):
            #fiajate aca que cuando el pc sea mayor 65535 se reincie
            if (self.punto_de_apoyo+i>65535 and diferencial==0):
                diferencial=self.punto_de_apoyo+i
            if self.punto_de_apoyo<0:
                pass
            entry = self.render_memory[i]
            ent = entry[0]
            if self.punto_de_apoyo + i in self.breakpoints:
                if pc_act == self.punto_de_apoyo + i - diferencial:
                    ent.config(text=f"  ◼️ x{format(self.punto_de_apoyo+i-diferencial,'04x').upper()}  <- ",fg="green",activeforeground="green")
                else:
                    ent.config(text=f"  ◻️ x{format(self.punto_de_apoyo+i-diferencial,'04x').upper()}",fg="red",activeforeground="red")
            else:
                if self.pc_memoria-self.punto_de_apoyo + diferencial == i:
                    ent.config(text=f"  ◼️ x{format(self.punto_de_apoyo+i-diferencial,'04x').upper()}  <- ",fg="green",activeforeground="green")
                else:
                    ent.config(text=f"  ◻️ x{format(self.punto_de_apoyo+i-diferencial,'04x').upper()}",fg=self.theme["fg"],activeforeground=self.theme["menu_active_fg"])
            for j in range(1,5):
                ent = entry[j]
                ent.config(state=tk.NORMAL)
                ent.delete(0, tk.END)
                try:
                    if diccionario[hex(self.punto_de_apoyo+i-diferencial)][j-1] is None:
                        ent.insert(tk.END, "")
                    else:
                        ent.insert(tk.END,diccionario.get(hex(self.punto_de_apoyo+i-diferencial))[j-1])
                except (KeyError, IndexError, TypeError):
                    pass
                ent.config(state=tk.DISABLED)
    def limpiar(self):
        """
        Restablece el visor de memoria a su estado inicial

        Elimina el contenido mostrado, borra todos los breakpoints,
        restaura la dirección inicial de memoria y reaplica el tema
        gráfico actual
        """
        if not self.seguimiento:
            self.seguir()
        # Reiniciar el estado interno de la memoria
        self.diccionario_memoria = {}
        self.pc_memoria = 0
        self.punto_de_apoyo = 12288
        self.breakpoints = []
        self.ensamblado = False

        # Limpiar las posiciones visibles de memoria
        for i, entry in self.render_memory.items():
            # Actualizar la dirección mostrada
            entry[0].config(
                text=f"  ◻️ x{format(self.punto_de_apoyo + i, '04x').upper()}"
            )

            # Vaciar el contenido de las celdas
            for j in range(1, 5):
                entry[j].config(state=tk.NORMAL)
                entry[j].delete(0, tk.END)
                entry[j].config(state=tk.DISABLED)

        # Restaurar los colores del tema actual
        self.tema(self.theme)
    def breakpoint(self,i: int):
        """
        Agrega o elimina un breakpoint sobre la dirección de memoria
        seleccionada por el usuario

        Parametros
        ----------
        i : int
            Índice de la posición visible dentro del visor de memoria
        """
        if self.ab_memoria == 1:
            if self.punto_de_apoyo+i in self.breakpoints:
                self.breakpoints.remove(self.punto_de_apoyo+i)
                self.breakpoints.sort()
            else:
                self.breakpoints.append(self.punto_de_apoyo+i)
                self.breakpoints.sort()
            self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.pc_memoria,False)
    #================================ FIN METODOS DE MAPEO DE MEMORIA ==============================
    #===============================================================================================