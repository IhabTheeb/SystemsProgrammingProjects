#********************************************************************
#*** NAME : Ihab Theeb                                             ***
#*** CLASS : CSc 354                                               ***
#*** ASSIGNMENT :  Assignment 4 - Pass 2 - F&R                     ***
#*** DUE DATE :   4/12/2024                                        ***
#*** INSTRUCTOR : George Hamer                                     ***
#********************************************************************
#*** DESCRIPTION : This program is a two-pass assembler for SIC/XE ***
#***               assembly language code. It reads in a source    ***
#***               file, processes it to generate intermediate     ***
#***               files, symbol and literal tables, and finally   ***
#***               produces a listing file and an object file.     ***
#********************************************************************

import sys
import re

# global declarations
opcode_table = {}
symbol_table = {}
literal_table = {}
location_counter = 0
start_address = 0
base_register = None
literal_queue = []
directives_list = ['START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE', 'EQU', 'EXTDEF', 'EXTREF']
registers_list = ['A', 'X', 'L', 'B', 'S', 'T', 'F']
intermediate_lines = []
modification_records = []
program_name = ""
program_length_pass1 = 0

#********************************************************************
#*** FUNCTION : read_opcode_file                                   ***
#********************************************************************
#*** DESCRIPTION : Reads the opcode file and stores the opcodes     ***
#***               in a global dictionary for later use.           ***
#*** INPUT ARGS : filename (str)                                   ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def read_opcode_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 3:
                mnemonic = parts[0]
                fmt = parts[1]
                opcode = parts[2]
                opcode_table[mnemonic] = {'opcode': opcode, 'format': int(fmt)}

#********************************************************************
#*** FUNCTION : handle_start_directive                              ***
#********************************************************************
#*** DESCRIPTION : Handles the START directive, sets start and lc. ***
#*** INPUT ARGS : value (str)                                      ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_start_directive(value):
    global location_counter, start_address, program_name
    value = value.replace('#', '')
    start_address = int(value, 16)
    location_counter = start_address

#********************************************************************
#*** FUNCTION : handle_base_directive                               ***
#********************************************************************
#*** DESCRIPTION : Handles the BASE directive to set base reg.     ***
#*** INPUT ARGS : value (str)                                      ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_base_directive(value):
    global base_register
    base_register = ('PENDING', value)

#********************************************************************
#*** FUNCTION : handle_byte_directive                               ***
#********************************************************************
#*** DESCRIPTION : Handles BYTE directive to reserve space.        ***
#*** INPUT ARGS : value (str)                                      ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_byte_directive(value):
    global location_counter
    if value.upper().startswith('0X'):
        hex_digits = value[2:]
        length = len(hex_digits)//2 if len(hex_digits)%2==0 else 0
    elif value.upper().startswith('0C'):
        chars = value[2:]
        length = len(chars)
    else:
        length = 1
    location_counter += length

#********************************************************************
#*** FUNCTION : handle_word_directive                               ***
#********************************************************************
#*** DESCRIPTION : Handles WORD directive to reserve word space.   ***
#*** INPUT ARGS : None                                             ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_word_directive():
    global location_counter
    location_counter += 3

#********************************************************************
#*** FUNCTION : handle_resb_directive                               ***
#********************************************************************
#*** DESCRIPTION : Handles RESB directive to reserve bytes.        ***
#*** INPUT ARGS : value (str)                                      ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_resb_directive(value):
    global location_counter
    if value.startswith('#'):
        value=value[1:]
    location_counter += int(value)

#********************************************************************
#*** FUNCTION : handle_resw_directive                               ***
#********************************************************************
#*** DESCRIPTION : Handles RESW directive to reserve words.        ***
#*** INPUT ARGS : value (str)                                      ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_resw_directive(value):
    global location_counter
    if value.startswith('#'):
        value=value[1:]
    increment=3*int(value)
    location_counter+=increment

