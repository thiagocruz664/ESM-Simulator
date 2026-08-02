#    ESM Simulator its a GUI for programing in assmbly of the ESMx16 ISA

#    Copyright © 2025 Cruz Thiago, Ryberg Brian, Meier Jonathan.

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

class BarraMenu:
    """
    Esta clase implementa la barra de menú superior de la aplicación.
    Su función es centralizar todos los controles relacionados con la gestión de archivos,
    ejecución del simulador, configuración de la interfaz y selección de idioma. Además,
    administra la creación y destrucción dinámica de los menús desplegables y aplica los
    cambios de apariencia y configuración durante la ejecución.
    """
    def __init__(self, ventana, lang, theme, zoom_value,
             nuevo_archivo, abrir_archivo, guardar_archivo,
             guardar_como, assembly, run, stepin, reset,
             toggle_mode, spanish, english, help_callback, about,
             gab, gah, ajustar_zoom):
        """
            Inicializa la barra de menú principal de la aplicación
        
            Crea los botones principales de la interfaz, el control
            de zoom y almacena las funciones asociadas a cada acción,
            además de inicializar los menús desplegables y sus
            estructuras de control
            
            Parametros:
            ----------
                ventana : Tk
                    Ventana principal de la aplicación
                lang : str
                    Idioma inicial de la interfaz ("es" o "en")
                theme : dict
                    Diccionario con los colores del tema seleccionado
                zoom_value : int
                    Valor inicial del nivel de zoom
                nuevo_archivo : function
                    Función encargada de crear un nuevo archivo
                abrir_archivo : function
                    Función para abrir un archivo existente
                guardar_archivo : function
                    Función para guardar el archivo actual
                guardar_como : function
                    Función para guardar el archivo con otro nombre
                assembly : function
                    Función que inicia el proceso de ensamblado
                run : function
                    Función que ejecuta el programa completo
                stepin : function
                    Función que ejecuta una instrucción del programa
                reset : function
                    Función que reinicia la simulación
                toggle_mode : function
                    Función que cambia el tema visual de la aplicación
                spanish : function
                    Función que cambia el idioma al español
                english : function
                    Función que cambia el idioma al inglés
                help_callback : function
                    Función que muestra la ayuda de uso y programación
                about : function
                    Función que muestra la información del programa
                gab : function
                    Función que guarda el programa en formato binario
                gah : function
                    Función que guarda el programa en formato hexadecimal
                ajustar_zoom : function
                    Función encargada de modificar el tamaño de la interfaz
        """
        self.ventana = ventana
        self.lang = lang
        self.theme = theme
        self.nuevo_archivo = nuevo_archivo
        self.abrir_archivo = abrir_archivo
        self.guardar_archivo = guardar_archivo
        self.guardar_como = guardar_como
        self.assembly = assembly
        self.run = run
        self.stepin = stepin
        self.reset = reset
        self.toggle_mode = toggle_mode
        self.spanish = spanish
        self.english = english
        self.help_callback = help_callback
        self.about = about
        self.guardar_archivo_binario = gab
        self.guardar_archivo_hexa = gah
        self.zoom_value = zoom_value
        self.ajustar_zoom = ajustar_zoom
        self.menu_frame = tk.Frame(self.ventana)
        self.menu_frame.grid(row=0,column=0,padx=0,pady=0,columnspan=2,sticky="nwe")
        self.separator = tk.Frame(self.menu_frame, height=2)  # Línea de 2px
        self.separator.pack(side="bottom",fill="x")
        self.archivo_button = tk.Button(self.menu_frame,
                                        text="🗂️ Archivo",
                                        command=self.toggle_archivo_menu,
                                        borderwidth=0,
                                        relief="flat",
                                        highlightthickness=0)
        self.archivo_button.pack(side="left", padx=5)
        self.ensamblar_button = tk.Button(self.menu_frame,
                                          text="🛠️ Ensamblar",
                                          command=self.assembly,
                                          borderwidth=0,
                                          relief="flat",
                                          highlightthickness=0)
        self.ensamblar_button.pack(side="left", padx=5)
        self.run_button = tk.Button(self.menu_frame,
                                    text="▶️",
                                    command=self.run,
                                    borderwidth=0,
                                    relief="flat",
                                    highlightthickness=0)
        self.run_button.pack(side="left", padx=5)
        self.stepin_button = tk.Button(self.menu_frame,
                                       text="↩️",
                                       command=self.stepin,
                                       borderwidth=0,
                                       relief="flat",
                                       highlightthickness=0)
        self.stepin_button.pack(side="left", padx=5)
        self.limpiar_button = tk.Button(self.menu_frame,
                                        text="↻",
                                        command=self.reset,
                                        borderwidth=0,
                                        relief="flat",
                                        highlightthickness=0)
        self.limpiar_button.pack(side="left", padx=5)
        self.setting_button = tk.Button(self.menu_frame,
                                        text="⚙️",
                                        command=self.toggle_frame_settings,
                                        borderwidth=0,
                                        relief="flat",
                                        highlightthickness=0)
        self.setting_button.pack(side="right", padx=5)
        self.zoom_slider = tk.Scale(self.menu_frame,
                                    from_=100,
                                    to=200,
                                    showvalue=False,
                                    orient=tk.HORIZONTAL,
                                    borderwidth=0,
                                    relief="flat",
                                    highlightthickness=0,
                                    command=self.actualizar_zoom)
        self.zoom_slider.pack(side="right", padx=50)

        self.archivo_menu_frame = None
        self.idioma_menu_frame = None
        self.settings_menu_frame = None
        self.archivo_menu_buttons={}
        self.idioma_menu_buttons={}
        self.settings_menu_buttons={}

    def tema(self, theme: dict[str, str]):
        """
        Aplica el tema gráfico seleccionado a todos los componentes
        de la barra de menú, actualizando colores de botones,
        fondos y controles de la interfaz
        
        Parametros:
            theme (dict): Diccionario que contiene los colores y estilos
            del tema a aplicar, con claves como "bg", "fg", "button_bg",
            "button_fg", "menu_active_bg", "menu_active_fg", etc.
        """
        self.theme = theme
        self.menu_frame.configure(bg=theme["button_bg"])
        self.separator.configure(bg=theme["menu_bg"])
        self.archivo_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],
                                      activebackground=theme["menu_active_bg"],
                                      activeforeground=theme["menu_active_fg"])
        self.ensamblar_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],
                                        activebackground=theme["menu_active_bg"],
                                        activeforeground=theme["menu_active_fg"])
        self.stepin_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],
                                     activebackground=theme["menu_active_bg"],
                                     activeforeground=theme["menu_active_fg"])
        self.run_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],
                                  activebackground=theme["menu_active_bg"],
                                  activeforeground=theme["menu_active_fg"])
        self.limpiar_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],
                                      activebackground=theme["menu_active_bg"],
                                      activeforeground=theme["menu_active_fg"])
        self.setting_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],
                                      activebackground=theme["menu_active_bg"],
                                      activeforeground=theme["menu_active_fg"])
        self.zoom_slider.configure(bg=theme["scroll_bg"],troughcolor=theme["scroll_fg"],
                                   activebackground=theme["scroll_active"],
                                   highlightbackground=theme["menu_bg"],
                                   highlightcolor=theme["menu_bg"])

    def actualizar_zoom(self, value):
        """
        Actualiza el valor interno del nivel de zoom y sincroniza el 
        control deslizante con el nuevo valor seleccionado.
                
        Parametros:
            value: Nuevo valor de zoom seleccionado por el usuario
        """
        self.zoom_value = value
        self.zoom_slider.set(value)
        self.ajustar_zoom(int(value))

    def toggle_archivo_menu(self):
        """
        Abre o cierra el menú Archivo

        Si otro menú se encuentra abierto, lo cierra antes de crear
        dinámicamente las opciones correspondientes al idioma
        seleccionado
        """
        if self.archivo_menu_frame:
            self.frame_close()
            return
        if self.settings_menu_frame:
            self.frame_close()
        if self.idioma_menu_frame:
            self.frame_close()

        self.archivo_menu_frame = tk.Frame(self.ventana, relief="solid")
        self.archivo_menu_frame.place(x=10, y=self.archivo_button.winfo_height())

        self.archivo_menu_frame.grab_set()
        
        if self.lang == "es":
            self.archivo_menu_buttons[0]=tk.Button(self.archivo_menu_frame, text="📄 Nuevo", anchor="w", command=self.nuevo_archivo,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[0].pack(fill="x")
            self.archivo_menu_buttons[1]=tk.Button(self.archivo_menu_frame, text="📂 Abrir", anchor="w", command=self.abrir_archivo,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[1].pack(fill="x")
            self.archivo_menu_buttons[2]=tk.Button(self.archivo_menu_frame, text="💾 Guardar", anchor="w", command=self.guardar_archivo,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[2].pack(fill="x")
            self.archivo_menu_buttons[5]=tk.Button(self.archivo_menu_frame, text="💾 Guardar bin", anchor="w", command=self.guardar_archivo_binario,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[5].pack(fill="x")
            self.archivo_menu_buttons[6]=tk.Button(self.archivo_menu_frame, text="💾 Guardar hex", anchor="w", command=self.guardar_archivo_hexa,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[6].pack(fill="x")
            self.archivo_menu_buttons[3]=tk.Button(self.archivo_menu_frame, text="📝 Guardar como", anchor="w", command=self.guardar_como,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[3].pack(fill="x")
            self.archivo_menu_buttons[4]=tk.Button(self.archivo_menu_frame, text="Salir", anchor="w", command=self.ventana.quit,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[4].pack(fill="x")
        elif self.lang == "en":
            self.archivo_menu_buttons[0]=tk.Button(self.archivo_menu_frame, text="📄 New", anchor="w", command=self.nuevo_archivo,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[0].pack(fill="x")
            self.archivo_menu_buttons[1]=tk.Button(self.archivo_menu_frame, text="📂 Open", anchor="w", command=self.abrir_archivo,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[1].pack(fill="x")
            self.archivo_menu_buttons[2]=tk.Button(self.archivo_menu_frame, text="💾 Save", anchor="w", command=self.guardar_archivo,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[2].pack(fill="x")
            self.archivo_menu_buttons[5]=tk.Button(self.archivo_menu_frame, text="💾 Save bin", anchor="w", command=self.guardar_archivo_binario,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[5].pack(fill="x")
            self.archivo_menu_buttons[6]=tk.Button(self.archivo_menu_frame, text="💾 Save hex", anchor="w", command=self.guardar_archivo_hexa,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[6].pack(fill="x")
            self.archivo_menu_buttons[3]=tk.Button(self.archivo_menu_frame, text="📝 Save as", anchor="w", command=self.guardar_como,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[3].pack(fill="x")
            self.archivo_menu_buttons[4]=tk.Button(self.archivo_menu_frame, text="Quit", anchor="w", command=self.ventana.quit,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.archivo_menu_buttons[4].pack(fill="x")
    
        self.ventana.bind("<Button-1>", self.verificar_clic_fuera)
        
    def toggle_frame_settings(self):
        """
        Abre el menú de configuración de la aplicación

        Permite acceder al cambio de tema, idioma y a la
        información del programa
        """
        if self.settings_menu_frame:
            self.frame_close()
            return
        if self.archivo_menu_frame:
            self.frame_close()
        if self.idioma_menu_frame:
            self.frame_close()

        self.settings_menu_frame = tk.Frame(self.ventana, relief="solid")
        self.settings_menu_frame.place(x=self.setting_button.winfo_x()-80, y=self.setting_button.winfo_height())

        self.settings_menu_frame.grab_set()

        if self.lang == "es":
            self.settings_menu_buttons["mode"]=tk.Button(self.settings_menu_frame, text="🌓 Modo", anchor="w", command=self.toggle_mode,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["mode"].pack(fill="x")
            self.settings_menu_buttons["lang"]=tk.Button(self.settings_menu_frame, text="🌐 Lenguaje", anchor="w", command=self.toggle_idioma_menu,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["lang"].pack(fill="x")
            self.settings_menu_buttons["help"]=tk.Button(self.settings_menu_frame, text="❓ Ayuda", anchor="w", command=self.help_callback,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["help"].pack(fill="x")
            self.settings_menu_buttons["about"]=tk.Button(self.settings_menu_frame,text="⚠️ Informacion", anchor="w", command=self.about,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["about"].pack(fill="x")
        elif self.lang == "en":
            self.settings_menu_buttons["mode"]=tk.Button(self.settings_menu_frame, text="🌓 Mode", anchor="w", command=self.toggle_mode,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["mode"].pack(fill="x")
            self.settings_menu_buttons["lang"]=tk.Button(self.settings_menu_frame, text="🌐 Language", anchor="w", command=self.toggle_idioma_menu,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["lang"].pack(fill="x")
            self.settings_menu_buttons["help"]=tk.Button(self.settings_menu_frame, text="❓ Help", anchor="w", command=self.help_callback,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["help"].pack(fill="x")
            self.settings_menu_buttons["about"]=tk.Button(self.settings_menu_frame,text="⚠️ About", anchor="w", command=self.about,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["about"].pack(fill="x")
        
        self.ventana.bind("<Button-1>", self.verificar_clic_fuera)
        
    def toggle_idioma_menu(self):
        """
        Despliega el menú de selección de idioma de la interfaz,
        permitiendo alternar entre español e inglés
        """
        if self.archivo_menu_frame:
            self.frame_close()
        if self.settings_menu_frame:
            self.frame_close()
        if self.idioma_menu_frame:
            self.frame_close()
            return

        self.idioma_menu_frame = tk.Frame(self.ventana)
        self.idioma_menu_frame.place(x=self.setting_button.winfo_x()-75, y=self.setting_button.winfo_height())
        
        self.idioma_menu_frame.grab_set()
        
        if self.lang == "es":
            self.idioma_menu_buttons["es"]=tk.Button(self.idioma_menu_frame, text="🇦🇷 Español", command=self.spanish,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["es"].pack(fill="x")
            self.idioma_menu_buttons["en"]=tk.Button(self.idioma_menu_frame, text="🇺🇸 Ingles", command=self.english,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["en"].pack(fill="x")
        elif self.lang == "en":
            self.idioma_menu_buttons["es"]=tk.Button(self.idioma_menu_frame, text="🇦🇷 Spanish", command=self.spanish,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["es"].pack(fill="x")
            self.idioma_menu_buttons["en"]=tk.Button(self.idioma_menu_frame, text="🇺🇸 English", command=self.english,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["en"].pack(fill="x")

        self.ventana.bind("<Button-1>", self.verificar_clic_fuera)

    def frame_close(self):
        """
        Cierra cualquier menú desplegable que se encuentre abierto
        y libera los recursos gráficos asociados
        """
        type(self.archivo_menu_buttons)
        if self.archivo_menu_frame:
            self.archivo_menu_frame.destroy()
            self.archivo_menu_frame = None
        if self.settings_menu_frame:
            self.settings_menu_frame.destroy()
            self.settings_menu_frame = None
        if self.idioma_menu_frame:
            self.idioma_menu_frame.destroy()
            self.idioma_menu_frame = None
            
    def verificar_clic_fuera(self, event: tk.Event):
        """
        Detecta si el usuario realizó un clic fuera del menú
        desplegable y, en ese caso, lo cierra automáticamente
                
        Parametros:
            event (tk.Event): Evento de clic del mouse generado por 
            Tkinter, que contiene información sobre la posición del clic
        """
        click_x = event.x_root - self.ventana.winfo_x()
        click_y = event.y_root - self.ventana.winfo_y()

        menu = None
        if self.archivo_menu_frame:
            menu = self.archivo_menu_frame
        elif self.settings_menu_frame:
            menu = self.settings_menu_frame
        elif self.idioma_menu_frame:
            menu = self.idioma_menu_frame

        if menu:
            menu_x = menu.winfo_x()
            menu_y = menu.winfo_y()
            menu_width = menu.winfo_width() + 10
            menu_height = menu.winfo_height() + 30

            # Verificar si el clic ocurrió fuera del menú
            if not (menu_x <= click_x <= menu_x + menu_width and menu_y <= click_y <= menu_y + menu_height):
                # Cerrar el menú si el clic fue fuera
                self.frame_close()

    def lenguaje(self,lang: str):
        """
        Actualiza el idioma de los textos visibles de la barra
        de menú según la selección del usuario
                
        Parametros:
            lang (str): Código de idioma seleccionado, 
            "es" para español y "en" para inglés
        """
        if lang == "es":
            self.lang = "es"
            self.archivo_button.config(text="🗂️ Archivo")
            self.ensamblar_button.config(text="🛠️ Ensamblar")
        if lang == "en":
            self.lang = "en"
            self.archivo_button.config(text="🗂️ Archive")
            self.ensamblar_button.config(text="🛠️ Assemble")
    
