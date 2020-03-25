#!/usr/bin/python3

import sys
import random
import time
import os

class SGDB_Solver:
	def getFromDIMACS(file):
		count = 0
		formula = []
		for line in file:
			c = []
			if line[0] == 'c':
				pass
			elif line[0] == 'p':
				p, cnf, variables, claus = line.split()
				lit_position = [[] for _ in range(2*int(variables)+1)]
			else:
				clause = []
				for lit in line.split():
					if int(lit) is not 0:
						clause.append(int(lit))
						lit_position[int(lit)].append(count)
		
				count+=1
				formula.append(clause)

		return SGDB_Solver(variables,len(line.split()[:-1]),lit_position,formula)

	def __init__(self,variables,lenclaus,lit_position,formula):
		self.variables = variables
		self.lenclaus = lenclaus
		self.lit_position = lit_position
		self.formula = formula

	def get_interpretation(self):
		return [i if random.random() < 0.5 else -i for i in range(int(self.variables) + 1)]

	def get_sat_literals(self,interpret):
		true_sat_lit = [0 for _ in self.formula]
		for index, clause in enumerate(self.formula):
			for lit in clause:
				if interpret[abs(lit)] == lit:
					true_sat_lit[index] += 1
		return true_sat_lit
	
	def satisfied_clauses(self, lit):
		return len(self.lit_position[lit])

	def best_lit_to_flip(self,literals):
		best = 0
		bestval = 0
		for lit in literals:
			r1 = self.satisfied_clauses(lit)
			r2 = self.satisfied_clauses(-lit)

			result = abs(r1-r2)
			if result>=bestval:
				best = lit
				bestval = result

		return bestval

	def get_unsat_clauses(self,sat_literals):
		clauses = []
		for i, lit in enumerate(sat_literals):
			if not lit: clauses.append(i) 
		return clauses

	def get_best_literal(self,clause,sat_literals):
		best_liter = []
		min_value = 9999999
		for lit in clause:				
			value = 0
								
			for index in self.lit_position[-lit]:
				if sat_literals[index] == 1:
					value+=1
			
			if min_value == value:
				best_liter.append(lit)

			elif min_value > value:
				min_value = value
				best_liter.clear()
				best_liter.append(lit)

		if random.random() > 0.65 and min_value>0: best_liter = clause
		return random.choice(best_liter)

	def update_interp_and_literals(self,lit,interpretation,sat_literals):
		for c in self.lit_position[lit]: 
			sat_literals[c] += 1
		for c in self.lit_position[-lit]: 
			sat_literals[c] -= 1

		interpretation[abs(lit)]*=-1

	def solve(self):
		max_flips = int(self.variables)*4
		
		while True:
			interpretation = self.get_interpretation()
			sat_literals = self.get_sat_literals(interpretation)

			for i in range(max_flips):
				unsat_clauses = self.get_unsat_clauses(sat_literals)
				
				if not unsat_clauses: return interpretation
				
				unsat_clause = self.formula[random.choice(unsat_clauses)]
				bestLiteral = self.get_best_literal(unsat_clause,sat_literals) 	
			
				self.update_interp_and_literals(bestLiteral,interpretation,sat_literals)

		

def generateOutput(correct_interp):
	msg = 's SATISFIABLE \n'
	msg+='v '
	for i,val in enumerate(correct_interp): 
		if i>0:
			if val>0: msg+=str(i)+' '
			else: msg+='-'+str(i)+' '
	msg+='0'
	
	print(msg)
	f = open("output.cnf", "w")
	f.write(msg)
	f.close()


if __name__ == "__main__":

	# Check parameters
	if len(sys.argv) != 2:
		sys.exit("Use: %s <input_cnf_formula>" % sys.argv[0])

	start_time = time.time()
	# Check path errors
	try:
		path = str(sys.argv[1])
	except:
		sys.exit("ERROR: input_cnf_formula not a file (%s)." % sys.argv[1])
	if path[-4:] != '.cnf':
		sys.exit("ERROR: input_cnf_formula must be ended with .cnf")

	cnf = SGDB_Solver.getFromDIMACS(open(path, 'r'))

	correct_interp = cnf.solve()
	generateOutput(correct_interp)
	print("--- %s seconds ---" % (time.time() - start_time))
	
	#Solution validator
	os.system("python solution-validator.py "+path+" output.cnf")


#LISTS WITH THE POSITION INSTEAD OF THE DICTIONARY -> WIll improve.
#1st version with dictionaries and random -> 10-30 2s 10-40 5s 20-40 2s 20-60 no. 2
#2nd version with lists and random -> 20-60 1s 
# 400 1100 3 -> 280 seg, prop 2,75
# 400 1000 -> 18 prop 2.5
