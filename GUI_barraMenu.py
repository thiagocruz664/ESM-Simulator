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
from tkinter import ttk

class BarraMenu:
    def __init__(self, ventana, lang, theme, nuevo_archivo, abrir_archivo, guardar_archivo, guardar_como, assembly, run, stepin, reset, toggle_mode, español, english, about, gab, gah):
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
        self.español = español
        self.english = english
        self.about = about
        self.guardar_archivo_binario = gab
        self.guardar_archivo_hexa = gah
        self.menu_frame = tk.Frame(self.ventana)
        self.menu_frame.grid(row=0,column=0,padx=0,pady=0,columnspan=2,sticky="nwe")
        self.separator = tk.Frame(self.menu_frame, height=2)  # Línea de 2px
        self.separator.pack(side="bottom",fill="x")

        self.archivo_button = tk.Button(self.menu_frame, text="🗂️ Archivo", command=self.toggle_archivo_menu,borderwidth=0, relief="flat",highlightthickness=0)
        self.archivo_button.pack(side="left", padx=5)
        print(type(self.archivo_button))
        self.ensamblar_button = tk.Button(self.menu_frame, text="🛠️ Ensamblar", command=self.assembly,borderwidth=0, relief="flat",highlightthickness=0)
        self.ensamblar_button.pack(side="left", padx=5)

        self.run_button = tk.Button(self.menu_frame, text="▶️", command=self.run,borderwidth=0, relief="flat",highlightthickness=0)
        self.run_button.pack(side="left", padx=5)

        self.stepin_button = tk.Button(self.menu_frame, text="↩️", command=self.stepin,borderwidth=0, relief="flat",highlightthickness=0)
        self.stepin_button.pack(side="left", padx=5)

        self.limpiar_button = tk.Button(self.menu_frame, text="↻", command=self.reset,borderwidth=0, relief="flat",highlightthickness=0)
        self.limpiar_button.pack(side="left", padx=5)
        
        self.setting_button = tk.Button(self.menu_frame, text="⚙️", command=self.toggle_frame_settings,borderwidth=0, relief="flat",highlightthickness=0)
        self.setting_button.pack(side="right", padx=5)

        self.archivo_menu_frame = None
        self.idioma_menu_frame = None
        self.settings_menu_frame = None
        self.archivo_menu_buttons={}
        self.idioma_menu_buttons={}
        self.settings_menu_buttons={}

    def tema(self,theme):
        self.theme = theme
        self.menu_frame.configure(bg=theme["button_bg"])
        self.separator.configure(bg=theme["menu_bg"])
        self.archivo_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.ensamblar_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.stepin_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.run_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.limpiar_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.setting_button.configure(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])

    def toggle_archivo_menu(self):
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
            self.settings_menu_buttons["about"]=tk.Button(self.settings_menu_frame,text="⚠️ Informacion", anchor="w", command=self.about,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["about"].pack(fill="x")
        elif self.lang == "en":
            self.settings_menu_buttons["mode"]=tk.Button(self.settings_menu_frame, text="🌓 Mode", anchor="w", command=self.toggle_mode,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["mode"].pack(fill="x")
            self.settings_menu_buttons["lang"]=tk.Button(self.settings_menu_frame, text="🌐 Language", anchor="w", command=self.toggle_idioma_menu,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["lang"].pack(fill="x")
            self.settings_menu_buttons["about"]=tk.Button(self.settings_menu_frame,text="⚠️ About", anchor="w", command=self.about,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.settings_menu_buttons["about"].pack(fill="x")
        
        self.ventana.bind("<Button-1>", self.verificar_clic_fuera)
    def toggle_idioma_menu(self):
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
            self.idioma_menu_buttons["es"]=tk.Button(self.idioma_menu_frame, text="🇦🇷 Español", command=self.español,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["es"].pack(fill="x")
            self.idioma_menu_buttons["en"]=tk.Button(self.idioma_menu_frame, text="🇺🇸 Ingles", command=self.english,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["en"].pack(fill="x")
        elif self.lang == "en":
            self.idioma_menu_buttons["es"]=tk.Button(self.idioma_menu_frame, text="🇦🇷 Spanish", command=self.español,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["es"].pack(fill="x")
            self.idioma_menu_buttons["en"]=tk.Button(self.idioma_menu_frame, text="🇺🇸 English", command=self.english,bg=self.theme["button_bg"],fg=self.theme["button_fg"],activebackground=self.theme["menu_active_bg"],activeforeground=self.theme["menu_active_fg"],borderwidth=0, relief="flat",highlightthickness=0)
            self.idioma_menu_buttons["en"].pack(fill="x")

        self.ventana.bind("<Button-1>", self.verificar_clic_fuera)

    def frame_close(self):
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
    def verificar_clic_fuera(self, event):
        click_x = event.x_root - self.ventana.winfo_x()
        click_y = event.y_root - self.ventana.winfo_y()
        if self.archivo_menu_frame:
            menu_x = self.archivo_menu_frame.winfo_x()
            menu_y = self.archivo_menu_frame.winfo_y()
            menu_width = self.archivo_menu_frame.winfo_width()+20
            menu_height = self.archivo_menu_frame.winfo_height()+20
        if self.settings_menu_frame:
            menu_x = self.settings_menu_frame.winfo_x()
            menu_y = self.settings_menu_frame.winfo_y()
            menu_width = self.settings_menu_frame.winfo_width()+20
            menu_height = self.settings_menu_frame.winfo_height()+20
        if self.idioma_menu_frame:
            menu_x = self.idioma_menu_frame.winfo_x()
            menu_y = self.idioma_menu_frame.winfo_y()
            menu_width = self.idioma_menu_frame.winfo_width()+40
            menu_height = self.idioma_menu_frame.winfo_height()+40
        # Verificar si el clic ocurrió fuera del menú
        if (self.idioma_menu_frame or self.archivo_menu_frame or self.settings_menu_frame):
            if not (menu_x <= click_x <= menu_x + menu_width and menu_y <= click_y <= menu_y + menu_height):
                # Cerrar el menú si el clic fue fuera
                self.frame_close()

    def lenguaje(self,lang):
        if lang == "es":
            self.lang = "es"
            self.archivo_button.config(text="🗂️ Archivo")
            self.ensamblar_button.config(text="🛠️ Ensamblar")
        if lang == "en":
            self.lang = "en"
            self.archivo_button.config(text="🗂️ Archive")
            self.ensamblar_button.config(text="🛠️ Assemble")
    