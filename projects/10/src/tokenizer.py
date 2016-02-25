import re
import sys
from itertools import chain
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
# TODO: write to file

tokens = []
token_it = ()
i = 0

def read(filename):
    with open(filename, 'r') as f:
        for line in f:
            #Get rid of comments
            tokenize_line(line)

def write_tokens(filename):
    with open (filename[:-4]+'T_sle.xml', 'w') as out_tok:
        for pair in tokens:
            out_tok.write('<'+pair[0]+'> '+pair[1]+' </'+pair[0]+'>\n')

def comp(filename, tree):
    out = open (filename[:-4]+'_sle.xml', 'w')
    out.write(tostring(tree))
    out.close()

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
        return 'keyword'
    elif token in symbols:
        return 'symbol'
    elif isnum(token):
        return 'int_const'
    elif re.match(string,token):
        return 'string_const'
    else:
        return 'identifier'

def return_val(token, token_type):
    if token_type == 'string_const':
        return token[1:-1]
    elif token_type == 'int_const':
        return int(token)
    else:
        return token

def isnum(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def compiler(tree):
    tok_type, tok  = next(token_it)
    while (True):
        if tok in ['static','field']:
            compile_class_vardec(tree, tok_type, tok)
        elif tok in ['constructor','function','method']:
            compile_subroutine(tree, tok_type, tok)
        elif tok=='}':
            temp = SubElement (tree, tok_type)
            temp.text = tok
            #Cierre parentesis
        else:
            print ('Error at compiler %s, %s', %(tok_type, tok))
        try:
            tok_type, tok  = next(token_it)
        except:
            break

def compile_class_vardec(tree, tok_type, tok):
    subR = SubElement(tree, 'classVarDec')
    while (tok != ';'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        try:
            tok_type, tok  = next(token_it)
        except:
            print ('No next on compile_class_vardec')
            break
    #We still want the ';' to be classVarDec
    temp = SubElement (subR, tok_type)
    temp.text = tok

def compile_subroutine (tree, tok_type, tok):
    subR = SubElement(tree, 'subroutineDec')
    while (True):
        if (tok=='('):
            tok_type, tok = compile_parameter_list(subR)
        temp = SubElement (subR, tok_type)
        temp.text = tok
        if (tok==')'):
            compile_subroutine_body (subR)

        if (tok=='}'):
            break
        tok_type, tok  = next(token_it)

def compile_subroutine_body(tree):
    #No need for a while loop
    subR = SubElement(tree, 'subroutineBody')
    tok_type, tok  = next(token_it)

    temp = SubElement (subR, tok_type)
    temp.text = tok #Opening '{'
    tok_type, tok  = next(token_it)
    if (tok=='var'):
        compile_var_dec (SubR, tok_type, tok)

    tok_type, tok = statements(subR)
    temp = SubElement (subR, tok_type)
    temp.text = tok #Closing '}'
    #while (True):

def compile_var_dec(tree, tok_type, tok):
    subR = SubElement(tree, 'varDec')
    while (tok!=';'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        tok_type, tok  = next(token_it)
    temp = SubElement (subR, tok_type)
    temp.text = tok #';'
    #return tok_type, tok

def statements(tree):
    subR = SubElement(tree, 'statements')
    while (tok!='}'):
        tok_type, tok  = next(token_it)
        if (tok=='let'):
            compile_let(subR, tok_type, tok)
        elif (tok=='do'):
            compile_do(subR, tok_type, tok)
        elif (tok=='while'):
            compile_while(subR, tok_type, tok)
        elif (tok=='if'):
            compile_if(subR, tok_type, tok)
        elif (tok=='return'):
            compile_return(subR, tok_type, tok)

        #Beware
        elif (tok=='expression'):
            compile_expression(subR, tok_type, tok)
        elif (tok=='term'):
            compile_term(subR, tok_type, tok)
    return tok_type, tok


def compile_do(tree, tok_type, tok):
    subR = SubElement(tree, 'doStatement')
    while (tok!=';'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        if (tok=='('):
            tok_type, tok = compile_expression_list(SubR)
            temp = SubElement (subR, tok_type)
            temp.text = tok
        tok_type, tok  = next(token_it)
    temp = SubElement (subR, tok_type)
    temp.text = tok #';'

def compile_let(tree, tok_type, tok):
    subR = SubElement(tree, 'letStatement')
    while (tok!=';'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        if (tok=='='):
            tok_type, tok = compile_expression(SubR)
            temp = SubElement (subR, tok_type)
            temp.text = tok
        tok_type, tok  = next(token_it)
    temp = SubElement (subR, tok_type)
    temp.text = tok #';'

def compile_while(tree, tok_type, tok):
    subR = SubElement(tree, 'whileStatement')
    # while
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    # '('
    temp = SubElement (subR, tok_type)
    temp.text = tok

    # ( INSIDE )
    tok_type, tok = compile_expression(SubR)

    # ')'
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    # '{'
    temp = SubElement (subR, tok_type)
    temp.text = tok

    tok_type, tok = statements(subR)

    # '}'
    temp = SubElement (subR, tok_type)
    temp.text = tok

def compile_if(tree, tok_type, tok):

    subR = SubElement(tree, 'ifStatement')
    # if
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    # '('
    temp = SubElement (subR, tok_type)
    temp.text = tok

    # ( INSIDE )
    tok_type, tok = compile_expression(SubR)

    # ')'
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    # '{'
    temp = SubElement (subR, tok_type)
    temp.text = tok

    tok_type, tok = statements(subR)

    # '}'
    temp = SubElement (subR, tok_type)
    temp.text = tok

def compile_return(tree, tok_type, tok):

    subR = SubElement(tree, 'returnStatement')

    # return
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    if (tok!=';'):
        tok_type, tok = compile_expression(SubR)

    # ';'
    temp = SubElement (subR, tok_type)
    temp.text = tok


def compile_expression(tree):
    subR = SubElement(tree, 'expression')
    tok_type, tok = compile_term(subR)
    while (tok in '=+-*/&|~<>'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        compile_term(subR)
        tok_type, tok  = next(token_it)
    return tok_type, tok


def compile_term(tree):
    subR = SubElement(tree, 'term')
    tok_type, tok  = next(token_it)
    if tok_type in ['string_const','int_const','keyword']:
        temp = SubElement (subR, tok_type)
        temp.text = tok
    elif tok_type == 'symbol':
        if tok=='(':
            temp = SubElement (subR, tok_type)
            temp.text = tok # '('
            tok_type, tok = compile_expression(subR)

        temp = SubElement (subR, tok_type)
        temp.text = tok # ')' or '-' | '~'
    elif tok_type == 'identifier':
        temp = SubElement (subR, tok_type)
        temp.text = tok
        tok_type, tok  = next(token_it)
        if tok == '[':
            temp = SubElement (subR, tok_type)
            temp.text = tok
            tok_type, tok = compile_expression(subR)

            self.writeNextToken(']')
        elif tok == '(':
            temp = SubElement (subR, tok_type)
            temp.text = tok
            compile_expression_list(subR)

            tok_type, tok  = next(token_it)

            self.writeNextToken(')')
        elif tok == '.':
            temp = SubElement (subR, tok_type)
            temp.text = tok # '.'
            tok_type, tok  = next(token_it)

            temp = SubElement (subR, tok_type)
            temp.text = tok # 'subRoutinename-identifier'
            tok_type, tok  = next(token_it)

            temp = SubElement (subR, tok_type)
            temp.text = tok # '('

            compile_expression_list(subR)

            tok_type, tok  = next(token_it)

        temp = SubElement (subR, tok_type)
        temp.text = tok # ')' | ']'
    else:
        print ('Error on compile_term: %s, %s' % (tok_type, tok))

def see_next():
    tok_type, tok  = next(token_it)
    token_it = chain([[tok_type, tok]], token_it)
    return tok_type, tok


def compile_expression_list(tree):
    subR = SubElement(tree, 'expressionList')
    while (True):
        tok_type, tok = compile_expression(SubR)
        if (tok==')'):
            break
        if (tok==','):
            temp = SubElement (subR, tok_type)
            temp.text = tok

        # No need?
        #tok_type, tok  = next(token_it)

    return tok_type, tok

def compile_parameter_list (tree):
    subR = SubElement(tree, 'parameterList')
    while (True):
        tok_type, tok  = next(token_it)
        if (tok==')'):
            break
        temp = SubElement (subR, tok_type)
        temp.text = tok

    return tok_type, tok



def compile_class():
    token_it = iter(tokens)

    tree = Element('class')
    tok = ''
    while (tok!='{')
        tok_type, tok  = next(token_it)
        temp = SubElement (tree, tok_type)
        temp.text = tok
    compiler(tree)
    return tree

def run(name):
    read(name)

    #tree = compile_class()
    #comp (name, tree)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py inputfile.jack')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        run(name)
