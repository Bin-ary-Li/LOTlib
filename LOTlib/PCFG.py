# -*- coding: utf-8 -*-

import numpy as np

from copy import deepcopy
from collections import defaultdict
from random import randint, random

from LOTlib.Miscellaneous import *
from LOTlib.FunctionNode import FunctionNode
from LOTlib.GrammarRule import GrammarRule

class PCFG:
	"""
		A PCFG class that can handle special types of rules:
			- Rules that introduce bound variables
			- Rules that sample from a continuous distribution
			- Variable resampling probabilities among the rules
			
		NOTE: Bound variables have a rule id < 0
		
		This class fixes a bunch of problems that were in earlier versions, such as 
			
	"""
	
	def __init__(self, BV_P=10.0, BV_RESAMPLE_P=1.0):
		self.__dict__.update(locals())
		
		self.rules = defaultdict(list) # a dict from nonterminals to lists of GrammarRules
		self.rule_count = 0
		self.bv_count = 0 # how many ruls in the grammar introduce bound variables?
		self.bv_rule_id = 0 # a unique idenifier for each bv rule id (may get quite large). The actual stored rule are negative this
	
	def is_nonterminal(self, x): 
		""" A nonterminal is just something that is not a list, and a key for self.rules"""
		return (not islist(x)) and (x in self.rules)
	def is_terminal(self, x):    
		""" A terminal is not a nonterminal and either has no children or its children are terminals themselves """
		if self.is_nonterminal(x): return False
		
		if isinstance(x, list):
			for k in x: 
				if not self.is_terminal(k): return False
				
		if isinstance(x, FunctionNode): # if you are structured, you must not contain nonterminals below
			for k in x.args:
				if not self.is_terminal(k): return False
		
		# else we get here for strings, etc.
		return True
		
	def display_rules(self):
		for k in self.rules.keys():
			for r in self.rules[k]:
				print r
	
	def nonterminals(self):
		return self.rules.keys()
		
	# these take probs instead of log probs, for simplicity
	def add_rule(self, nt, name, to, p, resample_p=1.0, bv=[], rid=None):
		"""
			Adds a rule, and returns the added rule (for use by add_bv)
		"""
		
		if rid is None: 
			rid = self.rule_count
			self.rule_count += 1
		
		assert_or_die( isinstance(bv, list),  "Bound variables must be a list of nonterminals:  " + str(locals()))
		
		if name is not None and name.lower() == 'lambda':
			self.bv_count += 1
			assert_or_die( len(to) == 1,  "Lambda must have exactly one argument: " + str(locals()))
		
		# Create the rule and add it
		newrule = GrammarRule(nt,name,to, p=p, resample_p=resample_p, bv=bv, rid=rid)
		self.rules[nt].append(newrule)
		
		return newrule
		
	############################################################
	## Bound variable rules
	############################################################
	
	def remove_rule(self, r):
		""" Remove a rule (comparison is done by nt and rid) """
		self.rules[r.nt].remove(r)
	
	# add a bound variable and return the rule
	def add_bv_rule(self, nt, d):
		""" Add an expansion to a bound variable of type t, at depth d. Add it and return it. """
		self.bv_rule_id += 1 # A unique identifier for each bound variable rule (may get quite large!)
		return self.add_rule( nt, name="y"+str(d), to=[], p=self.BV_P, resample_p=self.BV_RESAMPLE_P, rid=-self.bv_rule_id, bv=[])
					
	
	############################################################
	## generation
	############################################################

	def generate(self, x='START', d=0):
		"""
			Generate from the PCFG -- default is to start from 
			x - either a nonterminal or a FunctionNode
			
			TODO: We can make this limit the depth, if we want. Maybe that's dangerous?
		"""
		
		#print "GENERATE ", x
		
		if isinstance(x,list):
			
			# If we get a list, just map along it to generate. We don't count lists as depth--only FunctionNodes
			
			return map(lambda xi: self.generate(x=xi, d=d), x)
			
		if self.is_nonterminal(x):
			# if we generate a nonterminal, then sample a GrammarRule, convert it to a FunctionNode
			# via nt->returntype, name->name, to->args, 
			# And recurse.
			
			r, lp = weighted_sample(self.rules[x], return_probability=True, log=True)
			
			#print " IN GENERATE ADDING d=",d
			# what rules did we add? Possibly empty. This adds and returns them
			addedrules = [ self.add_bv_rule(b,d) for b in r.bv ]
			
			# expand the "to" part of our rule
			args = self.generate(r.to, d=d+1)

			# remove what we added
			[ self.remove_rule(rr) for rr in addedrules ]
			
			# create the new node
			fn = FunctionNode(returntype=r.nt, name=r.name, args=args, lp=lp, bv=addedrules, ruleid=r.rid )
			
			return fn
			
		else: # must be a terminal
			return x
			
		
	def iterate_subnodes(self, t, d=1, predicate=lambdaTrue, do_bv=True, yield_depth=False):
		"""
			Iterate through all subnodes of t, while updating my added rules (bound variables)
			so that at each subnode, the grammar is accurate to what it was 
			
			if We set do_bu=False, we don't do bound variables (useful for things like counting nodes, instead of having to update the grammar)
			
			yield_depth -- if True, we return (node, depth) instead of node
			predicate -- filter only the ones that match this
			
			# NOTE: if you DON'T iterate all the way through, you end up acculmulating bv rules
			# so NEVER stop this iteration in the middle!
		"""
		if isinstance(t, list):
			for ti in t: 
				for g in self.iterate_subnodes(ti, d=d, do_bv=do_bv, yield_depth=yield_depth):
					if predicate(g): yield g 
					
		if isinstance(t,FunctionNode):
			yield (t,d) if yield_depth else t
			
			if do_bv: # add the bound variables to the rules
				for r in t.bv: self.rules[r.nt].append(r)
			
			for a in t.args:
				for g in self.iterate_subnodes(a, d=d+1, do_bv=do_bv, yield_depth=yield_depth): # pass up anything from below
					if predicate(g): yield g
			
			# And remove them
			if do_bv: 
				for r in t.bv: self.remove_rule(r)
	
	def sample_random_node(self, t, prob=False, do_bv=True):
		"""
			Choose a node at random from the entire tree and return it (NOT a copy, so we can mutate)
			- prob - if True, return normalized log probability of the resample
			- do_bv - if True, we generate bound variables (to correctly handle the resampling prob, etc)
		"""
		
		Z = self.resample_normalizer(t) # the total probability
		
		r = random() * Z # now select a random number (giving a random node)
		sampled_node = None
		foundit = False
		thesum = 0.0
		the_resampled_p = None
		
		for ni in self.iterate_subnodes(t, do_bv=do_bv):
			thesum += ni.resample_p # the probability of resampling this thing
			if thesum >= r and not foundit: # our node
				foundit=True
				sampled_node = ni
				the_resampled_p = ni.resample_p
				if not do_bv: break # if not doing bv, we can quit
				else: pass # Must iterate through to keep handling the bound variables
		
		assert sampled_node is not None
		
		if prob: return [ log(the_resampled_p)-log(Z), sampled_node]
		else:    return sampled_node
			
		
	def resample_normalizer(self, t, predicate=lambdaTrue):
		Z = 0.0
		for ti in self.iterate_subnodes(t, do_bv=True):
			if predicate(ti): Z += ti.resample_p 
		return Z
	
	# choose a node at random and resample it
	def propose(self, t):
		""" resample a random subnode of t, returning a copy and a f/b probability """
			
		Z = self.resample_normalizer(t) # the total probability
		
		r = random() * Z # now select a random number (giving a random node)
		
		# copy since we modify in place
		newt = t.copy()
		
		sm = 0.0
		my_resample_p = 1.0
		foundit = False
		for ni, di in self.iterate_subnodes(newt, do_bv=True, yield_depth=True):
			sm += ni.resample_p
			if sm >= r and not foundit: # our node
				ni.resample(self, d=di)
				my_resample_p = ni.resample_p # which prob did we actually use?
				foundit = True
			# NOTE: Here you MUST evaluate on each loop iteration, or else this wont' remove the added bvrules -- no breaking!
		
		newZ = self.resample_normalizer(newt)
		
		#print "PROPOSED ", newt		
		f = (log(my_resample_p) - log(Z)) + newt.log_probability()
		b = (log(my_resample_p) - log(newZ))    + t.log_probability()
		
		return newt, f-b
	
	def get_replicating_rules(self, name):
		return filter(lambda x: x.name==name and any([a==name for a in x.args]), self.rules[x])
		
	def sample_node_via_iterate(self, predicate=lambdaTrue, do_bv=True):
		"""
			This will yield a random node in the middle of it's iteration, allowing us to expand bound variables properly
			(e.g. when the node is yielded, the state of the grammar is correct)
			It also yields the probability and the depth
			
			So use this via
			
			for ni, di, prb in sample_node_via_iterate():
				... do something
				
			and it should only execute once, despite the "for"
			The "for" is nice so that it will yeild back and clean up the bv
			
		"""
		
		Z = self.resample_normalizer(t, predicate=predicate) # the total probability
		r = random() * Z # now select a random number (giving a random node)
		my_resample_p = 1.0 # the prob of the one we actually resampled
		sm = 0.0
		foundit = False
		
		for ni, di in self.iterate_subnodes(newt, predicate=predicate, do_bv=do_bv, yield_depth=True):
			sm += ni.resample_p
			if sm >= r and not foundit: # our node
				foundit=True
				yield [ni, di, ni.resample_p/Z]
				
	
	def do_insert_delete(self, t):
		"""
			TODO: Include insert/delete proposals, such that we can take and_(X,Y) -> X and X->and_(X,Y)
		"""
		
		newt = t.copy()
		
		if random() < 0.5: # So we insert
			
			# For an insert, we must find a replicating rule and a node 
			replicating_rules = self.get_replicating_rules(ni.name)
			if len(replicating_rules) == 0: return [newt, 0.0]
			r, lp = weighted_sample(replicating_rules, return_probability=True, log=True) # choose a replicating rule
			
			# Now find a node with type r, if there is one
			
			
			
			
			
			
			
			
			
		
			# sample a replicating rule
			for ni, di, prb in self.sample_node_via_iterate( predicate=lambda x: x.is_replicating() ):
				
				# choose a replicating rule
				
				
					
				nrhs = len( [ x.to for x in r.to if x == ni.name] ) # how many on the rhs are there?
				replace_i = randint(nrhs) # choose the one to replace
					
				## Now expand args but only for the one we don't sample...
				args = []
				for x in ni.args:
					if x == ni.name:
						if replace_i == 0: args.append( ni ) # if it's the one we replace into
						else:              args.append( self.generate(x, d=di+1) ) #else generate like normal
						
						replace_i -= 1
				
				# create the new node
				ni.setto( FunctionNode(returntype=r.nt, name=r.name, args=args, lp=lp, bv=addedrules, ruleid=r.rid ) )
					
		else: # A delete move!
			for ni, di, prb in self.sample_node_via_iterate( predicate=lambda x: x.is_replicating() ):
		
			for ni, di in self.iterate_subnodes(newt, do_bv=True, yield_depth=True):
				sm += ni.resample_p
				if sm >= r and not foundit: # our node
					foundit=True
					
					# choose a replicating rule
					replicating_rules = self.get_replicating_rules(ni.name)
					if len(replicating_rules) == 0: return [newt, 0.0]
					r, lp = weighted_sample(replicating_rules, return_probability=True, log=True) # choose a replicating rule
					
					nrhs = len( [ x.to for x in r.to if x == ni.name] ) # how many on the rhs are there?
					replace_i = randint(nrhs) # choose the one to replace
					
					addedrules = [ self.add_bv_rule(b,d) for b in r.bv ]
					
					## Now expand args but only for the one we don't sample...
					args = []
					for x in ni.args:
						if x == ni.name:
							if replace_i == 0: args.append( ni ) # if it's the one we replace into
							else:              args.append( self.generate(x, d=di+1) ) #else generate like normal
							
							replace_i -= 1
					
					## remove what we added
					[ self.remove_rule(rr) for rr in addedrules ]
					
					# create the new node
					ni.setto( FunctionNode(returntype=r.nt, name=r.name, args=args, lp=lp, bv=addedrules, ruleid=r.rid ) )
					
			
			
			
	def increment_tree(self, x, depth):
		""" 
			A lazy version of tree enumeration. Here, we generate all trees, starting from a rule or a nonterminal symbol. 
			
			This is constant memory
		"""
		assert_or_die( self.bv_count==0, "Error: increment_tree not yet implemented for bound variables." )
		
		
		if isinstance(x, FunctionNode) and depth >= 0: 
			#print "FN:", x, depth
			
			# add the rules
			#addedrules = [ self.add_bv_rule(b,depth) for b in x.bv ]
				
			original_x = x.copy()
			
			# go all odometer on the kids below::
			iters = [self.increment_tree(y,depth) if self.is_nonterminal(y) else None for y in x.args]
			if len(iters) == 0: yield x.copy()
			else:
				
				# First, initialize the arguments
				for i in xrange(len(iters)):
					if iters[i] is not None: x.args[i] = iters[i].next()
				
				# the index of the last terminal symbol (may not be len(iters)-1),
				last_terminal_idx = max( [i if iters[i] is not None else -1 for i in xrange(len(iters))] )
				
				## Now loop through the args, counting them up
				continue_counting = True
				while continue_counting: # while we continue incrementing
					
					yield x.copy() # yield the initial tree, and then each successive tree
					
					# and then process each carry:
					for carry_pos in xrange(len(iters)): # index into which tree we are incrementing
						if iters[carry_pos] is not None: # we are not a terminal symbol (mixed in)
							
							try: 
								x.args[carry_pos] = iters[carry_pos].next()
								break # if we increment successfully, no carry, so break out of i loop
							except StopIteration: # if so, then "carry"								
								if carry_pos == last_terminal_idx: 
									continue_counting = False # done counting here
								elif iters[carry_pos] is not None:
									# reset the incrementer since we just carried
									iters[carry_pos] = self.increment_tree(original_x.args[carry_pos],depth)
									x.args[carry_pos] = iters[carry_pos].next() # reset this
									# and just continue your loop over i (which processes the carry)
				
			#print "REMOVING", addedrule
			#[ self.remove_rule(r) for r in addedrules ]# remove bv rule
			
		elif self.is_nonterminal(x): # just a single nonterminal  
			
			## TODO: somewhat inefficient since we do this each time:
			## Here we change the order of rules to be terminals *first*
			## else we don't enumerate small to large, which is clearly insane
			terminals = []
			nonterminals = []
			for k in self.rules[x]:
				if self.is_terminal(k.to):     terminals.append(k)
				else:                       nonterminals.append(k)
			
			#print ">>", terminals
			#print ">>", nonterminals
			
			Z = logsumexp([ r.lp for r in self.rules[x]] ) # normalizer
			
			if depth >= 0:
				# yield each of the rules that lead to terminals
				for r in terminals:
					n = FunctionNode(returntype=r.nt, name=r.name, args=deepcopy(r.to), lp=(r.lp - Z), bv=r.bv, ruleid=r.rid )
					yield n
			
			if depth > 0:
				# and expand each nonterminals
				for r in nonterminals:
					n = FunctionNode(returntype=r.nt, name=r.name, args=deepcopy(r.to), lp=(r.lp - Z), bv=r.bv, ruleid=r.rid )
					for q in self.increment_tree(n, depth-1): yield q
		else:   raise StopIteration
			
	def get_rule_counts(self, t):
		"""
			A list of vectors of counts of how often each nonterminal is expanded each way
			
			TODO: This is probably not super fast since we use a hash over rule ids, but
			      it is simple!
		"""
		
		counts = defaultdict(int) # a count for each hash type
		
		for ti in listifnot(t):
			for x in ti.all_subnodes():
				if x.ruleid >= 0: counts[x.ruleid] += 1
		
		# and convert into a list of vectors (with the right zero counts)
		out = []
		for nt in self.rules.keys():
			v = np.array([ counts.get(r.rid,0) for r in self.rules[nt] ])
			out.append(v)
		return out
		
	def RR_prior(self, t, prior=1.0):
		"""
			Compute the rational rules prior from Goodman et al. 
			
			NOTE: This has not yet been extensively debugged, so use with caution
			
			TODO: Add variable priors (different vectors, etc)
		"""
		lp = 0.0
		
		for c in self.get_rule_counts(t):
			theprior = np.repeat(prior,len(c))
			lp += (beta(c+theprior) - beta(theprior))
		return lp
		
	## ------------------------------------------------------------------------------------------------------------------------------
	## Here are some versions of old functions which can be added eventually -- they are for doing "pointwise" changes to hypotheses
	## ------------------------------------------------------------------------------------------------------------------------------	
	
	## yeild all pointwise changes to this function. this changes each function, trying all with the same type signature
	## and then yeilds the trees
	#def enumerate_pointwise(self, t):
		#"""
			#Returns a generator of all the ways you can change a function (keeping the types the same) for t. Each gneeration is a copy
		#"""
		#for x in make_p_unique(self.enumerate_pointwise_nonunique(t)):
			#yield x
			
	## this enumerates using rules, but it may over-count, creating more than one instance. So we have to wrap it in 
	## a filter above
	#def enumerate_pointwise_nonunique(self, t):
		#for ti in t.all_subnodes():
			#titype = ti.get_type_signature() # for now, keep terminals as they are
			#weightsum = logsumexp([ x.lp for x in self.rules[ti.returntype]])
			#old_name, old_lp = [ti.name, ti.lp] # save these to restore
			#possible_rules = filter(lambda ri: (ri.get_type_signature() == titype), self.rules[ti.returntype])
			#if len(possible_rules) > 1:  # let's not yeild ourselves in all the ways we can
				#for r in possible_rules: # for each rule of the same type
					## add this rule, copying over
					#ti.name = r.name
					#ti.lp = r.lp - weightsum # this is the lp -- the rule was unnormalized
					#yield t.copy() # now the pointers are updated so we can yield this
			#ti.name, lp = [old_name, old_lp]
			
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
if __name__ == "__main__":
	
	#AB_GRAMMAR = PCFG()
	#AB_GRAMMAR.add_rule('START', '', ['EXPR'], 1.0)
	#AB_GRAMMAR.add_rule('EXPR', '', ['A', 'EXPR'], 1.0)
	#AB_GRAMMAR.add_rule('EXPR', '', ['B', 'EXPR'], 1.0)
	
	#AB_GRAMMAR.add_rule('EXPR', '', ['A'], 1.0)
	#AB_GRAMMAR.add_rule('EXPR', '', ['B'], 1.0)
	
	#for i in xrange(1000):
		#x = AB_GRAMMAR.generate('START')
		#print x.log_probability(), x
	
	
	G = PCFG()
	G.add_rule('START', '', ['EXPR'], 1.0)
	G.add_rule('EXPR', 'plus_', ['EXPR', 'EXPR'], 4.0, resample_p=10.0)
	G.add_rule('EXPR', 'times_', ['EXPR', 'EXPR'], 3.0, resample_p=5.0)
	G.add_rule('EXPR', 'divide_', ['EXPR', 'EXPR'], 2.0)
	G.add_rule('EXPR', 'subtract_', ['EXPR', 'EXPR'], 1.0)
	G.add_rule('EXPR', 'x', [], 25.0) # these terminals should have None for their function type; the literals
	G.add_rule('EXPR', '1.0', [], 2.0)
	G.add_rule('EXPR', '13.0', [], 1.0)
	

	
	
	# We generate a few ways, mapping strings to the actual things
	print "Testing increment (no lambda)"
	TEST_INC = dict()
	for t in G.increment_tree('START',3): 
		TEST_INC[str(t)] = t
	
	print "Testing generate (no lambda)"
	TEST_GEN = dict()
	for i in xrange(10000): 
		t = G.generate('START')
		#print ">>", t
		TEST_GEN[str(t)] = t
	
	print "Testing MCMC (no lambda)"
	TEST_MCMC = dict()
	MCMC_STEPS = 10000
	import LOTlib.MetropolisHastings
	from LOTlib.Hypothesis import StandardExpression
	hyp = StandardExpression(G)
	for x in LOTlib.MetropolisHastings.mh_sample(hyp, [], MCMC_STEPS): 
		TEST_MCMC[str(x.value)] = x.value.copy()
	
	## Now print out the results and see what's up
	for x in TEST_GEN.values():
		
		# We'll only check values that appear in all
		if str(x) not in TEST_MCMC or str(x) not in TEST_INC: continue
			
		# If we print
		#print TEST_INC[str(x)].log_probability(),  TEST_GEN[str(x)].log_probability(),  TEST_MCMC[str(x)].log_probability(), x
		
		assert abs( TEST_INC[str(x)].log_probability() - TEST_GEN[str(x)].log_probability()) < 1e-9
		assert abs( TEST_INC[str(x)].log_probability() -  TEST_MCMC[str(x)].log_probability()) < 1e-9

	
	## # # # # # # # # # # # # # # # 
	### And now do a version with bound variables
	## # # # # # # # # # # # # # # # 

	G.add_rule('EXPR', 'apply', ['FUNCTION', 'EXPR'], 5.0)
	G.add_rule('FUNCTION', 'lambda', ['EXPR'], 1.0, bv=['EXPR']) # bvtype means we introduce a bound variable below
	
	print "Testing generate (lambda)" 
	TEST_GEN = dict()
	for i in xrange(10000): 
		x = G.generate('START')
		TEST_GEN[str(x)] = x
		#print x
		#x.fullprint()
	
	print "Testing MCMC (lambda)"
	TEST_MCMC = dict()
	TEST_MCMC_COUNT = defaultdict(int)
	MCMC_STEPS = 50000
	import LOTlib.MetropolisHastings
	from LOTlib.Hypothesis import StandardExpression
	hyp = StandardExpression(G)
	for x in LOTlib.MetropolisHastings.mh_sample(hyp, [], MCMC_STEPS): 
		TEST_MCMC[str(x.value)] = x.value.copy()
		TEST_MCMC_COUNT[str(x.value)] += 1 # keep track of these
		#print x
		#for kk in G.iterate_subnodes(x.value, do_bv=True, yield_depth=True):
			#print ">>\t", kk
		#print "\n"
		#x.value.fullprint()
	
	# Now print out the results and see what's up
	for x in TEST_GEN.values():
		
		# We'll only check values that appear in all
		if str(x) not in TEST_MCMC : continue
			
		#print TEST_GEN[str(x)].log_probability(),  TEST_MCMC[str(x)].log_probability(), x
		
		if abs( TEST_GEN[str(x)].log_probability() -  TEST_MCMC[str(x)].log_probability()) > 1e-9:
			print "----------------------------------------------------------------"
			print "--- Mismatch in tree probabilities:                          ---"
			print "----------------------------------------------------------------"
			TEST_GEN[str(x)].fullprint()
			print "----------------------------------------------------------------"
			TEST_MCMC[str(x)].fullprint()
			print "----------------------------------------------------------------"
		
		assert abs( TEST_GEN[str(x)].log_probability() -  TEST_MCMC[str(x)].log_probability()) < 1e-9

	# Now check that the MCMC actually visits the nodes the right number of time
	keys = [x for x in TEST_MCMC.values() if x.count_nodes() <= 10 ] # get a set of common trees
	cntZ = log(sum([ TEST_MCMC_COUNT[str(x)] for x in keys]))
	lpZ  = logsumexp([ TEST_MCMC[str(x)].log_probability() for x in keys])
	for x in sorted(keys, key=lambda x: TEST_MCMC[str(x)].log_probability()):
		#x.fullprint()
		print TEST_MCMC_COUNT[str(x)], log(TEST_MCMC_COUNT[str(x)])-cntZ, x.log_probability() - lpZ,  x.log_probability(), q(x), hasattr(x, 'my_log_probability')
		
		
		## TODO: ADD ASSERTIONS ETC
		
	# If success....
	print "---------------------------"
	print ":-) No complaints here!"
	print "---------------------------"
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	## We will use three four methods to generate a set of trees. Each of these should give the same probabilities:
	# - increment_tree('START')
	# - generate('START')
	# - MCMC with proposals (via counts)
	# - MCMC with proposals (via probabilities of found trees)
	
	
	
	#for i in xrange(1000):
		#x = ARITHMETIC_GRAMMAR.generate('START')
		
		#print x.log_probability(), ARITHMETIC_GRAMMAR.RR_prior(x), x
		#for xi in ARITHMETIC_GRAMMAR.iterate_subnodes(x):
			#print "\t", xi
		
	

	