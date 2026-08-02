# ESM-Simulator
ESM Simulator es una herramienta educativa de código abierto desarrollada en Python, Yacc y Lex, basada en la arquitectura de conjunto de instrucciones (ISA) de la Educational Stack Machine x16 (ESMx16). Su propósito principal es facilitar el aprendizaje y la enseñanza de la programación en lenguaje ensamblador, proporcionando un entorno interactivo e intuitivo para el desarrollo, prueba y traducción de código assembly. Este simulador ha sido diseñado específicamente para su uso en el ámbito académico de la Carrera de Ingeniería en Computación de la FIO-UNaM, contribuyendo al desarrollo de competencias en arquitectura de computadoras y programación de bajo nivel.
     ![image](https://github.com/user-attachments/assets/b82288c3-e78b-4e84-925b-435cb3042dfa)
La microarquitectura ESMx16 y su correspondiente ISA fueron desarrolladas por la cátedra de Fundamentos de Informática de la Facultad de Ingeniería de Oberá (FIO-UNaM) como una alternativa simplificada a la LC-3 de Yale Patt. Su propósito no es reemplazar a la LC-3, sino servir como un primer escalón en el proceso de enseñanza, facilitando la comprensión progresiva de los conceptos fundamentales de arquitectura de computadoras y programación en ensamblador. 

Mas información: 
https://drive.google.com/file/d/13sWqnlIF54dDIfUC_e0PlW9IuXdmEMA-/view?usp=sharing

# Equipo de Desarrollo: 
CRUZ, Thiago Agustín

cruzthiagoagustin664@gmail.com 
     
RYBERG, Brian Ezequiel 
        
ryberg.brian2@gmail.com 
     
MEIER, Jonathan Cristian 
        
jonny.meier26@gmail.com 

## Memoria unificada

El núcleo utiliza una única tabla `memoria[65536]`. Cada celda contiene:

- la palabra de 16 bits que lee y ejecuta el procesador;
- la línea de assembly que muestra la interfaz;
- la etiqueta asociada a esa dirección, cuando existe.

Las instrucciones y los datos comparten el mismo campo `palabra`. Por eso `LD`
puede cargar el código máquina de una instrucción en el acumulador y `ST` puede
escribirlo sobre cualquier dirección. Si luego el PC alcanza esa dirección, el
nucleo ejecuta la nueva palabra, aunque originalmente la celda hubiera sido un
dato, una reserva o una instrucción diferente.

La API histórica usada por `ESM.py` se conserva (`assemble`, `stepin`,
`get_line`, `get_etiq`, `buscarDireccionEtiqueta`,
`modificar_matriz_dato` y `reemplazar_linea_st`). Se agregaron `leer_memoria` y
`escribir_memoria`, junto con la notificación de la última escritura, para que
la GUI refleje el estado real del núcleo. `.FILL` admite valores con signo de
16 bits: desde `-32768` hasta `32767`, inclusive, y puede utilizarse con o sin
una etiqueta previa.

Al finalizar la primera pasada, el ensamblador valida todas las referencias
simbólicas. De esta forma conserva las referencias hacia etiquetas declaradas
más adelante, pero devuelve el error 314 cuando una etiqueta no existe.

La interfaz reconoce correctamente etiquetas de una sola letra (por ejemplo,
`I`, `L` y `K`) sin eliminar caracteres de la instrucción que sigue. En una
ejecución continua, la secuencia `TRAP x23` / `TRAP x21` refleja el carácter
una sola vez, al ejecutarse el segundo trap.

La opción **Ayuda** del menú de configuración abre la guía bilingüe definida en
`GUI_help.py`, con la sintaxis, los rangos y los ejemplos de OR y multiplicación
adaptados del paper Proyecto UMUx16.

La pestaña **Información** utiliza el mismo formato visual que Ayuda: encabezado
fijo, contenido desplazable, secciones y soporte para los temas claro y oscuro.
Las rutas históricas de sus imágenes se mantienen sin cambios.

### Regeneración y compilación

```bash
bison -Wall -d -o assemble.tab.c assemble.y
flex -o lex.yy.c assemble.l
gcc -std=gnu11 -fPIC -shared -o lib.so assemble.tab.c lex.yy.c
x86_64-w64-mingw32-gcc -std=gnu11 -shared -o lib.dll assemble.tab.c lex.yy.c
```

Prueba de regresión:

```bash
python test_memoria_unificada.py
```
     
