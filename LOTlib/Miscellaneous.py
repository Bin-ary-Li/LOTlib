# -*- coding: utf-8 -*-

"""
	Miscellaneous functions for LOTlib
	
	Steve Piantadosi - Sept 2011
"""

try:			from scipy.misc import logsumexp
except ImportError:	from scipy.maxentropy import logsumexp

from scipy.special import gammaln
import numpy as np
from random import random, sample, randint
import itertools
from math import exp, log, sqrt, pi, e
import functools # for memoize
import pickle
import os
import sys
import math

from lockfile import FileLock, LockFailed

import types # for checking if something is a function: isinstance(f, types.FunctionType)

## Some useful constants
Infinity = float("inf")
inf = float("inf")
Null = []
TAU = 6.28318530718

## For R-friendly
T=True
F=False

def first(x): return x[0]
def second(x): return x[1]
def third(x):  return x[2]
def fourth(x):  return x[3]
def fifth(x):  return x[4]
def sixth(x):  return x[5]
def seventh(x):  return x[6]
def eighth(x):  return x[7]



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Display functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


## for printing wiht debug levels. 
## Here we have a global variable (defaults to 10) we print all statements with l <= DEBUG_LEVEL
## Library internal debugging should have level >= 100, I think
from multiprocessing import Process # this forces prints to be flushed, so we can flush with dprint below to prevent threads from interrupting each other
global DEBUG_LEVEL
DEBUG_LEVEL = 10
def dprintn(l, *args):
	args = list(args)
	args.append("\n")
	dprint(l,*args)
def dprint(l, *args):
	global DEBUG_LEVEL
	if DEBUG_LEVEL >= l:
		for a in args: 
			print str(a),
	sys.stdout.flush()

def fprintn(dl, *args, **kwargs):
	
	f = kwargs.get('f',sys.stdout)
	
	if DEBUG_LEVEL >= dl:
		o = open(f, 'a')
		for a in args: 
			print >>o, str(a),
		print >>o, "\n",
		if f is not sys.stdout: o.close()
		
def q(x, quote='\"'): return quote+str(x)+quote
	
def display(x): print x
	
# for functional programming, print something and return it
def printr(x):
	print x
	return x
	
def tf201(x):
	if x: return 1
	else: return 0

# joins by commas with none at the end. Correctly handles null lists
def commalist(listtext, sep1=', ', sep2=', '):
	return sep1.join(listtext[:-2]+['']) + sep2.join(listtext[-2:])
	

from time import gmtime, strftime, time, localtime
## Functions for I/O
def display_option_summary(obj):
	"""
		Prints out a friendly format of all options -- for headers of output files
		This takes in an OptionParser object as an argument. As in, (options, args) = parser.parse_args()
	"""
	
	print "####################################################################################################"
	print "# Username: ", os.getlogin()
	print "# Date: ", strftime("%Y %b %d (%a) %H:%M:%S", localtime(time()) )
	print "# Uname: ", os.uname()
	print "# Pid: ", os.getpid()
	for slot in dir(obj):
		attr = getattr(obj, slot)
		if not isinstance(attr, (types.BuiltinFunctionType, types.FunctionType, types.MethodType)) and (slot is not "__doc__") and (slot is not "__module__"):
			print "#", slot, "=", attr
	print "####################################################################################################"

	
def assert_or_die(x,m):
	""" die and print m if something is false"""
	if not x: die(m)
	
def die(x):
	""" Say something and exit (via failed Assert) """
	print "*** " + x
	assert False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Genuine Miscellany
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# a wrapper so we can call this in the below weirdo composition
def raise_exception(e): raise e

def ifelse(x,y,z):
	if x: return y
	else: return z
	
# add to a hash list
def hashplus(d, k, v=1):
	if not k in d: d[k] = v
	else: d[k] = d[k] + v


# this takes a generator and by using a set (and thus a hash) it makes it unique, only returning each value once
# so this filters generators, making them unique
def make_generator_unique(gen):
	s = set()
	for gi in gen:
		if gi not in s:
			s.add(gi)
			yield gi

def listifnot(x):
	if isinstance(x,list): return x
	else:                  return [x]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Math functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	
def beta(a):
	""" Here a is a vector (of ints or floats) and this computes the Beta normalizing function,"""
	return np.sum(gammaln(np.array(a, dtype=float))) - gammaln(float(sum(a)))
		
def logplusexp(*args):
	return logsumexp(args)

def islist(x): return isinstance(x,list)


def normlogpdf(x, mu, sigma):
	""" The log pdf of a normal distribution """
	#print x, mu
	return math.log(math.sqrt(2. * pi) * sigma) - ((x - mu) * (x - mu)) / (2.0 * sigma * sigma)

