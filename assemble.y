//    ESM Simulator its a GUI for programing in assmbly of the ESMx16 ISA

//    Copyright © 2025 Cruz Thiago, Ryberg Brian, Meier Jonathan.

//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.

//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.

//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <https://www.gnu.org/licenses/>.

%{
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

/*
 * Detecta instrucciones o directivas cuyo operando fue escrito sin el
 * separador obligatorio. El lexer historico reconoce "ADD#-2" como los
 * tokens ADD y #-2, porque no conserva informacion sobre el espacio que habia
 * entre ambos. Esta validacion se ejecuta sobre la linea original antes de
 * enviarla a LEX/YACC, evitando que una sentencia invalida sea aceptada y que
 * Python termine representandola silenciosamente como una palabra cero.
 */
int validar_separacion_instruccion_operando(const char *linea){
	static const char *operaciones[] = {
		"ADD", "AND", "NOTA", "LD", "ST", "TRAP"
	};
	const char *cursor = linea;

	if (linea == NULL) {
		return 0;
	}

	while (*cursor != '\0') {
		while (*cursor != '\0' &&
			(isspace((unsigned char)*cursor) || *cursor == ';')) {
			cursor++;
		}
		if (*cursor == '\0' || (cursor[0] == '/' && cursor[1] == '/')) {
			break;
		}

		const char *fin_token = cursor;
		while (*fin_token != '\0' &&
			!isspace((unsigned char)*fin_token) && *fin_token != ';') {
			if (fin_token[0] == '/' && fin_token[1] == '/') {
				break;
			}
			fin_token++;
		}

		size_t longitud_token = (size_t)(fin_token - cursor);
		for (size_t i = 0;
			i < sizeof(operaciones) / sizeof(operaciones[0]);
			i++) {
			size_t longitud_operacion = strlen(operaciones[i]);
			if (longitud_token > longitud_operacion &&
				strncmp(cursor, operaciones[i], longitud_operacion) == 0 &&
				(cursor[longitud_operacion] == '#' ||
				 cursor[longitud_operacion] == 'x')) {
				return 321;
			}
		}

		/* Tambien se exige separacion en BR compacto y directivas con dato. */
		if (longitud_token > 2 && strncmp(cursor, "BR", 2) == 0) {
			for (const char *caracter = cursor + 2; caracter < fin_token; caracter++) {
				if (*caracter == '#' || *caracter == 'x') {
					return 321;
				}
			}
		}
		if ((longitud_token > 5 && strncmp(cursor, ".ORIG", 5) == 0 &&
			 cursor[5] == 'x') ||
			(longitud_token > 5 && strncmp(cursor, ".FILL", 5) == 0 &&
			 cursor[5] == '#')) {
			return 321;
		}

		cursor = fin_token;
	}

	return 0;
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

			int error_separacion = validar_separacion_instruccion_operando(linea);
			if (error_separacion != 0) {
				fclose(archivo);
				return (errores = error_separacion);
			}

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
		int error_separacion = validar_separacion_instruccion_operando(linea);
		if (error_separacion != 0) {
			fclose(archivo);
			return (errores = error_separacion);
		}

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
			} else if (vector == 0x25u) {
				/* HALT es el alias de TRAP x25 y finaliza normalmente. */
				pc = pc_siguiente;
				return 1;
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
%}

%union {
	int intval;
	char *str;
}

%token <str> ADD AND NOTA NOTB LD ST BR_FLAGS TRAP END ORIG FILL BLKW ETIQUETA NUMERO HEXA ERROR_NUMERO INVALIDO
	
	%type <str> intrucciones
	%type <str> reservas
	%type <str> dato
	%type <str> datoFill
	%type <str> direccion
	
	%start prog
	
	%%
prog:
		%empty
		|   prog intrucciones '\n'{printf("\n");
		//ACA SAQUE EL IF Y EL GETCHAR
	}
	|   prog ETIQUETA intrucciones '\n' {if(pre==1){
		registrar_etiqueta($2, pc);
		}
	}
	|	prog reservas '\n' {}
	|	prog INVALIDO {
		if(pre==1){
			/* Conservar errores especificos informados por el lexer. */
			if (errores == 0) {
				errores= 315;
			}
		}
	} 
;

intrucciones:
	ADD dato                    {if(pre==0){
		printf("REGISTRO: %i\n",acumulador);
		acumulador = overflow(acumulador);
		}
	}
	|   ADD direccion           {if(pre==0){
		modificar_acumulador(acumulador + memoria[direccionador].palabra);
		printf("REGISTRO: %i\n",acumulador);
		acumulador = overflow(acumulador);
	}}
	|	ADD error				{if(pre==1){
			errores= 300;
	}}
	|   AND dato                {if(pre==0){
		modificar_acumulador(acumulador & A);
		printf("REGISTRO: %i\n",acumulador);
	}
	}
	|   AND direccion           {if(pre==0){
		modificar_acumulador(acumulador & memoria[direccionador].palabra);
		printf("REGISTRO: %i\n",acumulador);
	}}
	|	AND error				{if(pre==1){
			errores= 300;
	}}
	|   NOTA direccion          {if(pre==0){
		modificar_acumulador(~memoria[direccionador].palabra);
		printf("REGISTRO: %i\n",acumulador);
	}}
	|	NOTA error				{if(pre==1){
			errores= 303;
	}}
	|   NOTB                    {if(pre==0){
		modificar_acumulador(~acumulador);
		printf("REGISTRO: %i\n",acumulador);

	}}
	|	NOTB error				{if(pre==1){
				errores= 301;
	}}
	|   LD direccion            {
		if(pre==0){
			modificar_acumulador(memoria[direccionador].palabra);
			printf("REGISTRO: %i\n",acumulador);
		}
	}
	| 	LD dato					{
		if(pre==0){
			modificar_acumulador(memoria[(pc+1+A) & 0xFFFF].palabra);
			printf("REGISTRO: %i\n",acumulador);
		}
	}
	|	LD error				{if(pre==1){
				errores= 300;
	}}
	|   ST direccion            {
		if(pre==0){
			escribir_memoria(direccionador, acumulador);
		}
		
	}
	|	ST dato					{
		if(pre==0){
			escribir_memoria((pc+1+A) & 0xFFFF, acumulador);
		}
	}
	|	ST error				{if(pre==1){
				errores= 300;
	}}
	|   BR_FLAGS datoBR           {if(pre==0){
		if(compararFlags($1)){
				pc=pc+A;
				banderaParaBranch=1;
		}
	}}
	|   BR_FLAGS direccionBR      {if(pre==0){
		if(compararFlags($1)){
			pc = direccionador - 1;
			banderaParaBranch=1;
		}
	}}
	|	BR_FLAGS error				{if(pre==1){
			errores= 300;
	}}
	|	BR_FLAGS INVALIDO error				{if(pre==1){
			errores= 300;
	}}
	|   TRAP direccion          {if(pre==0){
		if((int)direccionador==33){
			//ESTO ES TRAP 21 -> OUT
			printf("\n%c\n",acumulador);
			banderaParaTrapDeSalida=1;
			
			
		}
		if((int)direccionador==35){
			//ESTO ES TRAP 23 -> IN
			banderaParaTrapDeEntrada = 1;
			
		}
		if((int)direccionador==37){
			// TRAP x25 -> HALT
			errores = 1;
		}
		}
		if(pre==1){
			if((int)direccionador!=33 && (int)direccionador!=35 &&
			   (int)direccionador!=37){
					errores= 310;
			}
		}}
	|	TRAP error				{if(pre==1){
				errores= 310;
	}}
	|	error	{if(pre==1){
				errores= 315;
	}}

reservas:
	'.' ORIG HEXA              {if(pre==1){
		codigo_inicio = 0;
		origen=strtol($3+1, NULL,16);
	}}
	|'.' ORIG error             {if(pre==1){
        	errores= 311;
		}
		}
	|   '.' END                     {if(pre==1){
		fin= 7; //tengo tiempo, para saber
		memoria[pc].tipo = CELDA_FIN;
		}else{
		fin= 7;
			errores = 1;
	}
	}
	|   ETIQUETA '.' FILL datoFill      {if(pre==1){
		registrar_etiqueta($1, pc);
	}} //sacar de aca etiqueta_key para la tabla de etiquetas y de abajo el tipo dato sacar el $2 que es el valor
	|   ETIQUETA '.' BLKW                    {if(pre==1){
		registrar_etiqueta($1, pc);
	}}
datoFill:
	NUMERO {
		if(pre==1) {
			datardo = atoi($1+1);
			if (datardo > 32767 || datardo < -32768) {
				errores = 212;
			}
		}
	}
	| ERROR_NUMERO {
		errores = 312;
	}

dato:
	NUMERO {
        if(pre==0) {
            A = atoi($1+1);
        }
        if(pre==1) {
            datardo = atoi($1+1);
            if (datardo > 2047 || datardo <-2048) { 
					errores= 313;
            }
        }
    }
    | ERROR_NUMERO {
        	errores= 312;
    }

datoBR:
	NUMERO {
        if(pre==0) {
            A = atoi($1+1);
        }
        if(pre==1) {
            datardo = atoi($1+1);
            if (datardo > 511 || datardo <-512) { //cambiamos de 512 a 1024
					errores= 310;
            }
        }
    }
    | ERROR_NUMERO {
        	errores= 312;
    }



direccion: //no imprime, porque? no se, fijate (arreglado)
	HEXA                      {
		if(pre==1){direccionador=strtol($1+1, NULL,16);
		if (direccionador>65536 || direccionador<0) { // agregue || direccionador<0
			errores= 211;
		}
		}
		if(pre==0){direccionador=strtol($1+1, NULL,16);}
		
	}
	|   ETIQUETA                   {
		if(pre==0){
			direccionador = buscarDireccionEtiqueta($1);
			if(direccionador==-1){
					errores= 314;
					YYABORT;
			}
		}
	}

direccionBR: //no imprime, porque? no se, fijate (arreglado)
	HEXA                      {
		if(pre==1){direccionador=strtol($1+1, NULL,16);
		
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
		if(pre==0){direccionador=strtol($1+1, NULL,16);}
		
	}
	|   ETIQUETA                   {
		if(pre==0){
			direccionador = buscarDireccionEtiqueta($1);
			if(direccionador==-1){
					errores= 314;
					YYABORT;
			}
		}
	}
%%
	
	void yyerror(const char *msje) {
		printf("%s\n", msje);
	}
	
	int main(){
		yyparse();
	}
