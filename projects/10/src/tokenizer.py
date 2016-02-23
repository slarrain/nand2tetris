import re
import sys
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

string = r'(?:"[^"]*["])|(?:\'[^\']*[\'])'
comment = r'(?:(?:\/\*\*(?:.|\n)*?\*\/)|(?:\/\/[^\n]*\n))'
symbols = r'()[]{},;=.+-*/&|~<>'
delimiters = r'[\(\)\[\]\{\}\,\;\=\.\+\-\*\/\&\|\~\<\>]|'+string+'| *'
keywords = ('class','constructor','method','function','int','boolean','char','void',
            'var','static','field','let','do','if','else','while','return','true','false','null','this')

keys = ["class", "function", "method", "static", "var", "boolean", "null", "this", "let", "do", "if", "else", "while", "return"]
okeys = ["constructor", "field", "void", "int", "true"]
dkeys = ["char", "false"]
ops =  ["{", "+", ".", "}",",", "(", ")", "[","]", "-", "*", "/", "&", "|", "&", "<", ">", "=", "~", ";"]

# TODO: Take comments /**

tokens = []
token_it = ()
i = 0

def read(filename):
    with open(filename, 'r') as f:
        for line in f:
            #Get rid of comments

            tokenize_line(line)

def tokenize_line(line):
    line = " ".join(re.sub(comment,"",line).split())
    line_tokens = [token for token in re.split(r'('+ delimiters + r')',line) if token not in ('', ' ')]
    for x in line_tokens:
        tok_type = token_type(x)
        tokens.append((tok_type, return_val(x, tok_type)))
        print (x, tok_type(x))
    global i
    i = len(tokens)
    return tokens

def token_type(token):

    if token in keywords:
        return 'KEYWORD'
    elif token in symbols:
        return 'SYMBOL'
    elif isnum(token):
        return 'INT_CONST'
    elif re.match(string,token):
        return 'STRING_CONST'
    else:
        return 'IDENTIFIER'

def return_val(token, token_type):
    if token_type == 'STRING_CONST':
        return token[1:-1]
    elif token_type == 'INT_CONST':
        return int(token)
    else:
        return token

def isnum(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def comp(filename):
    out = open (filename[:-4]+'.xml', 'w')

    out.close()

def compiler(tree):
    tok_type, tok  = next(token_it)
    while (True):
        if tok in ['static','field']:
            compile_class_vardec(tree, tok_type, tok)
        elif tok in ['constructor','function','method']:
            compile_subroutine(tree, tok_type, tok)
        else:
            #Cierre parentesis
        try:
            tok_type, tok  = next(token_it)
        except:
            break

def compile_class_vardec(tree, tok_type, tok):
    subR = SubElement(tree, 'classVarDec')
    while (tok != ';'):
        SubElement (subR, tok_type, text=tok)
        try:
            tok_type, tok  = next(token_it)
        except:
            break
    #We still want the ';' to be classVarDec
    SubElement (subR, tok_type, text=tok)

def compile_subroutine (tree, tok_type, tok):
    subR = SubElement(tree, 'subroutineDec')
    while (True):

        SubElement (subR, tok_type, text=tok)

        if (tok=='('):
            


def compile_class():
    global i
    token_it = iter(tokens)

    # if tok!='class':
    #     print ('Error on compile class')
    tree = Element('class')
    for j in range(2):
        tok_type, tok  = next(token_it)
        SubElement (tree, tok_type, text=tok)
    compiler(tree)


    i+=1

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py inputfile.jack')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        read(name)
