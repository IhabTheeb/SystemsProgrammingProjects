#********************************************************************
#*** NAME : Ihab Theeb
#*** CLASS : CSC 354
#*** ASSIGNMENT : Assignment 5 - Linker Loader: F&R
#*** DUE DATE : 12/20/2025
#*** INSTRUCTOR : George Hamer
#*********************************************************************
#*** DESCRIPTION : This program implements a linking loader that
#*** reads multiple object files, resolves external references,
#*** applies relocations, and produces a linked memory map. The
#*** program also prints an external symbol table and displays a
#*** memory dump (with unknowns as ??) to both the MEMORY.DAT file
#*** and the monitor.
#*********************************************************************

import sys
from typing import Dict, List

class ObjectProgram:
    #********************************************************************
    #*** FUNCTION : __init__                                           ***
    #********************************************************************
    #*** DESCRIPTION : Constructor for ObjectProgram that initializes  ***
    #***               internal structures and parses the object file. ***
    #*** INPUT ARGS : content (str)                                    ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def __init__(self, content: str):
        self.content = [line.rstrip('\r\n') for line in content.strip().split('\n')]
        self.name = ''
        self.start_address = 0
        self.length = 0
        self.defines: Dict[str, int] = {}
        self.references: List[str] = []
        self.modifications: List[tuple] = []
        self.text_records: List[tuple] = []
        self.entry_point = 0
        self.parse_object_file()

    #********************************************************************
    #*** FUNCTION : parse_hex_field                                    ***
    #********************************************************************
    #*** DESCRIPTION : Parses a given field as hex, left-padding with  ***
    #***               zeros if shorter than the required length.      ***
    #*** INPUT ARGS : field (str), length (int)                        ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : int (parsed hex value)                               ***
    #********************************************************************
    def parse_hex_field(self, field: str, length: int = 6) -> int:
        field = field.strip()
        field = field.zfill(length)
        return int(field, 16)

    #********************************************************************
    #*** FUNCTION : parse_object_file                                  ***
    #********************************************************************
    #*** DESCRIPTION : Parses the object file lines, extracting header, ***
    #***               define, reference, text, modification, and end   ***
    #***               records to populate the program structures.      ***
    #*** INPUT ARGS : None                                             ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def parse_object_file(self):
        for line in self.content:
            line = line.strip()
            if not line:
                continue
            try:
                rec_type = line[0]
                if rec_type == 'H':
                    raw_name = line[1:5].strip('0 ').upper()
                    self.name = raw_name
                    length_str = line[13:].strip()
                    if length_str == '':
                        length_str = '0'
                    self.length = int(length_str, 16)
                elif rec_type == 'D':
                    defines_content = line[1:]
                    for i in range(0, len(defines_content), 10):
                        chunk = defines_content[i:i+10]
                        if len(chunk) < 10:
                            continue
                        symbol = chunk[0:4].strip('0 ').upper()
                        addr_str = chunk[4:10].upper()
                        if all(c in '0123456789ABCDEF' for c in addr_str):
                            addr_val = int(addr_str, 16)
                            if symbol:
                                self.defines[symbol] = addr_val
                elif rec_type == 'R':
                    ref_content = line[1:].strip()
                    parts = ref_content.split()
                    refs = [p.strip('0 ').upper() for p in parts]
                    self.references = refs
                elif rec_type == 'T':
                    if len(line) < 9:
                        continue
                    start_str = line[1:7].strip()
                    start_addr = self.parse_hex_field(start_str, 6)
                    length_str = line[7:9].strip()
                    if not length_str:
                        continue
                    length_val = int(length_str, 16)
                    data = line[9:9 + length_val * 2]
                    self.text_records.append((start_addr, length_val, data))
                elif rec_type == 'M':
                    start_str = line[1:7].strip()
                    start_addr = self.parse_hex_field(start_str, 6)
                    length_str = line[7:9].strip()
                    length_val = int(length_str, 16)
                    sign = line[9]
                    is_positive = (sign == '+')
                    symbol = line[10:].strip('0 ').upper()
                    self.modifications.append((start_addr, length_val, symbol, is_positive))
                elif rec_type == 'E':
                    if len(line) > 1:
                        entry_str = line[1:].strip()
                        if entry_str:
                            self.entry_point = self.parse_hex_field(entry_str, 6)
            except:
                pass

    #********************************************************************
    #*** FUNCTION : print_debug_info                                   ***
    #********************************************************************
    #*** DESCRIPTION : Prints basic information about the object        ***
    #***               program for debugging.                           ***
    #*** INPUT ARGS : None                                             ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def print_debug_info(self):
        print("\nDebug Information:")
        print(f"Program Name: {self.name}")
        print(f"Start Address: {self.start_address:04X}")
        print(f"Length: {self.length:04X}")
        print("Defines:")
        for symbol, addr in self.defines.items():
            print(f"  {symbol}: {addr:04X}")
        print("References:", self.references)
        print("Text Records:", len(self.text_records))
        print("Modifications:", len(self.modifications))
        print("Entry Point:", f"{self.entry_point:04X}" if self.entry_point else "None")
        print("-" * 40)


