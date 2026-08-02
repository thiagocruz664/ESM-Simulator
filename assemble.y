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
//#define YYDEBUG 1
#include <ctype.h>
#include "assemble.tab.h"
int yylex(void);
void yyerror(const char *s);
	
//MAPA MEMORIA
#define max_caracter 100
#define tamMat 65536
char map_memory[tamMat][max_caracter];
int dato[tamMat];
int acumulador, pc, pre, etiqueta_key, A,fin,codigo_inicio,origen,datardo;

//MAPA ETIQUETAS
char *matriz_etiquetas_k[tamMat] ={0};
int matriz_etiquetas_d[tamMat] = {0};
int contador_matriz_etiquets = 0;

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
	for(int i=0; i<strlen(flagsIns);i++){
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
  	char* line = (char*)malloc(100);
  	strcpy(line, map_memory[pc_line]);
  	return line;
}

char* get_etiq(int pc_line){
	// Esta funcion devuelve la etiqueta que se encuentra en la posicion de memoria indicada por pc_line
	char* etiq = (char*)malloc(100);
	for (int i = 0; i < contador_matriz_etiquets; i++) {
		if (matriz_etiquetas_d[i] == pc_line) {
			strcpy(etiq, matriz_etiquetas_k[i]);
			return etiq;
		}
	}
	return NULL;
}

int buscarDireccionEtiqueta(char *etiqueta){
	for(int i=0; i<contador_matriz_etiquets;i++){
		if(strcmp(matriz_etiquetas_k[i],etiqueta)==0){
			return matriz_etiquetas_d[i];
		}
	}
	return -1;
}

int buscarDato(char *etiqueta){
	int dir=buscarDireccionEtiqueta(etiqueta);
	return dato[dir];
}

void reemplazar_linea_st(char *nueva_linea, int pc_reemplazo){
	strcpy(map_memory[pc_reemplazo], nueva_linea);
}

void modificar_matriz_dato(int nuevo_dato, int pc_mod){
	dato[pc_mod] = nuevo_dato;
	printf("SE COLOCO EL DATO %i en la posicion %i\n",dato[pc_mod],pc_mod);
}
//========================================	FIN FUNCIONES DE MEMORIA ========================================
//===========================================================================================================



//========================================================================================================
//========================================	FUNCIONES PRINCIPALES ========================================
void reset() {
	// Reinicia todas las variables y estructuras de datos a sus valores iniciales
    memset(map_memory, 0, sizeof(map_memory));
    memset(dato, 0, sizeof(dato));
    acumulador = 0;
    pc = 0;
    pre = 0;
    etiqueta_key = 0;
    A = 0;
    fin = 0;
	codigo_inicio = 7;
    origen = 0;
    datardo = 0;
    for (int i = 0; i < tamMat; i++) {
        matriz_etiquetas_k[i] = NULL; // Reiniciar punteros
        matriz_etiquetas_d[i] = 0; // Reiniciar enteros
    }
    contador_matriz_etiquets = 0;
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
            strcpy(map_memory[pc], linea);
        }

        // Envía la línea al analizador léxico/sintáctico
        set_input_from_memory(linea, line_path);
        yyparse();
        yylex();

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

    // Verifica que el PC se encuentre dentro del rango válido de memoria
    if (pc < 0 || pc >= tamMat) {
        return (errores = 210);
    }

    // Si se alcanzó el final del programa, informa que no quedan instrucciones
    if (pc == fin) {
        return 1;
    }

    // Obtiene la instrucción almacenada en la posición actual del PC
    char *valor = map_memory[pc];

    // Envía la instrucción al analizador léxico y sintáctico
    set_input_from_memory(valor, line_path);
    yyparse();
    yylex();

    // Si ocurrió un error durante el análisis, finalizar la ejecución
    if (errores != 0) {
        return errores;
    }

	// Mantener esta llamada por compatibilidad
	// Originalmente resolvía un problema durante la ejecución
	// Revisar antes de eliminar
    fflush(stdin);

    pc++;// Avanza el contador de programa
    if (pc >= tamMat) { // Si se alcanza el final de la memoria, vuelve al inicio
        pc = 0;
    }
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
	%type <str> direccion
	
	%start prog
	
	%%
prog:
	|   prog intrucciones '\n'{printf("\n");
		//ACA SAQUE EL IF Y EL GETCHAR
	}
	|   prog ETIQUETA intrucciones '\n' {if(pre==1){
		matriz_etiquetas_k[contador_matriz_etiquets]=$2;
		matriz_etiquetas_d[contador_matriz_etiquets]=pc;
		contador_matriz_etiquets++;
		}
	}
	|	prog reservas '\n' {}
	|	prog INVALIDO {
		if(pre==1){
			errores= 315;
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
		modificar_acumulador(acumulador + dato[direccionador]);
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
		modificar_acumulador(acumulador & dato[direccionador]);
		printf("REGISTRO: %i\n",acumulador);
	}}
	|	AND error				{if(pre==1){
			errores= 300;
	}}
	|   NOTA direccion          {if(pre==0){
		modificar_acumulador(~dato[direccionador]);
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
			modificar_acumulador(dato[direccionador]);
			printf("REGISTRO: %i\n",acumulador);
		}
	}
	| 	LD dato					{
		if(pre==0){
			modificar_acumulador(dato[pc+1+A]);
			printf("REGISTRO: %i\n",acumulador);
		}
	}
	|	LD error				{if(pre==1){
				errores= 300;
	}}
	|   ST direccion            {
		if(pre==0){
			//strcpy(map_memory[direccionador], "");
			dato[direccionador] = acumulador;
		}
		
	}
	|	ST dato					{
		if(pre==0){
			//strcpy(map_memory[pc+1+A], "");
			dato[pc+1+A] = acumulador;
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
		}
		if(pre==1){
			if((int)direccionador!=33 &&  (int)direccionador!=35){
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
		origen=strtol($3+1, '\0',16);
	}}
	|'.' ORIG error             {if(pre==1){
        	errores= 311;
		}
		}
	|   '.' END                     {if(pre==1){
		fin= 7; //tengo tiempo, para saber
		}else{
		fin= 7;
			errores = 1;
	}
	}
	|   ETIQUETA '.' FILL dato      {if(pre==1){
		matriz_etiquetas_k[contador_matriz_etiquets]=$1;
		matriz_etiquetas_d[contador_matriz_etiquets]=pc;
		contador_matriz_etiquets++;
	}} //sacar de aca etiqueta_key para la tabla de etiquetas y de abajo el tipo dato sacar el $2 que es el valor
	|   ETIQUETA '.' BLKW                    {if(pre==1){
		matriz_etiquetas_k[contador_matriz_etiquets]=$1;
		matriz_etiquetas_d[contador_matriz_etiquets]=pc;
		contador_matriz_etiquets++;
	}}

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
		if(pre==1){direccionador=strtol($1+1, '\0',16);
		if (direccionador>65536 || direccionador<0) { // agregue || direccionador<0
			errores= 211;
		}
		}
		if(pre==0){direccionador=strtol($1+1, '\0',16);}
		
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
		if(pre==1){direccionador=strtol($1+1, '\0',16);
		
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
		if(pre==0){direccionador=strtol($1+1, '\0',16);}
		
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