#********************************************************************
#*** FUNCTION : handle_equ_directive                                ***
#********************************************************************
#*** DESCRIPTION : Handles EQU directive to define symbols.        ***
#*** INPUT ARGS : label (str), value (str)                         ***
#*** OUTPUT ARGS : None                                            ***
#*** IN/OUT ARGS : None                                            ***
#*** RETURN : None                                                 ***
#********************************************************************
def handle_equ_directive(label, value):
    if value == '*':
        symbol_table[label] = {
            'address': location_counter,
            'relative': True
        }
    else:
        val, is_rel = evaluate_expression(value)
        if val is not None:
            symbol_table[label] = {
                'address': val,
                'relative': is_rel
            }

#********************************************************************
#*** FUNCTION : handle_extdef_directive                             ***
#********************************************************************
#*** DESCRIPTION : Handles EXTDEF directive to define external syms.***
#*** INPUT ARGS : value (str)                                       ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def handle_extdef_directive(value):
    symbols = [sym.strip() for sym in value.split(',')]
    for sym in symbols:
        if sym not in symbol_table:
            symbol_table[sym] = {
                'address': None,
                'relative': True,
                'extdef': True
            }
        else:
            symbol_table[sym]['extdef'] = True
            symbol_table[sym]['relative'] = True

#********************************************************************
#*** FUNCTION : handle_extref_directive                             ***
#********************************************************************
#*** DESCRIPTION : Handles EXTREF directive to reference external syms***
#*** INPUT ARGS : value (str)                                       ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def handle_extref_directive(value):
    symbols = [sym.strip() for sym in value.split(',')]
    for sym in symbols:
        if sym not in symbol_table:
            symbol_table[sym] = {
                'address': None,
                'relative': False,
                'external': True,
                'referenced': True
            }
        else:
            symbol_table[sym]['external'] = True
            symbol_table[sym]['referenced'] = True

#********************************************************************
#*** FUNCTION : process_literal                                     ***
#********************************************************************
#*** DESCRIPTION : Checks and stores literals from operands.        ***
#*** INPUT ARGS : operand (str)                                     ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def process_literal(operand):
    if not validate_literal(operand):
        return
    if re.match(r"^=C'[^']+'$", operand, re.IGNORECASE):
        chars = operand[3:-1]
        length = len(chars)
        operand_value = 'C' + chars
    elif re.match(r"^=X'[0-9A-Fa-f]+'$", operand, re.IGNORECASE):
        hex_digits = operand[3:-1]
        length = len(hex_digits)//2
        operand_value = 'X' + hex_digits
    elif operand.upper().startswith('=0C'):
        chars = operand[3:]
        length = len(chars)
        operand_value = 'C' + chars
    elif operand.upper().startswith('=0X'):
        hex_digits = operand[3:]
        length = len(hex_digits)//2
        operand_value = 'X' + hex_digits
    else:
        return

    if operand not in literal_table:
        literal_table[operand] = {
            'operand_value': operand_value,
            'length': length,
            'address': None
        }
        literal_queue.append(operand)

#********************************************************************
#*** FUNCTION : place_literals                                      ***
#********************************************************************
#*** DESCRIPTION : Places literals at the end of the program.       ***
#*** INPUT ARGS : None                                              ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def place_literals():
    global location_counter
    for literal in literal_queue:
        if literal_table[literal]['address'] is None:
            literal_table[literal]['address']=location_counter
            length=literal_table[literal]['length']
            location_counter+=length
    literal_queue.clear()

#********************************************************************
#*** FUNCTION : process_directive                                   ***
#********************************************************************
#*** DESCRIPTION : Calls appropriate handler for each directive.    ***
#*** INPUT ARGS : label (str), directive (str), value (str)         ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def process_directive(label, directive, value):
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
    elif directive == "EXTDEF":
        handle_extdef_directive(value)
    elif directive == "EXTREF":
        handle_extref_directive(value)

#********************************************************************
#*** FUNCTION : validate_literal                                    ***
#********************************************************************
#*** DESCRIPTION : Validates the format of a literal.               ***
#*** INPUT ARGS : literal (str)                                     ***
#*** OUTPUT ARGS : bool                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : bool                                                  ***
#********************************************************************
def validate_literal(literal):
    if re.match(r"^=C'[^']+'$", literal, re.IGNORECASE):
        return True
    if re.match(r"^=X'[0-9A-Fa-f]+'$", literal, re.IGNORECASE):
        return True
    if re.match(r"^=0C[ -~]+$", literal, re.IGNORECASE):
        return True
    if re.match(r"^=0X[0-9A-Fa-f]+$", literal, re.IGNORECASE):
        return True
    return False

