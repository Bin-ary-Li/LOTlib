from WorldState import *
from copy import deepcopy
from collections import Counter


algorithmName = "sorting"

## testing param
wsHistoryList = []

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
# grammar.add_rule('ACTION', '%s = %s.grabBall(%s, %s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'BUCKET', 'HAND', 'COLOR'], 1.)
# grammar.add_rule('ACTION', '%s = %s.dropBall(%s, %s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'HAND', 'BUCKET', 'COLOR'], 1.)
# grammar.add_rule('ACTION', '%s = %s.grabRandomBall(%s, %s)', ['WORLDSTATE', 'WORLDSTATE', 'BUCKET', 'HAND'], 1.)
grammar.add_rule('ACTION', 'pass', None, .1)

grammar.add_rule('CONDITION', '%s', ['IF_STATEMENT'], 1.)
grammar.add_rule('CONDITION', '%s', ['WHILE_LOOP'], 1.)

grammar.add_rule('IF_STATEMENT', '''if %s:
%s}
else:
%s}''', ['BOOL', 'ACTION','ACTION'], 1.)

grammar.add_rule('WHILE_LOOP', '''while %s and x.getItrCounter() < 36:
%s
x.incItrCounter()
if x.getItrCounter() == 35:
x.resetItrCounter()
break}
}''', ['BOOL','ACTION'], 1.)

grammar.add_rule('WHILE_LOOP', '''while %s and x.getItrCounter() < 36:
%s
x.incItrCounter()
if x.getItrCounter() == 35:
x.resetItrCounter()
break}
}''', ['BOOL','IF_STATEMENT'], 1.)


grammar.add_rule('BOOL', 'x.existColor(%s, %s)', ['CONTAINER','COLOR'], 1.0)
grammar.add_rule('BOOL', 'x.canAddBall(%s, %s)', ['CONTAINER','COLOR'], 1.0)

grammar.add_rule('BOOL', '(%s >= %s)', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', '(%s <= %s)', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', '(%s > %s)', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', '(%s < %s)', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', '(x.getContainer(%s) == x.getContainer(%s))', ['CONTAINER','CONTAINER'], 1.0)
grammar.add_rule('BOOL', 'x.getContainer(%s).isEmpty()', ['CONTAINER'], 1.0)
grammar.add_rule('BOOL', 'not (%s)', ['BOOL'], 1.0)
grammar.add_rule('BOOL', 'True', None, .1)
grammar.add_rule('BOOL', 'False', None, .1)

grammar.add_rule('CONTAINER', '%s', ['BUCKET'], 1.)
grammar.add_rule('CONTAINER', '%s', ['HAND'], 1.)

grammar.add_rule('BUCKET', '\'bucket_0\'', None, 1.0)
grammar.add_rule('BUCKET', '\'bucket_1\'', None, 1.0)
grammar.add_rule('BUCKET', '\'bucket_2\'', None, 1.0)
grammar.add_rule('BUCKET', '\'bucket_3\'', None, 1.0)
grammar.add_rule('HAND', '\'hand_right\'', None, 5.0)
grammar.add_rule('HAND', '\'hand_left\'', None, 1.0)

grammar.add_rule('COLOR', '\'black\'', None, 1.0)
grammar.add_rule('COLOR', '\'red\'', None, 1.0)
grammar.add_rule('COLOR', '\'green\'', None, 1.0)


from math import log
from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis

######################################## 
## Define the hypothesis
######################################## 


class MyHypothesisX(LOTHypothesis):
    def __init__(self, **kwargs):
        LOTHypothesis.__init__(self, grammar=grammar, display='''def algo(x): \n%s\n    return x''', **kwargs)

    def __call__(self, ws):
        parsedCode = self.code_compilation(str(self))
        exec('''%s''' % parsedCode)
        worldS = algo(ws)
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
        inputWorld = deepcopy(datum.input[0])
        outputWorld = self.__call__(inputWorld)
        assert isinstance(outputWorld.getSnippetWS() - datum.output.getSnippetWS(), int), 'subtraction result is not an int'
        # print map(lambda x: x - datum.output.getSnippetWS(), outputWorld.getHistory())
        wsHistoryList.append(map(lambda x: x - datum.output.getSnippetWS(), outputWorld.getHistory()))
        return - ((outputWorld.getSnippetWS() - datum.output.getSnippetWS())*100 + outputWorld.getAffordanceViolateCnt())


######################################## 
## Creating the data
######################################## 

from ChildAlgoData import make_data


# from LOTlib.DataAndObjects import FunctionData

# initial_state_0 = {
#     'bucket_0': Bucket(black=1, red=0, green=0),
#     'bucket_1': Bucket(black=0, red=3, green=3),
# }

