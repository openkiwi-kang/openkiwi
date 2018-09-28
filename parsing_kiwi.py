'''
MIT License

Copyright (c) 2018 openkiwi-kang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE
'''

import html
import re
import sys

import ply.lex as lex
import ply.yacc as yacc

output = ""

tokens = (
        'COMMENT',
        #'LBRACE', 'RBRACE',
        # SYNTAX
        #'SYNTAX_WIKISTYLE',
        #'SYNTAX_HIGHLIGHT',
        #'SYNTAX_FOLDING',
        'SYNTAX_BRACE',
        # MACRO
        'MACRO',
        # PARAGRAPH SIZE
        'PH_6','PH_5','PH_4','PH_3','PH_2','PH_1',
        'P_6','P_5','P_4','P_3','P_2','P_1',
        # TEXT STYLE
        'TEXT_BOLD_ITALIC',
        'TEXT_BOLD',
        'TEXT_ITALIC',
        'TEXT_CANCEL1',
        'TEXT_CANCEL2',
        'TEXT_UNDERLINE',
        'TEXT_UPPER',
        'TEXT_LOWER',
        # TABLE
        'TABLE',
        'NAME',
        'NUMBER',
        )


# Tokens

def t_COMMENT(t):
    r"[#]{2}.*"
    print(t)

#def t_LBRACE(t):
#    r"\{\{\{"
#    print(t)

#def t_RBRACE(t):
#    r"\}\}\}"
#    print(t)
    
#def t_SYNTAX_WIKISTYLE(t):
#    r"[\{]{3}\#\!(wiki|WIKI|Wiki)(.|\r|\n)*?[\}]{3}"
#    print(t)   

#def t_SYNTAX_HIGHLIGHT(t):
#    r"[\{]{3}\#\!(syntax|SYNTAX|Syntax)(.|\r|\n)*?[\}]{3}"
#    print(t)  

#def t_SYNTAX_FOLDING(t):
#    r"[\{]{3}\#\!(folding|FOLDING|Folding)(.|\r|\n)*?[\}]{3}"
#    print(t)  

def t_SYNTAX_BRACE(t):
    r"(\{\{\{)[^#+-\{\}](.|\r|\n)*?(\}\}\})"
    print(t)  

def t_PH_6(t):
    r"[=]{6}[#]\s.*?\s[#][=]{6}"
    t.value = "6" + t.value[8:-8]
    return t
def t_PH_5(t):
    r"[=]{5}[#]\s.*?\s[#][=]{5}"
    t.value = "5" + t.value[7:-7]
    return t
def t_PH_4(t):
    r"[=]{4}[#]\s.*?\s[#][=]{4}"
    t.value = "4" + t.value[6:-6]
    return t
def t_PH_3(t):
    r"[=]{3}[#]\s.*?\s[#][=]{3}"
    t.value = "3" + t.value[5:-5]
    return t
def t_PH_2(t):
    r"[=]{2}[#]\s.*?\s[#][=]{2}"
    t.value = "2" + t.value[4:-4]
    return t
def t_PH_1(t):
    r"[=]{1}[#]\s.*?\s[#][=]{1}"
    t.value = "1" + t.value[3:-3]
    return t
def t_P_6(t):
    r"[=]{6}\s.*?\s[=]{6}"
    t.value = "6" + t.value[7:-7]
    return t
def t_P_5(t):
    r"[=]{5}\s.*?\s[=]{5}"
    t.value = "5" + t.value[6:-6]
    return t
def t_P_4(t):
    r"[=]{4}\s.*?\s[=]{4}"
    t.value = "4" + t.value[5:-5]
    return t
def t_P_3(t):
    r"[=]{3}\s.*?\s[=]{3}"
    t.value = "3" + t.value[4:-4]
    return t
def t_P_2(t):
    r"[=]{2}\s.*?\s[=]{2}"
    t.value = "2" + t.value[3:-3]
    return t
def t_P_1(t):
    r"[=]{1}\s.*?\s[=]{1}"
    t.value = "1" + t.value[2:-2]
    return t

def t_MACRO(t):
    r"\[(?:.*)\]"
    return t

def t_TEXT_BOLD_ITALIC(t):
    r"[']{3}\s[']{2}[^']*[']{2}\s[']{3}"
    return t

def t_TEXT_BOLD(t):
    r"[']{3}([^']*)[']{3}"
    return t

def t_TEXT_ITALIC(t):
    r"[']{2}([^']*)[']{2}"
    return t

def t_TEXT_CANCEL1(t):
    r"[~]{2}([^~]*)[~]{2}"
    return t

def t_TEXT_CANCEL2(t):
    r"[-]{2}([^-]*)[-]{2}"
    return t

def t_TEXT_UNDERLINE(t):
    r"[_]{2}([^_]*)[_]{2}"
    return t

def t_TEXT_UPPER(t):
    r"[\^]{2}([^\^]*)[\^]{2}"
    return t

def t_TEXT_LOWER(t):
    r"[,]{2}([^,]*)[,]{2}"

def t_TABLE(t):
    r"[|]{2}.+[|]{2}"
    return t

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t

def t_newline(t):
    r"(?:[\r]?\n)+"
    temp = t.value.count("\n")
    t.lexer.lineno += t.value.count("\n")
    for dummy in range( 1, temp ):
        print("<br>")

t_ignore = " \t"

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lexer  = lex.lex()       # Return lexer object


# Parsing rules

def p_wikidoc(p):
    '''wikidoc  : wikidoc expression
                | expression'''

def p_expression(p):
    '''expression : paragraph
                  | SYNTAX_BRACE'''

#def p_syntax_brace(p):
#    '''syntax_brace : LBRACE syntax_brace RBRACE
#                    | LBRACE RBRACE'''

def p_paragraph(p):
    '''paragraph  : PH_6
                  | PH_5
                  | PH_4
                  | PH_3
                  | PH_2
                  | PH_1
                  | P_6
                  | P_5
                  | P_4
                  | P_3
                  | P_2
                  | P_1'''
    global output
    output = output + "<h" + p[1][:1] + ">" + p[1][1:] + "</h" + p[1][:1] + "><hr>"


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


# Build the lexer
import ply.yacc as yacc
parser = yacc.yacc()     # Return parser object


def parser_kiwi(title,input):
    global output
    output = ""
    data = html.escape(input)
    #data = re.sub('\r\n','\n',input)
    #data = re.sub('\n', '<br>', input)
    data = re.sub("&#x27;","'",input)
    # data = textprocessing(input)
    #print(input)s
    #output = "<h2>"+title+"</h2>\n"+"<p>"+input+"<p>"
    #output is output_html

    # Give the lexer some input
    # lexer.input(input)
    # Run the yacc parser
    parser.parse(input,lexer=lexer)
    return output

#def textprocessing(data):
    #temp = data
    #Bold
    #temp = re.sub('''[']{3}(?P<text>[^']*)[']{3}''',"<strong>\g<text></strong>",temp)
    #italic
    #temp = re.sub('''[']{2}(?P<text>[^']*)[']{2}''',"<em>\g<text></em>",temp)
    #strikethrough1
    #temp = re.sub('''[-]{2}(?P<text>[^-]*)[-]{2}''',"<del>\g<text></del>",temp)
    #strikethrough2
    #temp = re.sub('''[~]{2}(?P<text>[^~]*)[~]{2}''',"<del>\g<text></del>",temp)
    #underline
    #temp = re.sub('''[_]{2}(?P<text>[^_]*)[_]{2}''',"<u>\g<text></u>",temp)
    #return temp