#********************************************************************
#*** FUNCTION : clean_operand                                       ***
#********************************************************************
#*** DESCRIPTION : Cleans operand by removing addressing chars.     ***
#*** INPUT ARGS : value (str)                                       ***
#*** OUTPUT ARGS : str                                              ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : str                                                   ***
#********************************************************************
def clean_operand(value):
    return value.lstrip('#@')

#********************************************************************
#*** FUNCTION : evaluate_expression                                 ***
#********************************************************************
#*** DESCRIPTION : Evaluates expressions for EQU and operands.     ***
#*** INPUT ARGS : expression (str)                                  ***
#*** OUTPUT ARGS : (int, bool)                                      ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : (value, is_relative)                                  ***
#********************************************************************
def evaluate_expression(expression):
    expression=clean_operand(expression)
    tokens=re.findall(r'[A-Za-z_][A-Za-z0-9_]*|\d+|[\+\-\*/()]',expression)
    evaluated_expr=''
    is_relative=False
    for token in tokens:
        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token):
            if token in symbol_table and symbol_table[token]['address'] is not None:
                value=symbol_table[token]['address']
                evaluated_expr+=str(value)
                is_relative=is_relative or symbol_table[token]['relative']
            else:
                return None,False
        else:
            evaluated_expr+=token
    try:
        result=eval(evaluated_expr)
        return result,is_relative
    except:
        return None,False

#********************************************************************
#*** FUNCTION : evaluate_expression_with_externals                  ***
#********************************************************************
#*** DESCRIPTION : Evaluates expressions including external refs.  ***
#*** INPUT ARGS : expression (str)                                  ***
#*** OUTPUT ARGS : (value, bool, externals)                         ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : (int, bool, list)                                     ***
#********************************************************************
def evaluate_expression_with_externals(expression):
    expression = clean_operand(expression)
    tokens = re.findall(r'[A-Za-z_][A-Za-z0-9_]*|\d+|[\+\-\*/()]', expression)
    value_stack = []
    external_refs = []
    sign = '+'
    if tokens and tokens[0] not in ['+', '-']:
        tokens.insert(0, '+')
    is_relative = False

    for token in tokens:
        if token in ['+', '-']:
            sign = token
        elif re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', token):
            if token in symbol_table:
                sym_info = symbol_table[token]
                if sym_info.get('external'):
                    value_stack.append((0, sign))
                    external_refs.append((token, sign))
                    is_relative = is_relative or sym_info['relative']
                else:
                    if sym_info['address'] is not None:
                        val = sym_info['address']
                        value_stack.append((val, sign))
                        is_relative = is_relative or sym_info['relative']
                    else:
                        value_stack.append((0, sign))
            else:
                value_stack.append((0, sign))
                external_refs.append((token, sign))
        elif token.isdigit():
            val = int(token)
            value_stack.append((val, sign))

    evaluated_value = 0
    for val, s in value_stack:
        if s == '+':
            evaluated_value += val
        else:
            evaluated_value -= val
    return evaluated_value, is_relative, external_refs

#********************************************************************
#*** FUNCTION : is_valid_symbol                                     ***
#********************************************************************
#*** DESCRIPTION : Checks if a symbol is valid in SIC/XE assembly.  ***
#*** INPUT ARGS : symbol (str)                                      ***
#*** OUTPUT ARGS : bool                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : bool                                                  ***
#********************************************************************
def is_valid_symbol(symbol):
    return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$',symbol) is not None

