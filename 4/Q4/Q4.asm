//Q4

@i
M=0
(LOOP)

@i
D=M
@5
D=D-A
@END
D;JEQ

@0
M=M+1

@i
M=M+1

@LOOP
0;JMP
(END)
@0
D=M
@1
M=D
(FINISH)
@FINISH
0;JMP