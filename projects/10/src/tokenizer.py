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

tokens = []
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
        token_type = tok_type(x)
        tokens.append((tok_type, return_val(x, token_type)))
        print (x, tok_type(x))
    global i
    i = len(tokens)
    return tokens

def tok_type(token):

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

def compiler(filename):
    out = open (filename[:-4]+'.xml', 'w')

    out.close()

def compile():
    tree = Element ()

def compile_class():
    global i
    token_it = iter(tokens)
    tree = Element('class')

    i+=1

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py inputfile.jack')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        read(name)
