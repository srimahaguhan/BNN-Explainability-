from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
import time
from tabulate import tabulate 
from helper_funs import *

def bnn(cnf_file_path):
    '''Initialize all time variables to be used later'''
    Max_SAT_time = 0
    SAT_time1 = 0
    SAT_time2 = 0
    SAT_time = 0
    start_MaxSAT_time = 0
    end_MaxSAT_time = 0
    
    try:
        with open(cnf_file_path, 'r') as f:
            content = f.read()
            #print(f"File content:\n{content}")
        clauses = parse_cnf_manually(content)
        print("made cnf")
        print(clauses)
        if not clauses:
            print("No valid clauses found in the file.")
            return

        wcnf = WCNF()
        wcnf_copy = WCNF()
        for clause in clauses:
            wcnf.append(clause)
            wcnf_copy.append(clause)

        print(f"Number of variables: {wcnf.nv}")
        print(f"Number of clauses: {len(wcnf.hard)}")
        #print(f"Clauses: {wcnf.hard}")

    except Exception as e:
        print(f"Error reading or parsing file: {e}")
        return

    input_vars = get_input_literals_manually(content)
    output_vars = get_output_literals_manually(content)
    output_var = output_vars[0]
    print(f"the input variables:",input_vars)
    print(f"the output variables:",output_vars)

    
    '''if c:
        wcnf.append([output_var])
    else:
        wcnf.append([-output_var])'''

    clauses_copy = clauses
    blocked_inputs= []
   # blocked_inputs.append((-1 * int(lit)) for lit in model)
   # n = 0
    c = 1 
    cumulative_table_data =[]
    while True:     
        table_data = [] 

        with Solver(name='g4', bootstrap_with=clauses_copy, use_timer=True) as solver: # First SAT check (To get a satisfying input instance)
            if c ==1:
                solver.solve([output_var])
                if solver.get_status():
                    print("c is true")
                    model = solver.get_model()
                else:
                    c = 0
                    if solver.solve([-output_var]):
                        print("c is false")
                        model = solver.get_model()
                    else:
                        print("No satisfying input instance")
                        return

            elif solver.solve([-output_var]):
                c = 0
                print("c is false")
                model = solver.get_model()
            else:
                print("No satisfying input instance")
                return
            

           # print(f"Unfiltered model:", model)
           # print("SAT")
          #  print(solver.get_status())
            #time1 = solver.time_accum()
            #print(f"Solving time for first SAT call: {time1} seconds")
            #print(f"Number of variables in the formula:", {solver.nof_vars()})
            #print(f"Number of solver calls: {solver.get_status()}")


        features_values =[]

        for j in range(len(input_vars)):
            if(input_vars[j] in model):
                features_values.append(int(input_vars[j]))
            else:
                features_values.append(-1 * int(input_vars[j]))
        
        #print(f"Input instance: {features_values}")
        all_explanations = []
        All_Filtered_MaxSAT_models =[]

        try:
            #print("started rc2")
            if c:
                wcnf.append([output_var])
                rc2 = RC2(wcnf)
            else:
                wcnf_copy.append([-output_var])
                rc2 = RC2(wcnf_copy)
            for value in features_values:
                value = -1 * int(value)
                rc2.add_clause([value], weight=1)
            
            start_MaxSAT_time = time.time()
            '''exp = rc2.enumerate()'''
            with Solver(name='g4', bootstrap_with=clauses , use_timer=True) as solver:
                m = 0
                Explanation_list = []
                for maxsat_model in rc2.enumerate():
                    '''if m == M: exit'''
                    #print(f"unfiltered MaxSAT model:", maxsat_model)
                    #print( f"COST:" ,rc2.cost)
                    filtered_model = []
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
                    all_explanations.append(value_exp)
                    
                    ''' accumulate each potential value_exp in this'''
                    potential_exp = [abs(ele) for ele in value_exp] #printing absolute value of explanation
                    # print(f"Potential explanation", explanation)

                    ''' Check if value_exp is a real explanation and accumulate it in Explanation_list'''
                    if c:
                        if not solver.solve(assumptions=value_exp + [-output_var]):
                            explanation_abs = [abs(ele) for ele in value_exp]
                            #print("Explanation is:", explanation_abs)
                            Explanation_list.append(explanation_abs)
                    else:
                        if not solver.solve(assumptions=value_exp + [output_var]):
                            explanation_abs = [abs(ele) for ele in value_exp]
                            #print("Explanation is:", explanation_abs)
                            Explanation_list.append(explanation_abs)
                    ''' code to exit prematurely, if you wish to based on time out to for MaxSAT '''
                    '''end_MaxSAT_time = end_MaxSAT_time + time.time() '''
                    '''if (end_MaxSAT_time - start_MaxSAT__time) >= MaxSAT_to: exit'''
                    
                SAT_time2 = solver.time_accum()

                
            end_MaxSAT_time = time.time()
            Max_SAT_time =  end_MaxSAT_time - start_MaxSAT_time
            SAT_time = SAT_time2 + SAT_time1
            
            # print(f"Compute time: {Max_SAT_time} seconds")
            # print("All potential explanations from MaxSAT:", all_explanations)
            #print(f"Solving time for both SAT calls: {SAT_time} seconds")
           
            
            rc2.delete()
        except Exception as e:
            print(f"Error in RC2 processing: {e}")

        ''' I am doing this incrementally now within the above for loop
        #print("started checking for real explanations")
        Explanation_list = []
        for explanation in all_explanations:
            with Solver(name='g4', bootstrap_with=clauses , use_timer=True) as solver:
                if c:
                    if not solver.solve(assumptions=explanation + [-output_var]):
                        explanation_abs = [abs(ele) for ele in explanation]
                        #print("Explanation is:", explanation_abs)
                        Explanation_list.append(explanation_abs)
                else:
                    if not solver.solve(assumptions=explanation + [output_var]):
                        explanation_abs = [abs(ele) for ele in explanation]
                        #print("Explanation is:", explanation_abs)
                        Explanation_list.append(explanation_abs)

        time2 = solver.time_accum()
        #print(f"Solving time for second SAT call: {time2} seconds")
        time = time1+time2
        #print(f"Solving time for both SAT calls: {SAT_time} seconds") '''

        table_data.append([c, features_values, SAT_time, Max_SAT_time, All_Filtered_MaxSAT_models, Explanation_list])
        cumulative_table_data.extend(table_data)

    
        #blocked_inputs = ((-1 * int(lit)) for lit in features_values)

        for lit in features_values:
            var = -1 * int(lit)
            blocked_inputs.append(var)
        

        clauses_copy.append(blocked_inputs)
       
        #print(f"BLOCKED INPUTS: ", blocked_inputs)
        blocked_inputs =[]
        #n = n+1
        with open("/home/guhan/code/output_table.txt", "w") as f: #Dump the table containing all the output info into a file 
            f.write(tabulate(cumulative_table_data, headers=["Output", "Input", "SAT time", "MaxSAT time", "Filtered MaxSAt models", "Explanations"], tablefmt="grid"))

        print(tabulate(cumulative_table_data, headers=["Output", "Input", "SAT time", "MaxSAT time", "Filtered MaxSAt models", "Explanations"], tablefmt="grid"))   
    

if __name__ == "__main__":
    cnf_file_path = read_cnf_file()
    
    start_time = time.time()
    bnn(cnf_file_path)
    end_time = time.time()
    
    #print(f"Total execution time: {end_time - start_time} seconds")
