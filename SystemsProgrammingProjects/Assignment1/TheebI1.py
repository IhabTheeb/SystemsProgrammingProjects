# ***************************************************************
# ***  NAME        : Ihab Theeb
# ***  CLASS       : CSc 354
# ***  ASSIGNMENT  : Assignment 1
# ***  DUE DATE    : 9/18/2024 @ 1 PM
# ***  INSTRUCTOR  : George Hamer
# ***************************************************************
# ***  DESCRIPTION : This program reads a symbol table from a file, 
# ***                checks for validity of symbols, flags, and values,
# ***                and then performs a search on the symbols from a 
# ***                separate file. It outputs any errors encountered 
# ***                and displays a formatted symbol table with valid entries.
# ***************************************************************

import re
import sys

class SymbolNode:
    # ***************************************************************
    # ***  FUNCTION SymbolNode (Constructor)                       ***
    # ***************************************************************
    # ***  DESCRIPTION : Constructor for the SymbolNode class. It initializes
    # ***                a node with a symbol, its value, rflag, iflag, and mflag.
    # ***  INPUT ARGS : symbol (str), value (int), rflag (bool), iflag (bool), mflag (bool)
    # ***  OUTPUT ARGS : None
    # ***  RETURN : None
    # ***************************************************************
    def __init__(self, symbol, value, rflag, iflag, mflag):
        self.symbol = symbol[:4].upper()  # Use only the first 4 characters and convert to uppercase
        self.full_symbol = symbol.upper()  # Store the full symbol separately for display
        self.value = value
        self.rflag = rflag
        self.iflag = iflag
        self.mflag = mflag
        self.left = None
        self.right = None

class SymbolTable:
    # ***************************************************************
    # ***  FUNCTION SymbolTable (Constructor)                      ***
    # ***************************************************************
    # ***  DESCRIPTION : Initializes an empty symbol table with a root node set to None.
    # ***  INPUT ARGS : None
    # ***  OUTPUT ARGS : None
    # ***  RETURN : None
    # ***************************************************************
    def __init__(self):
        self.root = None

    # ***************************************************************
    # ***  FUNCTION insert                                         ***
    # ***************************************************************
    # ***  DESCRIPTION : Inserts a new node into the symbol table. If the symbol
    # ***                already exists, the MFLAG is updated to True and an error is logged.
    # ***  INPUT ARGS : node (SymbolNode)
    # ***  OUTPUT ARGS : None
    # ***  RETURN : None
    # ***************************************************************
    def insert(self, node):
        existing_node = self.search(node.symbol)
        if existing_node:
            print(f"ERROR – symbol previously defined: {node.symbol}")
            existing_node.mflag = True
        else:
            if self.root is None:
                self.root = node
            else:
                self._insert(self.root, node)

    # ***************************************************************
    # ***  FUNCTION _insert                                        ***
    # ***************************************************************
    # ***  DESCRIPTION : Recursive function to insert a node into the symbol table.
    # ***  INPUT ARGS : root (SymbolNode), node (SymbolNode)
    # ***  OUTPUT ARGS : None
    # ***  RETURN : None
    # ***************************************************************
    def _insert(self, root, node):
        if node.symbol < root.symbol:
            if root.left is None:
                root.left = node
            else:
                self._insert(root.left, node)
        elif node.symbol > root.symbol:
            if root.right is None:
                root.right = node
            else:
                self._insert(root.right, node)

    # ***************************************************************
    # ***  FUNCTION search                                         ***
    # ***************************************************************
    # ***  DESCRIPTION : Searches the symbol table for a given symbol (first 4 characters).
    # ***  INPUT ARGS : symbol (str)
    # ***  OUTPUT ARGS : None
    # ***  RETURN : SymbolNode (if found), otherwise None
    # ***************************************************************
    def search(self, symbol):
        return self._search(self.root, symbol[:4].upper())  # Search only the first 4 characters

    # ***************************************************************
    # ***  FUNCTION _search                                        ***
    # ***************************************************************
    # ***  DESCRIPTION : Recursive helper function to search the symbol table.
    # ***  INPUT ARGS : root (SymbolNode), symbol (str)
    # ***  OUTPUT ARGS : None
    # ***  RETURN : SymbolNode (if found), otherwise None
    # ***************************************************************
    def _search(self, root, symbol):
        if root is None or root.symbol == symbol:
            return root
        if symbol < root.symbol:
            return self._search(root.left, symbol)
        return self._search(root.right, symbol)

    # ***************************************************************
    # ***  FUNCTION inorder                                        ***
    # ***************************************************************
    # ***  DESCRIPTION : Returns the symbol table in inorder traversal (sorted order).
    # ***  INPUT ARGS : None
    # ***  OUTPUT ARGS : None
    # ***  RETURN : List of SymbolNode objects in sorted order
    # ***************************************************************
    def inorder(self):
        results = []
        self._inorder(self.root, results)
        return results

    # ***************************************************************
    # ***  FUNCTION _inorder                                       ***
    # ***************************************************************
    # ***  DESCRIPTION : Recursive helper function to perform inorder traversal.
    # ***  INPUT ARGS : root (SymbolNode), results (list)
    # ***  OUTPUT ARGS : None
    # ***  RETURN : None
    # ***************************************************************
    def _inorder(self, root, results):
        if root is not None:
            self._inorder(root.left, results)
            results.append(root)
            self._inorder(root.right, results)

