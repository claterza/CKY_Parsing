#!/opt/python-3.4/bin/python3.4

##################################################
#							
# Author: Chris LaTerza
# 
# Converts a CFG grammar to Chomsky normal form
#
##################################################

import re

class Rule:
	def __init__(self, lhs, rhs=[]):
		self.lhs = lhs
		self.rhs = rhs #a single list of symbols

	def __str__(self):
		return self.lhs + ' -> ' + ' '.join(self.rhs) + '\n' 

	def __lt__(self,other):
		return self.lhs < other.lhs

	def __gt__(self, other):
		return self.lhs > other.lhs

	def __eq__(self,other):
		return self.lhs == other.lhs and self.rhs == other.rhs

class CNF_Converter:
	def __init__(self, old_rules, start_symbol):
		self.start_symbol = start_symbol
		self.old_rules = old_rules
		self.after_hybrid = []
		self.after_unit   = []
		self.after_long   = []
		self.final_rules  = []
		self.long_count = 0

	def __str__(self):
		start_rules = []
		non_start   = []
		for rule in self.final_rules:
			if rule.lhs == self.start_symbol:
				start_rules.append(rule)
			else:
				non_start.append(rule)
		non_start.sort()
		res = ''
		for rule in start_rules:
			res += str(rule)
		for rule in non_start:
			res += str(rule)
		return res

	def convert_hybrid(self, rule):
		new_rhs = []
		old_rhs = rule.rhs
		if len(old_rhs) >= 2:
			for sym in old_rhs:
				if self.is_terminal(sym):
					new_non_term = sym[1:-1].upper()
					new_rhs.append(new_non_term)
					self.after_hybrid.append(Rule(new_non_term, [sym]))
				else:
					new_rhs.append(sym)
		else:
			new_rhs = old_rhs
		self.after_hybrid.append(Rule(rule.lhs, new_rhs))

	def convert_unit(self, rule):
		if len(rule.rhs) == 1:
			curr_rules = self.after_hybrid# == old rules after hybrid conversion
			self.get_unit_rhs(rule.lhs, rule.rhs, curr_rules)
		else:
			self.after_unit.append(Rule(rule.lhs, rule.rhs))

	def get_unit_rhs(self, curr_lhs, temp_rhs, curr_rules):
		if len(temp_rhs) == 1 and self.is_terminal(temp_rhs[0]):
			self.after_unit.append(Rule(curr_lhs, temp_rhs))
		elif len(temp_rhs) >= 2:
			self.after_unit.append(Rule(curr_lhs, temp_rhs))
		else:
			for new_rhs in [r.rhs for r in curr_rules if r.lhs == temp_rhs[0]]:
				self.get_unit_rhs(curr_lhs, new_rhs, curr_rules)

	def convert_long(self, rule):
		if len(rule.rhs) <= 2:
			self.after_long.append(Rule(rule.lhs, rule.rhs))
		else:
			old_rhs = rule.rhs
			new_non_term = 'X%d'%(self.long_count)
			self.long_count += 1
			new_rhs = [old_rhs[0], new_non_term]
			self.after_long.append(Rule(rule.lhs, new_rhs))
			#recurse
			next_rule = Rule(new_non_term, old_rhs[1:])
			self.convert_long(next_rule)

	def convert_all_rules(self, conversion_function, input_rules):
		for rule in input_rules:
			conversion_function(rule)

	def is_terminal(self,symbol):
		return re.match(r"[\"\'].*[\"\']",symbol) != None

	def convert(self):
		self.convert_all_rules(self.convert_hybrid, self.old_rules)
		self.convert_all_rules(self.convert_unit, self.after_hybrid)
		self.convert_all_rules(self.convert_long, self.after_unit)
		self.final_rules = self.after_long

def convert_to_cnf(cfg_file, output_file):
	fin =  open(cfg_file,'r')
	fout = open(output_file,'w')
	old_rules = []
	start_symbol = ''
	for line in fin:
		if len(line.strip()) > 0 and line[0] not in '# ':
			#get start
			if len(start_symbol) == 0 or line[0] == '%':
				start_symbol = re.sub("\%start","",line).split()[0]
			if line[0] == '%':
				continue
			# add rules
			rules = line.strip().split('->')
			lhs = rules[0].strip()
			rhs = [(sym.split()) for sym in rules[1].strip().split('|')]
			for production in rhs:
				old_rules.append(Rule(lhs,production))
	cnf = CNF_Converter(old_rules, start_symbol)
	cnf.convert()
	fout.write(str(cnf))

if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser(__doc__)
	options, args = parser.parse_args()
	input_grammar  = args[0]
	output_grammar = args[1]
	convert_to_cnf(input_grammar, output_grammar)