#********************************************************************
#*** FUNCTION : pass1                                               ***
#********************************************************************
#*** DESCRIPTION : Pass 1: Calculates addresses, builds symbol tbl. ***
#*** INPUT ARGS : filename (str)                                    ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def pass1(filename):
    global location_counter, program_name, program_length_pass1
    start_processed=False
    with open("test1.int","w") as outfile:
        outfile.write("")
    with open(filename,'r') as file:
        line_counter=1
        for line in file:
            line=line.strip()
            if not line or line.startswith('.') or line.startswith(';'):
                line_counter+=1
                continue
            line=re.split(r'[.;]',line)[0].strip()
            tokens=line.split()
            label,opcode,operand=None,None,None

            if tokens:
                if tokens[0].endswith(':'):
                    label=tokens[0][:-1]
                    tokens=tokens[1:]
                elif is_valid_symbol(tokens[0]) and tokens[0].upper() not in opcode_table and tokens[0].upper() not in directives_list:
                    label=tokens[0]
                    tokens=tokens[1:]
                if tokens:
                    opcode=tokens[0]
                    operand=' '.join(tokens[1:]) if len(tokens)>1 else None
            else:
                line_counter+=1
                continue
            
            if opcode == "START" and operand and not start_processed:
                if label:
                    symbol_table[label] = {
                        'address': int(operand.replace('#', ''), 16),
                        'relative': True
                    }
                    program_name = label
                handle_start_directive(operand)
                start_processed = True
                with open("test1.int", "a") as outfile:
                    outfile.write(f"{line_counter:04}\t{location_counter:04X}\t{line}\n")
                line_counter += 1
                continue

            if label and opcode != "EQU":
                symbol_table[label] = {
                    'address': location_counter,
                    'relative': True
                }
            
            with open("test1.int", "a") as outfile:
                outfile.write(f"{line_counter:04}\t{location_counter:04X}\t{line}\n")
            
            if opcode == "END":
                break
            elif opcode in directives_list:
                process_directive(label, opcode, operand)
            elif opcode.startswith('+'):
                stripped_opcode = opcode[1:]
                if stripped_opcode in opcode_table:
                    location_counter += 4
            elif opcode in opcode_table:
                fmt = opcode_table[opcode]['format']
                if fmt == 1:
                    location_counter += 1
                elif fmt == 2:
                    location_counter += 2
                elif fmt == 3:
                    location_counter += 3

            if operand and operand.strip().startswith('='):
                process_literal(operand.strip())

            line_counter += 1

    program_length=location_counter-start_address
    program_length_pass1 = program_length
    with open("test1.int","a") as outfile:
        outfile.write(f"\nProgram Length: {program_length:04X}\n")

    place_literals()
    write_symbol_table_to_file()
    write_literal_table_to_file()

