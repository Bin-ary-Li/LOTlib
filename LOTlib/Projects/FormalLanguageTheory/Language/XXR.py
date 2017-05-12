import itertools
from FormalLanguage import FormalLanguage, compute_all_strings
from LOTlib.Projects.FormalLanguageTheory.Language.FormalLanguage import FormalLanguage
from LOTlib.Grammar import Grammar

class XXR(FormalLanguage):
    """
    (a,b)+ strings followed by their reverse.
    This can be generated by a CFG
    """

    def __init__(self):
        self.grammar = Grammar(start='S')
        self.grammar.add_rule('S', 'a%s', ['S'], 1.0)
        self.grammar.add_rule('S', 'b%s', ['S'], 1.0)
        self.grammar.add_rule('S', 'a',   None, 1.0)
        self.grammar.add_rule('S', 'b',   None, 1.0)

    def terminals(self):
        return list('ab')

    def sample_string(self): # fix that this is not CF
        s = str(self.grammar.generate()) # from {a,b}+
        return s+''.join(reversed(s))

    def all_strings(self):
        for l in itertools.count(1):
            for s in compute_all_strings(l, alphabet='ab'):
                yield s + s[::-1]

if __name__ == '__main__':
    language = XXR()
    print language.sample_data(10000)