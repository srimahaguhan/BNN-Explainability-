from pysat.formula import CNF, WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
import time

def read_cnf_file():
    file_path = input("Enter the path to the CNF file: ")
    return file_path

def bnn(cnf_file_path):
    cnf = CNF(from_file=cnf_file_path)
    wcnf = WCNF()
    solver = Solver()

    # Adding clauses to WCNF and solver
    for clause in cnf.clauses:
        wcnf.append(clause)
        solver.add_clause(clause)

    print(f"Total number of clauses: {len(cnf.clauses)}")

    features_values = [-1, 2, 3]
    all_explanations = []

    try:
        with RC2(wcnf) as rc2:
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

    except Exception as e:
        print(f"Error: {e}")

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
