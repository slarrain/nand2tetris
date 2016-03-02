import xml.etree.ElementTree as ET
from tokenizer import *

ops = {'=':'eq','+':'add','-':'sub','&':'and','|':'or','~':'not','<':'lt','>':'gt'}

class Compilator (object):

    def __init__ (self, tree, table, writer):
        self.tree = tree
        self.table  = table
        self.writer = writer
        self.className = ''
        self.funcName = ''
        self.n_if = 0
        self.n_while = 0

    def start(self, tree):

        #Assertion
        if self.tree.tag != 'class':
            print ('Error at start')

        for element in self.tree:

            # class name case
            if element.tag == 'identifier':
                # name = element.text
                self.className = element.text
            #
            # # class variable declarations cases
            # if element.tag == 'classVarDec':
            #     self.classVarDec (element)

            # subroutine's
            if element.tag == 'subroutineDec':
                self.compile_subroutine (element)

        self.writer.close()

        def compile_subroutine(self, tree):
            name = tree[2].text
            kind = tree[0].text

            self.writer.writeFunction(self.className+'.'+name, self.table.varCount('local', name))
            self.funcName = name
            if kind == 'constructor':              # if
                #count = self.table.varCount('field','outer')
                self.writer.writePush('constant',self.table.varCount('field'))
                self.writer.writeCall('Memory.alloc',1) ##allocate memory for object
                self.writer.writePop('pointer',0) ### assign pointer to object instance to pointer 0
            if kind == 'method':
                self.writer.writePush('argument',0) # if it's a method the first argument is
                self.writer.writePop('pointer',0)   # a pointer to 'this'

            state_tree = tree[-1].find('statements') #Should be tree[-1][1]
            self.compile_statements(state_tree)

        def compile_statements(self, tree):

            for element in tree:
                if element.tag == 'do':
                    self.compileDo(element)
                elif element.tag == 'let':
                    self.compileLet(element)
                elif element.tag == 'while':
                    self.compileWhile(element)
                elif element.tag == 'return':
                    self.compileReturn(element)
                elif element.tag == 'if':
                    self.compileIf(element)
                else:
                    raise Exception('%s should not begin a statement' %element.tag)

        def compile_expression(self, tree):

            if len(tree) == 1:
                self.compile_term(tree[0])
            else:
                op = None
                for element in tree:
                    if element.tag == 'term':
                        self.compile_term(element)
                    else:
                        if op not None:

                            if op == '/':
                                self.writer.writeCall('Math.divide',2)
                            elif op == '*':
                                self.writer.writeCall('Math.multiply',2)
                            else:
                                self.writer.writeArithmetic(ops[op])
                        op = element.text

                if op == '/':
                    self.writer.writeCall('Math.divide',2)
                elif op == '*':
                    self.writer.writeCall('Math.multiply',2)
                else:
                    self.writer.writeArithmetic(ops[op])


        def compile_expressionList(self, tree):
            expressions_tree = tree.findall('expression')
            for expression in expressions_tree:
                self.compile_expression(expression)

        def compile_subroutineCall(self, tree):
            explist_tree = tree.find('expressionList')
            count = len(explist_tree.findall('expression'))
            name = tree[0].text
            index = self.table.getindex(self.funcName, name)
            kind = self.table.getkind(self.funcName, name)
            sr_name = tree.findall('identifier')
            if len(sr_name)==2:  #className | varName . subroutineName case
                if kind in ('field','local','static'):
                    self.writer.writePush(kind,index)
                    count +=1
                ttype = self.table.getType(name)
                if ttype == None:
                    ttype = name
                self.writer.writeCall('%s.%s' %(ttype,sr_name[1].text),count)
            else:               # subroutineName (expression)   case`
                self.writer.writePush('pointer',0)
                count+=1
                self.compile_expressionList(explist_tree)
                self.writer.writeCall(self.className+'.'+name, count)

        def compile_term(self, tree):

            term = tree[0]

            if term.tag == 'integerConstant':
                self.writer.writePush('constant', term.text)

            elif term.tag == 'stringConstant':
                self.writer.writePush('constant',len(term.text))          # argument for String.new
                self.writer.writeCall('String.new',1)               # create empty string of length len(tok)
                for letter in term.text:
                    self.writer.writePush('constant',ord(letter))   # argument for String.appendChar
                    self.writer.writeCall('String.appendChar', 2)   # append each letter to string

            elif term.tag == 'keyword':
                if term.text in ['false','null']:
                    self.writer.writePush('constant',0)
                elif term.text == 'true':
                    self.writer.writePush('constant',0)
                    self.writer.writeArithmetic('not')
                elif term.text == 'this':
                    self.writer.writePush('pointer',0)             # so 'return this' actually returns the pointer
                else:
                    raise Exception('%s is not an acceptable term' %term.text)

            elif term.tag =='identifier':
                name = term.text
                # ####
                # index = self.table.subroutineTables[self.funcName][name][2]
                # kind = self.table.subroutineTables[self.funcName][name][1]

                index = self.table.getindex(self.funcName, name)
                kind = self.table.getkind(self.funcName, name)

                if len(tree) == 1:  #varName case
                     self.writer.writePush(kind,index)
                else:               # varName [expression] case
                    exp = tree.find('expression')
                    self.compile_expression(exp)

                    self.writer.writePush(kind,index)
                    self.writer.writeArithmetic('add')
                    self.writer.writePop('pointer',1)
                    self.writer.writePush('that',0)

            elif term.tag == 'symbol':
                if tree[1].tag == 'expression':
                    self.compileExpression(tree[1])
                elif tree[1].tag == 'term':
                    self.compile_term(tree[1])
                    if term.text == '-':
                        op = 'neg'
                    else:
                        op = 'not'
                    self.writer.writeArithmetic(op)
                else:
                    print ('Error inside term.symbol')
            else:
                print ("Error inside term")


        def compileDo(self, tree):
            self.compile_subroutineCall(tree)

        def compileLet(self, tree):
            name = tree[1].text

            index = self.table.getindex(self.funcName, name)
            kind = self.table.getkind(self.funcName, name)

            expressions = tree.findall('expression')

            if len(expressions)>1:      # 'let' varName ( '[' expression ']' )? '=' expression ';'
                self.compile_expression(expressions[0])
                self.writer.writePush(kind,index)
                self.writer.writeArithmetic('add') # add together index and base of array
                self.compile_expression(expressions[1])
                self.writer.writePop('temp',0)
                self.writer.writePop('pointer',1)
                self.writer.writePush('temp',0)
                self.writer.writePop('that',0)
            else:       #let varname = expression case
                self.compile_expression(expressions[0])
                self.writer.writePop(kind,index)

        def compileWhile(self, tree):
            label1 = 'WHILE_EXP%d' %self.whileNum
            label2 = 'WHILE_END%d' %self.whileNum
            self.n_while += 1
            self.writer.writeLabel(label1)              #WHILE_EXP
            self.compile_expression(tree.find('expression'))
            self.writer.writeArithmetic('not')          #compute ~(condition)
            self.writer.writeIf(label2)                 #if-goto WHILE_END
            self.compileStatements(tree.find('statements'))
            self.writer.writeGoto(label1)               #goto WHILE_EXP
            self.writer.writeLabel(label2)              #WHILE_END

        def compileReturn(self, tree):

        def compileIf(self, tree):
