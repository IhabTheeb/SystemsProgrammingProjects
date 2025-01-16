PROG:     START     #0
FIRST:    LDB       #BUFFER
          BASE      BUFFER
          STL       RETADDR
          LDX       #3600
          SVC       #8
AGAIN:    STSW      BUFFER,X
          SHIFTL    S,#4
          JEQ       @AGAIN
BUFFER:   RESW      #1200
RETADDR:  RESB      #3
          END       FIRST
