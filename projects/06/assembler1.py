#!/usr/bin/env python3

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
        return line[1:]
    else:
        return line[1:-1]

def dest (line):
    if '=' not in line:
        return None
    else:
        return line[:line.index('=')]

def comp ():
    if '=' in line:
        return line[line.index('=')+1:]
    elif ';' in line:
        return line[:line.index(';')]
    else:
        print ("Error with the format of the line: ", line)
        sys.exit()

def jump ():
    if ';' not in line:
        return None
    else:
        return line[line.index('=')+1:]

def bin_dest(nm):

def bin_comp(nm):

def bin_jump(nm):

def main(filename):
    fn = filename[:-3]+'out'

    with open (fn, 'r') as fi:

        fo = open (filename[:-3]+'hack', 'w')

        for line in fi:

            c_type = command_type(line)

            if (c_type=='A' or c_type=='L'):

                c_symbol = symbol(line)

            else:

                line_dest = dest(line)
                line_comp = comp(line)
                line_jump = jump(line)




        fo.close()

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print ('Usage: python rws.py inputfile.asm')
    elif len(sys.argv) == 2:
        remove(sys.argv[1], True)
        main()
    else:
        print ('Usage: python rws.py inputfile.asm')