#********************************************************************
#*** FUNCTION : pass2                                               ***
#********************************************************************
#*** DESCRIPTION : Pass 2: Generates object code and writes files.  ***
#*** INPUT ARGS : source_filename (str)                             ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def pass2(source_filename):
    global start_address,base_register
    intermediate_filename="test1.int"
    lst_filename=source_filename.replace('.asm','.lst')
    obj_filename=source_filename.replace('.asm','.obj')

    if base_register and isinstance(base_register,tuple) and base_register[0]=='PENDING':
        symbol_name=base_register[1]
        if symbol_name in symbol_table and symbol_table[symbol_name]['address'] is not None:
            base_register=symbol_table[symbol_name]['address']
        else:
            base_register=None

    with open(lst_filename,'w') as lst_file:
        lst_file.write("")
    with open(obj_filename,'w') as obj_file:
        obj_file.write("")

    with open(intermediate_filename,'r') as inter_file:
        lines=inter_file.readlines()

    content_lines=[]
    for line in lines:
        if line.strip()=="Symbol Table:":
            break
        content_lines.append(line)

    for line in content_lines:
        if not line.strip() or line.startswith("---") or line.startswith("Program Length"):
            continue
        if re.match(r'^\d{4}\t',line):
            parts=line.strip().split('\t',2)
            if len(parts)>=3:
                loc_ctr=int(parts[1],16)
                source_line=parts[2]
                intermediate_lines.append({
                    'loc_ctr':loc_ctr,
                    'source_line':source_line,
                    'object_code':''
                })

    for idx,line in enumerate(intermediate_lines):
        loc_ctr=line['loc_ctr']
        source_line=line['source_line']
        object_code=''

        tokens=source_line.split()
        label,opcode,operand=None,None,None

        if tokens:
            if tokens[0].endswith(':'):
                label=tokens[0][:-1]
                tokens=tokens[1:]
            elif is_valid_symbol(tokens[0]) and tokens[0].upper() not in opcode_table and tokens[0].upper() not in directives_list:
                label=tokens[0]
                tokens=tokens[1:]
            if tokens:
                opcode=tokens[0]
                operand=' '.join(tokens[1:]) if len(tokens)>1 else None

        if opcode=="BYTE":
            object_code=process_byte_operand(operand)
        elif opcode=="WORD":
            object_code=process_word_operand(operand, loc_ctr)
        elif opcode in directives_list:
            pass
        elif opcode is not None:
            if opcode in opcode_table or (opcode.startswith('+') and opcode[1:] in opcode_table):
                object_code=generate_object_code(opcode,operand,loc_ctr)

        intermediate_lines[idx]['object_code']=object_code

    with open(lst_filename,'a') as lst_file:
        for line in intermediate_lines:
            loc_str=f"{line['loc_ctr']:05X}"
            tokens=line['source_line'].split()
            lbl,opc,opr='','',''
            if tokens:
                if tokens[0].endswith(':'):
                    lbl=tokens[0][:-1]
                    tokens=tokens[1:]
                elif is_valid_symbol(tokens[0]) and tokens[0].upper() not in opcode_table and tokens[0].upper() not in directives_list:
                    lbl=tokens[0]
                    tokens=tokens[1:]
            if tokens:
                opc=tokens[0].upper()
                opr=' '.join(tokens[1:]) if len(tokens)>1 else ''
            obj=line['object_code']

            label_str = (lbl+":") if lbl else ""
            lst_file.write(f"{int(loc_str,16):05X} {label_str:<8}{opc:<8}{opr:<15}{obj}\n")

        lst_file.write("\nSYMBOL TABLE\n")
        lst_file.write("SYMBOL VALUE RFLAG MFLAG IOFLAG\n")

        for sym in sorted(symbol_table.keys()):
            info = symbol_table[sym]
            val = info['address']
            if val is None:
                val_str = "0"
            else:
                val_str = f"{val:X}".upper().lstrip('0')
                if val_str == '':
                    val_str = '0'
            rflag = "TRUE" if info['relative'] else "FALSE"
            mflag = "FALSE"
            ioflag = "EXTERNAL" if info.get('external') else "INTERNAL"
            lst_file.write(f"{sym.upper()} {val_str:<4} {rflag:<5} {mflag:<5} {ioflag}\n")

    write_object_program(obj_filename)

#********************************************************************
#*** FUNCTION : process_byte_operand                                ***
#********************************************************************
#*** DESCRIPTION : Processes BYTE operand to produce object code.   ***
#*** INPUT ARGS : operand (str)                                     ***
#*** OUTPUT ARGS : str                                              ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : str                                                   ***
#********************************************************************
def process_byte_operand(operand):
    if operand.upper().startswith('0X'):
        hex_digits=operand[2:]
        return hex_digits.upper()
    elif operand.upper().startswith('0C'):
        chars=operand[2:]
        return ''.join(f"{ord(c):02X}" for c in chars)
    elif operand.upper().startswith('C\''):
        chars=operand[2:-1]
        return ''.join(f"{ord(c):02X}" for c in chars)
    elif operand.upper().startswith('X\''):
        hex_digits=operand[2:-1]
        return hex_digits.upper()
    return ''

#********************************************************************
#*** FUNCTION : process_word_operand                                ***
#********************************************************************
#*** DESCRIPTION : Processes WORD operand and handles extern refs.  ***
#*** INPUT ARGS : operand (str), loc_ctr (int)                      ***
#*** OUTPUT ARGS : str                                              ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : str                                                   ***
#********************************************************************
def process_word_operand(operand, loc_ctr):
    evaluated_value, is_relative, external_refs = evaluate_expression_with_externals(operand)
    if evaluated_value is None:
        return ''
    obj_code = f"{evaluated_value & 0xFFFFFF:06X}"
    symbol_tokens = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', operand)
    for sym in symbol_tokens:
        sign_char = '+'
        for (ext_sym, ext_sign) in external_refs:
            if ext_sym == sym:
                sign_char = ext_sign
                break
        if sym in symbol_table:
            info = symbol_table[sym]
            if info.get('external'):
                modification_records.append(f"M^{loc_ctr:06X}^06{sign_char}{sym.upper()}")
            else:
                modification_records.append(f"M^{loc_ctr:06X}^06{sign_char}{program_name.upper()}")
        else:
            modification_records.append(f"M^{loc_ctr:06X}^06{sign_char}{sym.upper()}")
    return obj_code

