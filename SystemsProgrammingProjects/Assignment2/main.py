#**************************************************************************
#***  NAME  : Ihab Theeb                                                ***
#***  CLASS  : CSC 354                                                  ***
#***  ASSIGNMENT : Assignment 2                                         ***
#***  DUE DATE : F&R 2                                                  ***
#***  INSTRUCTOR : George Hamer                                         ***
#**************************************************************************
#***  DESCRIPTION : This program defines classes and functions for      ***
#***                managing a symbol table and a literal table,        ***
#***                evaluating expressions, and handling literals.      ***
#***                It includes methods for loading symbols, adding     ***
#***                literals, parsing expressions, and displaying       ***
#***                results in a formatted way.                         ***
#**************************************************************************

class SymbolTable:
    def __init__(self):
        self.symbols = {}  # Initialize an empty dictionary to store symbols

    #*********************************************************************
    #***  FUNCTION: load_symbols                                       ***
    #*********************************************************************
    #***  DESCRIPTION : Loads symbols from the specified file into the ***
    #***                symbol table.                                   ***
    #***  INPUT ARGS : filename: The name of the file containing        ***
    #***                symbols (default is 'SYMS.DAT').                ***
    #***  OUTPUT ARGS : None                                            ***
    #***  RETURN : None                                                 ***
    #*********************************************************************
    def load_symbols(self, filename='SYMS.DAT'):
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split(':')  # Split line into symbol and details
                if len(parts) == 2:
                    symbol = parts[0].strip()  # Extract symbol name
                    symbol_info = parts[1].strip().split()  # Extract symbol details
                    if len(symbol_info) == 2:
                        value = int(symbol_info[0])  # Symbol's numeric value
                        rflag = symbol_info[1].lower() == 'true'  # Relocatable flag
                        # Add the symbol to the symbol table
                        self.symbols[symbol] = {'value': value, 'rflag': rflag}

    #*********************************************************************
    #***  FUNCTION: get_symbol                                         ***
    #*********************************************************************
    #***  DESCRIPTION : Retrieves the details of a given symbol from   ***
    #***                the symbol table.                               ***
    #***  INPUT ARGS : symbol: The name of the symbol to retrieve.      ***
    #***  OUTPUT ARGS : None                                            ***
    #***  RETURN : A dictionary containing the symbol's value and       ***
    #***           relocatability flag, or None if the symbol is not    ***
    #***           found.                                               ***
    #*********************************************************************
    def get_symbol(self, symbol):
        return self.symbols.get(symbol, None)  # Return symbol details if found

class LiteralTable:
    def __init__(self):
        self.literals = []  # List to store literals

    #********************************************************************
    #***  FUNCTION: add_literal                                        ***
    #********************************************************************
    #***  DESCRIPTION : Adds a new literal to the literal table if it  ***
    #***                is not already present.                         ***
    #***  INPUT ARGS : name: The name of the literal.                   ***
    #***               value: The value associated with the literal.    ***
    #***               length: The length of the literal.               ***
    #***  OUTPUT ARGS : None                                            ***
    #***  RETURN : None                                                 ***
    #********************************************************************
    def add_literal(self, name, value, length):
        if name not in [entry['name'] for entry in self.literals]:  # Check if literal is unique
            address = len(self.literals)  # Address is the current length of the list
            # Add the new literal to the table
            self.literals.append({
                'name': name,
                'value': value,
                'length': length,
                'address': address
            })

    #********************************************************************
    #***  FUNCTION: display_literals                                   ***
    #********************************************************************
    #***  DESCRIPTION : Displays the contents of the literal table in  ***
    #***                a formatted way.                                ***
    #***  INPUT ARGS : literal_table: An instance of LiteralTable       ***
    #***  OUTPUT ARGS : None                                            ***
    #***  RETURN : None                                                 ***
    #********************************************************************
    def display_literals(literal_table):
        print("\nLITERAL TABLE")
        print(f"{'NAME':<20}{'VALUE':<20}{'LENGTH':<10}{'ADDRESS':<10}")
        for index, literal in enumerate(literal_table.literals):
            name = literal['name']
            value = literal['value']
            length = literal['length']
            address = index
            print(f"{name:<20}{value:<20}{length:<10}{address:<10}")

#********************************************************************
#***  FUNCTION: evaluate_literal                                   ***
#********************************************************************
#***  DESCRIPTION : Evaluates a given literal and returns its      ***
#***                hexadecimal representation if valid, otherwise  ***
#***                returns 'ERROR'.                                ***
#***  INPUT ARGS : literal: The literal string to be evaluated.     ***
#***  OUTPUT ARGS : None                                            ***
#***  RETURN : The hexadecimal representation of the literal or     ***
#***           'ERROR' if the format is invalid.                    ***
#********************************************************************
def evaluate_literal(literal):
    try:
        if literal.startswith('=0c'):
            return ''.join([f"{ord(c):02X}" for c in literal[3:]])
        elif literal.startswith('=0x'):
            return literal[3:].upper()
        elif literal.startswith("=C'") and literal.endswith("'"):
            return 'ERROR'
        else:
            return 'ERROR'
    except Exception:
        return 'ERROR'

