from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from pysat.solvers import Solver
import time
from tabulate import tabulate
from helper_funs import * 

def bnn(cnf_file_path): 
    try:
        with open(cnf_file_path, 'r') as f:
            content = f.read()
        clauses = parse_cnf_manually(content) #creating clauses for the bnn
        if not clauses:
            print("No valid clauses found in the file.")
            return

        #two copies of wcnf required, because RC2 solver does not support assumptions, to allow for setting the output to 0 and 1.
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
    #setting the intended output values; should ideally be read as input

    # making all but one output to be 1 except 110
    # reason: 
    set_output_vars = [-101, -102, -103, -104, -105, 106, -107, -108, -109, -110] 
    #output_var = output_vars[5]
    print(f"the input variables:",input_vars)
    print(f"the output variables:",output_vars)
    #print(f"Output Variable: ", output_var)
    
    '''if c:
        wcnf.append([output_var])
    else:
        wcnf.append([-output_var])'''
    
    #clauses_copy is used to incrementally generate multiple input instances 
    #clauses is used to check if a potential explanation is a real explanation
    clauses_copy = clauses
    blocked_inputs= []
   # blocked_inputs.append((-1 * int(lit)) for lit in model)

   # various parameters to control the number of models, explanations and input instances generated 
    n = 0 
    c = 1 
    N = 1 #bound on number of input instances 
    M = 1000 # bound on number of models generated 
    m = 0
    time_out = 2000 # bound on the total timeout allowed for generating all explanations for all instances 

    cumulative_table_data =[]
    while True:  # loop for generating explanations for each input instance upto N and time_out   
        table_data = [] 
        SAT_time = 0
        Max_SAT_time = 0
        time1 = 0
        time2 = 0
        Explanation_list = []

        #creating a g4 solver instance to generate a satisfying input instance that classifies an output to 1 or 0
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
                        print("Done with c == 1 instances")
                        return
                    
                    #for now we are setting output to 1 
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

        # This features_values stores the values of literals corresponding to input instances by extracting it from the input model instance
        features_values =[]

        for j in range(len(input_vars)): # Creating the input instance 
            if(input_vars[j] in model):
                features_values.append(int(input_vars[j]))
            else:
                features_values.append(-1 * int(input_vars[j]))
        
        print(f"Input instance: {features_values}")
        all_explanations = []
        All_Filtered_MaxSAT_models =[]

        try:   # Solving using MaxSAT(with RC2 solver) to generate all potential explanations 
            #print("started rc2")
            #adds negation of soft clauses as individual unit literals to wncf, which will be used as hardclauses in the rc2 solver
            if c:
                for var in set_output_vars:
                    wcnf.append([var])
                half_length_features_values = int(len(features_values)* 1)

                for ele in range(half_length_features_values):
                    wcnf.append([features_values[ele]])
                rc2 = RC2(wcnf)
                #print("INPUT INSTANCE:", features_values)
                #print("HARD CLAUSES after appending: ", wcnf)
                #print(half_length_features_values)
            else:
                for var in set_output_vars:
                    wcnf_copy.append([var])
                
                half_length_features_values = int(len(features_values) * 1)

                for ele in range(half_length_features_values):
                    wcnf_copy.append([features_values[ele]])
                rc2 = RC2(wcnf_copy)
            for value in features_values:
                value = -1 * int(value)
                rc2.add_clause([value], weight=1)
            
            start_time = time.time()
  
            #Explanation_list = []
            #creating a new g4 solver instance with scope to later check if a potential explanation generated is a real explanation
            with Solver(name='g4', bootstrap_with=clauses , use_timer=True) as solver:
                #m = 0
                #the following loop incrmentally generates maxsat models of different costs towards generating explanations of different sizes 
                while(True):
                    
                    #exiting the loop based on different exit criteria, currently done in a hardcoded way
                    '''if Explanation_list != []: 
                        print("Found an explanation")
                        break'''
                    
                    if Max_SAT_time >= time_out: 
                        print("MaxSAT timed out")
                        break
                    '''if (m == M):
                        print("Enumerated max no of models") 
                        break'''
                    #print("starting compute")
                    #generate a maxsat model 
                    maxsat_model = rc2.compute()
                    #print(f"end compute")
                    #print(f"EXP", maxsat_model)
                    '''if maxsat_model== None: 
                        print("breaking") 
                        break'''
                    #print(f"unfiltered MaxSAT model:", maxsat_model)
                    #print( f"COST:" ,rc2.cost)
                    '''if rc2.cost > 5: 
                        print("RC2 cost greater than 5")
                        break'''
                    filtered_model = []
                    for j in range(len(input_vars)):
                        if(input_vars[j] in maxsat_model):
                            filtered_model.append(int(input_vars[j]))
                        else:
                            filtered_model.append(-1 * int(input_vars[j]))
                    #print(f"filtered MaxSAT model:",filtered_model)
                    All_Filtered_MaxSAT_models.append(filtered_model)
                    value_exp = [] #contains literals that have the same value as the input 
                    for index in range(len(features_values)):
                        if features_values[index] in filtered_model:
                            value_exp.append(features_values[index])#value_exp contains the literals with the same values as in features_values
                    #all_explanations.append(value_exp)

                    # checking if a potential explanation is a real explanation 
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

                    #generating a negation of the maxsat model to block it in the following 
                    # iteration for generating next potential explanation
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

            print(f"Compute time: {Max_SAT_time} seconds")
           # print("All potential explanations from MaxSAT:", all_explanations)
            
            rc2.delete()
        except Exception as e:
            print(f"Error in RC2 processing: {e}")

        print("started checking for real explanations")
        
        #print(f"Solving time for second SAT call: {time2} seconds")
        SAT_time = time1+time2
        print(f"Solving time for both SAT calls: {SAT_time} seconds")

        table_data.append([c, SAT_time, Max_SAT_time, Explanation_list, len(All_Filtered_MaxSAT_models), len(Explanation_list)])
        cumulative_table_data.extend(table_data)

    
        #blocked_inputs = ((-1 * int(lit)) for lit in features_values)

        #constructing a clause to block the current input instance, to generate the next one 
        for lit in features_values:
            var = -1 * int(lit)
            blocked_inputs.append(var)
        

        clauses_copy.append(blocked_inputs)
       
        #print(f"BLOCKED INPUTS: ", blocked_inputs)
        blocked_inputs =[]
        n = n+1
        with open("/home/guhan/code/output_table.txt", "w") as f: #Dump the table containing all the output info into a file 
            f.write(tabulate(cumulative_table_data, headers=["Output", "SAT_time", "MaxSAT_time", "Explanations", "MM", "No EXP"], tablefmt="grid"))

        print(tabulate(cumulative_table_data, headers=["Output", "SAT_time", "MaxSAT_time", "Explanations", "MM", "No EXP"], tablefmt="grid"))   
    

if __name__ == "__main__":
    cnf_file_path = read_cnf_file()
    
    start_time = time.time()
    bnn(cnf_file_path)
    end_time = time.time()
    
    #print(f"Total execution time: {end_time - start_time} seconds")