#********************************************************************
#*** FUNCTION : generate_object_code                                ***
#********************************************************************
#*** DESCRIPTION : Generates object code for instructions.          ***
#*** INPUT ARGS : opcode (str), operand (str), loc_ctr (int)        ***
#*** OUTPUT ARGS : str                                              ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : str                                                   ***
#********************************************************************
def generate_object_code(opcode, operand, loc_ctr):
    ni_flag = 0
    x_flag = 0
    b_flag = 0
    p_flag = 0
    e_flag = 0

    is_format4 = False
    if opcode.startswith('+'):
        is_format4 = True
        opcode = opcode[1:]
        e_flag = 1

    opcode_info = opcode_table.get(opcode)
    if not opcode_info:
        return ''
    opcode_value = int(opcode_info['opcode'], 16)
    fmt = opcode_info['format']
    if is_format4:
        fmt = 4

    if fmt == 1:
        return f"{opcode_value:02X}"
    elif fmt == 2:
        if operand is None:
            return ''
        operands = operand.replace(' ', '').split(',')
        if len(operands) == 1:
            op = operands[0]
            if op.startswith('#') and op[1:].isdigit():
                val = int(op[1:])
                reg1 = val
                reg2 = 0
            else:
                reg1 = get_register_number(op)
                reg2 = 0
        elif len(operands) == 2:
            op1, op2 = operands
            reg1 = get_register_number(op1)
            if op2.startswith('#') and op2[1:].isdigit():
                val = int(op2[1:])
                reg2 = val
            else:
                reg2 = get_register_number(op2)
        return f"{opcode_value:02X}{reg1:X}{reg2:X}"

    address = 0
    ext_refs = []
    if operand:
        if operand.startswith('#'):
            ni_flag = 1
            operand_value = operand[1:]
        elif operand.startswith('@'):
            ni_flag = 2
            operand_value = operand[1:]
        else:
            ni_flag = 3
            operand_value = operand

        if ',X' in operand_value.upper():
            x_flag = 1
            operand_value = operand_value.replace(',X','').replace(',x','')

        operand_value = operand_value.strip()

        if operand_value.startswith('='):
            if operand_value in literal_table and literal_table[operand_value]['address'] is not None:
                address = literal_table[operand_value]['address']
                ext_refs = []
            else:
                return ''
        else:
            if operand_value.isdigit():
                val = int(operand_value)
                address = val
                ext_refs = []
            else:
                val, is_rel, external_refs = evaluate_expression_with_externals(operand_value)
                if val is None:
                    val = 0
                address = val
                ext_refs = external_refs
    else:
        ni_flag = 3
        address = 0

    opcode_bin = (opcode_value & 0xFC) | ni_flag
    first_byte = opcode_bin

    if fmt == 3:
        next_loc = loc_ctr + 3
        immediate_numeric = False
        immediate_value = 0
        if operand and operand.startswith('#'):
            imm_part = operand[1:]
            if imm_part.isdigit():
                immediate_numeric = True
                immediate_value = int(imm_part)

        if immediate_numeric:
            displacement = immediate_value - (next_loc)
            if -2048 <= displacement <= 2047:
                p_flag = 1
                disp = displacement & 0xFFF
            else:
                if 0 <= immediate_value <= 4095:
                    disp = immediate_value & 0xFFF
                else:
                    disp = immediate_value & 0xFFF
        else:
            displacement = address - next_loc
            if -2048 <= displacement <= 2047:
                p_flag = 1
                disp = displacement & 0xFFF
            else:
                if base_register is not None:
                    displacement = address - base_register
                    if 0 <= displacement <= 4095:
                        b_flag = 1
                        disp = displacement & 0xFFF
                    else:
                        disp = address & 0xFFF
                else:
                    disp = address & 0xFFF

        xbpe = (x_flag << 3) | (b_flag << 2) | (p_flag << 1) | e_flag
        return f"{first_byte:02X}{xbpe:01X}{disp:03X}"
    else:
        displacement = address
        xbpe = (x_flag << 3) | (b_flag << 2) | (p_flag << 1) | e_flag
        addr_20 = displacement & 0xFFFFF
        return f"{first_byte:02X}{xbpe:01X}{addr_20:05X}"

