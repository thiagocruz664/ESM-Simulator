%{
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

#include <string.h>
#include <stdlib.h>
#define YYSTYPE char*
extern YYSTYPE yylval;
#include "assemble.tab.h" // Incluir el encabezado generado por Bison

static char* duplicar_texto(const char* texto) {
    size_t longitud = strlen(texto) + 1;
    char* copia = (char*)malloc(longitud);
    if (copia != NULL) {
        memcpy(copia, texto, longitud);
    }
    return copia;
}

%}

flags       (n|z|p|n(z|p)|z(n|p)|p(n|z)|nzp|npz|znp|zpn|pnz|pzn)
numero      [-]?[0-9]+
letra       [A-Z]+
hexa        [abcdef0-9]+
minusculas  [a-z]

%%

"ADD"       { return ADD; }
"AND"       { return AND; }
"NOTA"      { return NOTA; }
"NOTB"      { return NOTB; }
"LD"        { return LD; }
"ST"        { return ST; }
"BR"{flags}        {{ 
    char* temp = duplicar_texto(yytext+2);  // Saltar "BR"
    yylval = temp; 
    return BR_FLAGS; 
}}
"BR "{flags}        {{ 
    char* temp = duplicar_texto(yytext+3);  // Saltar "BR "
    yylval = temp; 
    return BR_FLAGS; 
}}
"TRAP"      { return TRAP; }
"END"       { return END; }
"ORIG"      { return ORIG; }
"FILL"      { return FILL; }
"BLKW"      { return BLKW; }

"."         { return '.'; }

"#"{numero}            { yylval = duplicar_texto(yytext); return NUMERO; }
{numero}                { yylval = duplicar_texto(yytext); return ERROR_NUMERO; }
"x"{hexa}              { yylval = duplicar_texto(yytext); return HEXA;}
{letra}({numero}?)  { yylval = duplicar_texto(yytext); return ETIQUETA; }
{minusculas}        {yylval = duplicar_texto(yytext); return INVALIDO;}

[\t]+;      // Ignorar espacios
\n          {return '\n';}; // Ignorar nueva línea
.           { /* Ignorar otros caracteres */ }
%%

// Función principal (opcional)
int yywrap() {
    return 1; // Indica que no hay más entradas
}
