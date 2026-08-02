/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison implementation for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output, and Bison version.  */
#define YYBISON 30802

/* Bison version string.  */
#define YYBISON_VERSION "3.8.2"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Push parsers.  */
#define YYPUSH 0

/* Pull parsers.  */
#define YYPULL 1




/* First part of user prologue.  */
#line 18 "assemble.y"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
//#define YYDEBUG 1
#include <ctype.h>
#include "assemble.tab.h"
int yylex(void);
void yyerror(const char *s);
	
// MEMORIA UNIFICADA
#define max_caracter 100
#define tamMat 65536

typedef enum {
	CELDA_VACIA = 0,
	CELDA_PALABRA = 1,
	CELDA_FIN = 2
} TipoCelda;

typedef struct {
	uint16_t palabra;
	char linea[max_caracter];
	char etiqueta[max_caracter];
	uint8_t tipo;
} CeldaMemoria;

/*
 * Una única celda conserva la palabra de 16 bits que consume el procesador y
 * los metadatos que necesitan el ensamblador y la GUI. Las instrucciones y
 * los datos comparten exactamente el mismo campo `palabra`.
 */
CeldaMemoria memoria[tamMat];
int acumulador, pc, pre, etiqueta_key, A,fin,codigo_inicio,origen,datardo;

/* Estado de la última escritura, utilizado por Python para refrescar la GUI. */
int hubo_escritura_memoria = 0;
int ultima_direccion_escrita = -1;

char* data, *ALUFlags="z";
extern FILE *yyin; // Declaración de yyin

//VARIABLES PARA NUCLEO DE PROCESOS
int direccionador;
int banderaParaTrapDeEntrada=0;
int banderaParaTrapDeSalida=0;
int banderaParaBranch=0;
int langyacc=1;
int errores=0;
FILE *stream;

//=========================================================================================================
//========================================	FUNCIONES DE OPERACION ========================================
void modificar_acumulador(int nuevo_valor){
	//Actualiza el valor del acumulador
	acumulador = nuevo_valor;
	
	//Evalua el dato actual del acumulador y setea los flags de la ALU en consecuencia
	// Forzar a 16 bits
    unsigned short acum16 = (unsigned short)(acumulador & 0xFFFF);

    // Interpretar como 16 bits con signo
    short acum_signed = (short)acum16;
	if(acum_signed < 0){			ALUFlags = "n";
		}else{
			if(acum_signed == 0){	ALUFlags = "z";
			}else{					ALUFlags = "p";}
	}
}

int compararFlags(char *flagsIns){
	//Utilizada para los BRANCHES, compara los flads de la ALU con los flags de la instruccion,
	//si hay coincidencia devuelve 1, sino 0
	for(size_t i=0; i<strlen(flagsIns);i++){
		if(ALUFlags[0]==flagsIns[i]){
			return 1;
		}
	}
	return 0;
}

void bandera_check(){
	//Resetea las banderas de trap y branch, para que no se queden activas en el proximo ciclo
	banderaParaTrapDeEntrada=0;
	banderaParaTrapDeSalida=0;
	banderaParaBranch=0;
}

int overflow(int value) {
	//En caso de que ocurra un overflow, este lo corrige, para que el valor quede en el rango de -32768 a 32767
	while (value > 32767) { value -= 65536;
	}
	while (value < -32768) { value += 65536;
	}
	return value;
}

int extender_signo(uint16_t valor, int bits) {
	uint16_t mascara = (uint16_t)((1u << bits) - 1u);
	uint16_t signo = (uint16_t)(1u << (bits - 1));
	valor &= mascara;
	return (valor & signo) ? (int)(valor | (uint16_t)(~mascara)) : (int)valor;
}

int direccion_relativa(int base, int desplazamiento) {
	return (base + 1 + desplazamiento) & 0xFFFF;
}
//========================================	FIN FUNCIONES DE OPERACION ========================================
//=============================================================================================================



//=======================================================================================================
//========================================	FUNCIONES DE MEMORIA ========================================
void set_input_from_memory(const char* linea,const char *line_path) {
	//Esta funcion se encarga de crear un archivo temporal con la linea de codigo que se le pasa 
	//como parametro, para que el parser pueda leerlo

	if (stream) {fclose(stream);}// Cierra el archivo temporal anterior si existe
	
	stream = fopen(line_path, "w+b");// Abre un archivo temporal en modo binario para escritura y lectura 
	if (!stream) {
        perror("Error creando archivo temporal");
        return;
    }
    
	fwrite(linea, 1, strlen(linea), stream);// Escribe la línea en el archivo temporal
    rewind(stream);// Mueve el puntero del archivo al inicio para que pueda ser leído desde el principio

	yyin = stream;// Asigna el archivo temporal a yyin para que el parser lo lea
}

char* get_line(int pc_line){
	// Esta funcion devuelve la linea de codigo que se encuentra en la posicion de memoria indicada por pc_line
	if (pc_line < 0 || pc_line >= tamMat) {
		return NULL;
	}
	return memoria[pc_line].linea;
}

char* get_etiq(int pc_line){
	// Esta funcion devuelve la etiqueta que se encuentra en la posicion de memoria indicada por pc_line
	if (pc_line < 0 || pc_line >= tamMat || memoria[pc_line].etiqueta[0] == '\0') {
		return NULL;
	}
	return memoria[pc_line].etiqueta;
}

int buscarDireccionEtiqueta(char *etiqueta){
	if (etiqueta == NULL) {
		return -1;
	}
	for(int i=0; i<tamMat; i++){
		if(memoria[i].etiqueta[0] != '\0' && strcmp(memoria[i].etiqueta,etiqueta)==0){
			return i;
		}
	}
	return -1;
}

int buscarDato(char *etiqueta){
	int dir=buscarDireccionEtiqueta(etiqueta);
	return dir >= 0 ? memoria[dir].palabra : 0;
}

void registrar_etiqueta(const char *etiqueta, int direccion){
	if (etiqueta == NULL || direccion < 0 || direccion >= tamMat) {
		return;
	}
	strncpy(memoria[direccion].etiqueta, etiqueta, max_caracter - 1);
	memoria[direccion].etiqueta[max_caracter - 1] = '\0';
}

/*
 * Comprueba las referencias simbolicas una vez finalizada la primera pasada.
 * En ese momento ya se registraron tambien las etiquetas declaradas mas
 * adelante, por lo que solo se rechazan los simbolos realmente inexistentes.
 */
int validar_referencias_etiquetas(void){
	for (int direccion = 0; direccion < tamMat; direccion++) {
		if (memoria[direccion].linea[0] == '\0') {
			continue;
		}

		char copia[max_caracter];
		strncpy(copia, memoria[direccion].linea, max_caracter - 1);
		copia[max_caracter - 1] = '\0';

		char *token = strtok(copia, " \t\r\n");
		if (token == NULL) {
			continue;
		}

		/* Si la celda tiene etiqueta, el segundo token es la operacion. */
		if (memoria[direccion].etiqueta[0] != '\0' &&
			strcmp(token, memoria[direccion].etiqueta) == 0) {
			token = strtok(NULL, " \t\r\n");
			if (token == NULL) {
				continue;
			}
		}

		char *operando = NULL;
		if (strcmp(token, "ADD") == 0 || strcmp(token, "AND") == 0 ||
			strcmp(token, "NOTA") == 0 || strcmp(token, "LD") == 0 ||
			strcmp(token, "ST") == 0) {
			operando = strtok(NULL, " \t\r\n");
		} else if (strcmp(token, "BR") == 0) {
			/* Sintaxis separada: BR nzp ETIQUETA. */
			(void)strtok(NULL, " \t\r\n");
			operando = strtok(NULL, " \t\r\n");
		} else if (strncmp(token, "BR", 2) == 0) {
			/* Sintaxis compacta: BRnzp ETIQUETA. */
			operando = strtok(NULL, " \t\r\n");
		}

		if (operando != NULL && operando[0] != '#' && operando[0] != 'x' &&
			buscarDireccionEtiqueta(operando) == -1) {
			return 314;
		}
	}
	return 0;
}

