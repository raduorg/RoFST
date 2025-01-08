from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

@dataclass
class MorphemeRule:
    """Represents a morphological rule with its category and meaning."""
    category: str
    meaning: str
    allomorphs: Set[str]

class RomanianMorphemeFST:
    def __init__(self):
        # Define morpheme categories
        self.prefixes: Dict[str, MorphemeRule] = {
            'răs': MorphemeRule('prefix', 'again/against', {'răs', 'răz'}),
            'în': MorphemeRule('prefix', 'in/into', {'în', 'îm'}),
            'des': MorphemeRule('prefix', 'un/reverse', {'des', 'dez'}),
            'pre': MorphemeRule('prefix', 'pre/before', {'pre'}),
            'ne': MorphemeRule('prefix', 'negation', {'ne'}),
            'sub': MorphemeRule('prefix', 'under', {'sub', 'sup'}),
        }

        self.roots: Dict[str, MorphemeRule] = {
            'lucr': MorphemeRule('root', 'work', {'lucr'}),
            'face': MorphemeRule('root', 'do/make', {'fac', 'făc'}),
            'merg': MorphemeRule('root', 'walk/go', {'merg', 'mers'}),
            'scrie': MorphemeRule('root', 'write', {'scri', 'scris'}),
            'citi': MorphemeRule('root', 'read', {'cit', 'citit'}),
        }

        self.noun_suffixes: Dict[str, MorphemeRule] = {
            'tor': MorphemeRule('suffix', 'agent', {'tor', 'toare'}),
            'ție': MorphemeRule('suffix', 'action/result', {'ție', 'ții'}),
            'ime': MorphemeRule('suffix', 'collective', {'ime'}),
            'iță': MorphemeRule('suffix', 'diminutive', {'iță'}),
        }

        self.verb_suffixes: Dict[str, MorphemeRule] = {
            'esc': MorphemeRule('suffix', 'present.1sg', {'esc'}),
            'ează': MorphemeRule('suffix', 'present.3sg', {'ează'}),
            'at': MorphemeRule('suffix', 'participle', {'at'}),
            'ând': MorphemeRule('suffix', 'gerund', {'ând', 'ind'}),
        }

        self.plural_suffixes: Dict[str, MorphemeRule] = {
            'i': MorphemeRule('suffix', 'plural', {'i'}),
            'uri': MorphemeRule('suffix', 'plural', {'uri'}),
            'e': MorphemeRule('suffix', 'plural', {'e'}),
        }

        # Gender and case endings
        self.endings: Dict[str, MorphemeRule] = {
            'ul': MorphemeRule('ending', 'def.masc.sg', {'ul', 'l'}),
            'a': MorphemeRule('ending', 'def.fem.sg', {'a'}),
            'lui': MorphemeRule('ending', 'gen/dat.masc.sg', {'lui'}),
            'ei': MorphemeRule('ending', 'gen/dat.fem.sg', {'ei'}),
        }

    def decompose(self, word: str) -> List[Tuple[str, MorphemeRule]]:
        """
        Decompose a word into its morphemes.
        Returns a list of (morpheme, rule) tuples.
        """
        word = word.lower()
        morphemes = []
        remaining = word

        # Check for prefixes
        for prefix, rule in self.prefixes.items():
            if any(remaining.startswith(allomorph) for allomorph in rule.allomorphs):
                for allomorph in rule.allomorphs:
                    if remaining.startswith(allomorph):
                        morphemes.append((allomorph, rule))
                        remaining = remaining[len(allomorph):]
                        break

        # Find root
        root_found = False
        for root, rule in self.roots.items():
            for allomorph in rule.allomorphs:
                if allomorph in remaining:
                    idx = remaining.find(allomorph)
                    if idx == 0:  # Only match at the beginning
                        morphemes.append((allomorph, rule))
                        remaining = remaining[len(allomorph):]
                        root_found = True
                        break
            if root_found:
                break

        # Check for suffixes
        while remaining:
            suffix_found = False
            
            # Check verb suffixes
            for suffix, rule in self.verb_suffixes.items():
                if any(remaining.startswith(allomorph) for allomorph in rule.allomorphs):
                    for allomorph in rule.allomorphs:
                        if remaining.startswith(allomorph):
                            morphemes.append((allomorph, rule))
                            remaining = remaining[len(allomorph):]
                            suffix_found = True
                            break
                    break

            # Check noun suffixes
            if not suffix_found:
                for suffix, rule in self.noun_suffixes.items():
                    if any(remaining.startswith(allomorph) for allomorph in rule.allomorphs):
                        for allomorph in rule.allomorphs:
                            if remaining.startswith(allomorph):
                                morphemes.append((allomorph, rule))
                                remaining = remaining[len(allomorph):]
                                suffix_found = True
                                break
                        break

            # Check plural suffixes
            if not suffix_found:
                for suffix, rule in self.plural_suffixes.items():
                    if any(remaining.endswith(allomorph) for allomorph in rule.allomorphs):
                        for allomorph in rule.allomorphs:
                            if remaining.endswith(allomorph):
                                morphemes.append((allomorph, rule))
                                remaining = remaining[:-len(allomorph)]
                                suffix_found = True
                                break
                        break

            # Check endings
            if not suffix_found:
                for ending, rule in self.endings.items():
                    if any(remaining.endswith(allomorph) for allomorph in rule.allomorphs):
                        for allomorph in rule.allomorphs:
                            if remaining.endswith(allomorph):
                                morphemes.append((allomorph, rule))
                                remaining = remaining[:-len(allomorph)]
                                suffix_found = True
                                break
                        break

            if not suffix_found:
                # If no more morphemes can be identified, add remaining as unknown
                if remaining:
                    morphemes.append((remaining, MorphemeRule('unknown', 'unknown', {remaining})))
                break

        return morphemes

def test_morpheme_analyzer():
    analyzer = RomanianMorphemeFST()
    test_words = [
        'lucrător',      # lucr-ător (worker)
        'nelucrând',     # ne-lucr-ând (not working)
        'făcător',       # făc-ător (maker)
        'scriitor',      # scri-itor (writer)
        'citește',       # cit-ește (reads)
        'prefăcut',      # pre-făc-ut (pretended)
        'lucrările',     # lucr-ăr-ile (the works)
        'descoperire',   # des-coper-ire (discovery)
    ]

    print("Romanian Morphological Analysis:")
    print("-" * 50)
    for word in test_words:
        morphemes = analyzer.decompose(word)
        print(f"\nWord: {word}")
        for morpheme, rule in morphemes:
            print(f"  {morpheme}: {rule.category} - {rule.meaning}")

if __name__ == "__main__":
    test_morpheme_analyzer()