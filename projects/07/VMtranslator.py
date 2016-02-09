#!/usr/bin/env python3

#
#   Santiago Larrain
#   slarrain@uchicago.edu
#

arith = ['add','sub','neg','eq','gt','lt','and','or','not']
n = 0

def command_type(line):
    com = line[0]
    if com in arith:
        return "C_ARITHMETIC"
    else:
        return "C_"+com.uppercase()

def arg1(line):
    if command_type(line)=="C_RETURN":
        print "Error. C_RETURN"
    if command_type(line)=="C_ARITHMETIC":
        return line[0]
    else:
        return line[1]

def arg2(line):
    if command_type(line) in ['C_PUSH','C_POP','C_FUNCTION','C_CALL']:
        return int(line[2])
    else:
        print "Error. Invalid Call"
        return

def write_arithmetic (command):
    instructions = {
        'add':['@SP', 'MA=M-1', 'D=M', 'A=A+1', 'M=M-D'],
        'sub': ['@SP', 'MA=M-1', 'D=M', 'A=A-1', 'M=M-D'],
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
        'and':['@SP', 'MA=M-1', 'D=M', 'A=A+1', 'M=M&D'],
        'or':['@SP', 'MA=M-1', 'D=M', 'A=A+1', 'M=M|D'],
        'not':['@SP','A=M-1','M=!M']
                    }
    global n+=1
    return instructions[command]

def write_push_pop(command, segment, index):

    segs = {'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT'}

    push_end = ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    if segment=='constant':
        pre = ['A'+str(index), 'D=A']
    elif


    
