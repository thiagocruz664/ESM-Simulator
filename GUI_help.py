#    ESM Simulator its a GUI for programing in assmbly of the ESMx16 ISA

#    Copyright © 2025 Cruz Thiago, Ryberg Brian, Meier Jonathan.

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

import tkinter as tk


class Ayuda:
    """Vista de ayuda integrada del simulador ESMx16."""

    def __init__(self, ventana, lang, mode):
        self.lang = lang
        self.mode = mode

        self.frame_ayuda = tk.Frame(ventana)
        self.frame_ayuda.grid(
            row=0, column=0, rowspan=4, columnspan=3, sticky="nsew"
        )
        self.frame_ayuda.grid_rowconfigure(1, weight=1)
        self.frame_ayuda.grid_columnconfigure(0, weight=1)

        self.encabezado = tk.Frame(self.frame_ayuda)
        self.encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.encabezado.grid_columnconfigure(0, weight=1)

        self.titulo = tk.Label(
            self.encabezado,
            text="Ayuda de ESM Simulator",
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
        self.boton_idioma.grid(row=0, column=1, padx=(4, 8))

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
        self.boton_cerrar.grid(row=0, column=2, padx=(4, 16))

        self.contenido = tk.Text(
            self.frame_ayuda,
            wrap="word",
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            padx=28,
            pady=20,
            spacing1=2,
            spacing3=7,
        )
        self.contenido.grid(row=1, column=0, sticky="nsew")

        self.scroll = tk.Scrollbar(
            self.frame_ayuda,
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
            "subseccion", font=("Arial", 12, "bold"), spacing1=8, spacing3=4
        )
        self.contenido.tag_configure(
            "texto", font=("Arial", 11), lmargin1=8, lmargin2=8
        )
        self.contenido.tag_configure(
            "codigo",
            font=("Courier New", 11),
            lmargin1=22,
            lmargin2=22,
            rmargin=18,
            spacing1=8,
            spacing3=10,
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

        self.lenguaje()

    def _agregar(self, texto, etiqueta="texto"):
        self.contenido.insert(tk.END, texto, etiqueta)

    def lenguaje(self):
        self.contenido.config(state=tk.NORMAL)
        self.contenido.delete("1.0", tk.END)

        if self.lang == "es":
            self.titulo.config(text="Ayuda de ESM Simulator")
            self.boton_cerrar.config(text="Cerrar")
            self.boton_idioma.config(text="English")
            self._contenido_espanol()
        else:
            self.titulo.config(text="ESM Simulator Help")
            self.boton_cerrar.config(text="Close")
            self.boton_idioma.config(text="Español")
            self._contenido_ingles()

        self.contenido.config(state=tk.DISABLED)
        self.contenido.yview_moveto(0)

    def _contenido_espanol(self):
        self._agregar(
            "Esta guía resume el uso del simulador y la sintaxis aceptada por "
            "la ISA ESMx16. Los dos programas principales están adaptados de "
            "los ejemplos del paper Proyecto UMUx16.\n",
            "intro",
        )

        self._agregar("Flujo de trabajo\n", "seccion")
        self._agregar(
            "• Escriba o abra un programa.\n"
            "• Presione Ensamblar para validar el código y cargar la memoria.\n"
            "• Use ▶ para ejecutar de forma continua o ↩ para avanzar una instrucción.\n"
            "• Use ↻ para reiniciar el procesador y limpiar la memoria ensamblada.\n"
            "• Puede guardar también el codigo ensamblado en binario o hexadecimal.\n"
        )

        self._agregar("Estructura mínima\n", "seccion")
        self._agregar(
            ".ORIG define la primera dirección del programa y .END lo finaliza. "
            "Ambas directivas son obligatorias para código assembly.\n"
        )
        self._agregar(
            ".ORIG x3000\n"
            "ADD #1\n"
            ".END\n",
            "codigo",
        )
        self._agregar(
            "Los comentarios de línea comienzan con // . También puede separar "
            "instrucciones mediante punto y coma.\n",
            "nota",
        )

        self._agregar("Instrucciones\n", "seccion")
        self._agregar(
            "ADD #n / ADD ETQ     Suma al acumulador un inmediato o una palabra de memoria.\n"
            "AND #n / AND ETQ     Realiza AND bit a bit.\n"
            "NOTA ETQ             Niega bit a bit una palabra de memoria.\n"
            "NOTB                 Niega bit a bit el acumulador.\n"
            "LD ETQ               Carga una palabra de memoria en el acumulador.\n"
            "ST ETQ               Guarda el acumulador en memoria.\n"
            "BRn/BRz/BRp ETQ      Salta según N, Z o P; las flags pueden combinarse.\n"
            "TRAP x23             Lee un carácter y lo guarda en el acumulador.\n"
            "TRAP x21             Muestra el carácter contenido en el acumulador.\n",
            "codigo",
        )
        self._agregar(
            "Los inmediatos de ADD, AND, LD y ST admiten de -2048 a 2047. "
            "El desplazamiento de BR admite de -512 a 511.\n",
            "nota",
        )

        self._agregar("Directivas y etiquetas\n", "seccion")
        self._agregar(
            ".FILL #n reserva una palabra inicializada y puede escribirse con "
            "o sin etiqueta previa; n debe estar entre -32768 y 32767. "
            ".BLKW reserva una palabra sin inicializar.\n"
        )
        self._agregar(
            "Las etiquetas se escriben al comienzo de la línea, en mayúsculas, "
            "y se separan de la instrucción con al menos un espacio. Las etiquetas "
            "de una letra, como I, L y K, son válidas. No use como etiqueta el "
            "nombre exacto de una instrucción o directiva reservada.\n"
        )
        self._agregar(
            "I .BLKW\n"
            "K .FILL #3\n"
            "L ADD #-1\n"
            "BRp L\n",
            "codigo",
        )

        self._agregar("Entrada y salida con TRAPs\n", "seccion")
        self._agregar(
            "TRAP x23 (IN)\n"
            "Lee un carácter ingresado por la consola y lo almacena en el "
            "registro acumulador. Esta instrucción también puede "
            "referenciarse mediante el mnemónico IN.\n"
        )
        self._agregar(
            "TRAP x21 (OUT)\n"
            "Imprime en la consola el contenido del registro acumulador. "
            "Esta instrucción también puede referenciarse mediante el "
            "mnemónico OUT.\n"
        )
        self._agregar(
            ".ORIG x3000\n"
            "TRAP x23\n"
            "TRAP x21\n"
            ".END\n",
            "codigo",
        )

        self._agregar("Ejemplo: OR entre X e Y\n", "seccion")
        self._agregar(
            "El programa aplica De Morgan: (X' AND Y')'. El resultado se guarda en R.\n"
        )
        self._agregar(
            ".ORIG x0000\n"
            "NOTA X\n"
            "ST X\n"
            "NOTA Y\n"
            "AND X\n"
            "NOTB\n"
            "ST R\n"
            "X .FILL #10\n"
            "Y .FILL #18\n"
            "R .BLKW\n"
            ".END\n",
            "codigo",
        )

        self._agregar("Ejemplo: Multiplicación\n", "seccion")
        self._agregar(
            "Multiplica X por Y mediante sumas repetidas y deja el resultado en R.\n"
        )
        self._agregar(
            ".ORIG x3000\n"
            "LD Y\n"
            "ST CONT\n"
            "ACC LD X\n"
            "ADD R\n"
            "ST R\n"
            "LD CONT\n"
            "ADD #-1\n"
            "ST CONT\n"
            "BRp ACC\n"
            "X .FILL #5\n"
            "Y .FILL #3\n"
            "CONT .FILL #0\n"
            "R .FILL #0\n"
            ".END\n",
            "codigo",
        )

    def _contenido_ingles(self):
        self._agregar(
            "This guide summarizes simulator usage and the syntax accepted by "
            "the ESMx16 ISA. The two main programs are adapted from the examples "
            "in the Proyecto UMUx16 paper.\n",
            "intro",
        )

        self._agregar("Workflow\n", "seccion")
        self._agregar(
            "• Write or open a program.\n"
            "• Press Assemble to validate the source and load memory.\n"
            "• Use ▶ to run continuously or ↩ to execute one instruction.\n"
            "• Use ↻ to reset the processor and assembled memory.\n"
            "• The resulting assembled code can be saved as binary or hexadecimal.\n"
        )

        self._agregar("Minimum structure\n", "seccion")
        self._agregar(
            ".ORIG defines the first program address and .END terminates it. "
            "Both directives are required for assembly source.\n"
        )
        self._agregar(".ORIG x3000\nADD #1\n.END\n", "codigo")
        self._agregar(
            "Line comments start with // . A semicolon can also separate instructions.\n",
            "nota",
        )

        self._agregar("Instructions\n", "seccion")
        self._agregar(
            "ADD #n / ADD LABEL   Add an immediate or memory word to the accumulator.\n"
            "AND #n / AND LABEL   Perform a bitwise AND.\n"
            "NOTA LABEL           Negate a memory word bit by bit.\n"
            "NOTB                 Negate the accumulator bit by bit.\n"
            "LD LABEL             Load a memory word into the accumulator.\n"
            "ST LABEL             Store the accumulator in memory.\n"
            "BRn/BRz/BRp LABEL    Branch on N, Z or P; flags may be combined.\n"
            "TRAP x23             Read one character into the accumulator.\n"
            "TRAP x21             Display the character held in the accumulator.\n",
            "codigo",
        )
        self._agregar(
            "ADD, AND, LD and ST immediates range from -2048 to 2047. "
            "BR offsets range from -512 to 511.\n",
            "nota",
        )

        self._agregar("Directives and labels\n", "seccion")
        self._agregar(
            ".FILL #n reserves an initialized word and may be written with or "
            "without a preceding label; n must be between -32768 and 32767. "
            ".BLKW reserves one uninitialized word.\n"
        )
        self._agregar(
            "Labels appear at the beginning of a line, use uppercase letters, "
            "and must be separated from the instruction by whitespace. Single-letter "
            "labels such as I, L and K are valid. Do not use an exact instruction or "
            "directive name as a label.\n"
        )
        self._agregar("I .BLKW\nK .FILL #3\nL ADD #-1\nBRp L\n", "codigo")

        self._agregar("Input and output with TRAPs\n", "seccion")
        self._agregar(
            "TRAP x23 (IN)\n"
            "Reads a character entered from the console and stores it in the "
            "accumulator register. This instruction can also be referenced "
            "using the mnemonic IN.\n"
        )
        self._agregar(
            "TRAP x21 (OUT)\n"
            "Prints the contents of the accumulator register to the console. "
            "This instruction can also be referenced using the mnemonic OUT.\n"
        )
        self._agregar(
            ".ORIG x3000\n"
            "TRAP x23\n"
            "TRAP x21\n"
            ".END\n",
            "codigo",
        )
        
        self._agregar("Example: OR between X and Y\n", "seccion")
        self._agregar(
            "The program applies De Morgan's law: (X' AND Y')'. The result is stored in R.\n"
        )
        self._agregar(
            ".ORIG x0000\n"
            "NOTA X\n"
            "ST X\n"
            "NOTA Y\n"
            "AND X\n"
            "NOTB\n"
            "ST R\n"
            "X .FILL #10\n"
            "Y .FILL #18\n"
            "R .BLKW\n"
            ".END\n",
            "codigo",
        )

        self._agregar("Example: Multiplication\n", "seccion")
        self._agregar(
            "This program multiplies X by Y with repeated addition and leaves the result in R.\n"
        )
        self._agregar(
            ".ORIG x3000\n"
            "LD Y\n"
            "ST CONT\n"
            "ACC LD X\n"
            "ADD R\n"
            "ST R\n"
            "LD CONT\n"
            "ADD #-1\n"
            "ST CONT\n"
            "BRp ACC\n"
            "X .FILL #5\n"
            "Y .FILL #3\n"
            "CONT .FILL #0\n"
            "R .FILL #0\n"
            ".END\n",
            "codigo",
        )

    def tema(self):
        if self.mode == "dark":
            fondo = "#1E1E1E"
            texto = "#EAEAEA"
            encabezado = "#012940"
            codigo = "#2A2A2A"
            acento = "#7FD7FF"
            nota = "#B9C7D0"
            boton = "#164A63"
        else:
            fondo = "#FFFFFF"
            texto = "#1B1B1B"
            encabezado = "#012940"
            codigo = "#F1F4F6"
            acento = "#005A84"
            nota = "#425563"
            boton = "#E4EEF3"

        self.frame_ayuda.config(bg=fondo)
        self.encabezado.config(bg=encabezado)
        self.titulo.config(bg=encabezado, fg="white")
        self.contenido.config(bg=fondo, fg=texto, insertbackground=texto)
        self.contenido.tag_configure("seccion", foreground=acento)
        self.contenido.tag_configure("subseccion", foreground=acento)
        self.contenido.tag_configure("codigo", background=codigo, foreground=texto)
        self.contenido.tag_configure("nota", foreground=nota)
        self.scroll.config(bg=codigo, troughcolor=fondo)

        color_boton_texto = "white" if self.mode == "dark" else "#012940"
        for boton_widget in (self.boton_idioma, self.boton_cerrar):
            boton_widget.config(
                bg=boton,
                fg=color_boton_texto,
                activebackground=acento,
                activeforeground="white",
            )

    def change_lenguaje(self):
        self.lang = "en" if self.lang == "es" else "es"
        self.lenguaje()

    def cerrar(self):
        self.frame_ayuda.destroy()
