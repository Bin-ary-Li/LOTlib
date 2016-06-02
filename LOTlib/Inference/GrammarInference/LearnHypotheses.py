
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib.DataAndObjects import FunctionData, Obj

def make_data(n=1, alpha=0.9):
    return [FunctionData(input=[Obj(shape='square', color='red', size='large')], output=False, alpha=alpha),
            FunctionData(input=[Obj(shape='triangle', color='green', size='small')], output=False, alpha=alpha)]*n

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Grammar
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib.DefaultGrammars import DNF
from LOTlib.Miscellaneous import q

# DNF defaultly includes the logical connectives so we need to add predicates to it.
grammar = DNF

# Two predicates for checking x's color and shape
# Note: per style, functions in the LOT end in _
grammar.add_rule('PREDICATE', 'is_color_', ['x', 'COLOR'], 1.0)
grammar.add_rule('PREDICATE', 'is_shape_', ['x', 'SHAPE'], 1.0)
grammar.add_rule('PREDICATE', 'is_size_',  ['x', 'SIZE'],  1.0)

# Some colors/shapes each (for this simple demo)
# These are written in quotes so they can be evaled
grammar.add_rule('COLOR', q('red'), None, 1.0)
grammar.add_rule('COLOR', q('green'), None, 1.0)

grammar.add_rule('SHAPE', q('square'), None, 1.0)
grammar.add_rule('SHAPE', q('triangle'), None, 1.0)

grammar.add_rule('SIZE', q('small'), None, 1.0)
grammar.add_rule('SIZE', q('large'), None, 1.0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Hypothesis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from LOTlib.Hypotheses.RationalRulesLOTHypothesis import RationalRulesLOTHypothesis

def make_hypothesis(grammar=grammar, **kwargs):
    return RationalRulesLOTHypothesis(grammar=grammar, rrAlpha=1.0, **kwargs)


if __name__ == "__main__":

    from LOTlib.TopN import TopN
    hyps = TopN(N = 1000)

    from LOTlib.Inference.Samplers.MetropolisHastings import MHSampler
    from LOTlib import break_ctrlc
    mhs = MHSampler(make_hypothesis(), make_data(), 1000000, likelihood_temperature = 1., prior_temperature = 1.)

    for samples_yielded, h in break_ctrlc(enumerate(mhs)):
        hyps.add(h)

    import pickle
    with open('HypothesisSpace.pkl', 'w') as f:
        pickle.dump(hyps, f)