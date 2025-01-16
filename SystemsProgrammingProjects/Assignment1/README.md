## Assignment 1: Symbol Table Implementation for SIC/XE Assembler

### Description
This module implements a symbol table for the SIC/XE assembler using a binary search tree. The symbol table stores symbols and their attributes, supports insertion, searching, and viewing operations, and validates symbols for correctness.

### Features
- Binary search tree (BST) for symbol storage.
- Validation of symbols and attributes.
- Error messages for invalid symbols or attributes.
- Inorder traversal to display the symbol table.

### Input Files
1. `SYMS.DAT`: Contains symbols and their attributes.
   - Format: `SYMBOL VALUE RFLAG`
2. Search file: Contains symbols to be searched.

### How to Run
1. Place `SYMS.DAT` and the search file in the same directory as `main.py`.
2. Run the program:
   ```bash
   python main.py [search_file_name]
   ```
   If no search file is provided, the program will prompt for its name.

### Output
- Displays valid symbols with attributes.
- Outputs detailed error messages for invalid symbols or attributes.
- Performs an inorder traversal of the symbol table to display all entries.

### Example Run
Input `SYMS.DAT`:
```
ABCD: 50 True
B12_34: -3 False
```
Search file:
```
ABCD
XYZ
```

Output:
```
Valid Symbols:
- ABCD: Value=50, RFLAG=True
- B12_: Value=-3, RFLAG=False

Errors:
- XYZ: Symbol not found.

Symbol Table (Inorder Traversal):
- B12_: -3 False
- ABCD: 50 True
```

---