/*
 * .FILL no necesita una etiqueta. Se procesa antes del parser para mantener
 * compatibilidad tanto con la forma historica "ETQ .FILL #n" como con
 * ".FILL #n". Devuelve 1 si la linea era un .FILL sin etiqueta.
 */
int procesar_fill_sin_etiqueta(const char *linea){
	const char *cursor = linea;
	while (*cursor != '\0' && isspace((unsigned char)*cursor)) {
		cursor++;
	}

	if (strncmp(cursor, ".FILL", 5) != 0 ||
		(cursor[5] != '\0' && !isspace((unsigned char)cursor[5]))) {
		return 0;
	}

	cursor += 5;
	while (*cursor != '\0' && isspace((unsigned char)*cursor)) {
		cursor++;
	}
	if (*cursor != '#') {
		errores = 312;
		return 1;
	}

	char *fin_numero = NULL;
	long valor = strtol(cursor + 1, &fin_numero, 10);
	if (fin_numero == cursor + 1) {
		errores = 312;
		return 1;
	}
	while (*fin_numero != '\0' && isspace((unsigned char)*fin_numero)) {
		fin_numero++;
	}
	if (*fin_numero != '\0') {
		errores = 315;
		return 1;
	}
	if (valor < -32768 || valor > 32767) {
		errores = 212;
		return 1;
	}

	memoria[pc].palabra = (uint16_t)((int)valor & 0xFFFF);
	memoria[pc].tipo = CELDA_PALABRA;
	return 1;
}

void reemplazar_linea_st(char *nueva_linea, int pc_reemplazo){
	if (nueva_linea == NULL || pc_reemplazo < 0 || pc_reemplazo >= tamMat) {
		return;
	}
	strncpy(memoria[pc_reemplazo].linea, nueva_linea, max_caracter - 1);
	memoria[pc_reemplazo].linea[max_caracter - 1] = '\0';
}

void modificar_matriz_dato(int nuevo_dato, int pc_mod){
	if (pc_mod < 0 || pc_mod >= tamMat) {
		return;
	}
	memoria[pc_mod].palabra = (uint16_t)(nuevo_dato & 0xFFFF);
	memoria[pc_mod].tipo = CELDA_PALABRA;
	printf("SE COLOCO LA PALABRA %u en la posicion %i\n",memoria[pc_mod].palabra,pc_mod);
}

unsigned int leer_memoria(int direccion){
	if (direccion < 0 || direccion >= tamMat) {
		return 0;
	}
	return memoria[direccion].palabra;
}

void escribir_memoria(int direccion, int valor){
	if (direccion < 0 || direccion >= tamMat) {
		return;
	}
	memoria[direccion].palabra = (uint16_t)(valor & 0xFFFF);
	memoria[direccion].tipo = CELDA_PALABRA;
	hubo_escritura_memoria = 1;
	ultima_direccion_escrita = direccion;
}
//========================================	FIN FUNCIONES DE MEMORIA ========================================
//===========================================================================================================



//========================================================================================================
//========================================	FUNCIONES PRINCIPALES ========================================
void reset() {
	// Reinicia todas las variables y estructuras de datos a sus valores iniciales
	    memset(memoria, 0, sizeof(memoria));
    acumulador = 0;
    pc = 0;
    pre = 0;
    etiqueta_key = 0;
    A = 0;
    fin = 0;
	codigo_inicio = 7;
    origen = 0;
    datardo = 0;
	    hubo_escritura_memoria = 0;
	    ultima_direccion_escrita = -1;
    data = NULL;
    ALUFlags = "z";
    direccionador = 0;
    banderaParaTrapDeEntrada = 0;
    banderaParaTrapDeSalida = 0;
    banderaParaBranch = 0;
}

int assemble(int lang, const char *file_path, const char *line_path){
    errores = 0;
    langyacc = lang;

    // Reinicia el estado interno del ensamblador
    reset();
    FILE *archivo = fopen(file_path, "r");
    if (archivo == NULL) {
        return (errores = 100);
    }

    char linea[max_caracter];
    pre = 1;// Primera pasada del ensamblador

    // Si el codigo posee una directiva inicial (ej. .ORIG),
    // se procesa antes de comenzar a ensamblar el resto del archivo
    if (lang == 10) {
        if (fgets(linea, sizeof(linea), archivo) != NULL) {
            printf("LINEA: %s\n", linea);

            set_input_from_memory(linea, line_path);
            yyparse();
            yylex();

            // Verifica que la primera línea sea válida
            if (codigo_inicio != 0) {
                fclose(archivo);
                return (errores = 317);
            }
        }
    } else {
        // Dirección de origen por defecto (x3000), esto solo se ocupa en el caso de que el codigo este
		// escrito en hexadecimal o binario, ya que en el caso de que sea en ensamblador, la directiva .ORIG es obligatoria
        origen = 0x3000;
    }

    // Si ocurrió algún error durante la inicialización, finalizar
    if (errores != 0) {
        fclose(archivo);
        return errores;
    }

    pc = origen;// Inicializa el contador de programa
    // Recorre el archivo línea por línea hasta encontrar la directiva END
    // o llegar al final del archivo
    while (fin != 7 && fgets(linea, sizeof(linea), archivo) != NULL) {

        // Guarda una copia del código fuente para depuración.
        if (pc < tamMat) {
	            strncpy(memoria[pc].linea, linea, max_caracter - 1);
	            memoria[pc].linea[max_caracter - 1] = '\0';
        }

        // .FILL puede reservar una palabra sin requerir una etiqueta previa.
        if (!procesar_fill_sin_etiqueta(linea)) {
            // Envía el resto de las líneas al analizador léxico/sintáctico
            set_input_from_memory(linea, line_path);
            yyparse();
            yylex();
        }

        // Si el parser detectó un error, abortar el ensamblado
        if (errores != 0) {
            fclose(archivo);
            return errores;
        }

        pc++;// Avanza el contador de programa
        if (pc >= tamMat) {// Si se supera el tamaño de memoria, vuelve al inicio
            pc = 0;
        }
    }

    // Si nunca apareció la directiva END, reportar error
    if (fin != 7) {
        errores = 316;
    }

    if (errores == 0) {
        errores = validar_referencias_etiquetas();
    }

    // Guarda la dirección final del programa
    fin = pc;

    // Restaura el estado para la ejecución
    pc = origen;
    acumulador = 0;
    pre = 0;

    fclose(archivo);
    return errores;
}

