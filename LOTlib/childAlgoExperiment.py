from LOTlib.WorldState import *
from LOTlib.Eval import primitive
from copy import deepcopy


######################################## 
## Define a grammar
######################################## 

from LOTlib.Grammar import Grammar

grammar = Grammar()

grammar.add_rule('START', '', ['STATEMENT_SEQ'], 1.0)

## deprecated
# Recursively define a sequence of actions that can happen to a worldstate. 
grammar.add_rule('STATEMENT_SEQ', '    %s\n    %s',    ['STATEMENT', 'SEQ'], 1.0)
grammar.add_rule('SEQ', '%s\n    %s',    ['STATEMENT', 'SEQ'], .1)
grammar.add_rule('SEQ', '%s',    ['STATEMENT'], .1)
grammar.add_rule('STATEMENT', '%s',    ['ACTION'], .5)
grammar.add_rule('STATEMENT', '%s',    ['CONDITION'], .5)

# grammar.add_rule('ACTION_SEQ', '%s', ['ACTION_SEQ'], 1.0)
# grammar.add_rule('ACTION_SEQ', '%s', ['ACTION'], 1.0)

## deprecated
# @primitive
# def move_ball_(WS, container_0, container_1, color):
#     return WS.moveBall(container_0, container_1, color)
# grammar.add_rule('WORLDSTATE', 'x', None, 1.)
# grammar.add_rule('WORLDSTATE', 'move_ball_', ['WORLDSTATE', 'CONTAINER', 'CONTAINER', 'COLOR'], 1.)
# grammar.add_rule('ACTION', 'move_ball_', ['WORLDSTATE', 'CONTAINER', 'CONTAINER', 'COLOR'], 1.0)


grammar.add_rule('ACTION', '%s = %s.moveBall(%s, %s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'CONTAINER', 'CONTAINER', 'COLOR'], 1.0)
grammar.add_rule('WORLDSTATE', 'x', None, 1.)
# we can do this because moveBall() method will return a WorldState object
# grammar.add_rule('WORLDSTATE', '%s.moveBall(%s, %s, %s)', ['WORLDSTATE', 'CONTAINER', 'CONTAINER', 'COLOR'], 1.)
grammar.add_rule('ACTION', '%s = %s.moveRandomBall(%s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'CONTAINER', 'CONTAINER'], 1.)

grammar.add_rule('CONDITION', '''if %s:
        %s
    else:
        %s''', ['BOOL', 'ACTION','ACTION'], 1.)

grammar.add_rule('CONDITION', '''while %s and x._itrCounter < 26:
        %s
        if x._itrCounter == 25:
            x._itrCounter = 0
            break
        x._itrCounter += 1
    ''', ['BOOL','ACTION'], 1.)

# grammar.add_rule('ACTION_SEQ', '(%s if %s else %s)', ['ACTION', 'BOOL', 'ACTION'], 1.)

grammar.add_rule('BOOL', 'x.existColor(%s, %s)', ['CONTAINER','COLOR'], 1.0)
grammar.add_rule('BOOL', 'x.canAddBall(%s, %s)', ['CONTAINER','COLOR'], 1.0)

## "Bigger than"/"lesser than" method haven't overridden in the object class yet
# grammar.add_rule('BOOL', '(%s >= %s)', ['CONTAINER','CONTAINER'], 1.0)
# grammar.add_rule('BOOL', '(%s <= %s)', ['CONTAINER','CONTAINER'], 1.0)
# grammar.add_rule('BOOL', '(%s > %s)', ['CONTAINER','CONTAINER'], 1.0)
# grammar.add_rule('BOOL', '(%s < %s)', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', '(x._container[%s] == x._container[%s])', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', 'x._container[%s].isEmpty()', ['CONTAINER'], 1.0)

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
        # LOTHypothesis.__init__(self, grammar=grammar, display="lambda x: %s", **kwargs)
        LOTHypothesis.__init__(self, grammar=grammar, display="%s", **kwargs)
    
    # def __call__(self, *args):
    #     try:
    #         # try to do it from the superclass
    #         return LOTHypothesis.__call__(self, *args)
    #     except ZeroDivisionError:
    #         # and if we get an error, return nan
    #         return float("nan")

    # def __call__(ws):
    #     try: 
    #         LOTHypothesis.__call__(self, ws) --> (some tuple) (remember zero the violation count)
    #         return ws

    def __call__(self, ws):
    #     print '''def foo(x): \n%s \n    return x
    # ''' % self
        exec(
            '''def foo(x): \n%s \n    return x
    ''' % self)
        worldS = foo(ws)
        return worldS

    def compile_function (self):
        pass


    # Compute likelihood in term of difference between two world states
    def compute_single_likelihood(self, datum):
        x = deepcopy(datum.input[0])
        self.__call__(x)
        assert isinstance(x - datum.output, int), 'subtraction result is not an int'
        return - ((x - datum.output)*100 + x._affordanceViolateCnt)


######################################## 
## Define the data
######################################## 

from LOTlib.DataAndObjects import FunctionData

initial_state = {
    'bucket_0': Bucket(black=10, red=10, green=0),
    'bucket_1': Bucket(black=0, red=0, green=0),
    'bucket_2': Bucket(black=0, red=0, green=0),
    'bucket_3': Bucket(black=0, red=0, green=0),
    'hand_left': Hand(),
    'hand_right': Hand()
}

end_state = {
    'bucket_0': Bucket(black=0, red=0, green=0),
    'bucket_1': Bucket(black=10, red=10, green=0),
    'bucket_2': Bucket(black=0, red=0, green=0),
    'bucket_3': Bucket(black=0, red=0, green=0),
    'hand_left': Hand(),
    'hand_right': Hand()
}

WS_initial = WorldState(initial_state)
WS_end = WorldState(end_state)


data = [ FunctionData(input=[WS_initial], output=WS_end, alpha=0.95) ]

########################
## Testing Grammar
#########################
# for _ in xrange(20):
#     t = grammar.generate()
#     print grammar.log_probability(t), t 


####################################### 
# Actually run
####################################### 
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.SampleStream import *

h0 = MyHypothesisX()

# # Plain running
# for h in MHSampler(h0, data, steps=100):
#     print h.posterior_score, h
#     # pass


# Running and show only the top choice 
from LOTlib.TopN import TopN
topChoice = TopN(N=10)

for h in MHSampler(h0, data, steps=10000):
    topChoice.add(h)
for h in topChoice.get_all(sorted=True):
    print h.posterior_score, h
