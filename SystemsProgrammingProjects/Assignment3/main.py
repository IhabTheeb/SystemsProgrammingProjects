#********************************************************************
#***  NAME       : Ihab Theeb                                      ***
#***  CLASS      : CSC 354                                         ***
#***  ASSIGNMENT : Assignment 3                                    ***
#***  DUE DATE   : 10/30/2024                                      ***
#***  INSTRUCTOR : George Hamer                                    ***
#********************************************************************
#***  DESCRIPTION : This program processes assembly language       ***
#***  directives and manages opcode, symbol, and literal tables.   ***
#***  It includes functions for handling instructions, updating    ***
#***  the location counter, and managing literals and labels as    ***
#***  per specific assembly directives and formats.                ***
#********************************************************************

import sys
import re

# Opcode table and other global variables
opcode_table = {}
symbol_table = {}
literal_table = {}
location_counter = 0
start_address = 0
literal_queue = []  # Queue for literals to ensure they are placed after each instruction
directives_list = ['START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE', 'EQU']


#********************************************************************
#***  FUNCTION    : read_opcode_file
#********************************************************************
#***  DESCRIPTION : Reads an opcode file and populates the opcode table with mnemonics, opcodes, and formats.
#***  INPUT ARGS  : filename - string: the name of the file containing opcode information
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def read_opcode_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            mnemonic, opcode, fmt = line.split()
            opcode_table[mnemonic] = (opcode, int(fmt))

#********************************************************************
#***  FUNCTION    : handle_start_directive
#********************************************************************
#***  DESCRIPTION : Handles the START directive, setting the initial start address and location counter.
#***  INPUT ARGS  : value - string: the address specified with the START directive
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_start_directive(value):
    global location_counter, start_address
    value = value.replace('#', '')
    start_address = int(value, 16)
    location_counter = start_address
    print(f"DEBUG: START directive processed, start_address set to {start_address:04X}, location_counter initialized to {location_counter:04X}")
    
 
#********************************************************************
#***  FUNCTION    : handle_base_directive
#********************************************************************
#***  DESCRIPTION : Handles the BASE directive, setting the base register value.
#***  INPUT ARGS  : value - string: the symbol name to use as a base
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_base_directive(value):
    global base_register  # This line must be indented correctly
    if value not in symbol_table:
        symbol_table[value] = 0  # Add a default value if it's missing
    base_register = symbol_table[value]
    print(f"DEBUG: BASE directive processed, base_register set to {base_register:04X}")


#********************************************************************
#***  FUNCTION    : handle_byte_directive
#********************************************************************
#***  DESCRIPTION : Processes the BYTE directive, updating the location counter.
#***  INPUT ARGS  : value - string: BYTE operand in either character or hex format
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_byte_directive(value):
    global location_counter
    if value.startswith('0X') or value.startswith('0x'):
        hex_digits = value[2:]  # Remove '0X'
        if len(hex_digits) % 2 != 0:
            # Invalid hex literal, should be even number of digits
            print(f"ERROR: Invalid hex literal '{value}'")
            length = 0
        else:
            length = len(hex_digits) // 2  # Each pair of hex digits represents one byte
    elif value.startswith('0C') or value.startswith('0c'):
        chars = value[2:]  # Remove '0C'
        length = len(chars)
    else:
        length = 1  # Default to 1 byte
    location_counter += length
    print(f"DEBUG: BYTE directive processed, operand '{value}', length {length}, new location_counter is {location_counter:04X}")



#********************************************************************
#***  FUNCTION    : handle_word_directive
#********************************************************************
#***  DESCRIPTION : Processes the WORD directive, incrementing the location counter by 3.
#***  INPUT ARGS  : None
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_word_directive():
    global location_counter
    location_counter += 3
    print(f"DEBUG: WORD directive processed, new location_counter is {location_counter:04X}")

