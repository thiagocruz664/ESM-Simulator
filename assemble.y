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

	
#define max_caracter 100
#define tamMat 65536


	
//MAPA MEMORIA
char map_memory[tamMat][max_caracter];
int dato[tamMat];
int acumulador, pc, pre, etiqueta_key, A,fin,nofinoseainicio,origen,datardo;

//MAPA ETIQUETAS
char *matriz_etiquetas_k[65536] ={0};
int matriz_etiquetas_d[65536] = {0};
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
void set_input_from_memory(const char* linea,const char *line_path) {
	// fclose(stream);
   	// stream = fopen("./tempfile.tmp", "w+b");
	if (stream) {
        fclose(stream);
    }
	stream = fopen(line_path, "w+b");
    if (!stream) {
        perror("Error creando archivo temporal");
        return;
    }
	
    fwrite(linea, 1, strlen(linea), stream);
    rewind(stream);

    yyin = stream;
}

void bandera_check(){
	banderaParaTrapDeEntrada=0;
	banderaParaTrapDeSalida=0;
	banderaParaBranch=0;
}

int overflow(int value) {
	while (value > 32767) {
		value -= 65536;
	}
	while (value < -32768) {
		value += 65536;
	}
	return value;
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

void nzpeador(){
	// Forzar a 16 bits
    unsigned short acum16 = (unsigned short)(acumulador & 0xFFFF);

    // Interpretar como 16 bits con signo
    short acum_signed = (short)acum16;
	if(acum_signed<0){
			ALUFlags = "n";
		}else{
			if(acum_signed==0){
				ALUFlags = "z";
			}else{
				ALUFlags = "p";
			}
	}
}

void modificar_acumulador(int nuevo_valor){
	acumulador = nuevo_valor;
	nzpeador();
}

int compararFlags(char *flagsIns){
	for(int i=0; i<strlen(flagsIns);i++){
		if(ALUFlags[0]==flagsIns[i]){
			return 1;
		}
	}
	return 0;
}

void reemplazar_linea_st(char *nueva_linea, int pc_reemplazo){
	strcpy(map_memory[pc_reemplazo], nueva_linea);
}

void modificar_matriz_dato(int nuevo_dato, int pc_mod){
	dato[pc_mod] = nuevo_dato;
	printf("SE COLOCO EL DATO %i en la posicion %i\n",dato[pc_mod],pc_mod);
}

void reset() {
    memset(map_memory, 0, sizeof(map_memory));
    memset(dato, 0, sizeof(dato));
    acumulador = 0;
    pc = 0;
    pre = 0;
    etiqueta_key = 0;
    A = 0;
    fin = 0;
	nofinoseainicio = 7;
    origen = 0;
    datardo = 0;
    for (int i = 0; i < 65536; i++) {
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

int assemble(int lang,const char *file_path,const char *line_path){
	errores=0;
	langyacc=lang;
	reset();
	FILE *archivo;
	char linea[max_caracter];
	archivo = fopen(file_path, "r");
	if (archivo == NULL) {
		errores= 100;
		return errores;
	}
	pre=1;
	if (lang == 10){
		fgets(linea,sizeof(linea),archivo);
		printf("LINEA: %s\n",linea);
		set_input_from_memory(linea,line_path);
		yyparse();
		yylex();
		if (nofinoseainicio!=0){
			errores= 317;
			return errores;
		}
	}else{
		origen=12288; //x3000
	}
	if (errores!=0){
		return errores;
	}
	pc=origen;
	do {
		if (fgets(linea, sizeof(linea), archivo) != NULL) {
			if (pc < tamMat) {
				strcpy(map_memory[pc], linea);
			}
			set_input_from_memory(linea,line_path);
			yyparse(); 
			yylex();
			if (errores!=0){
				return errores;
			}
			//dato[pc] = datardo;
			//datardo=0;
			pc++;
			if(pc>65535){pc=0;};
		} else {
			break;
		}
	} while (fin != 7);
	if (fin!=7){
		errores=316;
	}
	fin=pc;
	pc=origen;
	acumulador = 0;
	pre = 0;
	fclose(archivo);
	return errores;
}

int stepin(int lang,const char *line_path){
	errores=0;
	langyacc=lang;
	char* valor;
	valor = map_memory[pc];
	if (pc>=0 && pc<=tamMat) {
		if(pc!=fin){
			if(valor!=NULL){
				set_input_from_memory(valor,line_path);
				yyparse();
				yylex();
				if (errores!=0){
					return errores;
				}
				fflush(stdin);
				pc++;
				if(pc>65535){pc=0;};
				printf("PC YACC: %i\n",pc);
				return 0;
			}
		} else {
			return 1;
		}
	} else{
		errores= 210;
	}
}


/*FUNCIONES PARA EL DICCIONARIO*/
char* get_line(int pc_line){
  	char* line = (char*)malloc(100);
  	strcpy(line, map_memory[pc_line]);
  	return line;
}

char* get_etiq(int pc_line){
	char* etiq = (char*)malloc(100);
	for (int i = 0; i < contador_matriz_etiquets; i++) {
		if (matriz_etiquetas_d[i] == pc_line) {
			strcpy(etiq, matriz_etiquetas_k[i]);
			return etiq;
		}
	}
	return NULL;
}

/*FUNCIONES PARA EL DICCIONARIO*/

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
		acumulador = acumulador + A;
		nzpeador();
		printf("REGISTRO: %i\n",acumulador);
		acumulador = overflow(acumulador);
		}
	}
	|   ADD direccion           {if(pre==0){
		acumulador = acumulador + dato[direccionador];
		nzpeador();
		printf("REGISTRO: %i\n",acumulador);
		acumulador = overflow(acumulador);
	}}
	|	ADD error				{if(pre==1){
			errores= 300;
	}}
	|   AND dato                {if(pre==0){
		acumulador = acumulador & A;
		nzpeador();
		printf("REGISTRO: %i\n",acumulador);
	}
	}
	|   AND direccion           {if(pre==0){
		acumulador = acumulador & dato[direccionador];
		nzpeador();
		printf("REGISTRO: %i\n",acumulador);
	}}
	|	AND error				{if(pre==1){
			errores= 300;
	}}
	|   NOTA direccion          {if(pre==0){
		acumulador = ~dato[direccionador];
		nzpeador();
		printf("REGISTRO: %i\n",acumulador);
	}}
	|	NOTA error				{if(pre==1){
			errores= 303;
	}}
	|   NOTB                    {if(pre==0){
		acumulador = ~acumulador;
		nzpeador();
		printf("REGISTRO: %i\n",acumulador);

	}}
	|	NOTB error				{if(pre==1){
				errores= 301;
	}}
	|   LD direccion            {
		if(pre==0){
			acumulador = dato[direccionador];
			nzpeador();
			printf("REGISTRO: %i\n",acumulador);
		}
	}
	| 	LD dato					{
		if(pre==0){
			acumulador = dato[pc+1+A];
			nzpeador();
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
		nofinoseainicio = 0;
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