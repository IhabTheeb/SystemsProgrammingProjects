. full line comment – ignore
CSC_354:	START	#0
ONE:		BYTE	0X0F
TWO:		BYTE	0C>
THREE:		BYTE	0X26AE
FOUR:		BYTE	0C/-\
FIVE:		RESW	#3		. partial line comment - ignore
SIX:		WORD	#97
BUFFER:		RESB	#512
SEVEN:		EQU	#1024
BUFEND:		EQU	*
MAX:		EQU	BUFEND-BUFFER
		END	ONE
