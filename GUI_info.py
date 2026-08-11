#    ESM Simulator its a GUI for programing in assmbly of the ESMx16 ISA

#    Copyright © 2025 Cruz Thiago, Ryberg Brian, Meier Jonathan.

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

import tkinter as tk
import webbrowser


class Informacion:
    """Vista de información con el mismo formato de la pestaña Ayuda."""

    def __init__(self, ventana, lang, mode):
        self.lang = lang
        self.mode = mode

        self.frame_info = tk.Frame(ventana)
        self.frame_info.grid(
            row=0, column=0, rowspan=4, columnspan=3, sticky="nsew"
        )
        self.frame_info.grid_rowconfigure(1, weight=1)
        self.frame_info.grid_columnconfigure(0, weight=1)

        self.encabezado = tk.Frame(self.frame_info)
        self.encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.encabezado.grid_columnconfigure(0, weight=1)

        self.titulo = tk.Label(
            self.encabezado,
            text="Información de ESM Simulator",
            font=("Arial", 20, "bold"),
            anchor="w",
            padx=20,
            pady=14,
        )
        self.titulo.grid(row=0, column=0, sticky="ew")

        self.boton_idioma = tk.Button(
            self.encabezado,
            text="English",
            command=self.change_lenguaje,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=8,
        )
        self.boton_idioma.grid(row=0, column=1, padx=(4, 4))

        self.boton_licencia = tk.Button(
            self.encabezado,
            text="Licencia",
            command=self.licencia,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=8,
        )
        self.boton_licencia.grid(row=0, column=2, padx=4)

        self.boton_acerca = tk.Button(
            self.encabezado,
            text="GitHub",
            command=self.acerca,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=8,
        )
        self.boton_acerca.grid(row=0, column=3, padx=4)

        self.boton_cerrar = tk.Button(
            self.encabezado,
            text="Cerrar",
            command=self.cerrar,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=8,
        )
        self.boton_cerrar.grid(row=0, column=4, padx=(4, 16))

        self.contenido = tk.Text(
            self.frame_info,
            wrap="word",
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padx=28,
            pady=20,
            spacing1=2,
            spacing3=7,
            cursor="arrow",
        )
        self.contenido.grid(row=1, column=0, sticky="nsew")

        self.scroll = tk.Scrollbar(
            self.frame_info,
            orient="vertical",
            command=self.contenido.yview,
        )
        self.scroll.grid(row=1, column=1, sticky="ns")
        self.contenido.configure(yscrollcommand=self.scroll.set)

        self.contenido.tag_configure(
            "intro", font=("Arial", 12), spacing3=12
        )
        self.contenido.tag_configure(
            "seccion", font=("Arial", 15, "bold"), spacing1=14, spacing3=7
        )
        self.contenido.tag_configure(
            "texto", font=("Arial", 11), lmargin1=8, lmargin2=8
        )
        self.contenido.tag_configure(
            "creditos",
            font=("Arial", 11),
            lmargin1=22,
            lmargin2=22,
            spacing1=5,
            spacing3=8,
        )
        self.contenido.tag_configure(
            "nota",
            font=("Arial", 11, "italic"),
            lmargin1=18,
            lmargin2=18,
            rmargin=18,
            spacing1=6,
            spacing3=10,
        )
        self.contenido.tag_configure(
            "link", font=("Arial", 11, "underline"), lmargin1=8, lmargin2=8
        )
        self.contenido.tag_configure("imagen", justify="center", spacing1=8, spacing3=12)
        self.contenido.tag_bind("link", "<Button-1>", self.open_pdf)

        self._cargar_imagenes()
        self.lenguaje()

    def cargar_imagen(self, nombre_base):
        # Se conservan las mismas rutas de imágenes de la pestaña original.
        if nombre_base == "micro_esm_isa_es":
            archivo = (
                f"./img/{nombre_base}_O.png"
                if self.mode == "dark"
                else f"./img/{nombre_base}.png"
            )
        else:
            archivo = f"./img/{nombre_base}.png"
        try:
            return tk.PhotoImage(file=archivo)
        except (FileNotFoundError, OSError, tk.TclError) as e:
            print(f"Error al cargar imagen: {archivo} → {e}")
            return None

    def _cargar_imagenes(self):
        self.img_encabezado = self.cargar_imagen("encabezado_fio")
        self.img_logo = self.cargar_imagen("logo_esm")
        self.img_micro = self.cargar_imagen("micro_esm_isa_es")

    def _agregar(self, texto, etiqueta="texto"):
        self.contenido.insert(tk.END, texto, etiqueta)

    def _agregar_imagen(
        self,
        imagen,
        justificado="center",
        ancho=None,
        alto=None,
        unidad="px",
        alineacion="baseline",
        mantener_proporcion=True
    ):
        if imagen is None:
            return

        # ---------------------------------------------------------
        # Tamaño original
        # ---------------------------------------------------------
        ancho_original = imagen.width()
        alto_original = imagen.height()

        # ---------------------------------------------------------
        # Calcular tamaño
        # ---------------------------------------------------------
        if unidad == "%":
            # Obtener el ancho disponible del Text
            ancho_disponible = self.contenido.winfo_width()

            # Si todavía no fue dibujado, usar reqwidth
            if ancho_disponible <= 1:
                ancho_disponible = self.contenido.winfo_reqwidth()

            # El porcentaje se aplica al ancho disponible
            if ancho is not None:
                ancho = int(ancho_disponible * ancho / 100)

            if alto is not None:
                alto = int(alto_original * alto / 100)

        elif unidad != "px":
            raise ValueError("La unidad debe ser 'px' o '%'")

        # ---------------------------------------------------------
        # Si no se especificó ancho, conservar el original
        # ---------------------------------------------------------
        if ancho is None:
            ancho = ancho_original

        # ---------------------------------------------------------
        # Mantener relación de aspecto
        # ---------------------------------------------------------
        if mantener_proporcion:

            # El ancho es el tamaño principal.
            # El alto se calcula automáticamente.
            alto = int(alto_original * (ancho / ancho_original))

        else:
            # Si no se mantiene la proporción, usamos el alto indicado.
            if alto is None:
                alto = alto_original

        # ---------------------------------------------------------
        # Redimensionar imagen
        # ---------------------------------------------------------
        if ancho != ancho_original or alto != alto_original:
            imagen = imagen.resize((ancho, alto), Image.Resampling.LANCZOS)

        # ---------------------------------------------------------
        # Insertar imagen
        # ---------------------------------------------------------
        inicio = self.contenido.index(tk.END)

        self.contenido.image_create(
            tk.END,
            image=imagen,
            align=alineacion
        )

        self.contenido.insert(tk.END, "\n")

        # ---------------------------------------------------------
        # Justificación horizontal
        # ---------------------------------------------------------
        self.contenido.tag_add(
            "imagen",
            inicio,
            tk.END
        )

        self.contenido.tag_configure(
            "imagen",
            justify=justificado
        )

    def _agregar_enlace(self, texto):
        self.contenido.insert(tk.END, texto, "link")

    def limpiar(self):
        self.contenido.config(state=tk.NORMAL)
        self.contenido.delete("1.0", tk.END)

    def lenguaje(self):
        self.limpiar()
        if self.lang == "es":
            self.titulo.config(text="Información de ESM Simulator")
            self.boton_cerrar.config(text="Cerrar")
            self.boton_licencia.config(text="Licencia")
            self.boton_idioma.config(text="English")
            self._contenido_espanol()
        else:
            self.titulo.config(text="About ESM Simulator")
            self.boton_cerrar.config(text="Close")
            self.boton_licencia.config(text="License")
            self.boton_idioma.config(text="Español")
            self._contenido_ingles()

        self.contenido.config(state=tk.DISABLED)
        self.contenido.yview_moveto(0)

    def _contenido_espanol(self):
        self._agregar_imagen(self.img_encabezado, justificado="center", ancho=100, unidad="%", mantener_proporcion=True)
        self._agregar("ESM Simulator v20\n", "seccion")
        self._agregar(
            "ESM Simulator es una herramienta educativa de código abierto "
            "desarrollada en Python, Yacc y Lex, basada en la arquitectura de "
            "conjunto de instrucciones (ISA) de la Educational Stack Machine x16 "
            "(ESMx16). Su propósito es facilitar el aprendizaje y la enseñanza "
            "de la programación en lenguaje ensamblador mediante un entorno "
            "interactivo para desarrollar, probar y traducir código assembly.\n",
            "intro",
        )
        self._agregar_imagen(self.img_logo, justificado="center", ancho=100, unidad="%", mantener_proporcion=True)

        self._agregar("Propósito académico\n", "seccion")
        self._agregar(
            "El simulador fue diseñado para el ámbito académico de la Carrera "
            "de Ingeniería en Computación de la FIO-UNaM. Contribuye al desarrollo "
            "de competencias en arquitectura de computadoras, programación de "
            "bajo nivel y comprensión de sistemas computacionales.\n"
        )

        self._agregar("Microarquitectura e ISA ESMx16\n", "seccion")
        self._agregar(
            "La microarquitectura ESMx16 y su ISA fueron desarrolladas por la "
            "cátedra de Fundamentos de Informática de la Facultad de Ingeniería "
            "de Oberá (FIO-UNaM) como una alternativa simplificada a la LC-3 de "
            "Yale Patt. No buscan reemplazarla, sino ofrecer un primer escalón "
            "para comprender progresivamente la arquitectura de computadoras y "
            "la programación en ensamblador.\n"
        )
        self._agregar_imagen(self.img_micro, justificado="center", ancho=1000, unidad="px", mantener_proporcion=True)

        self._agregar("Equipo de desarrollo\n", "seccion")
        self._agregar(
            "CRUZ, Thiago Agustín\n"
            "cruzthiagoagustin664@gmail.com\n\n"
            "RYBERG, Brian Ezequiel\n"
            "ryberg.brian2@gmail.com\n\n"
            "MEIER, Jonathan Cristian\n"
            "jonny.meier26@gmail.com\n",
            "creditos",
        )
        self._agregar(
            "Ante cualquier error, contacte a uno de los desarrolladores e "
            "incluya una descripción del problema para facilitar su corrección.\n",
            "nota",
        )

        self._agregar("Más información\n", "seccion")
        self._agregar_enlace(
            "Proyecto UMUx16\n"
            "https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing\n"
        )

    def _contenido_ingles(self):
        self._agregar_imagen(self.img_encabezado, justificado="center", ancho=100, unidad="%", mantener_proporcion=True)
        self._agregar("ESM Simulator v20\n", "seccion")
        self._agregar(
            "ESM Simulator is an open-source educational tool developed in "
            "Python, Yacc and Lex. It is based on the Instruction Set Architecture "
            "(ISA) of the Educational Stack Machine x16 (ESMx16). Its purpose is "
            "to support the learning and teaching of assembly language programming "
            "through an interactive environment for writing, testing and translating "
            "assembly code.\n",
            "intro",
        )
        self._agregar_imagen(self.img_logo, justificado="center", ancho=100, unidad="%", mantener_proporcion=True)

        self._agregar("Academic purpose\n", "seccion")
        self._agregar(
            "The simulator was designed for academic use in the Computer Engineering "
            "program at FIO-UNaM. It supports the development of skills in computer "
            "architecture, low-level programming and computational systems.\n"
        )

        self._agregar("ESMx16 microarchitecture and ISA\n", "seccion")
        self._agregar(
            "The ESMx16 microarchitecture and ISA were developed by the Fundamentals "
            "of Informatics department at the Faculty of Engineering in Oberá "
            "(FIO-UNaM) as a simplified alternative to Yale Patt's LC-3. They are "
            "not intended to replace LC-3, but to provide an introductory step for "
            "understanding computer architecture and assembly programming.\n"
        )
        self._agregar_imagen(self.img_micro, justificado="center", ancho=1000, unidad="px", mantener_proporcion=True)

        self._agregar("Development team\n", "seccion")
        self._agregar(
            "CRUZ, Thiago Agustín\n"
            "cruzthiagoagustin664@gmail.com\n\n"
            "RYBERG, Brian Ezequiel\n"
            "ryberg.brian2@gmail.com\n\n"
            "MEIR, Jonathan Cristian\n"
            "jonny.meier26@gmail.com\n",
            "creditos",
        )
        self._agregar(
            "If you encounter a bug, contact one of the developers and include a "
            "description of the issue so it can be reproduced and fixed.\n",
            "nota",
        )

        self._agregar("More information\n", "seccion")
        self._agregar_enlace(
            "https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing\n"
        )

    def tema(self):
        if self.mode == "dark":
            fondo = "#1E1E1E"
            texto = "#EAEAEA"
            encabezado = "#012940"
            panel = "#2A2A2A"
            acento = "#7FD7FF"
            nota = "#B9C7D0"
            boton = "#164A63"
        else:
            fondo = "#FFFFFF"
            texto = "#1B1B1B"
            encabezado = "#012940"
            panel = "#F1F4F6"
            acento = "#005A84"
            nota = "#425563"
            boton = "#E4EEF3"

        self._cargar_imagenes()
        self.lenguaje()

        self.frame_info.config(bg=fondo)
        self.encabezado.config(bg=encabezado)
        self.titulo.config(bg=encabezado, fg="white")
        self.contenido.config(bg=fondo, fg=texto, insertbackground=texto)
        self.contenido.tag_configure("seccion", foreground=acento)
        self.contenido.tag_configure("creditos", background=panel, foreground=texto)
        self.contenido.tag_configure("nota", foreground=nota)
        self.contenido.tag_configure("link", foreground=acento)
        self.scroll.config(bg=panel, troughcolor=fondo)

        color_boton_texto = "white" if self.mode == "dark" else "#012940"
        for boton_widget in (
            self.boton_idioma,
            self.boton_licencia,
            self.boton_acerca,
            self.boton_cerrar,
        ):
            boton_widget.config(
                bg=boton,
                fg=color_boton_texto,
                activebackground=acento,
                activeforeground="white",
            )

    def change_lenguaje(self):
        self.lang = "en" if self.lang == "es" else "es"
        self.lenguaje()

    def open_pdf(self, _event=None):
        webbrowser.open(
            "https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing"
        )

    def licencia(self):
        webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.html")

    def acerca(self):
        webbrowser.open_new("https://github.com/thiagocruz664/ESM-Simulator")

    def cerrar(self):
        self.frame_info.destroy()
