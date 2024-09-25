from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
import time
from tabulate import tabulate 
import argparse

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



def bnn(cnf_file_path, output_file_path): 
    try:
        with open(cnf_file_path, 'r') as f:
            content = f.read()
            #print(f"File content:\n{content}")
        clauses = parse_cnf_manually(content)
        #print("made cnf")
        #print(clauses)
        if not clauses:
            print("No valid clauses found in the file.")
            return

        wcnf = WCNF()
        wcnf_copy = WCNF()
        for clause in clauses:
            wcnf.append(clause)
            wcnf_copy.append(clause)

        print(f"Number of variables: {wcnf.nv}")
        #print(f"Number of clauses: {len(wcnf.hard)}")
        #print(f"Clauses: {wcnf.hard}")

    except Exception as e:
        print(f"Error reading or parsing file: {e}")
        return

    input_vars = get_input_literals_manually(content)
    output_vars = get_output_literals_manually(content)
    #set_output_vars = [-101, -102, -103, -104, -105, 106 , -107 ,-108 , -109, -110]
    set_output_vars = [output_vars[0]]
    #output_var = output_vars[5]
    print(f"the input variables:",input_vars)
    print(f"the output variables:",output_vars)
    print(f"Output Variable: ", set_output_vars)
    
    '''if c:
        wcnf.append([output_var])
    else:
        wcnf.append([-output_var])'''

    clauses_copy = clauses
    blocked_inputs= []
   # blocked_inputs.append((-1 * int(lit)) for lit in model)
    n = 0
    c = 1 
    N = 8
    M = 100
    time_out = 2000
    time1 =0 
    time2 = 0
    x =0

    cumulative_table_data =[]
    while True:     
        table_data = [] 
        SAT_time = 0
        Max_SAT_time = 0

        with Solver(name='g4', bootstrap_with=clauses_copy, use_timer=True) as solver: # First SAT check (To get a satisfying input instance)
            if n==N:
                print("Done with all input instances")
                return 
            else:
                if c ==1:
                    solver.solve(set_output_vars)
                    if solver.get_status():
                        print("c is true")
                        model = solver.get_model()
                    else:
                        print("Done with c ==1 instances")
                        return
                        '''c = 0
                        if solver.solve([-output_var]):
                            print("c is false")
                            model = solver.get_model()
                        else:
                            print("No satisfying input instance")
                            return'''

                '''elif solver.solve([-output_var]):
                    c = 0
                    print("c is false")
                    model = solver.get_model()
                else:
                    print("No satisfying input instance")
                    return'''
            

           # print(f"Unfiltered model:", model)
           # print("SAT")
          #  print(solver.get_status())
            time1 = solver.time_accum()
            print(f"Solving time for first SAT call: {time1} seconds")
            #print(f"Number of variables in the formula:", {solver.nof_vars()})
            #print(f"Number of solver calls: {solver.get_status()}")


        features_values =[]

        for j in range(len(input_vars)): # Creating the input instance 
            if(input_vars[j] in model):
                features_values.append(int(input_vars[j]))
            else:
                features_values.append(-1 * int(input_vars[j]))
        
        print(f"Input instance: {features_values}")
        all_explanations = []
        All_Filtered_MaxSAT_models =[]

        try:   # Solving using MaxSAT to generate all potential explanations 
            #print("started rc2")
            if c:
                for var in set_output_vars:
                    wcnf.append([var])
                
                if(x==0):
                    rc2 = RC2(wcnf)
                else:
                    rc2 = RC2(new_wcnf)
            else:
                for var in set_output_vars:
                    wcnf_copy.append([var])
                
                if(x==0):
                    rc2 = RC2(wcnf)
                else:
                    rc2 = RC2(new_wcnf)
            for value in features_values:
                value = -1 * int(value)
                rc2.add_clause([value], weight=1)
            
            start_time = time.time()
  
            Explanation_list = []
            with Solver(name='g4', bootstrap_with=clauses , use_timer=True) as solver:
                m = 0
                while(True):
                    '''if Explanation_list != []: 
                        print("Found an explanation")
                        break'''
                    
                    if Max_SAT_time >= time_out: 
                        print("MaxSAT timed out")
                        break
                    '''if (m == M):
                        print("Enumerated max no of models") 
                        break'''
                   # print("starting compute")
                    maxsat_model = rc2.compute()
                    #print(f"end compute")
                    #print(f"EXP", maxsat_model)
                    if maxsat_model== None: 
                        print("breaking") 
                        break
                    #print(f"unfiltered MaxSAT model:", maxsat_model)
                    #print( f"COST:" ,rc2.cost)
                    '''if rc2.cost > 5: 
                        print("RC2 cost greater than 5")
                        break'''
                    filtered_model = []
                    #print(input_vars)
                    for j in range(len(input_vars)):
                        if(input_vars[j] in maxsat_model):
                            filtered_model.append(int(input_vars[j]))
                        else:
                            filtered_model.append(-1 * int(input_vars[j]))
                   # print(f"filtered MaxSAT model:",filtered_model)
                    All_Filtered_MaxSAT_models.append(filtered_model)
                    value_exp = [] #contains literals that have the same value as the input 
                    for index in range(len(features_values)):
                        if features_values[index] in filtered_model:
                            value_exp.append(features_values[index])
                    #all_explanations.append(value_exp)
            
                    if c:
                        if not solver.solve(assumptions=value_exp + [-ele for ele in set_output_vars]):
                            explanation_abs = [abs(ele) for ele in value_exp]
                            #print("EXPLANATION IS:", explanation_abs)
                            Explanation_list.append(explanation_abs)
                            #print(f"EXPLANATION LIST", Explanation_list)
                    else:
                        if not solver.solve(assumptions=value_exp + set_output_vars):
                            explanation_abs = [abs(ele) for ele in value_exp]
                            #print("EXPLANATION IS:", explanation_abs)
                            Explanation_list.append(explanation_abs) 
                    
                    # Identify unsatisfied clauses and increase their weights
                    unsatisfied_clauses = []
                    for clause in features_values:
                        clause_satisfied = False
                        for lit in [clause]:
                            if lit in maxsat_model:
                                clause_satisfied = True
                                break
                        if not clause_satisfied:
                            unsatisfied_clauses.append(clause)
                    
                    #print(f"UNSATISFIED CLAUSES ",unsatisfied_clauses)
            
                    if clause_satisfied:
                        # Create a new WCNF object with increased weights for unsatisfied clauses
                        new_wcnf = WCNF()
                        #print(wcnf.hard)
                        for clause in wcnf.hard:
                            new_wcnf.append(clause)
                        
                        print(features_values)
                        for lit in features_values:
                            if lit in unsatisfied_clauses:
                                new_wcnf.append(clause, weight=50)  # Increase weight for unsatisfied clauses
                            else:
                                new_wcnf.append(clause, weight=1)  # Keep original weight for satisfied clauses
                        
                        # Reinitialize RC2 with the new weights
                        #rc2 = RC2(new_wcnf)
                        x = x +1 

                    next_blocked_maxsat = []    
                    for lit in maxsat_model:
                        var = -1 * int(lit)
                        next_blocked_maxsat.append(var)
                    rc2.add_clause(next_blocked_maxsat)
                   # print(f"blocked_maxsat_model", next_blocked_maxsat)
                    m = m+1
                    end_time = time.time()
                    Max_SAT_time = Max_SAT_time + (end_time - start_time)
                time2 = solver.time_accum()

            #print(f"Compute time: {Max_SAT_time} seconds")
           # print("All potential explanations from MaxSAT:", all_explanations)
            
            rc2.delete()
        except Exception as e:
            print(f"Error in RC2 processing: {e}")

        print("started checking for real explanations")
        
        print(f"Solving time for second SAT call: {time2} seconds")
        SAT_time = time1+time2
        print(f"Solving time for both SAT calls: {SAT_time} seconds")

        table_data.append([c, SAT_time, Max_SAT_time, Explanation_list, m, len(Explanation_list)])
        cumulative_table_data.extend(table_data)

    
        #blocked_inputs = ((-1 * int(lit)) for lit in features_values)

        for lit in features_values:
            var = -1 * int(lit)
            blocked_inputs.append(var)
        

        clauses_copy.append(blocked_inputs)
       
        #print(f"BLOCKED INPUTS: ", blocked_inputs)
        blocked_inputs =[]
        n = n+1
        with open(output_file_path, "w") as f: #Dump the table containing all the output info into a file 
            f.write(tabulate(cumulative_table_data, headers=["Output", "SAT_time", "MaxSAT_time", "Explanations", "MM", "No EXP"], tablefmt="grid"))

        print(tabulate(cumulative_table_data, headers=["Output", "SAT_time", "MaxSAT_time", "Explanations", "MM", "No EXP"], tablefmt="grid"))    
      
    
def main():
    parser = argparse.ArgumentParser(description="BNN script with configurable input and output paths")
    parser.add_argument("--input", required=True, help="Path to the input CNF file")
    parser.add_argument("--output", default="/home/guhan/code/output_table.txt", help="Path to the output file")
    args = parser.parse_args()

    start_time = time.time()
    bnn(args.input, args.output)
    end_time = time.time()

    print(f"Total execution time: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()