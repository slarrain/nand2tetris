#!/usr/bin/env python3

from rws import remove


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


def comp ():

def jump ():


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
