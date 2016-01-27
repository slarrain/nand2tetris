
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

//Set counter at beggining of Screen
// We will use RAM[13] for help
@SCREEN
D=A
@13
M=D

//Check if Keyboard was pressed
(CHECK)
@KBD
D=M
@WHITE
D;JEQ


(BLACK)
// Check if all screen is black
@13	//Counter
D=M
@24575
D=D-A	//Last screen pixel
@CHECK
D;JGE

// If its not all black, keep blacking it
@13
A=M
D=1
M=D
// Add one to the counter
@13
M=M+1
@CHECK
D;JMP	//GO back to the loop

(WHITE)
// Check if all screen is white
@13	//Counter
D=M
@16384
D=D-A	//First screen pixel
@CHECK
D;JLT

// If its not all white, keep whitening back
@13
A=M
D=0
M=D
// Substract one to the counter
@13
M=M-1
@CHECK
D;JMP	//GO back to the loop

