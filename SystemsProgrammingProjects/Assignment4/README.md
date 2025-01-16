## Assignment 4: Two-Pass Assembler (Pass 2)

### Description
The second pass of the assembler generates the final assembly listing and object program using the intermediate file from Pass 1. It also validates instructions and performs error checking.

### Features
- Produces an assembly listing with symbol table.
- Outputs an object program in SIC/XE format.
- Handles external references and relocatable addressing.

### Input
1. Intermediate file from Pass 1.
2. Opcode file: Contains mnemonic, opcode, and format.

### How to Run
```bash
python pass2.py [intermediate_file]
```

### Output
1. Assembly listing with symbol table.
2. Object program file (`.obj`).

### Example Output
Assembly Listing:
```
COPY START 1000
1003 LDA ALPHA
1006 STA BETA
Symbol Table:
- ALPHA: Address=1003
- BETA: Address=1006
```

Object Program:
```
H COPY 0000 0010
T 1000 03 00
T 1003 01 00
T 1006 02 00
E 1000
```

---
