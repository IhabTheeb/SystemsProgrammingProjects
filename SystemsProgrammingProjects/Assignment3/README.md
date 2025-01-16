## Assignment 3: Two-Pass Assembler (Pass 1)

### Description
The first pass of the two-pass assembler processes a SIC/XE source program to generate a symbol table, literal table, and intermediate file. It validates instructions, identifies errors, and calculates addresses.

### Features
- Processes a SIC/XE source program.
- Creates symbol and literal tables.
- Generates an intermediate file with line numbers and location counter (LC) values.
- Supports SIC/XE assembler directives.

### Input
1. Source program file (command-line argument).
   - Format: Free-format SIC/XE assembly instructions.

### How to Run
```bash
python pass1.py [source_file_name]
```

### Output
1. Symbol table.
2. Literal table.
3. Intermediate file: Contains source listing with LC values.

### Example Run
Source program:
```
COPY START 1000
LDA ALPHA
STA BETA
END
```

Output:
Symbol Table:
```
ALPHA: Address=1003
BETA: Address=1006
```

Intermediate File:
```
1000 COPY START 1000
1003 LDA ALPHA
1006 STA BETA
```

---