def logrange(mn,mx,steps):
	"""
		Logarithmically-spaced steps from mn to mx, with steps number inbetween
		mn - min value
		mx - max value
		steps - number of steps between. When 1, only mx is returned
	"""
	mn = np.log(mn)
	mx = np.log(mx)
	r = np.arange(mn, mx, (mx-mn)/(steps-1))
	r = np.append(r, mx)
	return np.exp(r)

def geometric_ldensity(n,p): 
	""" Log density of a geomtric distribution """
	return (n-1)*log(1.0-p)+log(p)

from math import expm1, log1p
def log1mexp(a):
	"""
		Computes log(1-exp(a)) according to Machler, "Accurately computing ..."
		Note: a should be a large negative value!
	"""
	if a > 0: print >>sys.stderr, "# Warning, log1mexp with a=", a, " > 0" 
	if a < -log(2.0): return log1p(-exp(a))
	else:             return log(-expm1(a))
	
	
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Sampling functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def sample1(*args): return sample_one(*args)
def sample_one(*args): 
	if len(args) == 1: return sample(args[0],1)[0] # use the list you were given
	else:             return sample(args, 1)[0]   # treat the arguments as a list

def flip(p): return (random() < p)

## TODO: THIS FUNCTION SUCKS PLEASE FIX IT
## TODO: Change this so that if N is large enough, you sort 
# takes unnormalized probabilities and returns a list of the log probability and the object
# returnlist makes the return always a list (even if N=1); otherwise it is a list for N>1 only
# NOTE: This now can take probs as a function, which is then mapped!
def weighted_sample(objs, N=1, probs=None, log=False, return_probability=False, returnlist=False, Z=None):
	# check how probabilities are specified
	# either as an argument, or attribute of objs (either probability or lp
	# NOTE: THis ALWAYS returns a log probability
	
	if len(objs) == 0: return None
	
	myprobs = None
	if probs is None:
		if hasattr(objs[0], 'probability'): # may be log or not
			myprobs = map(lambda x: x.probability, objs)
			log = False
		elif hasattr(objs[0], 'lp'): # MUST be logs
			myprobs = map(lambda x: x.lp, objs)
			log = True 
		else:
			myprobs = [1.0] * len(objs) # sample uniform
	elif isinstance(probs, types.FunctionType): #NOTE: this does not work for class instance methods
		myprobs = map(probs, objs)
	else: 
		myprobs = probs
	
	# make sure these are floats or things go badly
	myprobs = map(float, myprobs)
	
	# Now normalize and run
	if Z == None:
		if log: Z = logsumexp(myprobs)
		else: Z = sum(myprobs)
	#print log, myprobs, Z
	out = []
	
	for n in range(N):
		r = random()
		for i in range(len(objs)):
			if log: r = r - exp(myprobs[i] - Z) # log domain
			else: r = r - (myprobs[i]/Z) # probability domain
			#print r, myprobs
			if r <= 0: 
				if return_probability: 
					lp = 0
					if log: lp = myprobs[i] - Z
					else:   lp = math.log(myprobs[i]) - math.log(Z)
				
					out.append( [objs[i],lp] )
					break
				else:             
					out.append( objs[i] )
					break
					
	if N == 1 and (not returnlist): return out[0]  #don't give back a list if you just want one
	else:      return out


""" 
	This function is much more elegant than the above, but is painfully slower in tests, likely because it involves many logs and randoms
"""
def multinomial_sample_DO_NOT_USE_SUPER_SLOW(objs, probs='lp', log=True, return_probability=False):
	"""
		Use the A-ES algorithm to sample one object from objs (potentially a generator). See The paper, "Weighted Random Sampling over Data Streams"
		
		objs - the objects to sample
		probs - the probabilities, either a list (or generator) paired to objs, or a string describing an attribute of objs
		
		Returns the object and optionally the *log* probability of the sample
		
		This takes the probability to be stored in objs.attr, and treats this probability as a log probability
		if log=True
		
		  max of u ^ 1/w
		= max of u ^ 1/exp(lp)  [[log probabilities]]
		= max of log(u) / exp(lp)
		= min of -log(u) / exp(lp)
		= min of log(-log(u)) - lp
		
		TODO: Make this more elegantly handle 0 probability events
	#"""	
	
	best_value  = float("inf")
	best_obj    = None
	best_weight = float("inf")
	lZ = 0.0 # the log normalizer (for returning the probability)
	
	# then probs is an attribute
	if isinstance(probs,str): 
		are_probs_attr = True
	else:
		are_probs_attr = False
		next_prob = probs.__iter__() # we find probs by an interator
	
	# Now iterate through
	for o in objs:
		
		# recover the prob by either the attribute or the next element of the iterator
		if are_probs_attr: w = getattr(o, probs)
		else:              w = next_prob.next()
		
		# convert so weights are unnormalized log probabilities
		if not log: w = math.log(w) 
						
		# the above transfom. Keep the *lowest* k
		k = math.log( -math.log(random()) ) - w
				
		lZ = logplusexp(lZ,w) # keep track of the normalizer
		
		# and track the best value
		if k < best_value:
			best_value = k
			best_obj = o
			best_weight = w
		
		
	# and return at the end, potentially returning the (normalized) probability
	if return_probability: return best_obj, best_weight-lZ
	else:                  return best_obj


