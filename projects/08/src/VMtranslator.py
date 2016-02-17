#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

import glob
import sys

arith = ['add','sub','neg','eq','gt','lt','and','or','not']
n = 0
line_counter = 0

def command_type(line):
    '''
    Returns the command type.
    Receives a list with the words of the line. Ex. [push, constant, 33]
    '''
    if line=='return':  #Return would be a string and not a list.
        return 'C_RETURN'   #line[0]=='r' and thats useless
    com = line[0]
    if com in arith:
        return "C_ARITHMETIC"
    elif com=="if-goto":
        return "C_IF"
    else:
        return "C_"+com.upper()

def arg1(line):
    '''
    Returns the first argument
    Receives a list with the words of the line. Ex. [push, constant, 33]
    '''
    if command_type(line)=="C_RETURN":
        print ("Error. C_RETURN")
    if command_type(line)=="C_ARITHMETIC":
        return line[0]
    else:
        return line[1]

def arg2(line):
    '''
    Returns the second arguments
    Receives a list with the words of the line. Ex. [push, constant, 33]
    '''
    if command_type(line) in ['C_PUSH','C_POP','C_FUNCTION','C_CALL']:
        return int(line[2])
    else:
        print ("Error. Invalid Call")
        return

def write_arithmetic (command):
    '''
    Uses dictionary to write arithmetic. Uses a global variables for unique
    labels
    Input is the command itself.
    '''
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
    '''
    returns the filename for when it has a path
    Input: a [path+]filename
    '''
    return filename.split('/')[-1][:-2]

def write_push_pop(command, segment, index, filename):
    '''
    Push Pop implementation.
    A little dictionaries but more lists
    The inputs are: the command, the segment, the index and the path+filename
    '''

    segs = {'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT'}
    filename = static_filename(filename)

    if command == 'C_PUSH':
        push_end = ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        if segment=='constant':
            pre = ['@'+str(index), 'D=A']
        elif segment in segs.keys():
            pre = ['@'+segs[segment], 'D=M', '@'+str(index), 'A=D+A', 'D=M']
        elif segment == 'temp':
            pre = ['@'+str(5+index), 'D=M']
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

def write_label (func_name, label):
    rv = ['('+func_name+'$'+label+')']
    return rv

def write_goto(func_name, label):
    rv = ["@"+func_name+'$'+label, "0;JMP"]
    return rv

def write_if(func_name, label):
    rv = ['@SP', 'AM=M-1', 'D=M', '@'+func_name+'$'+label, 'D;JNE']
    return rv

def write_call (function_name, num_args):
    global line_counter
    return_adress = function_name+'$'+str(line_counter)
    c0 = ['@'+return_adress, 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    c1 = write_push_pop ('C_PUSH', 'local', '0', 'irrelevant')
    c2 = write_push_pop ('C_PUSH', 'argument', '0', 'irrelevant')
    c3 = write_push_pop ('C_PUSH', 'this', '0', 'irrelevant')
    c4 = write_push_pop ('C_PUSH', 'that', '0', 'irrelevant')
    x = num_args+5
    c5 = ['@'+str(x),'D=A','@SP','D=M-D','@ARG','M=D']
    #c5 = ['@5','D=A','@'+num_args,'D=D+A','@SP','D=M-D','@ARG','M=D']
    c6 = ['@SP', 'D=M', '@LCL', 'M=D']
    c7 = ["@"+function_name, "0;JMP"]
    c8 = ['('+return_adress+')']
    rv = c0+c1+c2+c3+c4+c4+c5+c6+c7+c8
    return rv

def write_function (function_name, num_locals):
    f0 = ['('+function_name+')']
    f1 = write_push_pop ('C_PUSH', 'constant', 0, 'irrelevant')
    rv = f0+f1*num_locals
    return rv

def write_return():

    r0 = ['@LCL', 'D=M', '@R13', 'M=D']
    r1 = ['@5','D=A','@R13','A=M-D','D=M','@R14','M=D']
    r2 = ['@SP','AM=M-1','D=M','@ARG','A=M','M=D']
    r3 = ['@ARG', 'D=M+1', '@SP', 'M=D']
    r4 = ['@1','D=A','@R13','A=M-D','D=M','@THAT','M=D']
    r5 = ['@2','D=A','@R13','A=M-D','D=M','@THIS','M=D']
    r6 = ['@3','D=A','@R13','A=M-D','D=M','@ARG','M=D']
    r7 = ['@4','D=A','@R13','A=M-D','D=M','@LCL','M=D']
    r8 = ['@R14','A=M', '0;JMP']
    rv = r0+r1+r2+r3+r4+r5+r6+r7+r8
    #rv = r0+r1+r2+r3+r4+r5+r6+r7
    return rv

def bootstrap():
    b0 = ['@256', 'D=A', '@SP', 'M=D']
    b1 = write_call('Sys.Init', 0)
    rv = b0+b1
    return rv


def main(filenames, name):
    '''
    It executes the program.
    Input: a list of filenames
    '''
    global line_counter
    if len(filenames)==1:
        fn = filenames[0][:-3]
    else:
        fn = name + name.split('/')[-1]

    fo = open (fn+'.asm', 'w')

    #Bootstrap
    initl = bootstrap()
    fo.writelines("%s\n" % l for l in initl)

    #list of filenames with length = 1 or more
    for filename in filenames:

        with open (filename, 'r') as fi:

            for line in fi:
                line_counter+=1

                #Avoid comments and empty lines
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


                    #Project 8

                    #Program flow
                    elif line_command=='C_LABEL':
                        wl = write_label (func_name, line_arg1)
                        fo.writelines("%s\n" % l for l in wl)
                    elif line_command=='C_GOTO':
                        wl = write_goto (func_name, line_arg1)
                        fo.writelines("%s\n" % l for l in wl)
                    elif line_command=='C_IF':
                        wl = write_if (func_name, line_arg1)
                        fo.writelines("%s\n" % l for l in wl)

                    elif line_command=='C_RETURN':
                        wl = write_return()
                        fo.writelines("%s\n" % l for l in wl)
                    elif line_command=='C_FUNCTION':
                        func_name = static_filename(filename)+'$'+line_arg1
                        wl = write_function(func_name, line_arg2)
                        fo.writelines("%s\n" % l for l in wl)
                    elif line_command=='C_CALL':
                        wl = write_call(func_name, line_arg2)
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
            filenames = glob.glob(name+'*.vm')
        main(filenames, name)


    
