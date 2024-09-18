#Incremental_Version_of_Compute_Multiple_Outputs_With_Negated_Soft_clause.py


The code is designed to compute explanations using MaxSAT for a given CNF. The process involves appending a certain number of soft clauses to the WCNF as hard clauses, which are then used to generate potential explanations. The code reads and parses CNF files, identifies input and output literals, and uses a combination of SAT solving and MaxSAT techniques to explore the solution space.

Some features of the code:
1) The CNF file is manually parsed to extract the clauses, input literals and the output literals.

2) An instance of a SAT solver is initially used to generate a satisfying input instance which is then processed using MaxSAT(RC2 solver) to generate potential explanations.

3) During the MaxSAT processing a certain number(preferably a large set >= 50%) of the negated soft clauses are appended to the WCNF as hard clauses to block them. The idea is to generate the larger explanations first by doing this.  

4) The code tracks time taken for both the SAT and MaxSAT computations.
