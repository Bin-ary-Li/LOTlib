- primitives -- the function types, etc. 
- prior -- bound on depth, etc. 

# Introduction

LOTlib is a library for inferring compositions of functions from observations of their inputs and outputs. This tutorial will introduce a very simple problem and how it can be solved in LOTlib. 

Suppose that you know basic arithmetic operations (called "primitives") like addition (+), subtraction (-), multiplication (*) and division (/). You observe a number which has been constructed using these operations, and wish to infer which operations were used. We'll assume that you observe the single number `12` and then do Bayesian inference in order to discover which operations occurred. For instance, 12 may be written as `(1+1) * 6`, involving an addition, a multiplication, two uses of 1, and one use of 6. Or it may have been written as ` 1 + 11`, or `2 * 3 * 2`, etc. There are lots of other ways.

## Grammars

The general strategy of LOTlib models is to specify a space of possible compositions using a grammar. The grammar is actually a probabilistic context free grammar (with one small modification described below) that specifies a prior distribution on trees, or equivalently compositional structures like (1+1)*6, 2+2+2+2+2+2, (1+1)+(2*5), etc. If this is unfamiliar, the wiki on [PCFGs](https://help.github.com/articles/markdown-basics/) would be useful to read first. 

However, the best way to understand the grammar is as a way of specifying a program: any expansion of the grammar "renders" into a python program, whose code can then be evaluated. This will be made more concrete later.

For now, here is how we can construct a grammar

```python
    from LOTlib.Grammar import Grammar
    
    # Define a grammar object
    # Defaultly this has a start symbol called 'START' but we want to call 
    # it 'EXPR'
    grammar = Grammar(start='EXPR')
    
    # Define some operations
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    # And define some numbers. We'll give them a 1/n^2 probability
    for n in xrange(1,10):
        grammar.add_rule('EXPR', str(n), None, 10.0/n**2)
```
A few things to note here. The grammar rules have the format
```python
    grammar.add_rule( <NONTERMINAL>, <FUNCTION>, <ARGUMENTS>, <PROBABILITY>)
```
where <NONTERMINAL> says what nonterminal this rule is expanding. Here there is only one kind of nonterminal, an expression (EXPR). <FUNCTION> here is the function that this rule represents. These are strings that name defined functions in LOTlib, but they can also be strings (as here) where the <ARGUMENTS> get substituted in via string substitution (so for instance, "(%s+%s)" can be viewed as the function `lambda x,y: eval("(%s+%s)"%(x,y)))`. The arguments are a list of the arguments to the function. Note that the <FUNCTION> string can be pretty complex. For division, we have `(float(%s) / float(%s))`, which forces the function to use floating point division, not python's default. 

If the <FUNCTION> is a terminal that does not take arguments (as in the numbers 1..10), the <ARGUMENTS> part of a rule should be None. Note that None is very different from an empty list:
```python
    grammar.add_rule('EXPR', 'hello', None, 1.0)
```
renders into the program "hello" but 
```python
    grammar.add_rule('EXPR', 'hello', [], 1.0)
```
renders into "hello()". 


The production probabilities are, for now, fixed. Note that the numbers have probabilities proportional to 1/n**2. But overall, these also have a multiplier of 10, making them as a group much more likely than other operations. This is important because the PCFG has to define a proper probability distribution. This means that a nonterminal must have a probability of 1 of eventually leading to a terminal (a terminal is any rule with `None` as its <ARGUMENTS>). The easiest way to ensure this is to upweight the probabilities on terminals like the numbers here. 

We can see some productions from this grammar if we call Grammar.generate. We will also show the probability of this tree according to the grammar, which is computed by renormalizing the <PROBABILITY> values of each rule when expanding each nonterminal:
```python
    for _ in xrange(100):
        t = grammar.generate()
        print grammar.log_probability(t), t 
```
As you can see, the longer/bigger trees have lower (more negative) probabilities, implementing essentially a simplicity bias. These PCFG probabilities will often be our prior for Bayesian inference. 

Note that even though each `t` is a tree (a hierarchy of LOTlib.FunctionNodes), it renders nicely above as a string. This is defaultly how to expressions are evaluated in python. But we can see more of the internal structure using `t.fullprint()`, which shows the nonterminals, functions, and arguments at each level:
```python
    t = grammar.generate()
    t.fullprint()
```
## Hypotheses

The grammar nicely specifies a space of expressions, but LOTlib needs a "hypothesis" to perform inference. In LOTlib, hypotheses must define functions for computing priors, computing the likelihood of data, and implementing proposals in order for MCMC to work. In most cases, a hypothesis will represent a single production from the grammar.

Fortunately, for our purposes, there is a simple hypothesis class that it built-in to LOTlib which defaultly implements these. Let's just use it here. 
```python
    from math import log
    from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis
    
    # define a 
    class MyHypothesis(LOTHypothesis):
        def __init__(self, **kwargs):
            LOTHypothesis.__init__(self, grammar=grammar, args=[], **kwargs)
    
        def compute_single_likelihood(self, datum):
            if self(*datum.input) == datum.output:
                return log((1.0-datum.alpha)/100. + datum.alpha)
            else:
                return log((1.0-datum.alpha)/100.)
            
```
There are a few things going on here. First, we import LOTHypothesis and use that to define the new class `MyHypothesis`. LOTHypothesis defines `compute_prior()` and `compute_likelihood(data)`--more about these later. We define the initializer `__init__`. We overwrite the LOTHypothesis default and specify that the grammar we want is the one defined above. LOTHypotheses also defaultly take an argument called `x` (more on this later), but for now we want our hypothesis to be a function of no arguments. So we set `args=[]`. 

Essentially, `compute_likelihood` maps `compute_single_likelihood` over a list of data (treating each as IID conditioned on the hypothesis). So when we want to define how the likelihood works, we typically want to overwrite `compute_single_likelihood` as we have above. In this function, we expect an input `datum` with attirbutes `input`, `output`, and `alpha`. The LOTHypothesis `self` can be viewed as a function (here, one with no arguments) and so it can be called on `datum.input`. The likelihood this defines is one in which we generate a random number from 1..100 with probability `1-datum.alpha` and the correct number with probability `datum.alpha`. Thus, when the hypothesis returns the correct value (e.g. `self(*datum.input) == datum.output`) we must add these quantities to get the total probability of producing the data. When it does not, we must return only the former. LOTlib.Hypotheses.Likelihoods defines a number of other standard likelihoods, including the most commonly used  one, `BinaryLikelihood`. 

## Data

Given that our hypothesis wants those kinds of data, we can then create data as follows:
```python
    from LOTlib.DataAndObjects import FunctionData
    data = [ FunctionData(input=[], output=12, alpha=0.95) ]
```
Note here that the most natural form of data is a list--even if its only a single element--where each element, a datum, gets passed to `compute_single_likelihood`. The data here specifies the input, output, and noise value `alpha`. Note that even though `alpha` could live as an attribute of hypotheses, it makes most sense to view it as a known part of the data. 

## Making hypotheses

We may now use our definition of a hypothesis to make one. If we call the initializer without a `value` keyword, LOTHypothesis just samples it from the given grammar: 
```python
    h = MyHypothesis()
    print h.compute_prior(), h.compute_likelihood(data), h
```
Even better, `MyHypothesis` also inherits a `compute_posterior` function:
```python
    print h.compute_posterior(data), h.compute_prior(), h.compute_likelihood(data), h
```
For convenience, when `compute_posterior` is called, it sets attributes on `h` for the prior, likelihood, and posterior (score):
```python
    h = MyHypothesis()
    h.compute_prior(data)
    print h.posterior_score, h.prior, h.likelihood, h
```

## Running MCMC

We are almost there. We have define a grammar and a hypothesis which uses the grammar to define a prior, and custom code to define a likelihood. LOTlib's main claim to fame is that we can simply import MCMC routines and do inference over the space defined by the grammar. It's very easy:
```python
    from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
    
    # define a "starting hypothesis". This one is essentially copied by 
    # all proposers, so the sampler doesn't need to know its type or anything. 
    h0 = MyHypothesis()
    
    # Now use the sampler like an iterator. In MHSampler, compute_posterior gets called
    # so when we have an h, we can get its prior and likelihood
    for h in MHSampler(h0, data, steps=100):
        print h.posterior_score, h.prior, h.likelihood, h 
```
That probably went by pretty fast. Here's another thing we can do:
```python
    h0 = MyHypothesis()
    
    from collections import Counter

    count = Counter()
    for h in MHSampler(h0, data, steps=1000):
        count[h] += 1
    
    for h in sorted(count.keys(), key=lambda x: count[x]):
        print count[h], h.posterior_score, h
```
LOTlib hypotheses are required to hash nicely, meaning that they can be saved or put into dictionaries and sets like this. 

## Making our hypothesis class more robust

It's possible that in running the above code, you got a zero division error. Can you see why this can happen?

Fortunately, we can hack our hypothesis class to address this by catching the exception. A smart way to do this is to override `__call__` and return an appropriate value when such an error occurs:
```python
    from math import log
    from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis

    class MyHypothesis(LOTHypothesis):
        def __init__(self, **kwargs):
            LOTHypothesis.__init__(self, grammar=grammar, args=[], **kwargs)
            
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
```

## Getting serious about running

Now with more robust code, we can run the `Counter` code above for longer and get a better picture of the posterior. 
```python
    h0 = MyHypothesis()
    
    from collections import Counter

    # run a bit, counting how often we get each hypothesis
    count = Counter()
    for h in MHSampler(h0, data, steps=100000):
        count[h] += 1
    
    # print the counts and the posteriors
    for h in sorted(count.keys(), key=lambda x: count[x]):
        print count[h], h.posterior_score, h
```
If our sampler is working correctly, it should be the case that the time average of the sampler (the `h`es from the for loop) should approximate the posterior distribution (e.g. their re-normalized scores). Let's use this code to see if that's true
```python
    # Miscellaneous stores a number of useful functions. Here, we need logsumexp, which will
    # compute the normalizing constant for posterior_scores when they are in log space
    from LOTlib.Miscellaneous import logsumexp 
    from numpy import exp # but things that are handy in numpy are not duplicated (usually)
    
    # get a list of all the hypotheses we found. This is necessary because we need a fixed order,
    # which count.keys() does not guarantee unless we make a new variable. 
    hypotheses = count.keys() 
    
    # first convert posterior_scores to probabilities. To this, we'll use a simple hack of 
    # renormalizing the psoterior_scores that we found. This is a better estimator of each hypothesis'
    # probability than the counts from the sampler
    z = logsumexp([h.posterior_score for h in hypotheses])
    
    posterior_probabilities = [ exp(h.posterior_score - z) for h in hypotheses ]
    
    # and compute the probabilities over the sampler run
    cntz = sum(count.values())    
    sampler_counts          = [ float(count[h])/cntz for h in hypotheses ] 
    
    ## and let's just make a simple plot
    import matplotlib.pyplot as pyplot
    fig = pyplot.figure()
    plt = fig.add_subplot(1,1,1)
    plt.scatter(posterior_probabilities, sampler_counts)
    plt.plot([0,1], [0,1], color='red')
    fig.show()
    
```


## Sample Streams

Often it is necessary to manipulate sequences of samples. This is useful in debugging in order to determine where samplers are and are not working. LOTlib has a series of classes in `LOTlib.SampleStream` that enable you to easily process and manipulate streams of samples. 
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    # Same as above, but we have wrapped MHSampler in a SampleStream
    for h in SampleStream(MHSampler(h0, data, steps=100)):
        print h 
```
Not much has changed. But reading in the SampleStream code, you will see a variety of functions which are defined. Importantly, they can be chained together using `>>` notation. For instance, ``PrintH`` is a special printing function that will print a posterior_score, prior, and likelihood. It can be added after the SampleStream:
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    # Stream from the sampler to a printer
    for h in SampleStream(MHSampler(h0, data, steps=100)) >> PrintH():
        pass
```
Note that we have replaced `print h` with a `pass` keyword, and the printing is now done by `PrintH()`. But that the `pass` command doesn't have to be a pass--`h` still ranges over every sample returned by the last stream operation. So for instance, the following will print each hypothesis with `PrintH` but then on the next line also print `h()` so you can see the number it generates (e.g. the result of its evaluation):
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    for h in SampleStream(MHSampler(h0, data, steps=100)) >> PrintH():
        print h()
```

Here's another useful stream operation: `Unique` will toss anything that is a repetition of a previous sample, using the ability of LOTHypotheses to be hashed. If we put that between the sampler and the print, only the unique ones will be printed
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    for h in SampleStream(MHSampler(h0, data, steps=100)) >> Unique() >> PrintH():
        pass
```


We can also save our hypotheses. SampleStreams work so that if execution is ever interrupted, every `__exit__` command is called, meaning that the save is guaranteed to correctly close the file. Here we save only the uniques in a pickle file, not printing any:
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    for h in SampleStream(MHSampler(h0, data, steps=100)) >> Unique() >> Save('myfile.pkl'):
        pass
```

Another useful stream operation is `Skip`, which skips some samples:
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    for h in SampleStream(MHSampler(h0, data, steps=100)) >> Skip(10) >> PrintH():
        pass
```
This makes the output more manageable, only printing 10 instead of 100. However, the intermediate samples are discarded. 

The stream operation `Tee` (named after the linux command) allows us split a stream into two or more streams. This might be useful if we want to view a stream with some skip (for debugging or monitoring), but also save all the unique samples we find:
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    for h in SampleStream(MHSampler(h0, data, steps=10000)) >> Tee(Skip(100) >> PrintH(), \
                                                                  Unique() >> Save('samples.pkl')):
        pass
```

## The best hypotheses

Very often, models in LOTlib approximate the full posterior distribution P(H|D) using the highest posterior hypotheses. There are two main ways to do this. One is a class named `LOTlib.TopN` which acts like a set--you can add to it, but it keeps only the ones with highest posterior_score (or whatever "key" is set). It will return them to you in a sorted order:
```python
    from LOTlib.TopN import TopN
    
    tn = TopN(N=10) # store the top N

    h0 = MyHypothesis()
    
    for h in MHSampler(h0, data, steps=10000):
        tn.add(h)

    for h in tn.get_all(sorted=True):
        print h.posterior_score, h 

```

Of course, SampleStream also has a way to get at the best hypotheses. It is the stream operation `Top` and it is somewhat special: only on exiting do the operations downstream of `Top` get to process samples, and they only do so on the top samples. 
```python
    from LOTlib.SampleStream import *

    h0 = MyHypothesis()

    for h in SampleStream(MHSampler(h0, data, steps=10000)) >> Top(10) >> PrintH():
        pass
```

## Hypotheses as functions

Remember how we made `args=[]` in the definition of MyHypothesis? That stated that a hypothesis was not a function of any arguments. However, you may have noticed that when a hypothesis is converting to a string (for printing or evaling) it acquired an additional `lambda` on the outside, indicating that the hypothesis was a function of no arguments. Compare a tree produced by the grammar, with the hypothesis created with the tree as its "value". To do this, we can pass the tree as a `value` in the hypothesis constructor:
```python
    t = grammar.generate()
    print str(t)

    h = MyHypothesis(value=t)
    print str(h)    
```
This is an important distinction: the result of `grammar.generate()` is always a tree, or a hierarchy of `LOTlib.FunctionNode`s which can get rendered into a string. A LOTHypothesis, in contrast, is always a function of some arguments. When there are no arguments, it is a [thunk](https://en.wikipedia.org/wiki/Thunk). 

Here is a new listing where a class like MyHypothesis requires an argument. Now, when it renders, it comes with a `lambda x` in front, rather than just a `lambda`. There are two other primary changes: the grammar now has to allow the argument (`x`) to be produced in expressions, and the `datum.input` has to provide an argument, which gets bound to `x` when the function is evaluated. 
```python
    ######################################## 
    ## Define a grammar
    ######################################## 

    from LOTlib.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    # Now define how the grammar uses x. The string 'x' must
    # be the same as used in the args below
    grammar.add_rule('EXPR', 'x', None, 1.0) 

    for n in xrange(1,10):
        grammar.add_rule('EXPR', str(n), None, 10.0/n**2)

    from math import log
    from LOTlib.Hypotheses.LOTHypothesis import LOTHypothesis

    ######################################## 
    ## Define the hypothesis
    ######################################## 
    
    # define a 
    class MyHypothesisX(LOTHypothesis):
        def __init__(self, **kwargs):
            LOTHypothesis.__init__(self, grammar=grammar, args=['x'], **kwargs)
        
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
    data = [ FunctionData(input=[3], output=12, alpha=0.95) ]

    ######################################## 
    ## Actually run
    ######################################## 
    from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
    from LOTlib.SampleStream import *

    h0 = MyHypothesisX()

    for h in SampleStream(MHSampler(h0, data, steps=10000)) >> Unique() >> PrintH():
        pass
```
Why does this matter? Well now instead of just explaining the data we saw, we can use the hypothesis to generalize to *new*, unseen data. For instane, we can take each hypothesis and see what it has to say about other numbers
```python

    from LOTlib.SampleStream import *

    h0 = MyHypothesisX()

    for h in SampleStream(MHSampler(h0, data, steps=10000)) >> Unique() >> PrintH():

        # And now for each hypothesis, we'll see what it maps 1..10 to 
        print map(h, range(1,11))
```
Thus, we have taken a single data point and used it to infer a function that can *generalize* to new, unseen data or arguments. Note, though, that there is no requirement that `x` is used in each hypothesis. (If we wanted that, a LOTlibian way to do it would be to modify the prior to assign trees that don't use `x` to have `-Infinity` log prior). 

Just for fun here, let's take the posterior predictive and see how likely we are to generalize this function to each other number. 
```python
    
    ## First let's make a bunch of hypotheses
    from LOTlib.TopN import TopN

    tn = TopN(1000) 

    h0 = MyHypothesisX()
    for h in MHSampler(h0, data, steps=1000000): # run more steps
        tn.add(h)

    # store these in a list (tn.get_all is defaultly a generator)
    hypotheses = list(tn.get_all())
    
    # Compute the normalizing constant
    from LOTlib.Miscellaneous import logsumexp
    z = logsumexp([h.posterior_score for h in hypotheses])

    ## Now compute a matrix of how likely each input is to go
    ## to each output
    M = 20 # an MxM matrix of values
    import numpy

    # The probability of generalizing
    G = numpy.zeros((M,M))

    # Now add in each hypothesis' predictive
    for h in hypotheses:
        print h 
        # the (normalized) posterior probability of this hypothesis
        p = numpy.exp(h.posterior_score - z)
        
        for x in xrange(M):
            output = h(x)
            
            # only keep those that are in the right range
            if 0 <= output < M:
                G[x][output] += p

    # And show the output
    print numpy.array_str(G, precision=3)
```
As you can see, observing that some (unseen) function maps 3->12 gives rise to nontrivial beliefs about the function underlying this transformation. 

# Lambdas

The power of this kind of representation comes not only from an ability to learn such simple functions, but to also learn functions with new kinds of abstractions. In programming languages, the simplest kind of abstraction is a variable--a value that is stored for later use. The variable `x` is created above on the level of a LOTHypothesis, but where things get more interesting is when the lower down values in a grammar can be used to define variables. Let's look at a grammar with two additional pieces
```python

    from LOTlib.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    grammar.add_rule('EXPR', 'x', None, 1.0) 

    for n in xrange(1,10):
        # We'll make these lower probability so we can see more lambdas below
        grammar.add_rule('EXPR', str(n), None, 5.0/n**2)

    # And allow lambda abstraction
    # First we define the application of a new nonterminal, FUNC, to a term EXPR
    grammar.add_rule('EXPR', '(%s)(%s)', ['FUNC', 'EXPR'], 1.0)
    # Here, FUNC should be thought of as a function
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR')

```
Here, `lambda` is a special LOTlib keyword that *introduces a bound variable* with a unique name in expanding the <ARGUMENT>s. In other words, when the grammar happens to sample a rule whose <FUNCTION> is `'lambda'`, it creates a new variable name, allows `bv_type` to expand to this variable, expands the <ARGUMENTS> to `lambda` (here, `EXPR`), and then removes the rule from the grammar. Let's look at some productions:
```python
    for _ in xrange(1000):
        print grammar.generate()
```
Now some of the trees contain `lambda` expressions, which bind a variable (defaultly rendered as `y1`). The variable `y1` can only be used below its corresponding lambda, making the grammar in LOTlib technically not context-free, but very weakly context-sensitive. The variables like `y1` are called **bound variables** in LOTlib. Note that they are numbered by their height in the tree, making them unique to the nodes below, but neither sequential, nor unique in the whole tree (underlyingly, they have unique names no matter what, but not when rendered into strings). 

These bound variables count towards the prior (when using `grammar.log_probability`) in exactly the way they should: when a nonterminal (specified in `bv_type`) can expand to a given bound variable, that costs probability, and other expansions must lose probability. The default in LOTlib is to always renormalize the probabilities specified. Note that in the `add_rule` command, we can change the probability that a EXPR->yi rule has by passing in a bv_p argument:
```python
    # make using yi 10x more likely than before
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR', bv_p=10.0)
```

Lambdas like these play the role of variable declarations in a normal programming language. But note that the variables aren't guaranteed to be useful. In fact, very often variables are stupid, as in the expression
```python
    (lambda y1: y1)((1 * 1))
```
where the lambda defines a variable that is used immediately without modification. This expression is therefore equivalent to 
```python
    (1 * 1)
```
in terms of its function, but not in terms of its prior. 

We can also change the name that bound variables get by setting `bv_prefix`:
```python
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR', bv_prefix='v')
```
will make bound variables named `v1`, `v2`, etc. 

## Here's where things get crazy

Of course, the true art of lambdas is not just that they can define variables, but that the variables themselves can be functions! This corresponds to *function declarations* in ordinary programming languages. If this is foreign or weird, I'd suggest reading [The Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sicp/). 

To define lambdas as functions, we only need to specify a `bv_args` list in the `lambda` declaration. `bv_args` is the type of arguments that are passed to each use of a bound variable each time it is used. But... then we have a problem of needing to bind that variable to something. If `yi` is itself a function of an EXPR, then its argument *also* has to be a function. That requires two lambdas. Here's how it works:
```python

    from LOTlib.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(float(%s) / float(%s))', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(-%s)', ['EXPR'], 1.0)
    
    grammar.add_rule('EXPR', 'x', None, 1.0)  

    for n in xrange(1,10):
        grammar.add_rule('EXPR', str(n), None, 5.0/n**2)

    # Allow ourselves to define functions. This means creating a bound 
    # variable that can be bound to a FUNC. Where, the bound variable
    # is defined (here, FUNCDEF) we are allowed to use it. 
    grammar.add_rule('EXPR', '((%s)(%s))',  ['FUNCDEF', 'FUNC'], 1.0)

    # The function definition has a bound variable who can be applied as
    # a function, whose arguments are an EXPR (set by the type of the FUNC above)
    # and whose name is F, and who when applied to an EXPR returns an EXPR
    # We'll also set bv_p here. Feel free to play with it and see what that does. 
    grammar.add_rule('FUNCDEF', 'lambda', ['EXPR'], 1.0, bv_type='EXPR', bv_args=['EXPR'], bv_prefix='F')

    # and we have to say what a FUNC is. It's a function (lambda) from an EXPR to an EXPR
    grammar.add_rule('FUNC', 'lambda', ['EXPR'], 1.0, bv_type='EXPR')

```
Let's look at some hypotheses. Here, we'll show only those that use `F1` as a function (thus contain the string `"F1("`:
```python
    import re 

    for _ in xrange(50000):
        t = grammar.generate()
        if re.search(r"F1\(", str(t)):
            print t
```
For instance, this code might generate the following expression, which is obscure, though acceptable, python:
```python
    ((lambda F1: F1(x+1))(lambda y1: y1+3))
```
Here, we have define a variable `F1` that really represents the *function* `lambda y1: y1+3`. The value that is returned is the value of applying `F1` to the overall hypothesis value `x` plus `1`. Note that LOTlib here has correctly used `F1` in a context where an EXPR is needed (due to `bv_type='EXPR'` on `FUNCDEF`). It knows that the argument to `F1` is also an EXPR, which here happens to be expanded to `x+1`. It also knows that `F1` is itself a function, and it binds this function (through the outermost apply) to `lambda y1: y1+3`. LOTlib knows that `F1` can only be used in the left hand side of this appyl, and `y1` can only be used on the right. This holds even if multiple bound variables of different types are generated. 

This ability to define functions provides some of the most interesting learning dynamics for the model. A nice example is provided in LOTlib.Examples.Magnetism, where learners take data and learn predicates classifying observable objects into two kinds, as well as laws stated over those kinds.

## Recursive functions

Well that's wonderful, but what if we want a function to refer to *itself*? This is common in programming languages in the form of recursive definitions. This takes a little finagling in the LOTlib internals, but there is a class that implements recursion straightforwardly: `RecursiveLOTHypothesis`. Internally, hypothesis of this type always have an argument (defaultly called `recurse_`) which binds to themselves! 

Here is a simple example:
```python

    ######################################## 
    ## Define the grammar
    ######################################## 
    
    from LOTlib.Grammar import Grammar
    grammar = Grammar(start='EXPR')
    
    # for simplicity, two operations
    grammar.add_rule('EXPR', '(%s + %s)', ['EXPR', 'EXPR'], 1.0)
    grammar.add_rule('EXPR', '(%s * %s)', ['EXPR', 'EXPR'], 1.0)
    
    # we'll just allow two terminals for simplicity
    # We have to upweight them a little to keep things well-defined
    grammar.add_rule('EXPR', 'x', None, 10.0) 
    grammar.add_rule('EXPR', '1', None, 10.0) 
    
    # If we're going to allow recursion, we better have a base case
    # But this probably requires an "if" statement. LOTlib's "if_" 
    # primitive will do the trick
    grammar.add_rule('EXPR', 'if_', ['BOOL', 'EXPR', 'EXPR'], 1.0)
    
    # and we need to define a boolean. For now, let's just check
    # if x=1
    grammar.add_rule('BOOL', 'x==1', None, 1.0)
    
    # and the recursive operation -- I am myself a function
    # from EXPR to EXPR, so recurse should be as well
    grammar.add_rule('EXPR', 'recurse_', ['x-1'], 1.0) 
    
    ######################################## 
    ## Define the hypothesis
    ######################################## 
    from LOTlib.Hypotheses.RecursiveLOTHypothesis import RecursiveLOTHypothesis
    
    
    class MyRecursiveHypothesis(RecursiveLOTHypothesis):
        def __init__(self, **kwargs):
            RecursiveLOTHypothesis.__init__(self, grammar=grammar, args=['x'], **kwargs)
        
    ######################################## 
    ## Look at some examples
    ######################################## 
    import re
    from LOTlib.Evaluation.EvaluationException import RecursionDepthException
    
    for _ in xrange(50000):
        h = MyRecursiveHypothesis()
        
        # Now when we call h, something funny may happen: we may get
        # an exception for recursing too deep. If this happens for some 
        # reasonable xes, let's not print the hypothesis -- it must not 
        # be well-defined
        try:
            # try our function out
            values = map(h, range(1,10))
        except RecursionDepthException:
            continue
            
        # if we succeed, let's only show hypotheses that use recurse:
        if re.search(r"recurse_\(", str(h)):
            print h 
            print values
```
Note that there is nothing special about the `recurse_` name: it can be changed by setting `recurse=...` in `RecursiveLOTHypothesis.__init__`, but then the name should also be changed in the grammar. In this tutorial, we have only looked at defining the grammar, not in inferring recursive hypotheses. LOTlib.Examples.Number is an example of learning a genuinely recursive function from data. 

# Lexicons

Part of what makes cognitive systems powerful is that we don't have just one function, we have many. A Lexicon is LOTlib's way of allowing inference to work on many functions at once. A Lexicon is a hypothesis class like any other (meaning it defines `Lexicon.compute_prior`, `Lexicon.compute_likelihood`, and `Lexicon.compute_posterior`) but it binds together any number of LOTHypotheses into the "meanings" for "words." Here is a simple example:
```python
    from LOTlib.Hypotheses.Lexicon import SimpleLexicon
    
    class MyLexicon(SimpleLexicon):
        def __init__()

```


# Grammar inference

## MPI

## Examples

Often, though, in LOTlib models it helps to start multiple chains. Each chain gets its own hypothesis which is randomly initialized from the grammar. This often helps the hypotheses to "fall" into the right regions of space. Let's import a class for running multiple chains and try it, running even more steps:
```
    from LOTlib.Inference.Samplers.MultipleChainMCMC import MultipleChainMCMC
    from collections import Counter
    
    # now instead of starting from a single h0, we need a function to make the h0. 
    # The constructor for MyHypothesis will do this well!

    count = Counter()
    for h in MultipleChainMCMC(MyHypothesis, data, steps=100000, nchains=10):
        # Note that this yields our sampled h back interwoven between chains
        count[h] += 1
    
    
    for h in sorted(count.keys(), key=lambda x: count[x]):
        print count[h], h.posterior_score, h.prior, h.likelihood, h 
```