#********************************************************************
#***  FUNCTION    : handle_resb_directive
#********************************************************************
#***  DESCRIPTION : Processes the RESB directive to reserve bytes.
#***  INPUT ARGS  : value - string: number of bytes to reserve
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_resb_directive(value):
    global location_counter
    if value.startswith('#'):
        value = value[1:]  # Remove the '#' before converting to an integer
    location_counter += int(value)
    print(f"DEBUG: RESB directive processed, increment by {int(value)}, new location_counter is {location_counter:04X}")


#********************************************************************
#***  FUNCTION    : handle_resw_directive
#********************************************************************
#***  DESCRIPTION : Processes the RESW directive to reserve words (3 bytes each).
#***  INPUT ARGS  : value - string: number of words to reserve
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_resw_directive(value):
    global location_counter
    if value.startswith('#'):
        value = value[1:]  # Remove the '#' before converting to an integer
    try:
        increment = 3 * int(value)
        location_counter += increment
        print(f"DEBUG: RESW directive processed, increment by {increment}, new location_counter is {location_counter:04X}")
    except ValueError:
        print(f"ERROR: Invalid operand '{value}' for RESW directive.")

    
    
#********************************************************************
#***  FUNCTION    : handle_equ_directive
#********************************************************************
#***  DESCRIPTION : Handles the EQU directive, which sets a label to a constant or an expression value.
#***  INPUT ARGS  : label - string: the label being defined
#***                value - string: the expression or constant to assign
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def handle_equ_directive(label, value):
    try:
        # Evaluate the value, taking care of special cases like '*'
        if value == '*':
            symbol_table[label] = location_counter
        else:
            # Clean the operand
            value = clean_operand(value)

            # Check for expressions involving symbols
            if '-' in value or '+' in value:
                evaluated_value = evaluate_expression(value)
                if evaluated_value is not None:
                    symbol_table[label] = evaluated_value
                else:
                    raise ValueError(f"Unable to evaluate expression '{value}'")
            else:
                # Convert to integer (handle hex if starts with 0x)
                symbol_table[label] = int(value, 16) if value.startswith("0x") else int(value)

        print(f"DEBUG: EQU directive processed, setting {label} to {symbol_table[label]:04X}")
    except Exception as e:
        print(f"ERROR: Unable to evaluate expression '{value}': {e}")


#********************************************************************
#***  FUNCTION    : process_literal
#********************************************************************
#***  DESCRIPTION : Adds a literal to the literal table if encountered.
#***  INPUT ARGS  : operand - string: the literal operand
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def process_literal(operand):
    if operand.startswith("="):
        literal_value = operand[1:]  # Remove '=' prefix

        if literal_value.startswith("0C"):
            # Character literal with '0C' prefix
            chars = literal_value[2:]  # Extract characters after '0C'
            length = len(chars)
        elif literal_value.startswith("0X"):
            # Hexadecimal literal with '0X' prefix
            hex_digits = literal_value[2:]
            if len(hex_digits) % 2 != 0:
                print(f"ERROR: Invalid hex literal '{operand}'")
                length = 0
            else:
                length = len(hex_digits) // 2
        else:
            print(f"ERROR: Invalid literal format '{operand}'")
            length = 0

        if operand not in literal_table:
            literal_table[operand] = {
                'operand_value': literal_value,
                'length': length,
                'address': None
            }
            literal_queue.append(operand)
    else:
        print(f"ERROR: Invalid literal '{operand}'")



#********************************************************************
#***  FUNCTION    : place_literals
#********************************************************************
#***  DESCRIPTION : Assigns addresses to literals and updates the location counter.
#***  INPUT ARGS  : None
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def place_literals():
    global location_counter
    for literal in literal_queue:
        if literal_table[literal]['address'] is None:
            literal_table[literal]['address'] = location_counter
            length = literal_table[literal]['length']
            print(f"DEBUG: Assigning literal {literal} to address {location_counter:04X}, length {length}")
            location_counter += length
    literal_queue.clear()



