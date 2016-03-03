#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

import xml.etree.ElementTree as ET
from tokenizer import *


class SymbolTable (object):

    def __init__ (self):
        self.classTable = {}
        self.subroutineTables = {}
        self.currentT = {}

    def start(self, tree):

        #Assertion
        if tree.tag != 'class':
            print ('Error at start')

        for element in tree:

            # class name case
            if element.tag == 'identifier':
                name = element.text
                self.classTable[name] = [name, 'class', 0]

            # class variable declarations cases
            if element.tag == 'classVarDec':
                self.classVarDec (element)

            # subroutine's
            if element.tag == 'subroutineDec':
                self.subroutineDec (element)

    def classVarDec(self, tree):
        '''
        Populates the table for class Var Dec's
        '''
        kind = tree[0].text
        ttype = tree[1].text
        for element in tree[2:]:
            if element.tag == 'identifier':
                name = element.text
                self.classTable[name] = [ttype, kind, self.varcount(kind)]

    def varcount(self, kind, table_name='class'):
        if table_name == 'class':
            table = self.classTable
        elif table_name==None:
            table = self.currentT
        else:
            table = self.subroutineTables[table_name]
        return len([k for [t, k, n] in table.values() if k == kind])

    def subroutineDec (self, tree):
        table = {}
        kind = tree[0].text
        ttype = tree[1].text
        name = tree[2].text

        self.subroutineTables[name] = table
        self.currentT = table

        #Regular case for cons, method, function
        self.classTable[name] = [ttype, kind, self.varcount(kind)]

        #parameter list
        param_list = tree.find('parameterList')

        # Solve case for 'this'
        if kind == 'method':
            table['this'] = [None, 'argument', 0]

        if len(param_list) != 0:    #if its not empty
            for i in range(len(param_list)):
                # Condition 2 and 3 solve the identifier identifier, case
                if param_list[i].tag == 'identifier' and i%3!=0 and i!=0:
                    name = param_list[i].text
                    ttype = param_list[i-1].text
                    kind = 'argument'
                    table[name] = [ttype, kind, self.varcount(kind, None)]

        self.subroutineBody (tree[-1])

    def not_in_table(name):
        if name in self.currentT or name in self.classTable:
            return False
        else:
            return True

    def subroutineBody (self, tree):
        varDec = tree.findall('varDec')
        if varDec is not None:
            self.vardec(varDec)

    def vardec (self, trees):
        '''
        Populates the table for Var Dec's in subroutineBody
        '''
        for varDec in trees:
            ttype = varDec[1].text
            kind = varDec[0].text
            for i in range(2, len(varDec)):
                if varDec[i].tag == 'identifier':
                    name = varDec[i].text
                    self.currentT[name] = [ttype, kind, self.varcount(kind, None)]

    def getindex(self, func, name):
        try:
            return self.subroutineTables[func][name][2]
        except KeyError:
            try:
                return self.classTable[name][2]
            except KeyError:
                return None
    def getkind(self, func, name):
        try:
            return self.subroutineTables[func][name][1]
        except KeyError:
            try:
                return self.classTable[name][1]
            except KeyError:
                return None

    def gettype(self, func, name):
        try:
            return self.subroutineTables[func][name][0]
        except KeyError:
            try:
                return self.classTable[name][0]
            except KeyError:
                return None


def run(name):
    read(name)
    tree = compile_class()
    st = SymbolTable()
    st.start(tree)
    print (st.classTable)
    print (st.subroutineTables)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py inputfile.jack')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        run(name)