# ***************************************************************
# ***  FUNCTION validate_symbol                                ***
# ***************************************************************
# ***  DESCRIPTION : Validates if the symbol contains only letters, digits, and underscores.
# ***  INPUT ARGS : symbol (str)
# ***  OUTPUT ARGS : None
# ***  RETURN : True if valid, False otherwise
# ***************************************************************
def validate_symbol(symbol):
    return re.match(r'^[A-Za-z][A-Za-z0-9_]*$', symbol)

# ***************************************************************
# ***  FUNCTION validate_rflag                                 ***
# ***************************************************************
# ***  DESCRIPTION : Validates if the rflag is either True or False. Logs an error if invalid.
# ***  INPUT ARGS : symbol (str), rflag (str)
# ***  OUTPUT ARGS : None
# ***  RETURN : True if valid, None if invalid
# ***************************************************************
def validate_rflag(symbol, rflag):
    if rflag.lower() in ['true', 'false']:
        return rflag.lower() == 'true'
    else:
        print(f"ERROR – symbol {symbol.upper()} invalid rflag: {rflag}")
        return None  # Return None to indicate invalid flag

# ***************************************************************
# ***  FUNCTION read_symbol_file                               ***
# ***************************************************************
# ***  DESCRIPTION : Reads symbols, values, and flags from the input file (SYMS.DAT)
# ***                and inserts valid symbols into the symbol table.
# ***  INPUT ARGS : filename (str), table (SymbolTable)
# ***  OUTPUT ARGS : None
# ***  RETURN : None
# ***************************************************************
def read_symbol_file(filename, table):
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if ':' in line:
                    symbol, rest = line.split(':', 1)
                    symbol = symbol.strip()
                    rest = rest.strip()
                    parts = rest.split()

                    if len(symbol) > 10:
                        print(f"ERROR – symbols contain 10 characters maximum: {symbol.lower()}")
                        continue  # Skip symbols that are too long
                    
                    if len(parts) == 2:
                        value_str, rflag_str = parts
                        try:
                            value = int(value_str)
                        except ValueError:
                            print(f"ERROR – symbol {symbol.upper()} invalid value: {value_str}")
                            continue
                        
                        rflag = validate_rflag(symbol, rflag_str)
                        if rflag is None:
                            continue  # Skip inserting the symbol if invalid
                        mflag = False  # Set mflag as False by default.
                    elif len(parts) == 3:
                        value_str, rflag_str, mflag_str = parts
                        try:
                            value = int(value_str)
                        except ValueError:
                            print(f"ERROR – symbol {symbol.upper()} invalid value: {value_str}")
                            continue
                        
                        rflag = validate_rflag(symbol, rflag_str)
                        if rflag is None:
                            continue  # Skip inserting the symbol if invalid
                        mflag = mflag_str.lower() == 'true'
                    else:
                        print(f"ERROR – symbol {symbol.upper()} invalid attributes")
                        continue
                    
                    if not validate_symbol(symbol):
                        print(f"ERROR – symbols contain letters, digits and underscore: {symbol.upper()}")
                        continue
                    
                    node = SymbolNode(symbol, value, rflag, True, mflag)
                    table.insert(node)
                else:
                    print(f"ERROR – invalid symbol line format: {line}")
                    
    except FileNotFoundError:
        print(f"ERROR – File {filename} not found.")


