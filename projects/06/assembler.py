#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

import sys
from rws import remove

djump = {None:"000", "JGT":"001", "JEQ":"010", "JGE":"011", "JLT":"100",
        "JNE":"101", "JLE":"110", "JMP":"111"}
ddest = {None:"000", "M":"001", "D":"010", "MD":"011", "A":"100",
        "AM":"101", "AD":"110", "AMD":"111"}
dcomp = {"0":"101010","1":"111111","-1":"111010","D":"001100","A":"110000",
        "!D":"001101","!A":"110001","-D":"001111","-A":"110011",
        "D+1":"011111","A+1":"110111","D-1":"001110","A-1":"110010",
        "D+A":"000010","D-A":"010011","A-D":"000111","D&A":"000000",
        "D|A":"010101","D|M":"010101","D&M":"000000","M-D":"000111",
        "D-M":"010011","D+M":"000010","M-1":"110010","M+1":"110111",
        "-M":"110011","!M":"110001","M":"110000"}

table ={"SP":"0", "LCL":"1","ARG":"2","THIS":"3","THAT":"4","R0":"0","R1":"1",
        "R2":"2","R3":"3","R4":"4","R5":"5","R6":"6","R7":"7","R8":"8",
        "R9":"9","R10":"10","R11":"11","R12":"12","R13":"13","R14":"14",
        "R15":"15","SCREEN":"16384","KBD":"24576"}

n_ram = 15

def command_type (line):
    '''
    Return the command type of a line: A, C or L
    '''
    if line[0]=='@':
        return 'A'
    elif line[0]=='(':
        return 'L'
    else:
        return 'C'

def symbol (line):
    '''
    Returns the symbol or decimal Xxx of the current command @Xxx or (Xxx).
    Should be called only when command_type()is A_COMMAND or L_COMMAND
    '''
    if line[0] == '@':
        #print (line)
        return line[1:]
    else:
        #print (line[1:-2])
        return line[1:-2]

def dest (line):
    '''
    Returns the "dest" mnemonic
    '''
    if '=' not in line:
        return None
    else:
        return line[:line.index('=')]

def comp (line):
    '''
    Returns the "comp" mnemonic
    '''
    if '=' in line:
        return line[line.index('=')+1:]
    elif ';' in line:
        return line[:line.index(';')]
    else:
        print ("Error with the format of the line: ", line)
        sys.exit()

def jump (line):
    '''
    Returns the "jump" mnemonic
    '''
    if ';' not in line:
        return None
    else:
        return line[line.index(';')+1:]

def defa(nm):
    '''
    Should 'a' be 1 or 0 ?
    '''
    a1 = ["D|M","D&M","M-D","D-M","D+M","M-1","M+1","-M","!M","M"]
    if nm in a1:
        return "1"
    else:
        return "0"

def populate_table(filename):
    '''
    First read of the file. Creates new variables for the Hash Table
    '''
    n = 0
    with open (filename, 'r') as fi:
        for line in fi:
            c_type= command_type(line)
            if c_type=='L':
                table[symbol(line)] = n
            else:
                n+=1

def check_symbol(symb):
    '''
    Checks if the xxx part of @xxx is a symbol and if it is, check if its
    in the table already or not
    '''
    if symb.isdigit():
        return symb
    else:
        if symb in table.keys():
            return table[symb]
        else:
            global n_ram
            n_ram = n_ram + 1
            table[symb] = n_ram
            return n_ram


def main(filename):
    '''
    Main function. Goes through every line and writes the binary code line
    on the hack file
    '''
    fn = filename[:-3]+'out'

    populate_table(fn)

    with open (fn, 'r') as fi:

        fo = open (filename[:-3]+'hack', 'w')

        for line in fi:

            line = line.split('\n', 1)[0]

            c_type = command_type(line)

            if c_type=='A':
                c_symbol = symbol(line)
                a_symbol = check_symbol(c_symbol)
                dataA = '0'+bin(int(a_symbol))[2:].zfill(15)
                fo.writelines(dataA+'\n')
            elif c_type=='C':
                line_dest = dest(line)
                line_comp = comp(line)
                line_jump = jump(line)

                bin_dest = ddest[line_dest]
                bin_comp = dcomp[line_comp]
                bin_jump = djump[line_jump]
                a = defa(line_comp)
                dataC = '111'+a+bin_comp+bin_dest+bin_jump

                fo.writelines(dataC+'\n')

            else:
                #L case
                #we skip this line
                continue
        fo.close()

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print ('Usage: python assembler.py inputfile.asm')
    elif len(sys.argv) == 2:
        remove(sys.argv[1], True)
        main(sys.argv[1])
    else:
        print ('Usage: python assembler.py inputfile.asm')