#from collections import defaultdict
#cnt = defaultdict(int)
#for i in xrange(15000):
	##v = multinomial_sample(range(1,100), probs=range(1,100), log=False)
	#v = weighted_sample(range(100), probs=range(100), log=False)
	##print v
	#cnt[v] += 1
#print cnt

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lambda calculus
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Some innate lambdas
def lambdaZero(*x): return 0
def lambdaOne(*x): return 1
def lambdaNull(*x): return []
def lambdaNone(*x): return x
def lambdaTrue(*x): return True
def lambdaFalse(*x): return True


"""
The Y combinator
#example:
#fac = lambda f: lambda n: (1 if n<2 else n*(f(n-1)))
#Y(fac)(10)
"""
Y = lambda f: (lambda x: x(x)) (lambda y : f(lambda *args: y(y)(*args)) )


class RecursionDepthException(Exception):
	# An exception class for recursing too deep
	def __init__(self): pass

"""
A fancy fixed point iterator that only goes MAX_RECURSION deep, else throwing a a RecusionDepthException

"""
MAX_RECURSION = 25
def Y_bounded(f):
	return (lambda x, n: x(x, n)) (lambda y, n: f(lambda *args: y(y, n+1)(*args)) if n < MAX_RECURSION else raise_exception(RecursionDepthException()), 0)

# here, e is an expression of the arguments. 
# this adds lambdas and returns a function which is optionally recursive. 
# if it is recursive, the "recurse" variable is what you use to call *this* function
def evaluate_expression(e, args=['x'], recurse="L_", addlambda=True):
	"""
	This evaluates an expression. If 
	- e         - the expression itself -- either a str or something that can be made a str
	- addlambda - should we include wrapping lambda arguments in args? lambda x: ...
	- recurse   - if addlambda, this is a special primitive name for recursion
	- args      - if addlambda, a list of all arguments to be added
	
	g = evaluate_expression("x*L(x-1) if x > 1 else 1")
	g(12)
	"""
	
	if not isinstance(e,str): e = str(e)
	f = None # the function
	
	try:
		if addlambda:
			f = eval('lambda ' + recurse + ': lambda ' + commalist(args) + ' :' + e)
			return Y_bounded(f)
		else: 
			f = eval(e)
			return f
	except:
		print "Error in evaluate_expression:", e
		raise RuntimeError
		exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Easier pickling
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def pickle_save(x, f):
	out_file = open(f, 'wb')
	pickle.dump(x, out_file)
	out_file.close()
def pickle_load(f):
	in_file = open(f, 'r')
	r = pickle.load(in_file)
	in_file.close()
	return r	
		

## this take sa dictionary d
## the keys of d must contain "lp", and d must contain counts
## this prints out a chi-squared test to make sure these are right
## NOTE: This doe snot do well if we have a fat tail, since we will necessarily sample some low probability events
##from scipy.stats import chisquare
### importantly, throw out counts less than min_count -- else we get crummy
#def test_expected_counts(d, display=True, sort=True, min_count=100):
	#keys = d.keys() # maintain an order for the keys
	#if sort:
		#keys = sorted(keys, key=lambda x: d[x])
	#lpZ = logsumexp([ k.lp for k in keys])
	#cntZ = sum(d.values())
	#if display:			
		#for k in keys:
			#ocnt = float(d[k])/cntZ
			#ecnt = exp(k.lp-lpZ)
			#print d[k], "\t", ocnt, "\t", ecnt, "\t", ocnt/ecnt, "\t", k
	## now update these with their other probs	
	#keeper_keys = filter(lambda x: d[x] >= min_count, keys)
	##print len( keeper_keys), len(keys), map(lambda x: d[x], keys)
	#lpZ = logsumexp([ k.lp for k in keeper_keys])
	#cntZ = sum([d[k] for k in keeper_keys])	
	
	## The chisquared test does not do well here iwth the low expected counts -- 
	#print chisquare( [ d[k] for k in keeper_keys ], f_exp=array( [ cntZ * exp(k.lp - lpZ) for k in keeper_keys] ))  ##UGH expected *counts*, not probs


	





from LOTlib.BasicPrimitives import * # Needed for calling "eval"
