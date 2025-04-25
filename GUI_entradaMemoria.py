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
    def __init__(self,ventana,guardar,abrir,mensaje):
        self.ventana = ventana
        self.guardar = guardar
        self.abrir = abrir
        self.archivo = False
        self.mensaje = mensaje
        self.frame_principal = tk.Frame(self.ventana)
        self.frame_principal.grid(row=1,column=0,padx=0,pady=0,sticky="nw")
        self.code_title = tk.Label(self.frame_principal,text="untitled.txt")
        self.code_title.grid(row=0,column=0,padx=15,pady=5,sticky="nw")
        self.code_editor = tk.Text(self.frame_principal,width=80, undo=True)  # Habilitar la opción de deshacer
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

    def deshacer(self, event=None):
        self.mensaje("Ctrl + Z")
        try:
            self.code_editor.edit_undo()
        except tk.TclError:
            self.abrir()
    def on_modified(self, event=None):
        if not self.archivo:
            self.code_editor.edit_separator()
            self.code_editor.edit_modified(False)
    def rehacer(self, event=None):
        self.mensaje("Ctrl + Y")
        try:
            self.code_editor.edit_redo()
        except tk.TclError:
            pass  # Ignorar el error si no hay nada que rehacer

    def tema(self,theme):
        self.frame_principal.configure(bg=theme["bg"])
        self.code_title.configure(bg=theme["bg"],fg=theme["fg"])
        self.code_editor.configure(bg=theme["entry_bg"],fg=theme["entry_fg"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"],insertbackground=theme["menu_fg"])
        self.scrollbar.configure(bg=theme["scroll_bg"],troughcolor=theme["scroll_fg"],activebackground=theme["scroll_active"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"])
    def lenguaje(self,lang):
        if lang == "es":
            self.code_title.config(text="sin_nombre.txt")
        if lang =="en":
            self.code_title.config(text="untitled.txt")

class Memoria:
    def __init__(self,ventana,dicc,pc,ab,theme):
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
        for i in range(20):
            entry = []
            entry0 = tk.Button(self.frame_memory,text=f"  ◽ x{format(12288+i,f'04x')}",font=("Arial", 8),borderwidth=0, relief="flat",highlightthickness=0,command=lambda i=i: self.breakpoint(i))
            entry0.grid(row=i+1,column=0,padx=0,pady=0,sticky="nswe")
            entry.append(entry0)
            for f in range(4):
                entry1 = tk.Entry(self.frame_memory, state=tk.DISABLED,borderwidth=1, relief="flat", highlightthickness=0,font=("Arial", 8))
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
        self.rowup = tk.Button(self.frame_funciones,text="▲",borderwidth=0, relief="flat",highlightthickness=0,font=("Arial", 8),command=self.up)
        self.rowup.grid(row=21,column=4,padx=0,pady=0,sticky="e")
        self.rowdown = tk.Button(self.frame_funciones,text="▼",borderwidth=0, relief="flat",highlightthickness=0,font=("Arial", 8),command=self.down)
        self.rowdown.grid(row=21,column=5,padx=0,pady=0,sticky="w")
        self.pc_search = tk.Entry(self.frame_funciones, state=tk.NORMAL, highlightthickness=0,font=("Arial", 8),width=8)
        self.pc_search.grid(row=21,column=3,padx=0,pady=0,sticky="w")
        self.x_search = tk.Label(self.frame_funciones,text="x",font=("Arial", 8))
        self.x_search.grid(row=21,column=2,padx=0,pady=0,sticky="e")
        self.search = tk.Button(self.frame_funciones,text="🔍",borderwidth=0, relief="flat",highlightthickness=0,font=("Arial", 8),command=self.buscar)
        self.search.grid(row=21,column=1,padx=0,pady=0,sticky="e")
        self.seguimiento = True
        self.seguimiento_button = tk.Button(self.frame_funciones,text="🔴",borderwidth=0, relief="flat",highlightthickness=0,font=("Arial", 8),command=self.seguir)
        self.seguimiento_button.grid(row=21,column=0,padx=0,pady=0,sticky="w")

        self.frame_memory.bind("<Enter>", self.on_frame)
        self.frame_memory.bind("<Leave>", self.not_on_frame)
        self.frame_memory.bind_all("<MouseWheel>", self._on_mousewheel)
        self.frame_memory.bind_all("<Button-4>", self._on_mousewheel)
        self.frame_memory.bind_all("<Button-5>", self._on_mousewheel) 
        self.on_frame_siono = False

        self.breakpoints = []

    def tema(self,theme):
        self.theme = theme
        self.frame_memory.configure(bg=theme["bg"])
        self.memoria_title.configure(bg=theme["bg"],fg=theme["fg"])
        self.frame_funciones.configure(bg=theme["bg"])
        self.rowup.configure(bg=theme["bg"],fg=theme["fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.rowdown.configure(bg=theme["bg"],fg=theme["fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.pc_search.configure(bg=theme["entry_bg"],fg=theme["entry_fg"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"],insertbackground=theme["menu_fg"])
        self.x_search.configure(bg=theme["bg"],fg=theme["fg"])
        self.search.configure(bg=theme["bg"],fg=theme["fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
        self.seguimiento_button.configure(bg=theme["bg"],fg=theme["fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"]) 
        for i in range(20):
            linea = self.render_memory[i]
            c=0
            for entry in linea:
                if c==0:
                    entry.configure(bg=theme["bg"],fg=theme["fg"],activebackground=theme["menu_active_bg"],activeforeground=theme["menu_active_fg"])
                    c=c+1
                else:
                    if i%2==0:
                        entry.configure(disabledbackground=theme["entry_bg"], disabledforeground=theme["entry_fg"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"])
                    else:
                        entry.configure(disabledbackground=theme["menu_bg"], disabledforeground=theme["menu_fg"],highlightbackground=theme["menu_bg"],highlightcolor=theme["menu_bg"])
        if self.ensamblado:
            self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.punto_de_apoyo,False)
    def lenguaje(self,lang):
        if lang == "es":
            self.memoria_title.config(text="Memoria:")
        if lang =="en":
            self.memoria_title.config(text="Memory:")

    def breakpoint(self,i):
        if self.ab_memoria == 1:
            if self.punto_de_apoyo+i in self.breakpoints:
                self.breakpoints.remove(self.punto_de_apoyo+i)
                self.breakpoints.sort()
            else:
                self.breakpoints.append(self.punto_de_apoyo+i)
                self.breakpoints.sort()
            self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.pc_memoria,False)
    
    def on_frame(self, event):
        self.on_frame_siono = True
    def not_on_frame(self, event):
        self.on_frame_siono = False
    def _on_mousewheel(self, event):
        try:
            if self.on_frame_siono:
                if event.num == 4 or event.delta > 0:
                    self.up()
                elif event.num == 5 or event.delta < 0:
                    self.down()
        except Exception as e:
            print("Error:", e)
    def up(self):
        try:
            self.punto_de_apoyo = self.punto_de_apoyo - 1
            if(self.punto_de_apoyo<0):
                self.punto_de_apoyo = 65536 + self.punto_de_apoyo
            self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.pc_memoria,False)
        except Exception as e:
            print("Error:", e)
    def down(self):
        try:
            self.punto_de_apoyo = self.punto_de_apoyo + 1
            if (self.punto_de_apoyo>=65535):
                self.punto_de_apoyo = self.punto_de_apoyo - 65536
            self.mapear_memoria(self.diccionario_memoria,self.punto_de_apoyo,self.pc_memoria,False)
        except Exception as e:
            print("Error:", e)
    def buscar(self):
        try:
            direccion = int(self.pc_search.get(),16)
            self.punto_de_apoyo = direccion
            self.mapear_memoria(self.diccionario_memoria,direccion,self.pc_memoria,False)
        except:
            pass
    def seguir(self):
        if self.seguimiento:
            self.seguimiento = False
            self.seguimiento_button.config(text="⭕")
        else:
            self.seguimiento = True
            self.seguimiento_button.config(text="🔴")
    
    def mapear_memoria(self,diccionario,origen,pc_act,bandera_stepin_llamado=True):
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
        for i in self.render_memory:
            #fiajate aca que cuando el pc sea mayor 65535 se reincie
            if (self.punto_de_apoyo+i>65535 and diferencial==0):
                diferencial=self.punto_de_apoyo+i
            if (self.punto_de_apoyo<0):
                pass
            entry = self.render_memory[i]
            ent = entry[0]
            """if pc_act == self.punto_de_apoyo + i:
                try:
                    ent.config(text=f"  ◼️ x{hex(self.punto_de_apoyo+i)}  <- ",fg=self.theme["fg"],activeforeground=self.theme["menu_active_fg"])
                    self.breakpoints.remove(self.punto_de_apoyo+i)
                except:
                    pass
            else:"""        #Esto hace que cuando pases por un breakpoint se borre, idk how is this working in real life
            if self.punto_de_apoyo + i in self.breakpoints:
                if pc_act == self.punto_de_apoyo + i - diferencial:
                    ent.config(text=f"  ◼️ x{format(self.punto_de_apoyo+i-diferencial,f'04x').upper()}  <- ",fg="green",activeforeground="green")
                else:
                    ent.config(text=f"  ◻️ x{format(self.punto_de_apoyo+i-diferencial,f'04x').upper()}",fg="red",activeforeground="red")
            else:
                if self.pc_memoria-self.punto_de_apoyo + diferencial == i:
                    ent.config(text=f"  ◼️ x{format(self.punto_de_apoyo+i-diferencial,f'04x').upper()}  <- ",fg="green",activeforeground="green")
                else:
                    ent.config(text=f"  ◻️ x{format(self.punto_de_apoyo+i-diferencial,f'04x').upper()}",fg=self.theme["fg"],activeforeground=self.theme["menu_active_fg"])
        
            for j in range(1,5):
                ent = entry[j]
                ent.config(state=tk.NORMAL)
                ent.delete(0, tk.END)
                try:
                    if diccionario[hex(self.punto_de_apoyo+i-diferencial)][j-1] == None:
                        ent.insert(tk.END, "")
                    else:
                        ent.insert(tk.END, diccionario.get(hex(self.punto_de_apoyo+i-diferencial))[j-1])
                except:
                    pass
                ent.config(state=tk.DISABLED)      
    def limpiar(self):
        if not self.seguimiento:
            self.seguir()
        self.breakpoints = []
        self.ensamblado = False
        for i in self.render_memory:
            entry = self.render_memory[i]
            ent = entry[0]
            self.punto_de_apoyo = 12288
            ent.config(text=f"  ◻️ x{hex(self.punto_de_apoyo+i)}")
            for j in range(1,5):
                ent = entry[j]
                ent.config(state=tk.NORMAL)
                ent.delete(0, tk.END)
                ent.config(state=tk.DISABLED)
        self.tema(self.theme)