#********************************************************************
#***  FUNCTION    : process_directive
#********************************************************************
#***  DESCRIPTION : Processes assembly directives like START, BYTE, WORD, RESB, RESW, and EQU.
#***  INPUT ARGS  : label - string, directive - string, value - string
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def process_directive(label, directive, value):
    global location_counter

    if directive == "BYTE":
        handle_byte_directive(value)
    elif directive == "WORD":
        handle_word_directive()
    elif directive == "RESB":
        handle_resb_directive(value)
    elif directive == "RESW":
        handle_resw_directive(value)
    elif directive == "BASE":
        handle_base_directive(value)
    elif directive == "EQU":
        handle_equ_directive(label, value)

    print(f"DEBUG: {directive} directive processed, location_counter now at {location_counter:04X}")




#********************************************************************
#***  FUNCTION    : validate_literal
#********************************************************************
#***  DESCRIPTION : Validates the format of a literal before processing.
#***  INPUT ARGS  : literal - string: the literal to validate
#***  OUTPUT ARGS : None
#***  RETURN      : bool: True if the literal is valid, False otherwise
#********************************************************************
def validate_literal(literal):
    # Check for literals starting with '=0C' or '=0X'
    if re.match(r"^=0[Cc].+$", literal) or re.match(r"^=0[Xx][0-9A-Fa-f]+$", literal):
        return True
    return False



import re


def clean_operand(value):
    # Remove '#' or '@' from the beginning of the operand
    return value.lstrip('#@')


#********************************************************************
#***  FUNCTION    : evaluate_expression
#********************************************************************
#***  DESCRIPTION : Evaluates an expression provided in an EQU directive.
#***  INPUT ARGS  : expression - string: the expression to evaluate
#***  OUTPUT ARGS : None
#***  RETURN      : int or None: the evaluated value of the expression
#********************************************************************
def evaluate_expression(expression):
    try:
        # Clean the expression
        expression = clean_operand(expression)

        # Replace symbols with their corresponding values from the symbol table
        for symbol in symbol_table:
            if symbol in expression:
                expression = re.sub(r'\b' + re.escape(symbol) + r'\b', str(symbol_table[symbol]), expression)

        # Use eval to safely evaluate the expression
        # Only allow numbers and arithmetic operators for safety
        if re.match(r'^[\d\+\-\*/\(\) ]+$', expression):
            return int(eval(expression))
        else:
            raise ValueError(f"Invalid characters in expression '{expression}'")
    except Exception as e:
        print(f"ERROR: Unable to evaluate expression '{expression}': {e}")
        return None


