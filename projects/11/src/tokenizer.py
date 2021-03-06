#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

import re
import sys
from itertools import chain
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring
from xml.dom import minidom

string = r'(?:"[^"]*["])|(?:\'[^\']*[\'])'
comment = r'(?:(?:\/\*\*(?:.|\n)*?\*\/)|(?:\/\/[^\n]*\n))'
symbols = r'()[]{},;=.+-*/&|~<>'
delimiters = r'[\(\)\[\]\{\}\,\;\=\.\+\-\*\/\&\|\~\<\>]|'+string+'| *'
keywords = ('class','constructor','method','function','int','boolean','char','void',
            'var','static','field','let','do','if','else','while','return','true','false','null','this')
tokens = []
token_it = []

def read(filename):
    global tokens
    global token_it
    tokens = []
    token_it = []
    with open(filename, 'r') as f:
        tokenize_line(f.read())

def write_tokens(filename):
    with open (filename[:-5]+'T_sle.xml', 'w') as out_tok:
        out_tok.write('<tokens>\n')
        for pair in tokens:
            out_tok.write('<'+pair[0]+'> '+str(pair[1])+' </'+pair[0]+'>\n')
        out_tok.write('</tokens>\n')

def comp(filename, tree):
    '''
    Write the XML output file.
    Beware that it writes a file with the same name that the provided one. It
    will overwrite it if on the same folder
    '''

    out = open (filename[:-5]+'.xml', 'w')

    #out.write(tostring(tree, short_empty_elements=False))
    output = prettify(tree)

    #Fixes output to make it look like the test file

    # First line
    output = output.replace('<?xml version="1.0" ?>\n', '')

    # Empty tags
    output = output.replace('expressionList/', 'expressionList>\n</expressionList')
    output = output.replace('parameterList/', 'parameterList>\n</parameterList')

    out.write(output)
    out.close()

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    From: https://pymotw.com/2/xml/etree/ElementTree/create.html#building-element-nodes
    """
    rough_string = tostring(elem, 'utf-8', short_empty_elements=False)
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def tokenize_line(line):
    line = " ".join(re.sub(comment,"",line).split())
    line_tokens = [token for token in re.split(r'('+ delimiters + r')',line) if token not in ('', ' ')]
    for x in line_tokens:
        tok_type = token_type(x)
        tokens.append((tok_type, return_val(x, tok_type)))


def token_type(token):
    '''
    Returns the token type
    '''

    if token in keywords:
        return 'keyword'
    elif token in symbols:
        return 'symbol'
    elif isnum(token):
        return 'integerConstant'
    elif re.match(string,token):
        return 'stringConstant'
    else:
        return 'identifier'

def return_val(token, token_type):
    if token_type == 'stringConstant':
        return token[1:-1]
    elif token_type == 'integerConstant':
        return token
    else:
        return token

def isnum(string):
    '''
    Check if is an integer
    '''
    try:
        int(string)
        return True
    except ValueError:
        return False

def compiler(tree):
    '''
    Main compiler executioner.
    Called by the <class>
    '''

    tok_type, tok  = next(token_it)
    while (True):
        if tok in ['static','field']:
            compile_class_vardec(tree, tok_type, tok)
        elif tok in ['constructor','function','method']:
            compile_subroutine(tree, tok_type, tok)
        if tok=='}':
            temp = SubElement (tree, tok_type)
            temp.text = tok
            break
            #Cierre parentesis
        # else:
        #     print ('Error at compiler %s, %s', tok_type, tok)
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
        except: #This should bever happen
            print ('No next on compile_class_vardec')
            break
    #We still want the ';' to be classVarDec
    temp = SubElement (subR, tok_type)
    temp.text = tok

def compile_subroutine (tree, tok_type, tok):
    subR = SubElement(tree, 'subroutineDec')
    while (True):
        if (tok=='('):
            temp = SubElement (subR, tok_type)
            temp.text = tok
            tok_type, tok = compile_parameter_list(subR)
        temp = SubElement (subR, tok_type)
        temp.text = tok

        if (tok==')'):
            compile_subroutine_body (subR)
            break
        a, b = see_next()
        if (b=='}'):
            break
        tok_type, tok  = next(token_it)


def compile_subroutine_body(tree):

    subR = SubElement(tree, 'subroutineBody')
    tok_type, tok  = next(token_it)

    temp = SubElement (subR, tok_type)
    temp.text = tok #Opening '{'
    tok_type, tok  = next(token_it)

    while (tok=='var'):
        compile_var_dec (subR, tok_type, tok)
        tok_type, tok  = next(token_it)

    tok_type, tok = statements(subR, tok_type, tok)

    temp = SubElement (subR, tok_type)
    temp.text = tok #Closing '}'

def compile_var_dec(tree, tok_type, tok):
    subR = SubElement(tree, 'varDec')
    while (tok!=';'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        tok_type, tok  = next(token_it)
    temp = SubElement (subR, tok_type)
    temp.text = tok #';'
    #return tok_type, tok

def statements(tree, tok_type, tok):
    subR = SubElement(tree, 'statements')
    while (True):
        if (tok=='}'):
            break
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
        tok_type, tok  = next(token_it)
    return tok_type, tok


def compile_do(tree, tok_type, tok):
    subR = SubElement(tree, 'doStatement')
    while (tok!=';'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        if (tok=='('):
            compile_expression_list(subR)
        tok_type, tok  = next(token_it)
    temp = SubElement (subR, tok_type)
    temp.text = tok #';'

def compile_let(tree, tok_type, tok):
    subR = SubElement(tree, 'letStatement')
    while (True):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        if (tok=='=' or tok=='['):
            tok_type, tok = compile_expression(subR)
            temp = SubElement (subR, tok_type)
            temp.text = tok
        if (tok==';'):
            break
        tok_type, tok  = next(token_it)

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
    tok_type, tok = compile_expression(subR)

    # ')'
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    # '{'
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    tok_type, tok = statements(subR, tok_type, tok)

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
    tok_type, tok = compile_expression(subR)

    # ')'
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    # '{'
    temp = SubElement (subR, tok_type)
    temp.text = tok
    tok_type, tok  = next(token_it)

    tok_type, tok = statements(subR, tok_type, tok)

    # '}'
    temp = SubElement (subR, tok_type)
    temp.text = tok

    ##### NEW #####
    tok_type1, tok1  = see_next()
    if tok1 == 'else':
        tok_type, tok  = next(token_it)
        # else
        temp = SubElement (subR, tok_type)
        temp.text = tok
        tok_type, tok  = next(token_it)

        # '{'
        temp = SubElement (subR, tok_type)
        temp.text = tok
        tok_type, tok  = next(token_it)

        tok_type, tok = statements(subR, tok_type, tok)

        # '}'
        temp = SubElement (subR, tok_type)
        temp.text = tok

def compile_return(tree, tok_type, tok):

    subR = SubElement(tree, 'returnStatement')

    # return
    temp = SubElement (subR, tok_type)
    temp.text = tok

    tok_type, tok  = see_next()

    if (tok!=';'):
        tok_type, tok = compile_expression(subR)
    else:
        tok_type, tok  = next(token_it)

    # ';'
    temp = SubElement (subR, tok_type)
    temp.text = tok


def compile_expression(tree):
    subR = SubElement(tree, 'expression')
    compile_term(subR)
    tok_type, tok  = next(token_it)
    while (tok in '=+-*/&|~<>'):
        temp = SubElement (subR, tok_type)
        temp.text = tok
        compile_term(subR)
        tok_type, tok  = next(token_it)
    return tok_type, tok


def compile_term(tree):
    subR = SubElement(tree, 'term')
    tok_type, tok  = next(token_it)
    if tok_type in ['stringConstant','integerConstant','keyword']:
        temp = SubElement (subR, tok_type)
        temp.text = tok
    elif tok_type == 'symbol':
        if tok=='(':
            temp = SubElement (subR, tok_type)
            temp.text = tok # '('
            tok_type, tok = compile_expression(subR)

            temp = SubElement (subR, tok_type)
            temp.text = tok # ')'
        else:
            temp = SubElement (subR, tok_type)
            temp.text = tok # '-' | '~'
            compile_term(subR)

    elif tok_type == 'identifier':
        temp = SubElement (subR, tok_type)
        temp.text = tok
        tok_type, tok  = see_next()
        if tok == '[':
            tok_type, tok  = next(token_it)
            temp = SubElement (subR, tok_type)
            temp.text = tok
            tok_type, tok = compile_expression(subR)
            temp = SubElement (subR, tok_type)
            temp.text = tok # ')' | ']'
        elif tok == '(':
            tok_type, tok  = next(token_it)
            temp = SubElement (subR, tok_type)
            temp.text = tok
            compile_expression_list(subR)

            tok_type, tok  = next(token_it)

        elif tok == '.':
            tok_type, tok  = next(token_it)
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
    '''
    Helper function. Its a nasty hack so I tried as hard as possible to avoid
    using it, failing a couple of times at the end
    '''
    global token_it
    tok_type, tok  = next(token_it)
    token_it = chain([(tok_type, tok)], token_it)
    return tok_type, tok


def compile_expression_list(tree):
    global token_it
    subR = SubElement(tree, 'expressionList')
    tok_type, tok = see_next()
    if (tok==')'):
        return  #Empty expressionList case
    else:
        while (tok!=')'):
            tok_type, tok = compile_expression(subR)
            if (tok==','):
                temp = SubElement (subR, tok_type)
                temp.text = tok
        token_it = chain([(tok_type, tok)], token_it)
        # No need?
        #tok_type, tok  = next(token_it)

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
    #Key part. Create the iterator from the list
    global token_it
    token_it = iter(tokens)

    # Create root tree. Only 'Element'. The rest are SubElements
    tree = Element('class')

    tok = ''    #Initialize to nothing
    while (tok!='{'):
        tok_type, tok  = next(token_it)
        temp = SubElement (tree, tok_type)
        temp.text = tok
    compiler(tree)
    return tree

def run(name):
    read(name)
    tree = compile_class()
    comp (name, tree)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py inputfile.jack')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        run(name)
