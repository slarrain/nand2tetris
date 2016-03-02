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

    def varcount(self, kind, table='class'):
        if table_name == 'class':
            table = self.classTable
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

        # TODO: Solve this case
        #Constructor case has an extra identifier
        if kind == 'constructor':
            table[ttype] = [None, kind, self.varcount(kind, table)]
        #Regular case for cons, method, function
        table[name] = [ttype, kind, self.varcount(kind, table)]

        #parameter list
        param_list = tree.find('parameterList')

        # TODO: Solve case for 'this'

        if len(param_list) != 0:    #if its not empty
            for i in range(len(param_list)):
                if param_list[i].tag == 'identifier':
                    name = param_list[i].text
                    ttype = param_list[i-1].text
                    kind = 'argument'
                    table[name] = [ttype, kind, self.varcount(kind, table)]

        self.subroutineBody (tree[-1])

    def not_in_table(name):
        if name in self.currentT or name in self.classTable:
            return False
        else:
            return True

    def subroutineBody (self, tree):
        varDec = tree.findall('varDec')
        #print (varDec)
        if varDec is not None:
            self.vardec(varDec)

    def vardec (self, trees):
        '''
        Populates the table for Var Dec's in subroutineBody
        '''
        # TODO: Solve case var identifier identifier

        for varDec in trees:
            #print (varDec)
            ttype = varDec[0].text
            kind = varDec[1].text
            for i in range(len(varDec)):
                print (varDec[i])
                if varDec[i].tag == 'identifier':
                    name = varDec[i].text
                    self.currentT[name] = [ttype, kind, self.varcount(kind, self.currentT)]

    def getindex(self, func, name):
        try:
            return self.subroutineTables[func][name][2]
        except KeyError:
            return None

    def getkind(self, func, name):
        try:
            return self.subroutineTables[func][name][1]
        except KeyError:
            return None

    def getkind(self, func, name):
        try:
            return self.subroutineTables[func][name][0]
        except KeyError:
            return None


def run(name):
    read(name)
    tree = compile_class()
    st = SymbolTable()
    st.start(tree)
    print (st.classTable)
    for x in st.subroutineTables:
        print (st.subroutineTables[x])
    #print (st.subroutineTables)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py inputfile.jack')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        run(name)
