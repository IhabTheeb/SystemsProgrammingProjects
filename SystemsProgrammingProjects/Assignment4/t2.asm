FA20_2:   START     #0
          EXTDEF    ONE,THREE
          EXTREF    TWO,FOUR
BEGIN:    +SSK      ONE
          +DIVF     TWO
          +WD       FOUR+#6
ONE:      WORD      THREE-TWO
THREE:    WORD      #97
          END       BEGIN
