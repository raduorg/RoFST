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
            'tură': MorphemeRule('suffix', 'action result', {'tură'})
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
        self.noun_endings: Dict[str, MorphemeRule] = {
            'ul': MorphemeRule('ending', 'def.masc.sg', {'ul', 'l'}),
            'a': MorphemeRule('ending', 'def.fem.sg', {'a'}),
            'lui': MorphemeRule('ending', 'gen/dat.masc.sg', {'lui'}),
            'ei': MorphemeRule('ending', 'gen/dat.fem.sg', {'ei'}),
            'lor': MorphemeRule('ending', 'gen/dat.fem.pl', {'lor'}),
        }

    def decompose(self, word: str, pos: str) -> List[Tuple[str, MorphemeRule]]:
        """
        Decompose a word into its morphemes based on its part of speech.
        Args:
            word: The word to decompose
            pos: Part of speech ('n' for noun, 'v' for verb)
        Returns:
            List of (morpheme, rule) tuples
        """
        word = word.lower()
        morphemes = []
        remaining = word

        # Check for prefixes (applies to all POS)
        for prefix, rule in self.prefixes.items():
            if any(remaining.startswith(allomorph) for allomorph in rule.allomorphs):
                for allomorph in rule.allomorphs:
                    if remaining.startswith(allomorph):
                        morphemes.append((allomorph, rule))
                        remaining = remaining[len(allomorph):]
                        break

        # Store potential root
        potential_root = remaining

        if pos == 'v':
            # Process verb suffixes
            for suffix, rule in self.verb_suffixes.items():
                if any(remaining.endswith(allomorph) for allomorph in rule.allomorphs):
                    for allomorph in rule.allomorphs:
                        if remaining.endswith(allomorph):
                            morphemes.append((allomorph, rule))
                            remaining = remaining[:-len(allomorph)]
                            potential_root = remaining
                            break

        elif pos == 'n':
            # Process noun suffixes
            for suffix, rule in self.noun_suffixes.items():
                if any(remaining.endswith(allomorph) for allomorph in rule.allomorphs):
                    for allomorph in rule.allomorphs:
                        if remaining.endswith(allomorph):
                            morphemes.append((allomorph, rule))
                            remaining = remaining[:-len(allomorph)]
                            potential_root = remaining
                            break

            # Process plural suffixes
            for suffix, rule in self.plural_suffixes.items():
                if any(remaining.endswith(allomorph) for allomorph in rule.allomorphs):
                    for allomorph in rule.allomorphs:
                        if remaining.endswith(allomorph):
                            morphemes.append((allomorph, rule))
                            remaining = remaining[:-len(allomorph)]
                            potential_root = remaining
                            break

            # Process endings
            for ending, rule in self.noun_endings.items():
                if any(remaining.endswith(allomorph) for allomorph in rule.allomorphs):
                    for allomorph in rule.allomorphs:
                        if remaining.endswith(allomorph):
                            morphemes.append((allomorph, rule))
                            remaining = remaining[:-len(allomorph)]
                            potential_root = remaining
                            break

        # Add the remaining part as root
        if potential_root:
            root_rule = MorphemeRule('root', 'root', {potential_root})
            morphemes.insert(1, (potential_root, root_rule))

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

def run_morpheme_analyzer():
    analyzer = RomanianMorphemeFST()
    word = input("Enter the word you want to analyze:")
    pos = input("what part of speech is the word you entered?(n/v)")
    morphemes = analyzer.decompose(word, pos)
    for morpheme, rule in morphemes:
        print(f"  {morpheme}: {rule.category} - {rule.meaning}")

if __name__ == "__main__":
    run_morpheme_analyzer()