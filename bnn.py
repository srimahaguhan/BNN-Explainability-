from pysat.pb import PBEnc
from pysat.formula import WCNF
from pysat.examples.rc2 import RC2
from typing import List

pbc_list = [[[1,2,3], [1,1,1], 2, 1], [[1,2,3], [1,1,1], 1, -1], [[1,-2,3], [1,1,1], 1, 1], [[1,-2,3], [1,1,1], 0, -1], [[-1,2,3], [1,1,1], 1, 1], [[-1,2,3], [1,1,1], 0, -1], [[1,2,-3], [1,1,1], 1, 1], [[1,2,-3], [1,1,1], 0, -1], [[-1,2,-3], [1,1,1], 1, 1], [[-1,2,-3], [1,1,1], 0, -1], [[4,5,6,7,8],[1,1,1,1,1],5,1], [[4,5,6,7,8],[1,1,1,1,1],4,-1]]

conditional_list = [[4],[-4],[5],[-5],[6],[-6],[7],[-7],[8],[-8],[9],[-9]]

wcnf = WCNF()
def conditionals(cnf: List[List[int]], pre_cond: List[int]): 
    # encoding [(v1 /\ v2 /\ ...) --> CNF] given lists [v1,v2,...] and list of clauses in CNF
    for list in cnf:
        for lit in pre_cond:
            list.append(-lit)
    
    print("conditionals",cnf.clauses)

print(pbc_list)
print(conditional_list)

for i in range(0, len(pbc_list)):
    if(pbc_list[i][3] == 1): 
        pb_enc = PBEnc.atleast(pbc_list[i][0], pbc_list[i][1], top_id = 10,bound=pbc_list[i][2])
    elif(pbc_list[i][3] == -1):
        pb_enc = PBEnc.atmost(pbc_list[i][0], pbc_list[i][1], top_id = 10,bound=pbc_list[i][2])
    elif(pbc_list[i][3] == 0):
        pb_enc = PBEnc.equals(pbc_list[i][0], pbc_list[i][1], top_id = 10,bound=pbc_list[i][2])
    print("PBEnc", pb_enc.clauses)

    
    if conditional_list[i] != []:
        conditionals(pb_enc, conditional_list[i])

  
    
    
    for clause in pb_enc.clauses:
        wcnf.append(clause)
       
        
try:
    with RC2(wcnf) as rc2:
        rc2.add_clause([9])
        rc2.add_clause([1], weight=1)
        rc2.add_clause([-2], weight=1)
        rc2.add_clause([3], weight=1)
        for model in rc2.enumerate():
            print("Enumerated", model)
except Exception as e:
   print(f"Error: {e}")
   