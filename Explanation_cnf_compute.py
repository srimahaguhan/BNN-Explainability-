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
            #print(f"File content:\n{content}")
        clauses = parse_cnf_manually(content)
        print("made cnf")
        if not clauses:
            print("No valid clauses found in the file.")
            return

        wcnf = WCNF()
        for clause in clauses:
            wcnf.append(clause)

        print(f"Number of variables: {wcnf.nv}")
        print(f"Number of clauses: {len(wcnf.hard)}")
        #print(f"Clauses: {wcnf.hard}")

    except Exception as e:
        print(f"Error reading or parsing file: {e}")
        return
    
    with Solver(name='g4', bootstrap_with=wcnf.hard, use_timer=True) as solver:
        if solver.solve():
            model = solver.get_model()
            print("SAT")
           # print(f"Satisfying assignment: {model}")
        else:
            print("UNSAT")
        
        time1 = solver.time_accum()
        print(f"Solving time for first SAT call: {time1} seconds")
        print(f"Number of variables in the formula:", {solver.nof_vars()})
        print(f"Number of solver calls: {solver.get_status()}")
    
    features_values =[]

    input_vars = [1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29 , 30, 31, 32,33, 34, 35, 36, 37 ,38 ,39 ,40 ,41 ,42 ,43 ,44 ,45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60 ,61 ,62 ,63, 64, 65]
    for j in range(len(input_vars)):
        solver.solve(assumptions= [model.append(input_vars[j])])
        if(solver.get_status == True):
            features_values.append(int(input_vars[j]))
        else:
            features_values.append(-1 * int(input_vars[j]))

    all_explanations = []

    try:
        rc2 = RC2(wcnf)
        rc2.add_clause([66])
        for value in features_values:
            value = -1 * int(value)
            rc2.add_clause([value], weight=1)
        
        start_time = time.time()
        exp = [rc2.compute()]
        for model in exp:
            explanation = []
            for index in range(len(features_values)):
                if features_values[index] in model:
                    explanation.append(abs(features_values[index]))
            all_explanations.append(explanation)
            print(f" Explanation: {explanation}")
        end_time = time.time()
        
        print(f"Compute time: {end_time - start_time} seconds")
        print("All explanations from MaxSAT:", all_explanations)
        
        rc2.delete()
    except Exception as e:
        print(f"Error in RC2 processing: {e}")

    with Solver(name='g4', bootstrap_with=wcnf.hard, use_timer= True) as solver:
        solver.add_clause([-66])
        for explanation in all_explanations:
            if not solver.solve(assumptions=explanation):
                print("Explanation is:", explanation)
    
        time2 = solver.time_accum()
        print(f"Solving time for second SAT call: {time2} seconds")

        print(f"Solving time for both SAT calls: {(time1+time2)} seconds")

if __name__ == "__main__":
    cnf_file_path = read_cnf_file()
    
    start_time = time.time()
    bnn(cnf_file_path)
    end_time = time.time()
    
    print(f"Total execution time: {end_time - start_time} seconds")
