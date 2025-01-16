## Assignment 2: Operand Evaluation Module

### Description
This program evaluates the operand field of assembly language statements for the SIC/XE assembler. It processes symbols, numeric literals, and expressions while supporting various addressing modes and arithmetic operations.

### Features
- Evaluates expressions with a maximum of two operands.
- Supports addition (+) and subtraction (-).
- Handles literals and updates a literal table.
- Displays detailed error messages for invalid expressions.

### Input Files
1. `SYMS.DAT`: Contains symbols and their attributes.
   - Format: `SYMBOL VALUE RFLAG`
2. Expression file: Contains one expression per line.

### How to Run
1. Place `SYMS.DAT` and the expression file in the same directory as `main.py`.
2. Run the program:
   ```bash
   python main.py [expression_file_name]
   ```
   If no expression file is provided, the program will prompt for its name.

### Output
- Evaluates each expression and displays its value and attributes.
- Updates and displays the literal table.

### Example Run
Input `SYMS.DAT`:
```
RED: 13 TRUE
BLUE: 5 FALSE
```
Expression file:
```
RED+BLUE
#10
=0CABC
```

Output:
```
Expressions:
- RED+BLUE: Value=18, Relocatable=True
- #10: Value=10, Relocatable=False
- =0CABC: Value=414243, Length=3, Relocatable=False

Literal Table:
- =0CABC: Value=414243, Length=3
```

---
