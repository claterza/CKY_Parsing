#!/opt/python-3.4/bin/python3.4

#################################################################
#
# Author : Chris LaTerza
#
# Implements a pure CKY parser for natural langauge sentences.
# Does not resolve ambiguity; instead, produces all possible 
# parses of a sentence. 
#
#################################################################

import re
import nltk

# keys (node_tups) are 4-tuples of the form
# (<nonterminal> <start-index> <stop-index> <unique-hash-code>)

class Rule:
	def __init__(self, lhs, rhs):
		self.lhs = lhs # a string for the nonterminal
		self.rhs = rhs # a list of strings

	def __str__(self):
		return self.lhs + ' -> ' + ' '.join(self.rhs) + '\n' 

class Grammar:
	def __init__(self, start_symbol, preterm_rules, branching_rules):
		self.start_symbol    = start_symbol
		self.preterm_rules   = preterm_rules
		self.branching_rules = branching_rules

class CKY_Parser:
	def __init__(self, grammar_filename):
		self.grammar = self.load_cnf_grammar(grammar_filename)
		self.hash_count = 0

	def load_cnf_grammar(self, grammar_filename):
		"""
		Loads a grammar in CNF from given file
		"""
		grammar_file = open(grammar_filename,'r')
		start_symbol    = ''
		preterm_rules   = []
		branching_rules = []
		for line in grammar_file:
			if len(line.strip()) > 0 and line[0] not in '# ':
				# get start symbol
				if len(start_symbol) == 0 or line[0] == '%':
					start_symbol = re.sub("\%start","",line).split()[0]
				if line[0] == '%':
					continue
				# add rules
				rules = line.strip().split('->')
				lhs = rules[0].strip()
				rhs = [(sym.split()) for sym in rules[1].strip().split('|')]
				for production in rhs:
					if len(production) == 1:
						preterm_rules.append(Rule(lhs,[w[1:-1] for w in production])) #removes quotes
					else:
						branching_rules.append(Rule(lhs,production))
		grammar_file.close()
		return Grammar(start_symbol, preterm_rules, branching_rules)


	def parse_sentence_file(self, sentence_filename, output_filename):
		"""
		Writes parse output for each sentence in the sentence file
		to the output file
		"""
		fin  = open(sentence_filename,'r')
		fout = open(output_filename,'w')
		#TOTAL_PARSES = 0.0
		#TOTAL_SENTS  = 0.0
		for line in fin:
			#TOTAL_SENTS += 1
			parses = self.parse_sentence(line)
			fout.write(line)
			for parse in parses:
				fout.write(parse+'\n')
				#TOTAL_PARSES += 1
			fout.write("Number of parses = %d\n\n"%(len(parses)))
		#fout.write("Avg parses = %f"%(TOTAL_PARSES/TOTAL_SENTS))
		fin.close()
		fout.close()

	def parse_sentence(self, sentence):
		"""
		Returns a list of a list of all parses as strings, 
		each string derived from an NLTK tree
		"""
		words = nltk.word_tokenize(sentence)
		table = self.build_cky_table(words)
		all_parses = []
		start_sym = self.grammar.start_symbol
		roots = [r for r in table[0][len(words)-1] if r[0] == self.grammar.start_symbol]
		for root in roots:
			tree = self.build_parse_tree(root, table)
			all_parses.append(str(tree))
		return all_parses

	def build_parse_tree(self, node_tup, table):
		"""
		Given a CKY table and node_tuple (key in table),
		recursively builds an NLTK tree.
		"""
		parent_sym  = node_tup[0]
		start_index = node_tup[1]
		stop_index  = node_tup[2]
		production  = table[start_index][stop_index][node_tup]
		if len(production) == 1:
			# preterminal: build leaf
			return nltk.Tree(parent_sym, production)
		else:
			# branching node, recurse
			left_tree  = self.build_parse_tree(production[0], table)
			right_tree = self.build_parse_tree(production[1], table)
			return nltk.Tree(parent_sym, [left_tree, right_tree])
			
	def build_cky_table(self, words):
		"""
		Builds a CKY table from a list of tokenized words.
		"""
		words.insert(0,None) # makes word indicies start at 1
		size = range(len(words))
		table  = [[{} for i in size] for i in size[:-1]]
		for j in range(1,len(words)):
			table[j-1][j] = self.add_preterminal(words[j],j-1,j)
			inner_range = range(0,j-1)
			inner_range = list(inner_range)
			inner_range.sort(reverse=True)
			for i in inner_range:
				for k in range(i+1,j):
					table[i][j] = self.add_branching_nonterminals(table,i,j,k) 
		return table

	def add_preterminal(self, terminal, i, j):
		"""
		Add lhs of rules of the form A -> a to cell i,j
		"""
		l = [r.lhs for r in self.grammar.preterm_rules if terminal in r.rhs]
		res = {}
		for preterm in l:
			key = (preterm, i, j, self.hash_count)
			res[key] = [terminal]
			self.hash_count += 1
		return res

	def add_branching_nonterminals(self, table, i, j, k):
		"""
		Add lhs of rules of the form A -> B C to cell i,j
		Uses k as splitting index
		"""
		res = table[i][j]
		for rule in self.grammar.branching_rules:
			l_child = rule.rhs[0]
			r_child = rule.rhs[1]
			for l_tup in table[i][k]:
				for r_tup in table[k][j]:
					if l_child == l_tup[0] and r_child == r_tup[0]:
						key = (rule.lhs, i, j, self.hash_count)
						res[key] = [l_tup, r_tup]
						self.hash_count += 1
		return res

if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser(__doc__)
	options, args = parser.parse_args()
	grammar_filename  = args[0]
	sentence_filename = args[1]
	output_filename   = args[2]
	parser = CKY_Parser(grammar_filename)
	parser.parse_sentence_file(sentence_filename, output_filename)


