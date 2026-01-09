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
from tkinter import font
import webbrowser

class Informacion:
    def __init__(self, ventana, lang, mode):
        self.lang = lang
        self.mode = mode
        self.ventana_tam = ventana.winfo_width()

        self.canvas = tk.Canvas(ventana)
        self.canvas.grid(row=0, column=0, rowspan=4, columnspan=3, sticky="nsew")

        self.scroll = tk.Scrollbar(ventana, orient="vertical", command=self.canvas.yview)
        self.scroll.grid(row=0, rowspan=3, column=3, sticky="nsw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.frame_info = tk.Frame(self.canvas)
        self.frame_info.grid_configure(sticky="nsew")
        self.canvas.create_window(((self.ventana_tam/2)-15, 0), window=self.frame_info, anchor="n")
        self.frame_info.bind("<Configure>", self.on_frame_configure)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.img_encabezado = self.cargar_imagen("encabezado_fio")
        self.encabezado = tk.Label(self.frame_info, image=self.img_encabezado)
        self.encabezado.grid(row=0, column=0, columnspan=3, sticky="ew")
        self.titulo = tk.Label(self.frame_info, text="ESM Simulator v19", font=("Times New Roman", 24), justify="center")
        self.titulo.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.parrafo1 = tk.Text(self.frame_info, font=("Times New Roman", 14), wrap="word", height=10, width=50, borderwidth=0, relief="flat", highlightthickness=0)
        self.parrafo1.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.parrafo1.tag_add("justificado", "1.0", "end")
        self.parrafo1.tag_configure("justificado", justify="left")
        self.parrafo1.config(state=tk.DISABLED)

        self.img_logo = self.cargar_imagen("logo_esm")
        self.logo = tk.Label(self.frame_info, image=self.img_logo)
        self.logo.grid(row=2, column=2, sticky="ew")

        self.img_micro = self.cargar_imagen("micro_esm_es")
        self.micro = tk.Label(self.frame_info, image=self.img_micro)
        self.micro.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.img_isa = self.cargar_imagen("isa_esm")
        self.isa = tk.Label(self.frame_info, image=self.img_isa)
        self.isa.grid(row=3, column=2, sticky="ew")

        self.creditos = tk.Text(self.frame_info, font=("Times New Roman", 12), wrap="word", height=12, width=20, borderwidth=0, relief="flat", highlightthickness=0)
        self.creditos.grid(row=4, column=0, sticky="ew")
        self.creditos.config(state=tk.DISABLED)

        self.parrafo2 = tk.Text(self.frame_info, font=("Times New Roman", 14), wrap="word", height=10, width=50, borderwidth=0, relief="flat", highlightthickness=0)
        self.parrafo2.grid(row=4, column=1, columnspan=2, sticky="ew")
        self.parrafo2.config(state=tk.DISABLED)

        self.button_frame = tk.Frame(self.frame_info)
        self.button_frame.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.boton_cerrar = tk.Button(self.button_frame, text="Cerrar", command=self.cerrar, borderwidth=0, relief="flat", highlightthickness=0)
        self.boton_cerrar.pack(side="right")
        self.boton_acerca = tk.Button(self.button_frame, text="GitHub", command=self.acerca, borderwidth=0, relief="flat", highlightthickness=0)
        self.boton_acerca.pack(side="right")
        self.boton_licencia = tk.Button(self.button_frame, text="Licencia", command=self.licencia, borderwidth=0, relief="flat", highlightthickness=0)
        self.boton_licencia.pack(side="right")
        self.boton_idioma = tk.Button(self.button_frame, text="Idioma", command=self.change_lenguaje, borderwidth=0, relief="flat", highlightthickness=0)
        self.boton_idioma.pack(side="right")

        self.frame_info.grid_rowconfigure(0, weight=1)
        self.frame_info.grid_rowconfigure(1, weight=1)
        self.frame_info.grid_rowconfigure(2, weight=1)
        self.frame_info.grid_rowconfigure(3, weight=1)
        self.frame_info.grid_rowconfigure(4, weight=1)
        self.frame_info.grid_rowconfigure(5, weight=1)
        self.frame_info.grid_columnconfigure(0, weight=1)
        self.frame_info.grid_columnconfigure(1, weight=1)
        self.frame_info.grid_columnconfigure(2, weight=1)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.create_window(((self.ventana_tam/2)-15, 0), window=self.frame_info, anchor="n")
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def cargar_imagen(self, nombre_base):
        archivo = f"./img/{nombre_base}_O.png" if self.mode == "dark" else f"./img/{nombre_base}.png"
        try:
            return tk.PhotoImage(file=archivo)
        except Exception as e:
            print(f"Error al cargar imagen: {archivo} → {e}")
            return None

    def tema(self):
        self.img_encabezado = self.cargar_imagen("encabezado_fio")
        self.encabezado.config(image=self.img_encabezado)
        self.img_logo = self.cargar_imagen("logo_esm")
        self.logo.config(image=self.img_logo)
        self.img_micro = self.cargar_imagen("micro_esm_es")
        self.micro.config(image=self.img_micro)
        self.img_isa = self.cargar_imagen("isa_esm")
        self.isa.config(image=self.img_isa)

        if self.mode == "light":
            bg_color = "white"
            text_color = "black"
        else:
            bg_color = "black"
            text_color = "white"

        self.canvas.config(bg=bg_color)
        self.frame_info.config(bg=bg_color)
        self.titulo.config(bg="#012940", fg="white")
        self.parrafo1.config(bg=bg_color, fg=text_color)
        self.parrafo2.config(bg=bg_color, fg=text_color)
        self.logo.config(bg=bg_color)
        self.micro.config(bg=bg_color)
        self.isa.config(bg=bg_color)
        self.creditos.config(bg=bg_color, fg=text_color)
        self.button_frame.config(bg="#012940")
        self.boton_idioma.config(bg="#012940", fg="white")
        self.boton_licencia.config(bg="#012940", fg="white")
        self.boton_acerca.config(bg="#012940", fg="white")
        self.boton_cerrar.config(bg="#012940", fg="white")

    def change_lenguaje(self):
        self.limpiar()
        if self.lang == "es":
            self.lang = "en"
        else:
            self.lang = "es"
        self.lenguaje()
    def limpiar(self):
        self.parrafo1.config(state=tk.NORMAL)
        self.creditos.config(state=tk.NORMAL)
        self.parrafo2.config(state=tk.NORMAL)
        self.parrafo1.delete(1.0,tk.END)
        self.creditos.delete(1.0,tk.END)
        self.parrafo2.delete(1.0,tk.END)
    def lenguaje(self):
        if self.lang == "es":
            self.parrafo1.insert(tk.END, "ESM Simulator es una herramienta educativa de código abierto desarrollada\n"
                                        "en Python, Yacc y Lex, basada en la arquitectura de conjunto de instrucciones\n"
                                        "(ISA) de la Educational Simplified Machine (ESM). Su propósito principal es\n"
                                        "facilitar el aprendizaje y la enseñanza de la programación en lenguaje ensamblador,\n"
                                        "proporcionando un entorno interactivo e intuitivo para el desarrollo, prueba y\n"
                                        "traducción de código assembly. Este simulador ha sido diseñado específicamente\n"
                                        "para su uso en el ámbito académico de la Carrera de Ingeniería en Computación de\n"
                                        "la FIO-UNaM, contribuyendo al desarrollo de competencias en arquitectura de\n"
                                        "computadoras y programación de bajo nivel.")
            self.parrafo1.tag_add("n1", "1.0", "1.14")  # Aplica negrita a "ESM Simulator"
            self.parrafo1.tag_configure("n1", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n2","1.46","1.60")
            self.parrafo1.tag_configure("n2", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n3", "2.3", "2.22")
            self.parrafo1.tag_configure("n3", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n4", "2.36", "3.50")
            self.parrafo1.tag_configure("n4", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n5", "7.41", "8.11")
            self.parrafo1.tag_configure("n5", font=("Times New Roman", 14, "bold"))
            self.parrafo1.config(state=tk.DISABLED)

            self.creditos.insert(tk.END, "Equipo de Desarrollo:\n"
                                        "       CRUZ, Thiago Agustín\n"
                                        "   cruzthiagoagustin664@gmail.com\n\n"
                                        "       RYBERG, Brian Ezequiel\n"
                                        "   ryberg.brian2@gmail.com\n\n"
                                        "       MEIER, Jonathan Cristian\n"
                                        "   jonny.meier26@gmail.com\n\n"
                                        "En caso de cualquier bug, contactar con algún desarrollador\n"
                                        "detallando el problema para poder solucionarlo. Gracias.")
            self.creditos.tag_add("negrita", "1.0", "1.21")  # Aplica negrita a "Equipo de Desarrollo:"
            self.creditos.tag_configure("negrita", font=("Times New Roman", 14, "bold"))
            self.creditos.tag_add("tcruz", "2.0", "2.11")  # Aplica negrita a "CRUZ, Thiago Agustín"
            self.creditos.tag_configure("tcruz", font=("Times New Roman", 12, "bold"))
            self.creditos.tag_add("bryberg", "5.0", "5.13")
            self.creditos.tag_configure("bryberg", font=("Times New Roman", 12, "bold"))
            self.creditos.tag_add("jmeir", "8.0", "8.11")
            self.creditos.tag_configure("jmeir", font=("Times New Roman", 12, "bold"))
            self.creditos.tag_add("contacto", "10.0", tk.END)
            self.creditos.tag_configure("contacto", font=("Times New Roman", 10))
            self.creditos.config(state=tk.DISABLED)

            self.parrafo2.insert(tk.END, "La microarquitectura ESM y su correspondiente ISA fueron desarrolladas\n"
                                        "por la cátedra de Fundamentos de Informática de la Facultad de Ingeniería de\n"
                                        "Oberá (FIO-UNaM) como una alternativa simplificada a la LC-3 de Yale Patt. Su\n"
                                        "propósito no es reemplazar a la LC-3, sino servir como un primer escalón en el\n"
                                        "proceso de enseñanza, facilitando la comprensión progresiva de los conceptos\n"
                                        "fundamentales de arquitectura de computadoras y programación en ensamblador.\n\n"
                                        "Mas información:\n"
                                        "https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing")
            self.parrafo2.tag_add("n1", "1.3", "1.27")
            self.parrafo2.tag_configure("n1", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n2", "1.49", "1.52")
            self.parrafo2.tag_configure("n2", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n3","2.7","2.44")
            self.parrafo2.tag_configure("n3", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n4", "2.55", "3.16")
            self.parrafo2.tag_configure("n4", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n5", "3.56", "3.73")
            self.parrafo2.tag_configure("n5", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n6", "4.32", "4.36")
            self.parrafo2.tag_configure("n6", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("info", "8.0", "8.16")
            self.parrafo2.tag_configure("info", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("link", "9.0", tk.END)
            self.parrafo2.tag_configure("link", font=("Times New Roman", 12, "underline"))
            self.parrafo2.tag_bind("link","<Button 1>",)
            self.parrafo2.config(state=tk.DISABLED)

            self.boton_cerrar.config(text="Cerrar")
            self.boton_licencia.config(text="Licencia")
            self.boton_idioma.config(text="Idioma")
        else:
            self.parrafo1.insert(tk.END, "ESM Simulator is an open-source educational tool developed in Python, Yacc, and \n"
                                        "Lex, based on the Instruction Set Architecture (ISA) of the Educational Simplified \n"
                                        "Machine (ESM). Its main purpose is to facilitate the learning and teaching \n"
                                        "of assembly language programming by providing an interactive and intuitive \n"
                                        "environment for the development, testing, and translation of assembly code. This \n"
                                        "simulator has been specifically designed for academic use in the Computer \n"
                                        "Engineering program at FIO-UNaM, contributing to the development of skills in \n"
                                        "computer architecture, low-level programming, and fostering a deeper understanding \n"
                                        "of computational systems.")
            self.parrafo1.tag_add("n1", "1.0", "1.13")  # Aplica negrita a "ESM Simulator"
            self.parrafo1.tag_configure("n1", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n2", "1.62", "2.3")
            self.parrafo1.tag_configure("n2", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n3", "2.18", "2.52")
            self.parrafo1.tag_configure("n3", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n4", "2.60", "3.20")
            self.parrafo1.tag_configure("n4", font=("Times New Roman", 14, "bold"))
            self.parrafo1.tag_add("n5", "6.65", "7.31")
            self.parrafo1.tag_configure("n5", font=("Times New Roman", 14, "bold"))
            self.parrafo1.config(state=tk.DISABLED)

            self.creditos.insert(tk.END, "Development Team:\n"
                                        "       CRUZ, Thiago Agustín\n"
                                        "   cruzthiagoagustin664@gmail.com\n\n"
                                        "       RYBERG, Brian Ezequiel\n"
                                        "   ryberg.brian2@gmail.com\n\n"
                                        "       MEIER, Jonathan Cristian\n"
                                        "   jonny.meier26@gmail.com\n\n"
                                        "In case of any bugs, please contact a developer with details\n"
                                        "about the issue so it can be resolved. Thank you.")
            self.creditos.tag_add("negrita", "1.0", "1.21")  # Aplica negrita a "Equipo de Desarrollo:"
            self.creditos.tag_configure("negrita", font=("Times New Roman", 14, "bold"))
            self.creditos.tag_add("tcruz", "2.0", "2.11")  # Aplica negrita a "CRUZ, Thiago Agustín"
            self.creditos.tag_configure("tcruz", font=("Times New Roman", 12, "bold"))
            self.creditos.tag_add("bryberg", "5.0", "5.13")
            self.creditos.tag_configure("bryberg", font=("Times New Roman", 12, "bold"))
            self.creditos.tag_add("jmeir", "8.0", "8.11")
            self.creditos.tag_configure("jmeir", font=("Times New Roman", 12, "bold"))
            self.creditos.tag_add("contacto", "10.0", tk.END)
            self.creditos.tag_configure("contacto", font=("Times New Roman", 10))
            self.creditos.config(state=tk.DISABLED)

            self.parrafo2.insert(tk.END, "The ESMx16 microarchitecture and its corresponding ISA were developed by the\n"
                                        "Fundamentals of Informatics department at the Faculty of Engineering in Oberá\n"
                                        "(FIO-UNaM) as a simplified alternative to Yale Patt’s LC-3. Its purpose is not\n"
                                        "to replace LC-3 but rather to serve as an introductory step in the teaching\n"
                                        "process, making it easier to progressively understand the fundamental concepts\n"
                                        "of computer architecture and assembly programming.\n\n"
                                        "More information:\n"
                                        "https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing")
            self.parrafo2.tag_add("n1", "1.4", "1.28")
            self.parrafo2.tag_configure("n1", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n2", "1.51", "1.54")
            self.parrafo2.tag_configure("n2", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n3", "2.0", "2.38")
            self.parrafo2.tag_configure("n3", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n4", "2.46", "3.10")
            self.parrafo2.tag_configure("n4", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n5", "3.42", "3.58")
            self.parrafo2.tag_configure("n5", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("n6", "4.11", "4.15")
            self.parrafo2.tag_configure("n6", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("info", "8.0", "8.16")
            self.parrafo2.tag_configure("info", font=("Times New Roman", 14, "bold"))
            self.parrafo2.tag_add("link", "9.0", tk.END)
            self.parrafo2.tag_configure("link", font=("Times New Roman", 12, "underline"))
            self.parrafo2.tag_bind("link","<Button 1>",self.open_pdf)
            self.parrafo2.config(state=tk.DISABLED)

            self.boton_cerrar.config(text="Close")
            self.boton_licencia.config(text="License")
            self.boton_idioma.config(text="Language")

    def open_pdf(self,event):
        webbrowser.open("https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing")
    def licencia(self):
        webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.html")
    def acerca(self):
        webbrowser.open_new("https://github.com/thiagocruz664/ESM-Simulator")
    def cerrar(self):
        self.frame_info.destroy()
        self.canvas.destroy()
        self.scroll.destroy()
