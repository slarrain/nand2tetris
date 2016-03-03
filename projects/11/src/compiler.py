#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

import tokenizer as tk
import symbolTable as SymT
import compilator as comp
import VMWriter as writer
import sys
import glob

def run(name):
    tk.read(name)

    tree = tk.compile_class()
    #print (tree.getchildren())
    st = SymT.SymbolTable()
    st.start(tree)
    print (name)
    wrt = writer.VMWriter(name[:-5])
    engine = comp.Compilator(tree, st, wrt)
    engine.start()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Usage: python3 tokenizer.py [inputfile.jack | source/to/files/')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        if name.endswith('.jack'):
            filenames = [name]
        else:
            filenames = glob.glob(name+'*.jack')
        #print (filenames)
        for n in filenames:
            run(n)