#********************************************************************
#*** FUNCTION : get_register_number                                 ***
#********************************************************************
#*** DESCRIPTION : Gets register number from register name.         ***
#*** INPUT ARGS : register (str)                                    ***
#*** OUTPUT ARGS : int                                              ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : int                                                   ***
#********************************************************************
def get_register_number(register):
    register=register.strip().upper()
    register_numbers={
        'A':0,'X':1,'L':2,'B':3,'S':4,'T':5,'F':6,'PC':8,'SW':9
    }
    return register_numbers.get(register,0)

#********************************************************************
#*** FUNCTION : write_object_program                                ***
#********************************************************************
#*** DESCRIPTION : Writes the object program file (H, T, M, E recs).***
#*** INPUT ARGS : obj_filename (str)                                ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def write_object_program(obj_filename):
    global start_address, modification_records, program_name, program_length_pass1
    program_name_local=''
    for line in intermediate_lines:
        if 'START' in line['source_line']:
            tokens=line['source_line'].split()
            if tokens[0].endswith(':'):
                program_name_local = tokens[0][:-1]
            else:
                program_name_local = tokens[0]
            break

    if not program_name_local:
        program_name_local = '      '

    header_record = f"H^{program_name_local[:6].upper()}^{start_address:06X}^{program_length_pass1:06X}\n"

    extdef_list = []
    extref_list = []
    for s, info in symbol_table.items():
        if info.get('extdef'):
            if info['address'] is not None:
                extdef_list.append((s, info['address']))
        if info.get('external') and info.get('referenced'):
            extref_list.append(s)

    d_record = ''
    if extdef_list:
        d_record = "D"
        for (sym, addr) in extdef_list:
            d_record += f"^{sym.upper()}^{addr:06X}"
        d_record += "\n"

    r_record = ''
    if extref_list:
        r_record = 'R'
        for sym in extref_list:
            r_record += f"^{sym.upper()}"
        r_record += "\n"

    text_records = []
    current_record_codes = []
    current_start = None
    current_length = 0

    for line in intermediate_lines:
        loc = line['loc_ctr']
        obj = line['object_code']
        if obj:
            if current_start is None:
                current_start = loc
                current_record_codes = []
                current_length = 0
            obj_len = len(obj) // 2
            if current_length + obj_len > 30:
                record_data = '^'.join(current_record_codes)
                text_records.append(f"T^{current_start:06X}^{current_length:02X}^{record_data}\n")
                current_start = loc
                current_record_codes = [obj]
                current_length = obj_len
            else:
                current_record_codes.append(obj)
                current_length += obj_len
        else:
            if current_start is not None:
                record_data = '^'.join(current_record_codes)
                text_records.append(f"T^{current_start:06X}^{current_length:02X}^{record_data}\n")
                current_start = None
                current_length = 0
                current_record_codes = []

    if current_start is not None:
        record_data = '^'.join(current_record_codes)
        text_records.append(f"T^{current_start:06X}^{current_length:02X}^{record_data}\n")

    formatted_mod_records = ''
    for mod in modification_records:
        match = re.match(r'M([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})([\+\-].+)', mod)
        if match:
            addr_hex = match.group(1)
            length_hex = match.group(2)
            symbol_part = match.group(3)
            formatted_mod_records += f"M^{addr_hex}^{length_hex}{symbol_part}\n"
        else:
            formatted_mod_records += mod + '\n'

    end_record = f"E^{start_address:06X}\n"

    with open(obj_filename, 'w') as obj_file:
        obj_file.write(header_record)
        if d_record:
            obj_file.write(d_record)
        if r_record:
            obj_file.write(r_record)
        for t_rec in text_records:
            obj_file.write(t_rec)
        if formatted_mod_records:
            obj_file.write(formatted_mod_records)
        obj_file.write(end_record)

