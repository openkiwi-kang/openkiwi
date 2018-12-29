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
        'SYN_FONT_P_LBRACE',
        'SYN_FONT_M_LBRACE',
        'SYN_HTML_LBRACE',
        'SYN_WIKI_LBRACE',
        'SYN_HIGHLIGHT_LBRACE',
        'SYN_FOLDING_LBRACE',
        'SYN_FONT_COLOR_LBRACE',
        'SYNTAX_BRACE',
        'TRI_LBRACE',
        'TRI_RBRACE',
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
        'HEX_COLOR',
        'NAME_COLOR',
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
    r"(\{\{\{)[^#+\-\{\}](?:.|\r|\n)*?(\}\}\})"
    t.value = t.value[3:-3]
    return t  

def t_SYN_FONT_P_LBRACE(t):
    r"\{\{\{+"
    print(t)
    global output
    output = output + "={{{+="

def t_SYN_FONT_M_LBRACE(t):
    r"\{\{\{-"
    print(t)
    global output
    output = output + "={{{-="

def t_SYN_HTML_LBRACE(t):
    r"\{\{\{\#\!(html|HTML|Html)"
    print(t)
    global output
    output = output + "={{{#!html="

def t_SYN_WIKI_LBRACE(t):
    r"\{\{\{\#\!(wiki|WIKI|Wiki)"
    print(t)
    global output
    output = output + "={{{#!wiki="

def t_SYN_HIGHLIGHT_LBRACE(t):
    r"\{\{\{\#\!(syntax|SYNTAX|Syntax)"
    print(t)
    global output
    output = output + "={{{#!highlight="

def t_SYN_FOLDING_LBRACE(t):
    r"\{\{\{\#\!(folding|FOLDING|Folding)"
    print(t)
    global output
    output = output + "={{{#!folding="

def t_SYN_FONT_COLOR_LBRACE(t):
    r"\{\{\{\#"
    print(t)
    global output
    output = output + "={{{#="

def t_TRI_LBRACE(t):
    r"\{\{\{"
    print(t)
    global output
    output = output + "={{{="

def t_TRI_RBRACE(t):
    r"\}\}\}"
    print(t)
    global output
    output = output + "=}}}="

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

def t_HEX_COLOR(t):
    r"\#[0-9a-fA-F]{6}"
    t.value = "#" + t.value
    return t

def t_NAME_COLOR(t):
    r'''(?:WHITE|White|white|
        SILVER|Silver|silver|
        GRAY|Gray|gray|
        BLACK|Black|black|
        RED|Red|red|
        MAROON|Maroon|maroon|
        YELLOW|Yellow|yellow|
        OLIVE|Olive|olive|
        LIME|Lime|lime|
        GREEN|Green|green|
        AQUA|Aqua|aqua|
        TEAL|Teal|teal|
        BLUE|Blue|blue|
        NAVY|Navy|navy|
        PUCHSIA|Puchsia|puchsia|
        PURPLE|Purple|purple)'''
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
                  | text_effect
                  | no_markup_expression
                  | font_p_expression
                  | font_m_expression
                  | html_expression
                  | wiki_expression
                  | highlight_expression
                  | folding_expression
                  | font_color_expression
                  | brace_expression'''

def p_no_markup_expression(p):
    '''no_markup_expression : SYNTAX_BRACE'''
    global output
    output = output + "\n<code>" + p[1] + "<\\code>\n"

def p_brace_expression(p):
    '''brace_expression : TRI_LBRACE expression TRI_RBRACE'''
    global output
    output = output + "\n<brace_expression>" + p[2] + "<\\brace_expression>\n"

def p_font_p_expression(p):
    '''font_p_expression : SYN_FONT_P_LBRACE NUMBER expression TRI_RBRACE'''
    global output
    output = output + "\n<font_p_expression>" + p[2] + "<\\font_p_expression>\n"

def p_font_m_expression(p):
    '''font_m_expression : SYN_FONT_M_LBRACE NUMBER expression TRI_RBRACE'''
    global output
    output = output + "\n<font_m_expression>" + p[2] + p[3] + "<\\font_m_expression>\n"

def p_html_expression(p):
    '''html_expression : SYN_HTML_LBRACE expression TRI_RBRACE'''
    global output
    output = output + "\n<html_style_expression>" + p[2] + "<\\html_style_expression>\n"

def p_wiki_expression(p):
    '''wiki_expression : SYN_WIKI_LBRACE expression TRI_RBRACE'''
    global output
    output = output + "\n<wiki_style_expression>" + p[2] + "<\\wiki_style_expression>\n"

def p_highlight_expression(p):
    '''highlight_expression : SYN_HIGHLIGHT_LBRACE expression TRI_RBRACE'''
    global output
    output = output + "\n<highlight_expression>" + p[2] + "<\\highlight_expression>\n"

def p_folding_expression(p):
    '''folding_expression : SYN_FOLDING_LBRACE expression TRI_RBRACE'''
    global output
    output = output + "\n<folding_expression>" + p[2] + "<\\folding_expression>\n"

def p_font_color_expression(p):
    '''font_color_expression : SYN_FONT_COLOR_LBRACE NAME_COLOR expression TRI_RBRACE
                            | SYN_FONT_COLOR_LBRACE HEX_COLOR expression TRI_RBRACE'''
    global output
    output = output + "\n<font_color_expression>" + p[2] + p[3] + "<\\font_color_expression>\n"


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
    output = output + "<h" + p[1][:1] + ">" + p[1][1:] + "</h" + p[1][:1] + "><br><hr>"

def p_text_effect(p):
    '''text_effect : TEXT_BOLD_ITALIC
                    | TEXT_BOLD
                    | TEXT_ITALIC
                    | TEXT_CANCEL1
                    | TEXT_CANCEL2
                    | TEXT_UNDERLINE
                    | TEXT_UPPER
                    | TEXT_LOWER'''
    global output
    output = output + p[1]

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
