from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
import time

def read_cnf_file():
    file_path = input("Enter the path to the CNF file: ")
    return file_path

def parse_cnf_manually(content):
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

def bnn(cnf_file_path):
    try:
        with open(cnf_file_path, 'r') as f:
            content = f.read()
            print(f"File content:\n{content}")

        ''' Calling the function to manually parse the cnf file 
        because we are unable to use 'from_file' or CNF() in this case'''
        clauses = parse_cnf_manually(content)
        
        if not clauses:
            print("No valid clauses found in the file.")
            return

        wcnf = WCNF()
        for clause in clauses:
            wcnf.append(clause)

        print(f"Number of variables: {wcnf.nv}")
        print(f"Number of clauses: {len(wcnf.hard)}")
        print(f"Clauses: {wcnf.hard}")

    except Exception as e:
        print(f"Error reading or parsing file: {e}")
        return
    
    with Solver(name='g4', bootstrap_with=wcnf.hard, use_timer=True) as solver:
        if solver.solve():
            model = solver.get_model()
            print("SAT")
            print(f"Satisfying assignment: {model}")
        else:
            print("UNSAT")
        
        print(f"Solving time: {solver.time()} seconds")
        print(f"Number of solver calls: {solver.nof_vars()}")

    features_values = [1, 2, -3]
    all_explanations = []

    try:
        rc2 = RC2(wcnf)
        rc2.add_clause([9])
        for value in features_values:
            value = -1 * int(value)
            rc2.add_clause([value], weight=1)
        
        start_time = time.time()
        for model in rc2.enumerate():
            explanation = []
            for index in range(len(features_values)):
                if features_values[index] in model:
                    explanation.append(abs(features_values[index]))
            all_explanations.append(explanation)
            print(f"Model: {model}, Explanation: {explanation}")
        end_time = time.time()
        
        print(f"Enumerate time: {end_time - start_time} seconds")
        print("All explanations from MaxSAT:", all_explanations)
        
        rc2.delete()
    except Exception as e:
        print(f"Error in RC2 processing: {e}")

    with Solver(name='g4', bootstrap_with=wcnf.hard) as solver:
        solver.add_clause([-9])
        for explanation in all_explanations:
            if not solver.solve(assumptions=explanation):
                print("Explanation is:", explanation)
                
if __name__ == "__main__":
    cnf_file_path = read_cnf_file()
    
    start_time = time.time()
    bnn(cnf_file_path)
    end_time = time.time()
    
    print(f"Total execution time: {end_time - start_time} seconds")