int stepin(int lang, const char *line_path){
	    errores = 0;
	    langyacc = lang;
	    (void)line_path;
	    hubo_escritura_memoria = 0;
	    ultima_direccion_escrita = -1;

	    // Verifica que el PC se encuentre dentro del rango válido de memoria
	    if (pc < 0 || pc >= tamMat) {
	        return (errores = 210);
	    }

	    // Si se alcanzó .END (o el final histórico), no quedan instrucciones.
	    if (pc == fin || memoria[pc].tipo == CELDA_FIN) {
	        return 1;
	    }

	/*
	 * El procesador ejecuta la misma palabra de 16 bits que leen LD y escriben
	 * ST. Así una instrucción puede tratarse como dato y ejecutarse luego de ser
	 * creada o modificada durante la ejecución.
	 */
	uint16_t instruccion = memoria[pc].palabra;
	unsigned int opcode = (instruccion >> 13) & 0x7u;
	int pc_siguiente = (pc + 1) & 0xFFFF;
	int desplazamiento;
	int direccion;

	switch (opcode) {
		case 0: // ADD: relativo (bit 12=0) o inmediato (bit 12=1)
			desplazamiento = extender_signo(instruccion, 12);
			if (instruccion & 0x1000u) {
				modificar_acumulador(overflow(acumulador + desplazamiento));
			} else {
				direccion = direccion_relativa(pc, desplazamiento);
				modificar_acumulador(overflow(acumulador + memoria[direccion].palabra));
			}
			break;

		case 1: // AND: relativo (bit 12=0) o inmediato (bit 12=1)
			desplazamiento = extender_signo(instruccion, 12);
			if (instruccion & 0x1000u) {
				modificar_acumulador(acumulador & desplazamiento);
			} else {
				direccion = direccion_relativa(pc, desplazamiento);
				modificar_acumulador(acumulador & memoria[direccion].palabra);
			}
			break;

		case 2: // NOTA relativo o NOTB sobre el acumulador
			if (instruccion & 0x1000u) {
				modificar_acumulador(~acumulador);
			} else {
				desplazamiento = extender_signo(instruccion, 12);
				direccion = direccion_relativa(pc, desplazamiento);
				modificar_acumulador(~memoria[direccion].palabra);
			}
			break;

		case 3: // LD (bit 12=0) / ST (bit 12=1)
			desplazamiento = extender_signo(instruccion, 12);
			direccion = direccion_relativa(pc, desplazamiento);
			if (instruccion & 0x1000u) {
				escribir_memoria(direccion, acumulador);
			} else {
				modificar_acumulador(memoria[direccion].palabra);
			}
			break;

		case 4: { // BR: NZP + PCoffset10
			char flags[4];
			int indice = 0;
			if (instruccion & 0x1000u) flags[indice++] = 'n';
			if (instruccion & 0x0800u) flags[indice++] = 'z';
			if (instruccion & 0x0400u) flags[indice++] = 'p';
			flags[indice] = '\0';
			if (compararFlags(flags)) {
				desplazamiento = extender_signo(instruccion, 10);
				pc_siguiente = direccion_relativa(pc, desplazamiento);
				banderaParaBranch = 1;
			}
			break;
		}

		case 7: { // TRAP: vector de 13 bits
			unsigned int vector = instruccion & 0x1FFFu;
			if (vector == 0x21u) {
				banderaParaTrapDeSalida = 1;
			} else if (vector == 0x23u) {
				banderaParaTrapDeEntrada = 1;
			} else {
				return (errores = 310);
			}
			break;
		}

		default:
			return (errores = 315);
	}

	pc = pc_siguiente;
		printf("PC YACC: %i\n", pc);
		return 0;
}
//========================================	FIN FUNCIONES PRINCIPALES =========================================
//=============================================================================================================

#line 502 "assemble.tab.c"

# ifndef YY_CAST
#  ifdef __cplusplus
#   define YY_CAST(Type, Val) static_cast<Type> (Val)
#   define YY_REINTERPRET_CAST(Type, Val) reinterpret_cast<Type> (Val)
#  else
#   define YY_CAST(Type, Val) ((Type) (Val))
#   define YY_REINTERPRET_CAST(Type, Val) ((Type) (Val))
#  endif
# endif
# ifndef YY_NULLPTR
#  if defined __cplusplus
#   if 201103L <= __cplusplus
#    define YY_NULLPTR nullptr
#   else
#    define YY_NULLPTR 0
#   endif
#  else
#   define YY_NULLPTR ((void*)0)
#  endif
# endif

#include "assemble.tab.h"
/* Symbol kind.  */
enum yysymbol_kind_t
{
  YYSYMBOL_YYEMPTY = -2,
  YYSYMBOL_YYEOF = 0,                      /* "end of file"  */
  YYSYMBOL_YYerror = 1,                    /* error  */
  YYSYMBOL_YYUNDEF = 2,                    /* "invalid token"  */
  YYSYMBOL_ADD = 3,                        /* ADD  */
  YYSYMBOL_AND = 4,                        /* AND  */
  YYSYMBOL_NOTA = 5,                       /* NOTA  */
  YYSYMBOL_NOTB = 6,                       /* NOTB  */
  YYSYMBOL_LD = 7,                         /* LD  */
  YYSYMBOL_ST = 8,                         /* ST  */
  YYSYMBOL_BR_FLAGS = 9,                   /* BR_FLAGS  */
  YYSYMBOL_TRAP = 10,                      /* TRAP  */
  YYSYMBOL_END = 11,                       /* END  */
  YYSYMBOL_ORIG = 12,                      /* ORIG  */
  YYSYMBOL_FILL = 13,                      /* FILL  */
  YYSYMBOL_BLKW = 14,                      /* BLKW  */
  YYSYMBOL_ETIQUETA = 15,                  /* ETIQUETA  */
  YYSYMBOL_NUMERO = 16,                    /* NUMERO  */
  YYSYMBOL_HEXA = 17,                      /* HEXA  */
  YYSYMBOL_ERROR_NUMERO = 18,              /* ERROR_NUMERO  */
  YYSYMBOL_INVALIDO = 19,                  /* INVALIDO  */
  YYSYMBOL_20_n_ = 20,                     /* '\n'  */
  YYSYMBOL_21_ = 21,                       /* '.'  */
  YYSYMBOL_YYACCEPT = 22,                  /* $accept  */
  YYSYMBOL_prog = 23,                      /* prog  */
  YYSYMBOL_intrucciones = 24,              /* intrucciones  */
  YYSYMBOL_reservas = 25,                  /* reservas  */
  YYSYMBOL_datoFill = 26,                  /* datoFill  */
  YYSYMBOL_dato = 27,                      /* dato  */
  YYSYMBOL_datoBR = 28,                    /* datoBR  */
  YYSYMBOL_direccion = 29,                 /* direccion  */
  YYSYMBOL_direccionBR = 30                /* direccionBR  */
};
typedef enum yysymbol_kind_t yysymbol_kind_t;




#ifdef short
# undef short
#endif

/* On compilers that do not define __PTRDIFF_MAX__ etc., make sure
   <limits.h> and (if available) <stdint.h> are included
   so that the code can choose integer types of a good width.  */

#ifndef __PTRDIFF_MAX__
# include <limits.h> /* INFRINGES ON USER NAME SPACE */
# if defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stdint.h> /* INFRINGES ON USER NAME SPACE */
#  define YY_STDINT_H
# endif
#endif

/* Narrow types that promote to a signed type and that can represent a
   signed or unsigned integer of at least N bits.  In tables they can
   save space and decrease cache pressure.  Promoting to a signed type
   helps avoid bugs in integer arithmetic.  */

#ifdef __INT_LEAST8_MAX__
typedef __INT_LEAST8_TYPE__ yytype_int8;
#elif defined YY_STDINT_H
typedef int_least8_t yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef __INT_LEAST16_MAX__
typedef __INT_LEAST16_TYPE__ yytype_int16;
#elif defined YY_STDINT_H
typedef int_least16_t yytype_int16;
#else
typedef short yytype_int16;
#endif