#********************************************************************
#*** FUNCTION : write_symbol_table_to_file                          ***
#********************************************************************
#*** DESCRIPTION : Writes the symbol table to the intermediate file.***
#*** INPUT ARGS : None                                              ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def write_symbol_table_to_file():
    with open("test1.int","a") as file:
        file.write("\nSymbol Table:\nSYMBOL\tValue\tRFLAG\tMFLAG\tIOFLAG\n")
        for symbol,info in symbol_table.items():
            rflag='TRUE' if info['relative'] else 'FALSE'
            mflag='FALSE'
            ioflag='EXTERNAL' if info.get('external') else 'INTERNAL'
            address = f"{info['address']:X}" if info['address'] is not None else "0"
            address=address.upper().lstrip('0')
            if address=='':
                address='0'
            file.write(f"{symbol.upper()}\t{address}\t{rflag}\t{mflag}\t{ioflag}\n")

#********************************************************************
#*** FUNCTION : write_literal_table_to_file                         ***
#********************************************************************
#*** DESCRIPTION : Writes the literal table to the intermediate file.***
#*** INPUT ARGS : None                                              ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def write_literal_table_to_file():
    with open("test1.int","a") as file:
        file.write("\nLiteral Table:\nLITERAL\tVALUE\tLENGTH\tADDRESS\n")
        for literal,info in literal_table.items():
            operand_value=info['operand_value']
            if operand_value.upper().startswith('C'):
                chars=operand_value[1:]
                val_str=''.join(f"{ord(c):02X}" for c in chars)
                file.write(f"=C'{chars}'\t{val_str}\t{info['length']}\t{info['address']:X}\n")
            elif operand_value.upper().startswith('X'):
                val_str=operand_value[1:].upper()
                file.write(f"=X'{val_str}'\t{val_str}\t{info['length']}\t{info['address']:X}\n")

#********************************************************************
#*** FUNCTION : print_pass_outputs                                  ***
#********************************************************************
#*** DESCRIPTION : Prints contents of intermediate, lst, obj files. ***
#*** INPUT ARGS : source_filename (str)                             ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def print_pass_outputs(source_filename):
    print("\n--- test1.int Contents (After Pass 1) ---")
    with open("test1.int","r") as f:
        print(f.read())
    print("--- End of test1.int ---")

    lst_filename = source_filename.replace('.asm', '.lst')
    obj_filename = source_filename.replace('.asm', '.obj')

    print(f"\n--- {lst_filename} Contents (After Pass 2) ---")
    try:
        with open(lst_filename,'r') as lst_file:
            print(lst_file.read())
    except FileNotFoundError:
        print("No .lst file found.")
    print(f"--- End of {lst_filename} ---")

    print(f"\n--- {obj_filename} Contents (After Pass 2) ---")
    try:
        with open(obj_filename,'r') as obj_file:
            print(obj_file.read())
    except FileNotFoundError:
        print("No .obj file found.")
    print(f"--- End of {obj_filename} ---")

#********************************************************************
#*** FUNCTION : main                                                ***
#********************************************************************
#*** DESCRIPTION : Main driver function. Reads source and compiles. ***
#*** INPUT ARGS : None                                              ***
#*** OUTPUT ARGS : None                                             ***
#*** IN/OUT ARGS : None                                             ***
#*** RETURN : None                                                  ***
#********************************************************************
def main():
    with open("test1.int","w") as outfile:
        outfile.write("")
    if len(sys.argv)>1:
        source_filename=sys.argv[1]
    else:
        source_filename=input("Enter source file name: ")
    read_opcode_file("opcodes")
    pass1(source_filename)
    pass2(source_filename)
    print_pass_outputs(source_filename)

if __name__=="__main__":
    main()
