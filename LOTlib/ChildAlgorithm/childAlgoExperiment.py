from WorldState import *
from LOTlib.Eval import primitive
from copy import deepcopy


######################################## 
## Define a grammar
######################################## 

from LOTlib.Grammar import Grammar

grammar = Grammar()

grammar.add_rule('START', '', ['STATEMENT_SEQ'], 1.0)

# Recursively define a sequence of actions that can happen to a worldstate. 
grammar.add_rule('STATEMENT_SEQ', '%s\n%s',    ['STATEMENT', 'STATEMENT_SEQ'], 1.)
grammar.add_rule('STATEMENT_SEQ', '%s',    ['STATEMENT'], 1.)
grammar.add_rule('STATEMENT', '%s', ['ACTION'], 1.)
grammar.add_rule('STATEMENT', '%s', ['CONDITION'], 1.)

grammar.add_rule('WORLDSTATE', 'x', None, 1.)
grammar.add_rule('ACTION', '%s = %s.moveBall(%s, %s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'CONTAINER', 'CONTAINER', 'COLOR'], 1.)
grammar.add_rule('ACTION', '%s = %s.moveRandomBall(%s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'CONTAINER', 'CONTAINER'], 1.)
grammar.add_rule('ACTION', 'pass', None, .1)

grammar.add_rule('CONDITION', '%s', ['IF_STATEMENT'], 1.)
grammar.add_rule('CONDITION', '%s', ['WHILE_LOOP'], 1.)

grammar.add_rule('IF_STATEMENT', '''if %s:
%s}
else:
%s}''', ['BOOL', 'ACTION','ACTION'], 1.)

grammar.add_rule('WHILE_LOOP', '''while %s and x._itrCounter < 26:
%s
x._itrCounter += 1
if x._itrCounter == 25:
x._itrCounter = 0
break}
}''', ['BOOL','ACTION'], 1.)

grammar.add_rule('WHILE_LOOP', '''while %s and x._itrCounter < 26:
%s
x._itrCounter += 1
if x._itrCounter == 25:
x._itrCounter = 0
break}
}''', ['BOOL','IF_STATEMENT'], 1.)


grammar.add_rule('BOOL', 'x.existColor(%s, %s)', ['CONTAINER','COLOR'], 1.0)
grammar.add_rule('BOOL', 'x.canAddBall(%s, %s)', ['CONTAINER','COLOR'], 1.0)

## "Bigger than"/"lesser than" method haven't overridden in the object class yet
# grammar.add_rule('BOOL', '(%s >= %s)', ['CONTAINER','CONTAINER'], 1.0)
# grammar.add_rule('BOOL', '(%s <= %s)', ['CONTAINER','CONTAINER'], 1.0)
# grammar.add_rule('BOOL', '(%s > %s)', ['CONTAINER','CONTAINER'], 1.0)
# grammar.add_rule('BOOL', '(%s < %s)', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', '(x._container[%s] == x._container[%s])', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', 'x._container[%s].isEmpty()', ['CONTAINER'], 1.0)
grammar.add_rule('BOOL', 'not (%s)', ['BOOL'], 1.0)

grammar.add_rule('CONTAINER', '\'bucket_0\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'bucket_1\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'bucket_2\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'bucket_3\'', None, 1.0)
grammar.add_rule('CONTAINER', '\'hand_right\'', None, 5.0)
grammar.add_rule('CONTAINER', '\'hand_left\'', None, 1.0)

grammar.add_rule('COLOR', '\'black\'', None, 1.0)
grammar.add_rule('COLOR', '\'red\'', None, 1.0)
grammar.add_rule('COLOR', '\'green\'', None, 1.0)


from math import log
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis

######################################## 
## Define the hypothesis
######################################## 


# define a 
class MyHypothesisX(LOTHypothesis):
    def __init__(self, **kwargs):
        # LOTHypothesis.__init__(self, grammar=grammar, display="lambda x: %s", **kwargs)
        # LOTHypothesis.__init__(self, grammar=grammar, display='''def foo(x): \n%s \n    return x''', **kwargs)
        LOTHypothesis.__init__(self, grammar=grammar, display='''def foo(x): \n%s\n    return x''', **kwargs)

    def __call__(self, ws):
        # rawCode = str(self)
        parsedCode = self.code_compilation(str(self))
        # print '''def foo(x): \n%s \n    return x''' % parsedCode
        # exec('''def foo(x): \n%s \n    return x''' % parsedCode)
        # print '''%s''' % parsedCode
        exec('''%s''' % parsedCode)
        worldS = foo(ws)
        return worldS


    def compile_function (self):
        pass

    def code_compilation (self, code):
        indentCnt = 1
        parsedCodeList = []
        firstLine = code.split('\n')[0]
        lastLine = code.split('\n')[-1]
        parsedCodeList.append(firstLine)
        codeList = code.split('\n')[1:-1]
        def checkLine(line, indentCnt):
            if line[-1:] == ":":
                indentCnt += 1
            elif line[-1:] == "}":
                indentCnt -= 1
            return indentCnt
        for line in codeList:
            parsedCodeList.append('    '*indentCnt + line)
            indentCnt = checkLine(line, indentCnt)
        for index, line in enumerate(parsedCodeList):
            if line[-1:] == "}":
                parsedCodeList[index] = line[:-1]
        if lastLine[-1:] == "}":
            lastLine = lastLine[:-1]
        parsedCodeList.append(lastLine)
        parsedCode = '\n'.join(parsedCodeList)
        return parsedCode


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

initial_state_0 = {
    'bucket_0': Bucket(black=1, red=0, green=0),
    'bucket_1': Bucket(black=0, red=3, green=3),
    'bucket_2': Bucket(black=0, red=0, green=0),
    'bucket_3': Bucket(black=0, red=0, green=0),
    'hand_left': Hand(),
    'hand_right': Hand()
}

end_state_0 = {
    'bucket_0': Bucket(black=1, red=0, green=0),
    'bucket_1': Bucket(black=0, red=0, green=0),
    'bucket_2': Bucket(black=0, red=3, green=0),
    'bucket_3': Bucket(black=0, red=0, green=3),
    'hand_left': Hand(),
    'hand_right': Hand()
}

initial_state_1 = {
    'bucket_0': Bucket(black=1, red=0, green=0),
    'bucket_1': Bucket(black=0, red=3, green=5),
}

end_state_1 = {
    'bucket_0': Bucket(black=1, red=0, green=0),
    'bucket_2': Bucket(black=0, red=3, green=0),
    'bucket_3': Bucket(black=0, red=0, green=5),
}

WS0_initial = WorldState(initial_state_0)
WS0_end = WorldState(end_state_0)

WS1_initial = WorldState(initial_state_1)
WS1_end = WorldState(end_state_1)


# data = [ FunctionData(input=[WS0_initial], output=WS0_end, alpha=0.95) ]
data = [ FunctionData(input=[WS0_initial], output=WS0_end, alpha=0.95), FunctionData(input=[WS1_initial], output=WS1_end, alpha=0.95)]

########################
## Testing Grammar
#########################
# for _ in xrange(20):
#     t = grammar.generate()
#     # print grammar.log_probability(t), t 
#     print t


####################################### 
# Actually run
####################################### 
from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
from LOTlib.SampleStream import *

h0 = MyHypothesisX()

# # Plain running
# for h in MHSampler(h0, data, steps=100):
#     # print h.posterior_score, h
#     pass


# Running and show only the top choice 
from LOTlib.TopN import TopN
topChoice = TopN(N=10)
steps = []
posProbs = []

for step, h in enumerate(MHSampler(h0, data, steps=100000)):
    if step % 5000 == 0:
        print ('current step: %d, current posterior score: %f' % (step, h.posterior_score))
    steps.append(step)
    posProbs.append(h.posterior_score)
    topChoice.add(h)
for h in topChoice.get_all(sorted=True):
    print h.posterior_score, h

# Plotting
import numpy as np
import matplotlib.pyplot as plt

stepArray = np.asarray(steps)
posProbArray = np.asarray(posProbs)
plt.plot(stepArray,posProbArray)
plt.ylabel('likelihood')
plt.xlabel('step')
plt.savefig('./childAlgoResultPlot/sorting_step_prob.png')
