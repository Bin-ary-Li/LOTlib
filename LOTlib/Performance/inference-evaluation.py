# -*- coding: utf-8 -*-
"""
	Simple evaluation of number schemes -- read LOTlib.Performance.Evaluation to see what the output is
"""

from LOTlib import lot_iter

import os
from itertools import product
from SimpleMPI.MPI_map import MPI_map, synchronize_variable, MPI_done

from optparse import OptionParser

parser = OptionParser()
parser.add_option("--out", dest="OUT", type="string", help="Output prefix", default="output/inference")
parser.add_option("--samples", dest="SAMPLES", type="int", default=100000, help="Number of samples to run")
parser.add_option("--repetitions", dest="REPETITONS", type="int", default=100, help="Number of repetitions to run")
parser.add_option("--model", dest="MODEL", type="str", default="Number", help="Which model to run on (Number, Galileo, RationalRules, SimpleMagnetism, RegularExpression)")
parser.add_option("--print-every", dest="PRINTEVERY", type="int", default=1000, help="Evaluation prints every this many")
options, _ = parser.parse_args()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the test model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if options.MODEL == "Number":
	# Load the data
	from LOTlib.Examples.Number.Shared import generate_data, grammar,  make_h0
	data = synchronize_variable( lambda : generate_data(300)  )

elif options.MODEL == "Galileo":
	from LOTlib.Examples.SymbolicRegression.Galileo import data, grammar, make_h0	

elif options.MODEL == "RationalRules":
	
	from LOTlib.Examples.RationalRules.Shared import grammar, data, make_h0
	
elif options.MODEL == "SimpleMagnetism":
	from LOTlib.Examples.Magnetism.SimpleMagnetism import grammar, data, make_h0

elif options.MODEL == "RegularExpression":
	from LOTlib.Examples.RegularExpression.RegularExpressionInferece import grammar, data, make_h0
else:
	assert false, "Unimplemented model: %s" % options.MODEL

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run MCMC
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# These get defined for each process
from SimpleMPI.ParallelBufferedIO import ParallelBufferedIO
from LOTlib.Performance.Evaluation import evaluate_sampler
from LOTlib.Inference.TemperedTransitions import tempered_transitions_sample
from LOTlib.Inference.ParallelTempering import ParallelTemperingSampler
from LOTlib.Inference.MetropolisHastings import MHSampler
from LOTlib.Inference.TabooMCMC import TabooMCMC
from LOTlib.Inference.ParticleSwarm import ParticleSwarm
from LOTlib.Inference.MultipleChainMCMC import MultipleChainMCMC

# Where we store the output
out_hypotheses = open(os.devnull,'w') #ParallelBufferedIO(options.OUT + "-hypotheses.txt")
out_aggregate  = ParallelBufferedIO(options.OUT + "-aggregate.txt")

def run_one(iteration, sampler_type):
	
	h0 = make_h0()
	
	# Create a sampler
	if sampler_type == 'mh_sample_A':               sampler = MHSampler(h0, data, options.SAMPLES,  likelihood_temperature=1.0)
	elif sampler_type == 'mh_sample_B':             sampler = MHSampler(h0, data, options.SAMPLES,  likelihood_temperature=1.1)
	elif sampler_type == 'mh_sample_C':             sampler = MHSampler(h0, data, options.SAMPLES,  likelihood_temperature=1.25)
	elif sampler_type == 'mh_sample_D':             sampler = MHSampler(h0, data, options.SAMPLES,  likelihood_temperature=2.0 )
	elif sampler_type == 'mh_sample_E':             sampler = MHSampler(h0, data, options.SAMPLES,  likelihood_temperature=5.0 )
	elif sampler_type == 'particle_swarm_A':        sampler = ParticleSwarm(make_h0, data, steps=options.SAMPLES, within_steps=10)
	elif sampler_type == 'particle_swarm_B':        sampler = ParticleSwarm(make_h0, data, steps=options.SAMPLES, within_steps=100)
	elif sampler_type == 'particle_swarm_C':        sampler = ParticleSwarm(make_h0, data, steps=options.SAMPLES, within_steps=200)
	elif sampler_type == 'multiple_chains_A':       sampler = MultipleChainMCMC(make_h0, data, steps=options.SAMPLES, nchains=10)
	elif sampler_type == 'multiple_chains_B':       sampler = MultipleChainMCMC(make_h0, data, steps=options.SAMPLES, nchains=100)
	elif sampler_type == 'multiple_chains_C':       sampler = MultipleChainMCMC(make_h0, data, steps=options.SAMPLES, nchains=1000)
	elif sampler_type == 'parallel_tempering_A':    sampler = ParallelTemperingSampler(make_h0, data, steps=options.SAMPLES, within_steps=10, temperatures=[1.0, 1.025, 1.05], swaps=1, yield_only_t0=False)
	elif sampler_type == 'parallel_tempering_B':    sampler = ParallelTemperingSampler(make_h0, data, steps=options.SAMPLES, within_steps=10, temperatures=[1.0, 1.25, 1.5], swaps=1, yield_only_t0=False)
	elif sampler_type == 'parallel_tempering_C':    sampler = ParallelTemperingSampler(make_h0, data, steps=options.SAMPLES, within_steps=10, temperatures=[1.0, 2.0, 5.0], swaps=1, yield_only_t0=False)
	elif sampler_type == 'taboo_A':                 sampler = TabooMCMC( h0, data, steps=options.SAMPLES, skip=0, penalty=.10)
	elif sampler_type == 'taboo_B':                 sampler = TabooMCMC( h0, data, steps=options.SAMPLES, skip=0, penalty=1.0)
	elif sampler_type == 'taboo_C':                 sampler = TabooMCMC( h0, data, steps=options.SAMPLES, skip=0, penalty=10.0)
	else: assert False, "Bad sampler type: %s" % sampler_type
	
	# Run evaluate on it, printing to the right locations
	evaluate_sampler(sampler, prefix="\t".join(map(str, [options.MODEL, iteration, sampler_type])),  out_hypotheses=out_hypotheses, out_aggregate=out_aggregate, print_every=options.PRINTEVERY)
 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create all parameters
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# For each process, create the lsit of parameter
params = [ list(g) for g in product(range(options.REPETITONS), ['multiple_chains_A', 'multiple_chains_B', 'multiple_chains_C', 
												'taboo_A', 'taboo_B', 'taboo_C', 
												'particle_swarm_A', 'particle_swarm_B', 'particle_swarm_C', 
												'mh_sample_A', 'mh_sample_B', 'mh_sample_C', 'mh_sample_D', 'mh_sample_E',
												 'parallel_tempering_A', 'parallel_tempering_B', 'parallel_tempering_C',
												])]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Actually run
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MPI_map(run_one, params, random_order=False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Clean up
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

out_hypotheses.close()
out_aggregate.close()

MPI_done()

#import sys
#sys.exit(0)