/* Work around bug in HP-UX 11.23, which defines these macros
   incorrectly for preprocessor constants.  This workaround can likely
   be removed in 2023, as HPE has promised support for HP-UX 11.23
   (aka HP-UX 11i v2) only through the end of 2022; see Table 2 of
   <https://h20195.www2.hpe.com/V2/getpdf.aspx/4AA4-7673ENW.pdf>.  */
#ifdef __hpux
# undef UINT_LEAST8_MAX
# undef UINT_LEAST16_MAX
# define UINT_LEAST8_MAX 255
# define UINT_LEAST16_MAX 65535
#endif

#if defined __UINT_LEAST8_MAX__ && __UINT_LEAST8_MAX__ <= __INT_MAX__
typedef __UINT_LEAST8_TYPE__ yytype_uint8;
#elif (!defined __UINT_LEAST8_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST8_MAX <= INT_MAX)
typedef uint_least8_t yytype_uint8;
#elif !defined __UINT_LEAST8_MAX__ && UCHAR_MAX <= INT_MAX
typedef unsigned char yytype_uint8;
#else
typedef short yytype_uint8;
#endif

#if defined __UINT_LEAST16_MAX__ && __UINT_LEAST16_MAX__ <= __INT_MAX__
typedef __UINT_LEAST16_TYPE__ yytype_uint16;
#elif (!defined __UINT_LEAST16_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST16_MAX <= INT_MAX)
typedef uint_least16_t yytype_uint16;
#elif !defined __UINT_LEAST16_MAX__ && USHRT_MAX <= INT_MAX
typedef unsigned short yytype_uint16;
#else
typedef int yytype_uint16;
#endif

#ifndef YYPTRDIFF_T
# if defined __PTRDIFF_TYPE__ && defined __PTRDIFF_MAX__
#  define YYPTRDIFF_T __PTRDIFF_TYPE__
#  define YYPTRDIFF_MAXIMUM __PTRDIFF_MAX__
# elif defined PTRDIFF_MAX
#  ifndef ptrdiff_t
#   include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  endif
#  define YYPTRDIFF_T ptrdiff_t
#  define YYPTRDIFF_MAXIMUM PTRDIFF_MAX
# else
#  define YYPTRDIFF_T long
#  define YYPTRDIFF_MAXIMUM LONG_MAX
# endif
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned
# endif
#endif

#define YYSIZE_MAXIMUM                                  \
  YY_CAST (YYPTRDIFF_T,                                 \
           (YYPTRDIFF_MAXIMUM < YY_CAST (YYSIZE_T, -1)  \
            ? YYPTRDIFF_MAXIMUM                         \
            : YY_CAST (YYSIZE_T, -1)))

#define YYSIZEOF(X) YY_CAST (YYPTRDIFF_T, sizeof (X))


/* Stored state numbers (used for stacks). */
typedef yytype_int8 yy_state_t;

/* State numbers in computations.  */
typedef int yy_state_fast_t;

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif


#ifndef YY_ATTRIBUTE_PURE
# if defined __GNUC__ && 2 < __GNUC__ + (96 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_PURE __attribute__ ((__pure__))
# else
#  define YY_ATTRIBUTE_PURE
# endif
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# if defined __GNUC__ && 2 < __GNUC__ + (7 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_UNUSED __attribute__ ((__unused__))
# else
#  define YY_ATTRIBUTE_UNUSED
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YY_USE(E) ((void) (E))
#else
# define YY_USE(E) /* empty */
#endif

/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
#if defined __GNUC__ && ! defined __ICC && 406 <= __GNUC__ * 100 + __GNUC_MINOR__
# if __GNUC__ * 100 + __GNUC_MINOR__ < 407
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")
# else
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")              \
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# endif
# define YY_IGNORE_MAYBE_UNINITIALIZED_END      \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif

#if defined __cplusplus && defined __GNUC__ && ! defined __ICC && 6 <= __GNUC__
# define YY_IGNORE_USELESS_CAST_BEGIN                          \
    _Pragma ("GCC diagnostic push")                            \
    _Pragma ("GCC diagnostic ignored \"-Wuseless-cast\"")
# define YY_IGNORE_USELESS_CAST_END            \
    _Pragma ("GCC diagnostic pop")
#endif
#ifndef YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_END
#endif


#define YY_ASSERT(E) ((void) (0 && (E)))

#if !defined yyoverflow

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined EXIT_SUCCESS
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
      /* Use EXIT_SUCCESS as a witness for stdlib.h.  */
