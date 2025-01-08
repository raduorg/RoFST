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

        self.noun_suffixes: Dict[str, MorphemeRule] = {
            'tor': MorphemeRule('suffix', 'agent', {'tor', 'toare'}),
            'ție': MorphemeRule('suffix', 'action/result', {'ție', 'ții'}),
            'ime': MorphemeRule('suffix', 'collective', {'ime'}),
            'iță': MorphemeRule('suffix', 'diminutive', {'iță'}),
            'tură': MorphemeRule('suffix', 'action result', {'tură'}),
            're': MorphemeRule('suffix', 'action result, long infinitive', {'re'})
        }

        self.verb_suffixes: Dict[str, MorphemeRule] = {
            'esc': MorphemeRule('suffix', 'present.1sg', {'esc'}),
            'ează': MorphemeRule('suffix', 'present.3sg', {'ează'}),
            'at': MorphemeRule('suffix', 'participle', {'at', 't'}),
            'ând': MorphemeRule('suffix', 'gerund', {'ând', 'ind'}),
        }

        self.plural_suffixes: Dict[str, MorphemeRule] = {
            'i': MorphemeRule('suffix', 'plural', {'i'}),
            'uri': MorphemeRule('suffix', 'plural', {'uri'}),
            'e': MorphemeRule('suffix', 'plural', {'e'})
        }

        # Gender and case endings
        self.noun_endings: Dict[str, MorphemeRule] = {
            'ul': MorphemeRule('ending', 'def.masc.sg', {'ul', 'l'}),
            'a': MorphemeRule('ending', 'def.fem.sg', {'a'}),
            'lui': MorphemeRule('ending', 'gen/dat.masc.sg', {'lui'}),
            'ei': MorphemeRule('ending', 'gen/dat.fem.sg', {'ei'}),
            'lor': MorphemeRule('ending', 'gen/dat.pl', {'lor'}),
        }
    def _get_morpheme_order(self, morpheme_tuple: Tuple[str, MorphemeRule]) -> int:
        """Helper method to determine morpheme order for sorting"""
        category = morpheme_tuple[1].category
        if category == 'prefix':
            return 0
        elif category == 'root':
            return 1
        elif category == 'suffix':
            return 2
        elif category == 'ending':
            return 3
        return 4  # fallback for unknown categories

    def _find_prefixes(self, word: str) -> Tuple[List[Tuple[str, MorphemeRule]], str]:
        """
        Recursively find all prefixes in a word.
        Returns tuple of (prefix_matches, remaining_word)
        """
        for prefix, rule in self.prefixes.items():
            if any(word.startswith(allomorph) for allomorph in rule.allomorphs):
                for allomorph in rule.allomorphs:
                    if word.startswith(allomorph):
                        # Recursive call with remaining word
                        next_matches, remaining = self._find_prefixes(word[len(allomorph):])
                        return [(allomorph, rule)] + next_matches, remaining
        return [], word

    def _find_suffix_matches(self, word: str, suffix_dict: Dict[str, MorphemeRule]) -> List[Tuple[str, MorphemeRule, int]]:
        """Helper to find all suffix matches with their positions"""
        matches = []
        for suffix, rule in suffix_dict.items():
            if any(word.endswith(allomorph) for allomorph in rule.allomorphs):
                for allomorph in rule.allomorphs:
                    if word.endswith(allomorph):
                        start_pos = len(word) - len(allomorph)
                        matches.append((allomorph, rule, start_pos))
        return matches

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
        # Find all prefixes recursively
        prefix_matches, remaining = self._find_prefixes(remaining)
        morphemes.extend(prefix_matches)
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

        if pos == 'n':
            '''
            Find all possible suffix matches. 
            In Romanian, we expect case endings to come last, then plural markers,
            and only then suffixes which are part of the noun in its Nominative-non-det. sg. form (like "tor" in "muncitor")
            '''
            matches = []
            matches.extend(self._find_suffix_matches(remaining, self.noun_endings))
            matches.extend(self._find_suffix_matches(remaining, self.plural_suffixes))
            matches.extend(self._find_suffix_matches(remaining, self.noun_suffixes))
            print(f"all matches are: {matches}")
            # Sort by position from end. we are matching in reverse order (giving priority to longer suffixes)
            matches.sort(key=lambda x: x[2], reverse=True)

            # Apply non-overlapping matches
            used_positions = set()
            result = list(remaining)  # Convert to list for easier character replacement
            
            for allomorph, rule, start_pos in matches:
                end_pos = start_pos + len(allomorph)
                overlap = any(p in used_positions for p in range(start_pos, end_pos))
                
                print(f"Checking {allomorph} at pos {start_pos}-{end_pos}, overlap: {overlap}")
                
                if not overlap:
                    morphemes.append((allomorph, rule))
                    used_positions.update(range(start_pos, end_pos))
                    for i in range(start_pos, end_pos):
                        result[i] = ''
                    print(f"Applied {allomorph}, remaining: {''.join(result)}")
            
            # Rebuild remaining text removing empty positions
            remaining = ''.join(c for c in result if c)

            potential_root = remaining


        # Add the remaining part as root
        if potential_root:
            root_rule = MorphemeRule('root', 'root', {potential_root})
            morphemes.insert(1, (potential_root, root_rule))
        # Before returning, sort morphemes by category to make reading the output more intuitive
        morphemes.sort(key=self._get_morpheme_order)
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
        'lucrările',     # lucr-ăr-i-le (the works)
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