#********************************************************************
#***  FUNCTION: parse_expression                                    ***
#********************************************************************
#***  DESCRIPTION : Parses an expression to evaluate its value,     ***
#***                relocatability, and addressing mode flags.      ***
#***  INPUT ARGS : symbol_table: An instance of SymbolTable         ***
#***               literal_table: An instance of LiteralTable       ***
#***               expression: The expression to be evaluated       ***
#***  OUTPUT ARGS : None                                            ***
#***  RETURN : A tuple containing the value, relocatability flag,   ***
#***           N-bit, I-bit, and X-bit values, or an error message  ***
#********************************************************************
def parse_expression(symbol_table, literal_table, expression):
    if expression.startswith('='):
        literal_value = evaluate_literal(expression)
        if literal_value == 'ERROR':
            return None, f"{expression} => ERROR"
        length = len(literal_value) // 2
        literal_table.add_literal(expression, literal_value, length)
        return None, None

    n_bit, i_bit, x_bit = 1, 1, 0
    is_immediate = expression.startswith('#')
    if is_immediate:
        i_bit = 0
        expression = expression[1:]
    elif expression.startswith('@'):
        n_bit = 0
        expression = expression[1:]

    if expression.endswith(',x'):
        x_bit = 1
        expression = expression[:-2]
        if is_immediate or not n_bit:
            return None, f"{expression} => ERROR (@ and ,x or # and ,x combination not allowed)"

    tokens = expression.replace('+', ' + ').replace('-', ' - ').split()
    result_value, result_rflag = None, None
    operation = None

    for token in tokens:
        if token in ('+', '-'):
            operation = token
        else:
            if token.lstrip('#').isnumeric():
                value, rflag = int(token.lstrip('#')), False
            else:
                symbol_data = symbol_table.get_symbol(token)
                if symbol_data is None:
                    return None, f"{token} => ERROR"
                value, rflag = symbol_data['value'], symbol_data['rflag']

            if result_value is None:
                result_value, result_rflag = value, rflag
            else:
                if operation == '+':
                    if result_rflag and rflag:
                        return None, f"{expression} => ERROR (Cannot add two relocatable values)"
                    result_value += value
                elif operation == '-':
                    if not result_rflag and rflag:
                        return None, f"{expression} => ERROR (Cannot subtract relocatable from absolute)"
                    result_value -= value
                result_rflag = result_rflag or rflag

    if is_immediate:
        result_rflag = False

    return (result_value, result_rflag, n_bit, i_bit, x_bit), None

#********************************************************************
#***  FUNCTION: display_expression_results                          ***
#********************************************************************
#***  DESCRIPTION : Displays the results of expression evaluations  ***
#***                in a formatted table.                           ***
#***  INPUT ARGS : expressions: Dictionary of evaluated expressions  ***
#***               errors: Dictionary of errors for invalid         ***
#***               original_order: List of expressions in original   ***
#***               order                                            ***
#***  OUTPUT ARGS : None                                             ***
#***  RETURN : None                                                  ***
#********************************************************************
def display_expression_results(expressions, errors, original_order):
    header = f"{'Expression':<20}{'Value':<20}{'Relocatable':<15}{'N':<10}{'I':<10}{'X':<10}"
    print(header)
    print("-" * len(header))
    for exp in original_order:
        if exp in expressions:
            value, relocatable, n_bit, i_bit, x_bit = expressions[exp]
            relocatable_str = 'RELATIVE' if relocatable else 'ABSOLUTE'
            print(f"{exp:<20}{value:<20}{relocatable_str:<15}{n_bit:<10}{i_bit:<10}{x_bit:<10}")
        elif exp in errors:
            print(f"{exp:<20}{errors[exp]:<20}")

def main():
    #******************************************************************
    #***  MAIN FUNCTION: main                                        ***
    #******************************************************************
    #***  DESCRIPTION : Loads the symbol table, reads expressions,    ***
    #***                evaluates them, and displays results.         ***
    #***  INPUT ARGS : None                                           ***
    #***  OUTPUT ARGS : None                                           ***
    #***  RETURN : None                                                ***
    #******************************************************************
    symbol_table = SymbolTable()
    literal_table = LiteralTable()

    try:
        symbol_table.load_symbols()
    except FileNotFoundError:
        print("Error: 'SYMS.DAT' file not found.")
        return

    filename = input("Enter the name of the expression file: ").strip()
    expressions = {}
    errors = {}
    original_order = []

    try:
        with open(filename, 'r') as file:
            for line in file:
                expression = line.strip()
                if not expression:
                    continue
                original_order.append(expression)
                result, error = parse_expression(symbol_table, literal_table, expression)
                if result is not None:
                    expressions[expression] = result
                if error is not None:
                    errors[expression] = error
    except FileNotFoundError:
        print(f"Error: Expression file '{filename}' not found.")
        return

    if expressions or errors:
        display_expression_results(expressions, errors, original_order)

    if literal_table.literals:
        literal_table.display_literals()

if __name__ == "__main__":
    main()  # Execute main function if script is run directly
