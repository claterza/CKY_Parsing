#!/opt/python-3.4/bin/python3.4

#########################################
#
# Author : Chris LaTerza
#
# Induces a PCFG with parent annotation
#
#########################################

import re
import nltk

class PCFG_Inducer:
	def __init__(self):
		self.rule_counts = {}
		self.parent_counts = {}
		self.start_symbol = ''

	def get_rule_counts(self, treebank_filename):
		"""
		Counts occurrances of each rule in a treebank file.
		"""
		fin = open(treebank_filename,'r')
		for line in fin:
			line = line.strip()
			if len(line) > 0 and line[0] != '#':
				tree = nltk.Tree.fromstring(line)
				if self.start_symbol == '':
					self.start_symbol = tree.label()
				tree = self.add_parent_annotation(tree)
				print(tree)
				self.update_counts(tree)
		fin.close()

	def add_parent_annotation(self, tree):
		"""
		Takes an nltk.Tree and returns one with parent annotation
		on each nonterminal. If the original tree has a child node
		label C and parent node labeled P, the child node in the 
		new tree will be C^P.  Start node is unannotated.
		"""
		if len(tree) == 1:
			return tree
		else:
			left = tree[0]
			right = tree[1]
			parent = tree.label().split('^')[0]
			left.set_label('%s^%s'%(left.label(),parent))
			right.set_label('%s^%s'%(right.label(), parent))
			left = self.add_parent_annotation(left)
			right = self.add_parent_annotation(right)
			return nltk.Tree(tree.label(), [left, right])

	def update_counts(self, tree):
		"""
		Updates the global rule counts from a single nltk.Tree.
		"""
		if len(tree) == 1:
			terminal = "'%s'"%(tree[0]) #add single quotes to terminal
			self.increment_counts(tree.label(), terminal)
		else:
			left_tree = tree[0]
			right_tree = tree[1]
			production = "%s %s"%(left_tree.label(), right_tree.label())
			print(type(tree.label()))
			self.increment_counts(tree.label(), production)
			self.update_counts(left_tree)
			self.update_counts(right_tree)

	def increment_counts(self, parent, production):
		"""
		From a given parent and its production, adds one to 
		both the parent counts and rule counts.  Both parent
		and production arguments are strings.
		"""
		# update rule counts
		if parent not in self.rule_counts:
			self.rule_counts[parent] = {}
		if production not in self.rule_counts[parent]:
			self.rule_counts[parent][production] = 0
		self.rule_counts[parent][production] += 1
		# increment parent counts
		if parent not in self.parent_counts:
			self.parent_counts[parent] = 0
		self.parent_counts[parent] += 1

	def print_pcfg(self, output_PCFG_file):
		"""
		Prints the induced PCFG to the given output file.  This is 
		where probabilities are calculated.
		"""
		fout = open(output_PCFG_file,'w')
		non_terminals  = self.rule_counts.keys()
		non_start_syms = [s for s in non_terminals if s != self.start_symbol]
		non_start_syms.sort()
		parents = [self.start_symbol] + non_start_syms
		for parent in parents:
			productions = list(self.rule_counts[parent].keys())
			productions.sort()
			for production in productions:
				rule_count = self.rule_counts[parent][production]
				prob = rule_count/float(self.parent_counts[parent])
				fout.write('%s -> %s [%.4f]\n'%(parent, production, prob))
		fout.close()


if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser(__doc__)
	options, args = parser.parse_args()
	treebank_filename  = args[0]
	output_PCFG_file   = args[1]
	converter = PCFG_Inducer()
	converter.get_rule_counts(treebank_filename)
	converter.print_pcfg(output_PCFG_file)
