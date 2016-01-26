// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.

//Set RAM[2]=0
@2
M=0
//Check if RAM[1]==0
// If it is, go to end
@1
D=M
@END
D;JEQ
(START)
// SUM
@0
D=M
@2
M=M+D
// SUBSTRACT ONE TO RAM[1]
@1
M=M-1
//Check if RAM[1]==0
//If it is NOT, go to START
D=M
@START
D;JNE
(END)
