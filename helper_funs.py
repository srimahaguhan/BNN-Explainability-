def read_cnf_file():
    file_path = input("Enter the path to the CNF file: ")
    return file_path

def parse_cnf_manually(content): # Function to read the DIMACS file and return all the cnf clauses 
    lines = content.strip().split('\n')
    clauses = []
    for line in lines:
        if line.startswith('p cnf'):
            continue
        if line.startswith('c'):
            continue
        clause = [int(x) for x in line.strip().split()[:-1]]  # Exclude the 0 in the end of each line 
        if clause:
            clauses.append(clause)
    return clauses

def get_input_literals_manually(content): # Function to read the DIMACS file and return the input variables
    lines = content.strip().split('\n')
    clauses = []
    for line in lines:
        if line.startswith('c ind'):
            clause = [int(x) for x in line.strip().split()[2:-1]]  # Remove the trailing zero
            clauses.extend(clause)
    
    return clauses

def get_output_literals_manually(content): # Function to read the DIMACS file and return the output variables
    lines = content.strip().split('\n')
    clauses = []
    for line in lines:
        if line.startswith('c out'):
            clause = [int(x) for x in line.strip().split()[2:-1]]  # Remove the trailing zero
            clauses.extend(clause)
    
    return clauses