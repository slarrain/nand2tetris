#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

import glob
import sys
from rws import remove

arith = ['add','sub','neg','eq','gt','lt','and','or','not']
n = 0

def command_type(line):
    com = line[0]
    if com in arith:
        return "C_ARITHMETIC"
    else:
        return "C_"+com.upper()

def arg1(line):
    #print (line)
    if command_type(line)=="C_RETURN":
        print ("Error. C_RETURN")
    if command_type(line)=="C_ARITHMETIC":
        return line[0]
    else:
        return line[1]

def arg2(line):
    if command_type(line) in ['C_PUSH','C_POP','C_FUNCTION','C_CALL']:
        return int(line[2])
    else:
        print ("Error. Invalid Call")
        return

def write_arithmetic (command):
    global n

    instructions = {
        'add':['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M+D'],
        'sub': ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M-D'],
        'gt':['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'D=M-D', '@FALSE'+str(n),'D;JLE',
                '@SP', 'A=M-1', 'M=-1', '@CONTINUE'+str(n), '0;JMP',
                '(FALSE'+str(n)+')','@SP', 'A=M-1', 'M=0', '(CONTINUE'+str(n)+')'],
        'lt':['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'D=M-D', '@FALSE'+str(n),'D;JGE',
                '@SP', 'A=M-1', 'M=-1', '@CONTINUE'+str(n), '0;JMP',
                '(FALSE'+str(n)+')','@SP', 'A=M-1', 'M=0', '(CONTINUE'+str(n)+')'],
        'eq':['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'D=M-D', '@FALSE'+str(n),'D;JNE',
                '@SP', 'A=M-1', 'M=-1', '@CONTINUE'+str(n), '0;JMP',
                '(FALSE'+str(n)+')','@SP', 'A=M-1', 'M=0', '(CONTINUE'+str(n)+')'],
        'neg': ['@SP', 'A=M-1', 'M=-M'],
        'and':['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M&D'],
        'or':['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M|D'],
        'not':['@SP','A=M-1','M=!M']
                    }

    n+=1
    return instructions[command]

def static_filename(filename):
    return filename.split('/')[-1][:-2]

def write_push_pop(command, segment, index, filename):

    segs = {'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT'}
    filename = static_filename(filename)
    if command == 'C_PUSH':
        push_end = ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        if segment=='constant':
            pre = ['@'+str(index), 'D=A']
        elif segment in segs.keys():
            pre = ['@'+segs[segment], 'D=M', '@'+str(index), 'A=D+A', 'D=M']
        elif segment == 'temp':
            pre = ['@5', 'D=M', '@'+str(index), 'A=D+A', 'D=M']
        elif segment == 'pointer':
            if index==0:
                v='THIS'
            elif index==1:
                v='THAT'
            pre = ['@'+v, 'D=M']
        elif segment=='static':
            pre = ['@'+filename+str(index), 'D=M']
        return pre+push_end

    elif command == 'C_POP':
        if segment == 'pointer':
            if index==0:
                v='THIS'
            elif index==1:
                v='THAT'
            rv = ['@SP', 'AM=M-1', 'D=M', '@'+v, 'M=D']
        elif segment in segs.keys():
            rv = ['@'+segs[segment], 'D=M', '@'+str(index), 'D=D+A', '@R13', 'M=D',
                    '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D']
        elif segment == 'temp':
            rv = ['@5', 'D=A', '@'+str(index), 'D=D+A', '@R13', 'M=D',
                    '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D']
        elif segment =='static':
            rv = ['@SP', 'AM=M-1', 'D=M', '@'+filename+str(index), 'M=D']

        return rv

def main(filenames):

    fo = open (filenames[0][:-2]+'asm', 'w')

    for filename in filenames:

        with open (filename, 'r') as fi:

            for line in fi:
                if line and line[0]!='/' and line!='\n':
                    line = line.split('\n', 1)[0].split(' ')

                    line_command = command_type(line)

                    if command_type(line)!="C_RETURN":
                        line_arg1 = arg1(line)
                    if line_command in ['C_PUSH','C_POP','C_FUNCTION','C_CALL']:
                        line_arg2 = arg2(line)

                    if line_command=="C_ARITHMETIC":
                        wl = write_arithmetic(line_arg1)
                        fo.writelines("%s\n" % l for l in wl)

                    elif line_command in ['C_PUSH','C_POP']:
                        wl = write_push_pop(line_command, line_arg1, line_arg2, filename)
                        fo.writelines("%s\n" % l for l in wl)

    fo.close()




if __name__ == '__main__':

    if len(sys.argv) != 2:
        print ('Usage: python3 VMtranslator.py inputfile.vm')
    elif len(sys.argv) == 2:
        name = sys.argv[1]
        if name.endswith('.vm'):
            filenames = [name]
        else:
            filename = glob.glob(name+'*.vm')
        main(filenames)


    
