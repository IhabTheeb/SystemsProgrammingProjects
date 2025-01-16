## Assignment 5: Linker/Loader

### Description
This program links multiple object files into a single executable, loading the code into memory. The output is displayed in a formatted memory map and saved to `MEMORY.DAT`.

### Features
- Links multiple object files.
- Generates absolute machine code.
- Displays memory map and execution address.

### Input
1. Object files (command-line arguments).
   - Format: `.obj` files from Assignment 4.

### How to Run
```bash
python linker_loader.py file1.obj file2.obj
```

### Output
1. `MEMORY.DAT`: Contains the absolute machine code.
2. Memory map printed to the screen.

### Example Output
```
03300 XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX
03310 XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX XX
...
Execution begins at address 03300
```

