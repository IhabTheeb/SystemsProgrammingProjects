CSC_354:  START     #0
FIRST:    RESW      #1
GO:       LDA       =0CABCDE
          LDA       =0X00ff
          +LDT      =0X02468A
SECOND:   BYTE      0Cxyz
THIRD:    RESB      #6
FOURTH:   BYTE      0X00FF
FIFTH:    BYTE      0Cxyz
          END       GO
