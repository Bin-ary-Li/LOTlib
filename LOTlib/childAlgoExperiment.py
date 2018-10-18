from LOTlib.WorldState import *
from LOTlib.Eval import primitive

######################################## 
## Define a grammar
######################################## 

from LOTlib.Grammar import Grammar

@primitive
def move_ball_(WS, container_0, container_1, color):
    return WS.moveBall(container_0, container_1, color)

grammar = Grammar()

grammar.add_rule('START', '', ['ACTION_SEQUENCE'], 1.0)

# Recursively define a sequence of actions that can happen to a worldstate. 
grammar.add_rule('ACTION_SEQUENCE', '%s\n%s',    ['ACTION', 'SEQUENCE'], 1.0)
grammar.add_rule('SEQUENCE', '%s\n%s',    ['ACTION', 'SEQUENCE'], .1)
grammar.add_rule('SEQUENCE', '%s',    ['ACTION'], .5)

grammar.add_rule('WORLDSTATE', 'x', None, 1.)

#grammar.add_rule('ACTION', 'x.moveBall(%s, %s, %s)', ['CONTAINER', 'CONTAINER', 'COLOR'], 1.0)
grammar.add_rule('ACTION', 'move_ball_', ['WORLDSTATE', 'CONTAINER', 'CONTAINER', 'COLOR'], 1.0)

grammar.add_rule('ACTION', '(%s if %s else %s)', ['ACTION', 'BOOL', 'ACTION'], .001)

grammar.add_rule('BOOL', 'x.existColor(%s, %s)', ['CONTAINER','COLOR'], 1.0)

grammar.add_rule('BOOL', '(%s == %s)', ['CONTAINER','CONTAINER'], 1.0)

grammar.add_rule('CONTAINER', '\'bucket_0\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'bucket_1\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'bucket_2\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'bucket_3\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'hand_right\'', None, 5.0)
grammar.add_rule('CONTAINER', '\'hand_left\'', None, 1.0)

grammar.add_rule('COLOR', '\'black\'', None, 1.0)
grammar.add_rule('COLOR', '\'red\'', None, 1.0)
grammar.add_rule('COLOR', '\'green\'', None, 100.0)


from math import log
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis

######################################## 
## Define the hypothesis
######################################## 

# define a 
class MyHypothesisX(LOTHypothesis):
    def __init__(self, **kwargs):
        LOTHypothesis.__init__(self, grammar=grammar, display="lambda x: %s", **kwargs)
    
    def __call__(self, *args):
        try:
            # try to do it from the superclass
            return LOTHypothesis.__call__(self, *args)
        except ZeroDivisionError:
            # and if we get an error, return nan
            return float("nan")

    def compute_single_likelihood(self, datum):
        if self(*datum.input) == datum.output:
            return log((1.0-datum.alpha)/100. + datum.alpha)
        else:
            return log((1.0-datum.alpha)/100.)

######################################## 
## Define the data
######################################## 

from LOTlib.DataAndObjects import FunctionData

# Now our data takes input x=3 and maps it to 12
# What could the function be?
initial_state = {
    'bucket_0': Bucket(black=1, red=0, green=0),
    'bucket_1': Bucket(black=0, red=1, green=2),
    'bucket_2': Bucket(black=0, red=0, green=0),
    'bucket_3': Bucket(black=0, red=0, green=0),
    'hand_left': Hand(),
    'hand_right': Hand()
}

end_state = {
    'bucket_0': Bucket(black=1, red=0, green=0),
    'bucket_1': Bucket(black=0, red=1, green=1),
    'bucket_2': Bucket(black=0, red=0, green=0),
    'bucket_3': Bucket(black=0, red=0, green=0),
    'hand_left': Hand(green=1),
    'hand_right': Hand()
}

WS_initial = WorldState(initial_state)
WS_end = WorldState(end_state)


data = [ FunctionData(input=[WS_initial], output=WS_end, alpha=0.95) ]

######################################## 
## Actually run
######################################## 
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.SampleStream import *

h0 = MyHypothesisX()

for h in SampleStream(MHSampler(h0, data, steps=100)) >> Unique() >> PrintH():
    pass