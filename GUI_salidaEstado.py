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
from queue import Queue
import re

class Consola:
    def __init__(self,ventana,lang):
        self.ventana = ventana
        self.tib = 0
        self.lang = lang
        self.tob_estuvo_aqui = False
        self.frame_principal = tk.Frame(self.ventana)
        self.frame_principal.grid(row=2,column=0,padx=0,pady=0,sticky="nw")
        self.consola_title = tk.Label(self.frame_principal,text="Consola:")
        self.consola_title.grid(row=0,column=0,padx=15,pady=5,sticky="nw")
        self.clear_botton = tk.Button(self.frame_principal,text="Limpiar",command=self.limpiar,borderwidth=0,highlightthickness=0)
        self.clear_botton.grid(row=0,column=1,padx=15,pady=5,sticky="ne")
        self.consola = tk.Text(self.frame_principal,state=tk.DISABLED,width=80, height=10)    
        self.consola.grid(row=1,column=0,columnspan=2,sticky="nsew",padx=5,pady=5)
        self.consola_scrollbar = tk.Scrollbar(self.frame_principal, command=self.consola.yview)
        self.consola_scrollbar.grid(row=1, column=2, sticky="ns")
        self.consola.config(yscrollcommand=self.consola_scrollbar.set)
    
    def tema(self,theme):
        self.frame_principal.configure(bg=theme["bg"])
        self.consola_title.config(bg=theme["bg"], fg=theme["fg"])
        self.consola.config(bg=theme["entry_bg"], fg=theme["entry_fg"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"])
        self.consola_scrollbar.configure(bg=theme["scroll_bg"],troughcolor=theme["scroll_fg"],activebackground=theme["scroll_active"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"])
        self.clear_botton.config(bg=theme["button_bg"],fg=theme["button_fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
    
    def ajustar_zoom(self, zoom_value):
        font_size = int(zoom_value * 0.10)
        self.consola.config(font=("Arial", font_size))
        self.consola_title.config(font=("Arial", font_size))
        self.clear_botton.config(font=("Arial", font_size))
        # Ajusta el ancho para compensar el tamaño de fuente
        self.consola.config(width=int(800/font_size), height=int(100/font_size))

    def print(self,mensaje,tob=0):
        if tob == 1:
            self.consola.config(state=tk.NORMAL)
            self.consola.insert(tk.END,mensaje)
            self.consola.config(state=tk.DISABLED)
            self.consola.see(tk.END)
            self.tob_estuvo_aqui = True
        else:
            if self.tob_estuvo_aqui:
                self.consola.config(state=tk.NORMAL)
                self.consola.insert(tk.END,"\n"+mensaje+"\n")
                self.consola.config(state=tk.DISABLED)
                self.consola.see(tk.END)
                self.tob_estuvo_aqui = False
            else:
                self.consola.config(state=tk.NORMAL)
                self.consola.insert(tk.END,mensaje+"\n")
                self.consola.config(state=tk.DISABLED)
                self.consola.see(tk.END)
    def limpiar(self):
        self.consola.config(state=tk.NORMAL)
        self.consola.delete(1.0,tk.END)
        self.consola.config(state=tk.DISABLED)
    
    def lenguaje(self, lang, errores_lang):
        if lang == "es":
            self.consola_title.config(text="Consola: ")
            self.clear_botton.config(text="Limpiar")
        if lang == "en":
            self.consola_title.config(text="Console: ")
            self.clear_botton.config(text="Clear")

        if self.lang != lang:
            self.consola.config(state=tk.NORMAL)
            lines = self.consola.get("1.0", tk.END).strip().split("\n")
            queue = Queue()
            translated_lines = []
            for line in lines:
                parts = line.split(":")
                if parts and parts[0].startswith("Error"):
                    try:
                        error_code = int(parts[0].split()[1])
                        queue.put(("error", error_code))
                    except ValueError:
                        continue
                elif "Ingrese un carácter" in line:
                    match = re.search(r"Ingrese un carácter --> (.+)", line)
                    char = match.group(1) if match else ""
                    queue.put(("char_input", char))
                elif "Código ensamblado exitosamente" in line:
                    queue.put(("success", ""))
                elif "Deteniendo programa" in line:
                    queue.put(("stop", ""))
                elif "Input a character" in line:
                    match = re.search(r"Input a character --> (.+)", line)
                    char = match.group(1) if match else ""
                    queue.put(("char_input", char))
                elif "¡Assembly successful!" in line:
                    queue.put(("success", ""))
                elif "Halting program…" in line:
                    queue.put(("stop", ""))
                else:
                    queue.put(("char_output", line))

            self.consola.delete("1.0", tk.END)
            while not queue.empty():
                msg_type, data = queue.get()
                if msg_type == "error" and data in errores_lang[lang]:
                    translated_lines.append(errores_lang[lang][data])
                elif msg_type == "char_output":
                    translated_lines.append(errores_lang[lang]["char_output"].format(data))
                elif msg_type == "char_input":
                    translated_lines.append(errores_lang[lang]["char_input"].format(data))
                elif msg_type in errores_lang[lang]:
                    translated_lines.append(errores_lang[lang][msg_type])

            texto_final = "\n".join(translated_lines).strip()
            if texto_final:
                self.consola.insert(tk.END, texto_final + "\n")

            self.consola.config(state=tk.DISABLED)
            self.lang = lang

class Variables:
    def __init__(self, ventana):
        self.ventana = ventana
        self.frame_principal = tk.Frame(self.ventana)
        self.frame_principal.grid(row=2,column=1,padx=0,pady=0)
        self.register = tk.Label(self.frame_principal,text="Register: ",font=("Arial",16))
        self.register.grid(row=0,column=0,padx=15,pady=5,sticky="nw")
        self.data_register = tk.Label(self.frame_principal,text=" 0 ",font=("Arial",16))
        self.data_register.grid(row=0,column=1,padx=15,pady=5,sticky="nw")
        self.status = tk.Label(self.frame_principal,text="Status: ",font=("Arial",16))
        self.status.grid(row=1,column=0,padx=15,pady=5,sticky="nw")
        self.data_status = tk.Label(self.frame_principal,text=" 0 ",font=("Arial",16))
        self.data_status.grid(row=1,column=1,padx=15,pady=5,sticky="nw")
        self.pc = tk.Label(self.frame_principal,text="PC: ",font=("Arial",16))
        self.pc.grid(row=2,column=0,padx=15,pady=5,sticky="nw")
        self.data_pc = tk.Label(self.frame_principal,text=" 0 ",font=("Arial",16))
        self.data_pc.grid(row=2,column=1,padx=15,pady=5,sticky="nw")

    def tema(self,theme):
        self.frame_principal.configure(bg=theme["bg"])
        self.register.configure(bg=theme["bg"],fg=theme["fg"])
        self.data_register.configure(bg=theme["bg"],fg=theme["fg"])
        self.status.configure(bg=theme["bg"],fg=theme["fg"])
        self.data_status.configure(bg=theme["bg"],fg=theme["fg"])
        self.pc.configure(bg=theme["bg"],fg=theme["fg"])
        self.data_pc.configure(bg=theme["bg"],fg=theme["fg"])

    def ajustar_zoom(self, zoom_value):
        font_size = int(zoom_value * 0.16)
        self.register.configure(font=("Arial", font_size))
        self.data_register.configure(font=("Arial", font_size))
        self.status.configure(font=("Arial", font_size))
        self.data_status.configure(font=("Arial", font_size))
        self.pc.configure(font=("Arial", font_size))
        self.data_pc.configure(font=("Arial", font_size))
        # Ajusta el ancho para compensar el tamaño de fuente
        self.frame_principal.config(height=int((10*16)/font_size))

    def lenguaje(self,lang):
        if lang == "es":
            self.register.config(text="Registro: ")
            self.status.config(text="Estado: ")
        if lang == "en":
            self.register.config(text="Register: ")
            self.status.config(text="Status: ")

    def actualizar(self,register,status,pc):
        self.data_register.config(text=str(register))
        self.data_status.config(text=str(status))
        self.data_pc.config(text=str(pc.upper()))
    def limpiar(self):
        self.data_register.config(text=" 0 ")
        self.data_status.config(text=" 0 ")
        self.data_pc.config(text=" 0 ")