class Linker:
    #********************************************************************
    #*** FUNCTION : __init__                                           ***
    #********************************************************************
    #*** DESCRIPTION : Initializes the Linker with a given load address ***
    #***               and internal structures.                         ***
    #*** INPUT ARGS : load_address (int)                                ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def __init__(self, load_address: int):
        self.load_address = load_address
        self.memory = {}
        self.symbol_table = {}
        self.programs: List[ObjectProgram] = []
        self.execution_address = 0
        self.csects = []

    #********************************************************************
    #*** FUNCTION : load_program                                       ***
    #********************************************************************
    #*** DESCRIPTION : Creates an ObjectProgram from the given content  ***
    #***               and appends it to the linker's program list.     ***
    #*** INPUT ARGS : content (str)                                    ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def load_program(self, content: str):
        program = ObjectProgram(content)
        program.print_debug_info()
        self.programs.append(program)

    #********************************************************************
    #*** FUNCTION : first_pass                                         ***
    #********************************************************************
    #*** DESCRIPTION : Processes all programs to build the symbol table ***
    #***               and determine memory assignments.                ***
    #*** INPUT ARGS : None                                             ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def first_pass(self):
        current_address = self.load_address
        for program in self.programs:
            relocation_factor = current_address
            if program.name:
                if program.name in self.symbol_table:
                    pass
                self.symbol_table[program.name] = relocation_factor
                self.csects.append((program.name, relocation_factor, program.length))
            for symbol, value in program.defines.items():
                if symbol in self.symbol_table:
                    pass
                self.symbol_table[symbol] = value + relocation_factor
            current_address += program.length

    #********************************************************************
    #*** FUNCTION : second_pass                                        ***
    #********************************************************************
    #*** DESCRIPTION : Processes text records and applies modifications ***
    #***               based on the symbol table built in first_pass.   ***
    #*** INPUT ARGS : None                                             ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def second_pass(self):
        current_address = self.load_address
        referenced_symbols = set()
        for program in self.programs:
            referenced_symbols.update(program.references)
        for ref_sym in referenced_symbols:
            if ref_sym not in self.symbol_table:
                print(f"Warning: Reference to undefined symbol '{ref_sym}'.")

        for program in self.programs:
            relocation_factor = current_address
            for start, length, data in program.text_records:
                abs_address = start + relocation_factor
                for i in range(0, len(data), 2):
                    byte = int(data[i:i+2], 16)
                    self.memory[abs_address + i // 2] = byte
            for mod_start, mod_length, symbol, is_positive in program.modifications:
                abs_address = mod_start + relocation_factor
                value = 0
                for i in range(mod_length):
                    value = (value << 8) | self.memory.get(abs_address + i, 0)
                if symbol not in self.symbol_table:
                    print(f"Warning: Modification symbol '{symbol}' not found.")
                    modification = 0
                else:
                    modification = self.symbol_table[symbol]
                if is_positive:
                    new_value = value + modification
                else:
                    new_value = value - modification
                temp_val = new_value
                for i in range(mod_length - 1, -1, -1):
                    self.memory[abs_address + i] = temp_val & 0xFF
                    temp_val >>= 8
            if program.entry_point != 0:
                self.execution_address = program.entry_point + relocation_factor
            current_address += program.length

    #********************************************************************
    #*** FUNCTION : print_symbol_table                                  ***
    #********************************************************************
    #*** DESCRIPTION : Prints the external symbol table in a format     ***
    #***               similar to the professor's specification.        ***
    #*** INPUT ARGS : None                                             ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def print_symbol_table(self):
        print("Print The External Symbol Table")
        print("CSECT   SYMBOL   ADDR     CSADDR  LDADDR  LENGTH")
        csect_map = {c[0]: (c[1], c[2]) for c in self.csects}
        for csect_name, (csaddr, length) in csect_map.items():
            csect_length_str = f"{length:06X}"
            print(f"{csect_name:<6}  {'$':<6}  {'$':<7}  {csaddr:04X}    {'$':<6}  {csect_length_str}")
            for symbol, addr in self.symbol_table.items():
                if symbol == csect_name:
                    continue
                if csaddr <= addr < csaddr + length:
                    offset = addr - csaddr
                    offset_str = f"{offset:06X}"
                    addr_str = f"{addr:04X}"
                    print(f"{'$':<6}  {symbol:<6}  {offset_str:<7}  {'$':<7}  {addr_str:<6}  {'$'}")

    #********************************************************************
    #*** FUNCTION : write_memory_map                                   ***
    #********************************************************************
    #*** DESCRIPTION : Writes the memory map to a file named MEMORY.DAT ***
    #***               and also displays it on the monitor. Uninitialized***
    #***               locations are marked with '??'. Also prints one  ***
    #***               extra empty line (with ??) at the end.           ***
    #*** INPUT ARGS : filename (str)                                    ***
    #*** OUTPUT ARGS : None                                            ***
    #*** IN/OUT ARGS : None                                            ***
    #*** RETURN : None                                                 ***
    #********************************************************************
    def write_memory_map(self, filename: str):
        if not self.memory:
            print("No memory to display.")
            return
        min_addr = min(self.memory.keys())
        max_addr = max(self.memory.keys())
        lines = []
        header = '          0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F'
        lines.append(header)
        current_addr = min_addr - (min_addr % 16)
        while current_addr <= max_addr:
            line_str = f'{current_addr:05X}    '
            for offset in range(16):
                addr = current_addr + offset
                if addr in self.memory:
                    line_str += f'{self.memory[addr]:02X} '
                else:
                    line_str += '?? '
            lines.append(line_str)
            current_addr += 16

        # Add one extra line of ?? as requested
        line_str = f'{current_addr:05X}    '
        for _ in range(16):
            line_str += '?? '
        lines.append(line_str)

        if self.execution_address:
            lines.append(f'\nExecution begins at address {self.execution_address:06X}')

        # Write to file
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line + '\n')

        # Also print to monitor
        for line in lines:
            print(line)

#********************************************************************
#*** FUNCTION : main                                               ***
#********************************************************************
#*** DESCRIPTION : Entry point of the program. Loads object files,  ***
#***               performs linking (first and second pass), prints ***
#***               symbol table and memory map.                     ***
#*** INPUT ARGS : None (uses sys.argv)                              ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def main():
    if len(sys.argv) < 2:
        print("Usage: python linker.py prog1.obj prog2.obj ...")
        return

    linker = Linker(0x3300)

    for obj_file in sys.argv[1:]:
        try:
            with open(obj_file, 'r') as f:
                content = f.read()
            linker.load_program(content)
        except FileNotFoundError:
            print(f"Error: Could not find file {obj_file}")
            return
        except Exception as e:
            print(f"Error processing {obj_file}: {str(e)}")
            return

    try:
        linker.first_pass()
        linker.second_pass()
        linker.print_symbol_table()
        linker.write_memory_map('MEMORY.DAT')
        print("Linking complete. Output written to MEMORY.DAT")
    except Exception as e:
        print(f"Error during linking: {str(e)}")

if __name__ == "__main__":
    main()