#********************************************************************
#***  FUNCTION    : pass1
#********************************************************************
#***  DESCRIPTION : Pass 1 for assembly code processing, including label, opcode, and operand handling.
#***  INPUT ARGS  : filename - string: name of the assembly source file
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def pass1(filename):
    global location_counter
    start_processed = False  # Local flag for tracking START processing

    with open(filename, 'r') as file:
        line_counter = 1
        for line in file:
            line = line.strip()
            # Ignore full line comments
            if not line or line.startswith('.'):
                line_counter += 1
                continue

            # Split the line and remove any partial comments
            line = line.split('.')  # Split by comment marker
            line = line[0].strip()  # Take the part before the comment

            tokens = line.split()
            label, opcode, operand = None, None, None

            # Parsing tokens for label, opcode, and operand
            if len(tokens) == 3:
                label, opcode, operand = tokens
            elif len(tokens) == 2:
                if tokens[0].endswith(':'):
                    label = tokens[0]
                    opcode = tokens[1]
                else:
                    opcode, operand = tokens
            elif len(tokens) == 1:
                opcode = tokens[0]
            else:
                print(f"ERROR: Unexpected format at line {line_counter}")
                line_counter += 1
                continue

            # Clean the label
            if label and label.endswith(':'):
                label = label[:-1]  # Remove the trailing ':'

            # For debug: print parsed label, opcode, operand
            print(f"DEBUG: Parsed label='{label}', opcode='{opcode}', operand='{operand}'")

            # Handling START directive
            if opcode == "START" and operand and not start_processed:
                handle_start_directive(operand)
                start_processed = True
                line_counter += 1
                continue

            # If label exists, add it to symbol table (unless opcode is EQU)
            if label:
                if opcode != 'EQU':
                    symbol_table[label] = location_counter
                    print(f"DEBUG: Label '{label}' added to symbol table with address {location_counter:04X}")

            # Process directives
            if opcode == "END":
                print(f"DEBUG: END directive processed, location_counter now at {location_counter:04X}")
                break

            elif opcode in ['BYTE', 'WORD', 'RESB', 'RESW', 'BASE', 'EQU']:
                process_directive(label, opcode, operand)
            elif opcode.startswith('+'):
                # Format 4 instruction handling
                stripped_opcode = opcode[1:]
                if stripped_opcode in opcode_table:
                    format = 4
                    location_counter += 4
                    print(f"DEBUG: Processing format-4 opcode '{opcode}', location_counter updated to {location_counter:04X}")
                else:
                    print(f"ERROR: Illegal instruction '{opcode}' at line {line_counter}")
                    continue
            elif opcode in opcode_table:
                format = opcode_table[opcode][1]
                location_counter += format
                print(f"DEBUG: Processing opcode '{opcode}', format size {format}, location_counter updated to {location_counter:04X}")
            else:
                print(f"ERROR: Illegal instruction '{opcode}' at line {line_counter}")
                continue

            # Process literals (start with =) only if opcode is not a directive
            if operand and operand.startswith("=") and opcode not in directives_list:
                process_literal(operand)


            # Write intermediate output
            with open("test1.int", "a") as outfile:
                outfile.write(f"{line_counter:04}\t{location_counter:04X}\t{line}\n")

            line_counter += 1

    place_literals()
    write_symbol_table_to_file()
    write_literal_table_to_file()



#********************************************************************
#***  FUNCTION    : write_symbol_table_to_file
#********************************************************************
#***  DESCRIPTION : Writes the symbol table to the output file.
#***  INPUT ARGS  : None
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def write_symbol_table_to_file():
    with open("test1.int", "a") as file:
        file.write("\nSymbol Table:\nSymbol\t\tValue\n")
        for symbol, address in symbol_table.items():
            file.write(f"{symbol:10} {address:05X}\n")

#********************************************************************
#***  FUNCTION    : write_literal_table_to_file
#********************************************************************
#***  DESCRIPTION : Writes the literal table to the output file.
#***  INPUT ARGS  : None
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def write_literal_table_to_file():
    with open("test1.int", "a") as file:
        file.write("\nLiteral Table:\nLiteral Name\tOperand Value\tLength\tAddress\n")
        for literal, info in literal_table.items():
            address_str = f"{info['address']:05X}" if info['address'] is not None else "N/A"
            file.write(f"{literal:<15} {info['operand_value']:<12} {info['length']:<10} {address_str}\n")

#********************************************************************
#***  FUNCTION    : print_pass1_contents
#********************************************************************
#***  DESCRIPTION : Prints the contents of the test1.int output file.
#***  INPUT ARGS  : None
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
def print_pass1_contents():
    with open("test1.int", "r") as file:
        print("\n--- test1.int Contents ---")
        print(file.read())
        print("--- End of test.int ---")

#********************************************************************
#***  FUNCTION    : main
#********************************************************************
#***  DESCRIPTION : Main function to drive the assembler, handling opcode file loading and pass 1 execution.
#***  INPUT ARGS  : None (expects filename from command-line arguments)
#***  OUTPUT ARGS : None
#***  RETURN      : None
#********************************************************************
if __name__ == "__main__":
    
    # Clear the output file before writing new content
    with open("test1.int", "w") as outfile:
        outfile.write("")  # Clear file contents

    if len(sys.argv) > 1:
        source_filename = sys.argv[1]
    else:
        source_filename = input("Enter source file name: ")

    read_opcode_file("opcodes")
    pass1(source_filename)
    
    print_pass1_contents()