# end_state_0 = {
#     'bucket_0': Bucket(black=1, red=0, green=0),
#     'bucket_2': Bucket(black=0, red=3, green=0),
#     'bucket_3': Bucket(black=0, red=0, green=3),
# }

# initial_state_1 = {
#     'bucket_0': Bucket(black=1, red=0, green=0),
#     'bucket_1': Bucket(black=0, red=3, green=5),
# }

# end_state_1 = {
#     'bucket_0': Bucket(black=1, red=0, green=0),
#     'bucket_2': Bucket(black=0, red=3, green=0),
#     'bucket_3': Bucket(black=0, red=0, green=5),
# }

# initial_state_2 = {
#     'bucket_0': Bucket(black=5, red=0, green=0),
#     'bucket_1': Bucket(black=0, red=10, green=8),
# }

# end_state_2 = {
#     'bucket_0': Bucket(black=5, red=0, green=0),
#     'bucket_2': Bucket(black=0, red=10, green=0),
#     'bucket_3': Bucket(black=0, red=0, green=8),
# }

# WS0_initial = WorldState(initial_state_0)
# WS0_end = WorldState(end_state_0)

# WS1_initial = WorldState(initial_state_1)
# WS1_end = WorldState(end_state_1)

# WS2_initial = WorldState(initial_state_2)
# WS2_end = WorldState(end_state_2)

# data = [ FunctionData(input=[WS0_initial], output=WS0_end, alpha=0.95)]
# data_1 = [ FunctionData(input=[WS0_initial], output=WS0_end, alpha=0.95), FunctionData(input=[WS1_initial], output=WS1_end, alpha=0.95)]

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
# from LOTlib.TopN import TopN
# topChoice = TopN(N=10)

# print "\n\n\n\n\n\n_________1 data point____________\n"
# for h in MHSampler(h0, data, steps=5000):
#     print h.posterior_score
#     topChoice.add(h)
# else: 
#     print "\n\n\n\n\n_________2 data point____________\n"
#     for h in MHSampler(h0, data_1, steps=5000):
#         print h.posterior_score



# Running and show only the top choice 
from LOTlib.TopN import TopN
topChoice = TopN(N=10)
posProbs = []
stepNum = 40000

for step, h in enumerate(MHSampler(h0, make_data(data_size=1), steps=stepNum)):
    if step % 5000 == 0:
        print ('current step: %d, current posterior score: %f' % (step, h.posterior_score))
    posProbs.append(h.posterior_score)
    topChoice.add(h)
    h0 = h

# for step, h in enumerate(MHSampler(h0, make_data(data_size=2), steps=stepNum)):
#     if step % 5000 == 0:
#         print ('current step: %d, current posterior score: %f' % (step, h.posterior_score))
#     posProbs.append(h.posterior_score)
#     topChoice.add(h)
#     h0 = h

# for step, h in enumerate(MHSampler(h0, make_data(data_size=3), steps=stepNum)):
#     if step % 5000 == 0:
#         print ('current step: %d, current posterior score: %f' % (step, h.posterior_score))
#     posProbs.append(h.posterior_score)
#     topChoice.add(h)
#     h0 = h

for h in topChoice.get_all(sorted=True):
    print h.posterior_score, h

wsHistoryListTuple = map(tuple, wsHistoryList)
historyC = Counter(wsHistoryListTuple)

print "\n\n\n\n\n----<history of world state>------\b"
print historyC.most_common(100)
print "\b----<history of world state>------\n\n\n\n\n"

# Plotting
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import datetime

stepArray = np.arange(len(posProbs))
posProbArray = np.asarray(posProbs)

# If running for single data point: 
plt.plot(stepArray, posProbArray) 
plt.xlabel('Step')
plt.ylabel('Likelihood')


# # If running for multiple data points: 

# dataPt1 = np.ma.masked_where(stepArray < 0, stepArray)
# dataPt2 = np.ma.masked_where( stepArray < stepNum , stepArray)
# dataPt3 = np.ma.masked_where(stepArray < stepNum*2, stepArray)

# plt.plot(dataPt1, posProbArray, 'r-', label='w/ 1 dataPt') 
# plt.plot(dataPt2, posProbArray, 'g-', label='w/ 2 dataPt') 
# plt.plot(dataPt3, posProbArray, 'b-', label='w/ 3 dataPt')
# plt.xlabel('Step')
# plt.ylabel('Likelihood')

# plt.legend(loc='lower left')


# Save plot
currentTime = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M")
plt.savefig('./childAlgoResultPlot/' + algorithmName + '_' + currentTime + '.png')


