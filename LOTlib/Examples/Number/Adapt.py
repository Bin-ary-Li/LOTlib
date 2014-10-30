# -*- coding: utf-8 -*-

"""
Use optimal adaptation code to adapt show possible adpatations to the Number grammar.
"""

import pickle
import Model.Inference as I
from LOTlib.sandbox.OptimalGrammarAdaptation import print_subtree_adaptations

## Set up how much data we want
datas = map(I.generate_data, xrange(0, 400, 10))
print "# Generated data!"

#hypotheses = set([ NumberExpression(G) for i in xrange(10)])
hypotheses = pickle.load(open("out/2014Feb10_small.pkl", 'r')).get_all()
print "# Loaded hypotheses"

# Clean out ones with 0 probability, or else KL computation in print_subtree_adaptations goes to hell
hypotheses = filter(lambda h: sum(h.compute_posterior(datas[0])) > -I.Infinity,  hypotheses)

## And evaluate each hypothesis on it
posteriors = map( lambda d: [ sum(h.compute_posterior(d)) for h in hypotheses], datas)
print "# Rescored hypotheses!"


## Generate a set of subtrees
subtrees = set()
for h in I.lot_iter(hypotheses):
    for x in h.value: # for each subtree
        for i in xrange(I.N_SUBTREES_PER_NODE):  #take subtree_multiplier random partial subtrees
            subtrees.add(   x.random_partial_subtree(p=I.SUBTREE_P)   )
print "# Generated", len(subtrees), "subtrees"

## And call from OptimalGrammarAdaptation
print_subtree_adaptations(hypotheses, posteriors, subtrees)