# ***************************************************************
# ***  FUNCTION search_symbols                                 ***
# ***************************************************************
# ***  DESCRIPTION : Reads symbols from a file (search.txt) and searches for each in the symbol table.
# ***                Logs any errors for invalid symbols and prints the corresponding entries.
# ***  INPUT ARGS : filename (str), table (SymbolTable)
# ***  OUTPUT ARGS : None
# ***  RETURN : None
# ***************************************************************
def search_symbols(filename, table):
    seen_symbols = set()  # Track seen symbols to prevent duplicates

    try:
        with open(filename, 'r') as file:
            for line in file:
                full_symbol = line.strip().upper()  # Get the full symbol and convert to uppercase
                symbol = full_symbol[:4]  # Only consider the first 4 characters for comparison

                if len(full_symbol) > 10:
                    print(f"ERROR – symbols contain 10 characters maximum: {full_symbol.lower()}")
                    continue
                
                if symbol in seen_symbols:
                    continue  # Skip if this symbol has already been processed
                
                seen_symbols.add(symbol)  # Mark this symbol as seen
                
                if not validate_symbol(full_symbol):  # Validate the full symbol, not just the first 4 characters
                    print(f"ERROR – symbols contain letters, digits and underscore: {full_symbol}")
                    continue
                
                node = table.search(symbol)
                if node:
                    print(f"{node.symbol: <4}   {node.value: <5} {int(node.rflag): <5} {int(node.iflag): <5} {int(node.mflag): <5}")
                else:
                    print(f"ERROR – {full_symbol} not found in symbol table")
                    
    except FileNotFoundError:
        print(f"ERROR – File {filename} not found.")

# ***************************************************************
# ***  FUNCTION display_table                                  ***
# ***************************************************************
# ***  DESCRIPTION : Displays the symbol table in a formatted manner, with appropriate headers.
# ***  INPUT ARGS : table (SymbolTable)
# ***  OUTPUT ARGS : None
# ***  RETURN : None
# ***************************************************************
def display_table(table):
    symbols = table.inorder()
    
    # Define headers with proper width for each column
    print("\n{:<8} {:<6} {:<5} {:<5} {:<5}".format("Symbol", "Value", "RFlag", "IFlag", "MFlag"))
    print("------------------------------------")
    
    # Display each symbol with aligned columns
    for symbol in symbols:
        print("{:<8} {:<6} {:<5} {:<5} {:<5}".format(
            symbol.symbol, symbol.value, int(symbol.rflag), int(symbol.iflag), int(symbol.mflag)))

# ***************************************************************
# ***  FUNCTION main                                           ***
# ***************************************************************
# ***  DESCRIPTION : Main function that reads the symbol table from SYMS.DAT,
# ***                processes the search file, and displays the symbol table.
# ***  INPUT ARGS : None
# ***  OUTPUT ARGS : None
# ***  RETURN : None
# ***************************************************************
def main():
    if len(sys.argv) < 2:
        print("Usage: python A1.py <search_file>")
        sys.exit(1)

    symbol_table = SymbolTable()
    read_symbol_file('SYMS.DAT', symbol_table)
    
    search_file = sys.argv[1]
    print(f"\nSearching in file: {search_file}")
    search_symbols(search_file, symbol_table)
    
    display_table(symbol_table)

if __name__ == "__main__":
    main()
