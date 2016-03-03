# Helper class
# Almost no changes from the API suggested by the book. Just small hacks in Push and Pop

class VMWriter(object):
    def __init__(self,name):
        self.outname = name + '.vm'
        self.outfile = open(self.outname, 'w')
    def writePush(self,segment,index):
        if segment == 'field': segment = 'this'
        if segment == 'var': segment = 'local'
        self.outfile.write('push %s %d\n' %(segment,index))
    def writePop(self,segment,index):
        if segment == 'field': segment = 'this'
        if segment == 'var': segment = 'local'
        self.outfile.write('pop %s %d\n' %(segment,index))
    def writeArithmetic(self,command):
        self.outfile.write('%s\n' %command)
    def writeLabel(self,label):
        self.outfile.write('label %s\n' %label)
    def writeGoto(self,label):
        self.outfile.write('goto %s\n' %label)
    def writeIf(self,label):
        self.outfile.write('if-goto %s\n' %label)
    def writeCall(self,name,nArgs):
        self.outfile.write('call %s %d\n' %(name,nArgs))
    def writeFunction(self,name,nLocals):
        self.outfile.write('function %s %s\n'%(name,nLocals))
    def writeReturn(self):
        self.outfile.write('return\n')
    def close(self):
        self.outfile.close()