#     ifndef EXIT_SUCCESS
#      define EXIT_SUCCESS 0
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's 'empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined EXIT_SUCCESS \
       && ! ((defined YYMALLOC || defined malloc) \
             && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef EXIT_SUCCESS
#    define EXIT_SUCCESS 0
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined EXIT_SUCCESS
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined EXIT_SUCCESS
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* !defined yyoverflow */

#if (! defined yyoverflow \
     && (! defined __cplusplus \
         || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yy_state_t yyss_alloc;
  YYSTYPE yyvs_alloc;
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (YYSIZEOF (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (YYSIZEOF (yy_state_t) + YYSIZEOF (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

# define YYCOPY_NEEDED 1

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack_alloc, Stack)                           \
    do                                                                  \
      {                                                                 \
        YYPTRDIFF_T yynewbytes;                                         \
        YYCOPY (&yyptr->Stack_alloc, Stack, yysize);                    \
        Stack = &yyptr->Stack_alloc;                                    \
        yynewbytes = yystacksize * YYSIZEOF (*Stack) + YYSTACK_GAP_MAXIMUM; \
        yyptr += yynewbytes / YYSIZEOF (*yyptr);                        \
      }                                                                 \
    while (0)

#endif

#if defined YYCOPY_NEEDED && YYCOPY_NEEDED
/* Copy COUNT objects from SRC to DST.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(Dst, Src, Count) \
      __builtin_memcpy (Dst, Src, YY_CAST (YYSIZE_T, (Count)) * sizeof (*(Src)))
#  else
#   define YYCOPY(Dst, Src, Count)              \
      do                                        \
        {                                       \
          YYPTRDIFF_T yyi;                      \
          for (yyi = 0; yyi < (Count); yyi++)   \
            (Dst)[yyi] = (Src)[yyi];            \
        }                                       \
      while (0)
#  endif
# endif
#endif /* !YYCOPY_NEEDED */

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  2
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   83

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  22
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  9
/* YYNRULES -- Number of rules.  */
#define YYNRULES  44
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  61

/* YYMAXUTOK -- Last valid token kind.  */
#define YYMAXUTOK   274


/* YYTRANSLATE(TOKEN-NUM) -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, with out-of-bounds checking.  */
#define YYTRANSLATE(YYX)                                \
  (0 <= (YYX) && (YYX) <= YYMAXUTOK                     \
   ? YY_CAST (yysymbol_kind_t, yytranslate[YYX])        \
   : YYSYMBOL_YYUNDEF)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex.  */
static const yytype_int8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
      20,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,    21,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19
};

#if YYDEBUG
/* YYRLINE[YYN] -- Source line where rule number YYN was defined.  */
static const yytype_int16 yyrline[] =
{
       0,   466,   466,   467,   470,   474,   475,   483,   488,   493,
     496,   501,   505,   508,   512,   515,   520,   523,   529,   535,
     538,   544,   549,   552,   558,   564,   567,   570,   589,   592,
     597,   601,   605,   613,   616,   620,   628,   633,   644,   649,
     660,   667,   676,   687,   704
};
#endif

/** Accessing symbol of state STATE.  */
#define YY_ACCESSING_SYMBOL(State) YY_CAST (yysymbol_kind_t, yystos[State])

#if YYDEBUG || 0
/* The user-facing name of the symbol whose (internal) number is
   YYSYMBOL.  No bounds checking.  */
static const char *yysymbol_name (yysymbol_kind_t yysymbol) YY_ATTRIBUTE_UNUSED;

/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "\"end of file\"", "error", "\"invalid token\"", "ADD", "AND", "NOTA",
  "NOTB", "LD", "ST", "BR_FLAGS", "TRAP", "END", "ORIG", "FILL", "BLKW",
  "ETIQUETA", "NUMERO", "HEXA", "ERROR_NUMERO", "INVALIDO", "'\\n'", "'.'",
  "$accept", "prog", "intrucciones", "reservas", "datoFill", "dato",
  "datoBR", "direccion", "direccionBR", YY_NULLPTR
};

static const char *
yysymbol_name (yysymbol_kind_t yysymbol)
{
  return yytname[yysymbol];
}
#endif

#define YYPACT_NINF (-8)

#define yypact_value_is_default(Yyn) \
  ((Yyn) == YYPACT_NINF)

#define YYTABLE_NINF (-16)

#define yytable_value_is_error(Yyn) \
  0

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
static const yytype_int8 yypact[] =
{
      -8,     0,    -8,    -8,    35,    40,     1,    10,    44,    48,
      16,    53,    19,    -8,    26,    -7,    24,    -8,    -8,    -8,
      -8,    -8,    -8,    -8,    -8,    -8,    -8,    -8,    -8,    -8,
      -8,    -8,    -8,    -8,    -8,    -8,    -8,    -8,    -8,    -8,
      -8,    47,    -8,    -8,    -8,    -8,    33,    49,    -8,    66,
      -8,    -8,    -8,    -4,    -8,    -8,    -8,    -8,    -8,    -8,
      -8
};

/* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
   Performed when YYTABLE does not specify something else to do.  Zero
   means the default is an error.  */
static const yytype_int8 yydefact[] =
{
       2,     0,     1,    29,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     6,     0,     0,     0,     9,    42,    37,
      41,    38,     7,     8,    12,    10,    11,    14,    13,    16,
      19,    18,    17,    22,    21,    20,    25,    44,    39,    43,
      40,     0,    23,    24,    28,    27,     0,     0,    32,     0,
       3,     5,    26,     0,    34,     4,    31,    30,    35,    36,
      33
};

/* YYPGOTO[NTERM-NUM].  */
static const yytype_int8 yypgoto[] =
{
      -8,    -8,    59,    -8,    -8,    34,    -8,    67,    -8
};

/* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int8 yydefgoto[] =
{
       0,     1,    15,    16,    60,    22,    42,    23,    43
};

/* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule whose
   number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_int8 yytable[] =
{
       2,     3,    27,     4,     5,     6,     7,     8,     9,    10,
      11,    29,    58,    50,    59,    12,    18,    36,    20,    13,
       3,    14,     4,     5,     6,     7,     8,     9,    10,    11,
     -15,    37,    38,    39,    40,    41,    17,    48,    49,    25,
      46,    24,    31,    34,    51,    30,    53,    54,    52,    33,
      18,    19,    20,    21,    44,    18,    19,    20,    21,    18,
      19,    20,    21,    18,    19,    20,    21,    56,    18,    55,
      20,    47,    26,    28,     0,    32,    35,     0,    45,     0,
       0,     0,     0,    57
};

static const yytype_int8 yycheck[] =
{
       0,     1,     1,     3,     4,     5,     6,     7,     8,     9,
      10,     1,    16,    20,    18,    15,    15,     1,    17,    19,
       1,    21,     3,     4,     5,     6,     7,     8,     9,    10,
      20,    15,    16,    17,    18,    19,     1,    11,    12,     5,
      21,     1,     8,     9,    20,     1,    13,    14,     1,     1,
      15,    16,    17,    18,     1,    15,    16,    17,    18,    15,
      16,    17,    18,    15,    16,    17,    18,     1,    15,    20,
      17,    12,     5,     6,    -1,     8,     9,    -1,    11,    -1,
      -1,    -1,    -1,    17
};

/* YYSTOS[STATE-NUM] -- The symbol kind of the accessing symbol of
   state STATE-NUM.  */
static const yytype_int8 yystos[] =
{
       0,    23,     0,     1,     3,     4,     5,     6,     7,     8,
       9,    10,    15,    19,    21,    24,    25,     1,    15,    16,
      17,    18,    27,    29,     1,    27,    29,     1,    29,     1,
       1,    27,    29,     1,    27,    29,     1,    15,    16,    17,
      18,    19,    28,    30,     1,    29,    21,    24,    11,    12,
      20,    20,     1,    13,    14,    20,     1,    17,    16,    18,
      26
};

/* YYR1[RULE-NUM] -- Symbol kind of the left-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr1[] =
{
       0,    22,    23,    23,    23,    23,    23,    24,    24,    24,
      24,    24,    24,    24,    24,    24,    24,    24,    24,    24,
      24,    24,    24,    24,    24,    24,    24,    24,    24,    24,
      25,    25,    25,    25,    25,    26,    26,    27,    27,    28,
      28,    29,    29,    30,    30
};

/* YYR2[RULE-NUM] -- Number of symbols on the right-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr2[] =
{
       0,     2,     0,     3,     4,     3,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     1,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     3,     2,     2,     1,
       3,     3,     2,     4,     3,     1,     1,     1,     1,     1,
       1,     1,     1,     1,     1
};


enum { YYENOMEM = -2 };

#define yyerrok         (yyerrstatus = 0)
#define yyclearin       (yychar = YYEMPTY)

#define YYACCEPT        goto yyacceptlab
#define YYABORT         goto yyabortlab
#define YYERROR         goto yyerrorlab
#define YYNOMEM         goto yyexhaustedlab


#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)                                    \
  do                                                              \
    if (yychar == YYEMPTY)                                        \
      {                                                           \
        yychar = (Token);                                         \
        yylval = (Value);                                         \
        YYPOPSTACK (yylen);                                       \
        yystate = *yyssp;                                         \
        goto yybackup;                                            \
      }                                                           \
    else                                                          \
      {                                                           \
        yyerror (YY_("syntax error: cannot back up")); \
        YYERROR;                                                  \
      }                                                           \
  while (0)

/* Backward compatibility with an undocumented macro.
   Use YYerror or YYUNDEF. */
#define YYERRCODE YYUNDEF


/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)                        \
do {                                            \
  if (yydebug)                                  \
    YYFPRINTF Args;                             \
} while (0)




# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)                    \
do {                                                                      \
  if (yydebug)                                                            \
    {                                                                     \
      YYFPRINTF (stderr, "%s ", Title);                                   \
      yy_symbol_print (stderr,                                            \
                  Kind, Value); \
      YYFPRINTF (stderr, "\n");                                           \
    }                                                                     \
} while (0)


/*-----------------------------------.
| Print this symbol's value on YYO.  |
`-----------------------------------*/

static void
yy_symbol_value_print (FILE *yyo,
                       yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  FILE *yyoutput = yyo;
  YY_USE (yyoutput);
  if (!yyvaluep)
    return;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/*---------------------------.
| Print this symbol on YYO.  |
`---------------------------*/

static void
yy_symbol_print (FILE *yyo,
                 yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyo, "%s %s (",
             yykind < YYNTOKENS ? "token" : "nterm", yysymbol_name (yykind));

  yy_symbol_value_print (yyo, yykind, yyvaluep);
  YYFPRINTF (yyo, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

static void
yy_stack_print (yy_state_t *yybottom, yy_state_t *yytop)
{
  YYFPRINTF (stderr, "Stack now");
  for (; yybottom <= yytop; yybottom++)
    {
      int yybot = *yybottom;
      YYFPRINTF (stderr, " %d", yybot);
    }
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)                            \
do {                                                            \
  if (yydebug)                                                  \
    yy_stack_print ((Bottom), (Top));                           \
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

static void
yy_reduce_print (yy_state_t *yyssp, YYSTYPE *yyvsp,
                 int yyrule)
{
  int yylno = yyrline[yyrule];
  int yynrhs = yyr2[yyrule];
  int yyi;
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %d):\n",
             yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YYFPRINTF (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr,
                       YY_ACCESSING_SYMBOL (+yyssp[yyi + 1 - yynrhs]),
                       &yyvsp[(yyi + 1) - (yynrhs)]);
      YYFPRINTF (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)          \
do {                                    \
  if (yydebug)                          \
    yy_reduce_print (yyssp, yyvsp, Rule); \
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args) ((void) 0)
# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif






/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg,
            yysymbol_kind_t yykind, YYSTYPE *yyvaluep)
{
  YY_USE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yykind, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/* Lookahead token kind.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;
/* Number of syntax errors so far.  */
int yynerrs;




/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
    yy_state_fast_t yystate = 0;
    /* Number of tokens to shift before error messages enabled.  */
    int yyerrstatus = 0;

    /* Refer to the stacks through separate pointers, to allow yyoverflow
       to reallocate them elsewhere.  */

    /* Their size.  */
    YYPTRDIFF_T yystacksize = YYINITDEPTH;

    /* The state stack: array, bottom, top.  */
    yy_state_t yyssa[YYINITDEPTH];
    yy_state_t *yyss = yyssa;
    yy_state_t *yyssp = yyss;

    /* The semantic value stack: array, bottom, top.  */
    YYSTYPE yyvsa[YYINITDEPTH];
    YYSTYPE *yyvs = yyvsa;
    YYSTYPE *yyvsp = yyvs;

  int yyn;
  /* The return value of yyparse.  */
  int yyresult;
  /* Lookahead symbol kind.  */
  yysymbol_kind_t yytoken = YYSYMBOL_YYEMPTY;
  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;



#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yychar = YYEMPTY; /* Cause a token to be read.  */

  goto yysetstate;


/*------------------------------------------------------------.
| yynewstate -- push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;


/*--------------------------------------------------------------------.
| yysetstate -- set current state (the top of the stack) to yystate.  |
`--------------------------------------------------------------------*/
yysetstate:
  YYDPRINTF ((stderr, "Entering state %d\n", yystate));
  YY_ASSERT (0 <= yystate && yystate < YYNSTATES);
  YY_IGNORE_USELESS_CAST_BEGIN
  *yyssp = YY_CAST (yy_state_t, yystate);
  YY_IGNORE_USELESS_CAST_END
  YY_STACK_PRINT (yyss, yyssp);

  if (yyss + yystacksize - 1 <= yyssp)
#if !defined yyoverflow && !defined YYSTACK_RELOCATE
    YYNOMEM;
#else
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYPTRDIFF_T yysize = yyssp - yyss + 1;

# if defined yyoverflow
      {
        /* Give user a chance to reallocate the stack.  Use copies of
           these so that the &'s don't force the real ones into
           memory.  */
        yy_state_t *yyss1 = yyss;
        YYSTYPE *yyvs1 = yyvs;

        /* Each stack pointer address is followed by the size of the
           data in use in that stack, in bytes.  This used to be a
           conditional around just the two extra args, but that might
           be undefined if yyoverflow is a macro.  */
        yyoverflow (YY_("memory exhausted"),
                    &yyss1, yysize * YYSIZEOF (*yyssp),
                    &yyvs1, yysize * YYSIZEOF (*yyvsp),
                    &yystacksize);
        yyss = yyss1;
        yyvs = yyvs1;
      }
# else /* defined YYSTACK_RELOCATE */
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
        YYNOMEM;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
        yystacksize = YYMAXDEPTH;

      {
        yy_state_t *yyss1 = yyss;
        union yyalloc *yyptr =
          YY_CAST (union yyalloc *,
                   YYSTACK_ALLOC (YY_CAST (YYSIZE_T, YYSTACK_BYTES (yystacksize))));
        if (! yyptr)
          YYNOMEM;
        YYSTACK_RELOCATE (yyss_alloc, yyss);
        YYSTACK_RELOCATE (yyvs_alloc, yyvs);
#  undef YYSTACK_RELOCATE
        if (yyss1 != yyssa)
          YYSTACK_FREE (yyss1);
      }
# endif

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;

      YY_IGNORE_USELESS_CAST_BEGIN
      YYDPRINTF ((stderr, "Stack size increased to %ld\n",
                  YY_CAST (long, yystacksize)));
      YY_IGNORE_USELESS_CAST_END

      if (yyss + yystacksize - 1 <= yyssp)
        YYABORT;
    }
#endif /* !defined yyoverflow && !defined YYSTACK_RELOCATE */


  if (yystate == YYFINAL)
    YYACCEPT;

  goto yybackup;


/*-----------.
| yybackup.  |
`-----------*/
yybackup:
  /* Do appropriate processing given the current state.  Read a
     lookahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to lookahead token.  */
  yyn = yypact[yystate];
  if (yypact_value_is_default (yyn))
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either empty, or end-of-input, or a valid lookahead.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token\n"));
      yychar = yylex ();
    }

  if (yychar <= YYEOF)
    {
      yychar = YYEOF;
      yytoken = YYSYMBOL_YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else if (yychar == YYerror)
    {
      /* The scanner already issued an error message, process directly
         to error recovery.  But do not keep the error token as
         lookahead, it is too special and may lead us to an endless
         loop in error recovery. */
      yychar = YYUNDEF;
      yytoken = YYSYMBOL_YYerror;
      goto yyerrlab1;
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yytable_value_is_error (yyn))
        goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the lookahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);
  yystate = yyn;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END

  /* Discard the shifted token.  */
  yychar = YYEMPTY;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     '$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
  case 3: /* prog: prog intrucciones '\n'  */
#line 467 "assemble.y"
                                          {printf("\n");
		//ACA SAQUE EL IF Y EL GETCHAR
	}
#line 1558 "assemble.tab.c"
    break;

  case 4: /* prog: prog ETIQUETA intrucciones '\n'  */
#line 470 "assemble.y"
                                            {if(pre==1){
		registrar_etiqueta((yyvsp[-2].str), pc);
		}
	}
#line 1567 "assemble.tab.c"
    break;

  case 5: /* prog: prog reservas '\n'  */
#line 474 "assemble.y"
                                   {}
#line 1573 "assemble.tab.c"
    break;

  case 6: /* prog: prog INVALIDO  */
#line 475 "assemble.y"
                              {
		if(pre==1){
			errores= 315;
		}
	}
#line 1583 "assemble.tab.c"
    break;

  case 7: /* intrucciones: ADD dato  */
#line 483 "assemble.y"
                                    {if(pre==0){
		printf("REGISTRO: %i\n",acumulador);
		acumulador = overflow(acumulador);
		}
	}
#line 1593 "assemble.tab.c"
    break;

  case 8: /* intrucciones: ADD direccion  */
#line 488 "assemble.y"
                                    {if(pre==0){
		modificar_acumulador(acumulador + memoria[direccionador].palabra);
		printf("REGISTRO: %i\n",acumulador);
		acumulador = overflow(acumulador);
	}}
#line 1603 "assemble.tab.c"
    break;

  case 9: /* intrucciones: ADD error  */
#line 493 "assemble.y"
                                                        {if(pre==1){
			errores= 300;
	}}
#line 1611 "assemble.tab.c"
    break;

  case 10: /* intrucciones: AND dato  */
#line 496 "assemble.y"
                                    {if(pre==0){
		modificar_acumulador(acumulador & A);
		printf("REGISTRO: %i\n",acumulador);
	}
	}
#line 1621 "assemble.tab.c"
    break;

  case 11: /* intrucciones: AND direccion  */
#line 501 "assemble.y"
                                    {if(pre==0){
		modificar_acumulador(acumulador & memoria[direccionador].palabra);
		printf("REGISTRO: %i\n",acumulador);
	}}
#line 1630 "assemble.tab.c"
    break;

  case 12: /* intrucciones: AND error  */
#line 505 "assemble.y"
                                                        {if(pre==1){
			errores= 300;
	}}
#line 1638 "assemble.tab.c"
    break;

  case 13: /* intrucciones: NOTA direccion  */
#line 508 "assemble.y"
                                    {if(pre==0){
		modificar_acumulador(~memoria[direccionador].palabra);
		printf("REGISTRO: %i\n",acumulador);
	}}
#line 1647 "assemble.tab.c"
    break;

  case 14: /* intrucciones: NOTA error  */
#line 512 "assemble.y"
                                                        {if(pre==1){
			errores= 303;
	}}
#line 1655 "assemble.tab.c"
    break;

  case 15: /* intrucciones: NOTB  */
#line 515 "assemble.y"
                                    {if(pre==0){
		modificar_acumulador(~acumulador);
		printf("REGISTRO: %i\n",acumulador);

	}}
#line 1665 "assemble.tab.c"
    break;

  case 16: /* intrucciones: NOTB error  */
#line 520 "assemble.y"
                                                        {if(pre==1){
				errores= 301;
	}}
#line 1673 "assemble.tab.c"
    break;

  case 17: /* intrucciones: LD direccion  */
#line 523 "assemble.y"
                                    {
		if(pre==0){
			modificar_acumulador(memoria[direccionador].palabra);
			printf("REGISTRO: %i\n",acumulador);
		}
	}
#line 1684 "assemble.tab.c"
    break;

  case 18: /* intrucciones: LD dato  */
#line 529 "assemble.y"
                                                        {
		if(pre==0){
			modificar_acumulador(memoria[(pc+1+A) & 0xFFFF].palabra);
			printf("REGISTRO: %i\n",acumulador);
		}
	}
#line 1695 "assemble.tab.c"
    break;

  case 19: /* intrucciones: LD error  */
#line 535 "assemble.y"
                                                        {if(pre==1){
				errores= 300;
	}}
#line 1703 "assemble.tab.c"
    break;

  case 20: /* intrucciones: ST direccion  */
#line 538 "assemble.y"
                                    {
		if(pre==0){
			escribir_memoria(direccionador, acumulador);
		}
		
	}
#line 1714 "assemble.tab.c"
    break;

  case 21: /* intrucciones: ST dato  */
#line 544 "assemble.y"
                                                        {
		if(pre==0){
			escribir_memoria((pc+1+A) & 0xFFFF, acumulador);
		}
	}
#line 1724 "assemble.tab.c"
    break;

  case 22: /* intrucciones: ST error  */
#line 549 "assemble.y"
                                                        {if(pre==1){
				errores= 300;
	}}
#line 1732 "assemble.tab.c"
    break;

  case 23: /* intrucciones: BR_FLAGS datoBR  */
#line 552 "assemble.y"
                                      {if(pre==0){
		if(compararFlags((yyvsp[-1].str))){
				pc=pc+A;
				banderaParaBranch=1;
		}
	}}
#line 1743 "assemble.tab.c"
    break;

  case 24: /* intrucciones: BR_FLAGS direccionBR  */
#line 558 "assemble.y"
                                      {if(pre==0){
		if(compararFlags((yyvsp[-1].str))){
			pc = direccionador - 1;
			banderaParaBranch=1;
		}
	}}
#line 1754 "assemble.tab.c"
    break;

  case 25: /* intrucciones: BR_FLAGS error  */
#line 564 "assemble.y"
                                                        {if(pre==1){
			errores= 300;
	}}
#line 1762 "assemble.tab.c"
    break;

  case 26: /* intrucciones: BR_FLAGS INVALIDO error  */
#line 567 "assemble.y"
                                                                {if(pre==1){
			errores= 300;
	}}
#line 1770 "assemble.tab.c"
    break;

  case 27: /* intrucciones: TRAP direccion  */
#line 570 "assemble.y"
                                    {if(pre==0){
		if((int)direccionador==33){
			//ESTO ES TRAP 21 -> OUT
			printf("\n%c\n",acumulador);
			banderaParaTrapDeSalida=1;
			
			
		}
		if((int)direccionador==35){
			//ESTO ES TRAP 23 -> IN
			banderaParaTrapDeEntrada = 1;
			
		}
		}
		if(pre==1){
			if((int)direccionador!=33 &&  (int)direccionador!=35){
					errores= 310;
			}
		}}
#line 1794 "assemble.tab.c"
    break;

  case 28: /* intrucciones: TRAP error  */
#line 589 "assemble.y"
                                                        {if(pre==1){
				errores= 310;
	}}
#line 1802 "assemble.tab.c"
    break;

  case 29: /* intrucciones: error  */
#line 592 "assemble.y"
                        {if(pre==1){
				errores= 315;
	}}
#line 1810 "assemble.tab.c"
    break;

  case 30: /* reservas: '.' ORIG HEXA  */
#line 597 "assemble.y"
                                   {if(pre==1){
		codigo_inicio = 0;
		origen=strtol((yyvsp[0].str)+1, NULL,16);
	}}
#line 1819 "assemble.tab.c"
    break;

  case 31: /* reservas: '.' ORIG error  */
#line 601 "assemble.y"
                                    {if(pre==1){
        	errores= 311;
		}
		}
#line 1828 "assemble.tab.c"
    break;

  case 32: /* reservas: '.' END  */
#line 605 "assemble.y"
                                        {if(pre==1){
		fin= 7; //tengo tiempo, para saber
		memoria[pc].tipo = CELDA_FIN;
		}else{
		fin= 7;
			errores = 1;
	}
	}
#line 1841 "assemble.tab.c"
    break;

  case 33: /* reservas: ETIQUETA '.' FILL datoFill  */
#line 613 "assemble.y"
                                            {if(pre==1){
		registrar_etiqueta((yyvsp[-3].str), pc);
	}}
#line 1849 "assemble.tab.c"
    break;

  case 34: /* reservas: ETIQUETA '.' BLKW  */
#line 616 "assemble.y"
                                                 {if(pre==1){
		registrar_etiqueta((yyvsp[-2].str), pc);
	}}
#line 1857 "assemble.tab.c"
    break;

  case 35: /* datoFill: NUMERO  */
#line 620 "assemble.y"
               {
		if(pre==1) {
			datardo = atoi((yyvsp[0].str)+1);
			if (datardo > 32767 || datardo < -32768) {
				errores = 212;
			}
		}
	}
#line 1870 "assemble.tab.c"
    break;

  case 36: /* datoFill: ERROR_NUMERO  */
#line 628 "assemble.y"
                       {
		errores = 312;
	}
#line 1878 "assemble.tab.c"
    break;

  case 37: /* dato: NUMERO  */
#line 633 "assemble.y"
               {
        if(pre==0) {
            A = atoi((yyvsp[0].str)+1);
        }
        if(pre==1) {
            datardo = atoi((yyvsp[0].str)+1);
            if (datardo > 2047 || datardo <-2048) { 
					errores= 313;
            }
        }
    }
#line 1894 "assemble.tab.c"
    break;

  case 38: /* dato: ERROR_NUMERO  */
#line 644 "assemble.y"
                   {
        	errores= 312;
    }
#line 1902 "assemble.tab.c"
    break;

  case 39: /* datoBR: NUMERO  */
#line 649 "assemble.y"
               {
        if(pre==0) {
            A = atoi((yyvsp[0].str)+1);
        }
        if(pre==1) {
            datardo = atoi((yyvsp[0].str)+1);
            if (datardo > 511 || datardo <-512) { //cambiamos de 512 a 1024
					errores= 310;
            }
        }
    }
#line 1918 "assemble.tab.c"
    break;

  case 40: /* datoBR: ERROR_NUMERO  */
#line 660 "assemble.y"
                   {
        	errores= 312;
    }
#line 1926 "assemble.tab.c"
    break;

  case 41: /* direccion: HEXA  */
#line 667 "assemble.y"
                                  {
		if(pre==1){direccionador=strtol((yyvsp[0].str)+1, NULL,16);
		if (direccionador>65536 || direccionador<0) { // agregue || direccionador<0
			errores= 211;
		}
		}
		if(pre==0){direccionador=strtol((yyvsp[0].str)+1, NULL,16);}
		
	}
#line 1940 "assemble.tab.c"
    break;

  case 42: /* direccion: ETIQUETA  */
#line 676 "assemble.y"
                                       {
		if(pre==0){
			direccionador = buscarDireccionEtiqueta((yyvsp[0].str));
			if(direccionador==-1){
					errores= 314;
					YYABORT;
			}
		}
	}
#line 1954 "assemble.tab.c"
    break;

  case 43: /* direccionBR: HEXA  */
#line 687 "assemble.y"
                                  {
		if(pre==1){direccionador=strtol((yyvsp[0].str)+1, NULL,16);
		
		if (direccionador>65536 || direccionador<0) { // agregue || direccionador<0
				errores= 211;
		}
		//ESTE ES EL ERROR PARA CUANDO EL OFFSET DEL BR ES MAS QUE 9 bits 

		if(direccionador - pc > 511 || direccionador - pc < -512){ //cambiamos de 512 a 1024
			if (65535-(direccionador-pc) > 512 && (direccionador-pc)+65535 > 511){
				errores= 318;
			}
		}
		}
		if(pre==0){direccionador=strtol((yyvsp[0].str)+1, NULL,16);}
		
	}
#line 1976 "assemble.tab.c"
    break;

  case 44: /* direccionBR: ETIQUETA  */
#line 704 "assemble.y"
                                       {
		if(pre==0){
			direccionador = buscarDireccionEtiqueta((yyvsp[0].str));
			if(direccionador==-1){
					errores= 314;
					YYABORT;
			}
		}
	}
#line 1990 "assemble.tab.c"
    break;


#line 1994 "assemble.tab.c"

      default: break;
    }
  /* User semantic actions sometimes alter yychar, and that requires
     that yytoken be updated with the new translation.  We take the
     approach of translating immediately before every use of yytoken.
     One alternative is translating here after every semantic action,
     but that translation would be missed if the semantic action invokes
     YYABORT, YYACCEPT, or YYERROR immediately after altering yychar or
     if it invokes YYBACKUP.  In the case of YYABORT or YYACCEPT, an
     incorrect destructor might then be invoked immediately.  In the
     case of YYERROR or YYBACKUP, subsequent parser actions might lead
     to an incorrect destructor call or verbose syntax error message
     before the lookahead is translated.  */
  YY_SYMBOL_PRINT ("-> $$ =", YY_CAST (yysymbol_kind_t, yyr1[yyn]), &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;

  *++yyvsp = yyval;

  /* Now 'shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */
  {
    const int yylhs = yyr1[yyn] - YYNTOKENS;
    const int yyi = yypgoto[yylhs] + *yyssp;
    yystate = (0 <= yyi && yyi <= YYLAST && yycheck[yyi] == *yyssp
               ? yytable[yyi]
               : yydefgoto[yylhs]);
  }

  goto yynewstate;


/*--------------------------------------.
| yyerrlab -- here on detecting error.  |
`--------------------------------------*/
yyerrlab:
  /* Make sure we have latest lookahead translation.  See comments at
     user semantic actions for why this is necessary.  */
  yytoken = yychar == YYEMPTY ? YYSYMBOL_YYEMPTY : YYTRANSLATE (yychar);
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
      yyerror (YY_("syntax error"));
    }

  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
         error, discard it.  */

      if (yychar <= YYEOF)
        {
          /* Return failure if at end of input.  */
          if (yychar == YYEOF)
            YYABORT;
        }
      else
        {
          yydestruct ("Error: discarding",
                      yytoken, &yylval);
          yychar = YYEMPTY;
        }
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:
  /* Pacify compilers when the user code never invokes YYERROR and the
     label yyerrorlab therefore never appears in user code.  */
  if (0)
    YYERROR;
  ++yynerrs;

  /* Do not reclaim the symbols of the rule whose action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;      /* Each real token shifted decrements this.  */

  /* Pop stack until we find a state that shifts the error token.  */
  for (;;)
    {
      yyn = yypact[yystate];
      if (!yypact_value_is_default (yyn))
        {
          yyn += YYSYMBOL_YYerror;
          if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYSYMBOL_YYerror)
            {
              yyn = yytable[yyn];
              if (0 < yyn)
                break;
            }
        }

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
        YYABORT;


      yydestruct ("Error: popping",
                  YY_ACCESSING_SYMBOL (yystate), yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", YY_ACCESSING_SYMBOL (yyn), yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturnlab;


/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturnlab;


/*-----------------------------------------------------------.
| yyexhaustedlab -- YYNOMEM (memory exhaustion) comes here.  |
`-----------------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  goto yyreturnlab;


/*----------------------------------------------------------.
| yyreturnlab -- parsing is finished, clean up and return.  |
`----------------------------------------------------------*/
yyreturnlab:
  if (yychar != YYEMPTY)
    {
      /* Make sure we have latest lookahead translation.  See comments at
         user semantic actions for why this is necessary.  */
      yytoken = YYTRANSLATE (yychar);
      yydestruct ("Cleanup: discarding lookahead",
                  yytoken, &yylval);
    }
  /* Do not reclaim the symbols of the rule whose action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
                  YY_ACCESSING_SYMBOL (+*yyssp), yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif

  return yyresult;
}

#line 713 "assemble.y"

	
	void yyerror(const char *msje) {
		printf("%s\n", msje);
	}
	
	int main(){
		yyparse();
	}
