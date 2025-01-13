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
            'supra': MorphemeRule('prefix', 'above', {'supra'}),
            'ante': MorphemeRule('prefix', 'before', {'ante'}),
            'post': MorphemeRule('prefix', 'after', {'post'}),
            'pseudo': MorphemeRule('prefix', 'fake', {'pseudo'}),
            'sin': MorphemeRule('prefix', 'together', {'sin','sim'})
        }

        self.noun_suffixes: Dict[str, MorphemeRule] = {
            'tor': MorphemeRule('suffix', 'agent', {'tor', 'toare'}),
            'ție': MorphemeRule('suffix', 'action/result', {'ție', 'ții'}),
            'ime': MorphemeRule('suffix', 'collective', {'ime'}),
            'iță': MorphemeRule('suffix', 'diminutive', {'iță'}),
            'tură': MorphemeRule('suffix', 'action result', {'tură'}),
            're': MorphemeRule('suffix', 'action result, long infinitive', {'re'}),
            'ie':MorphemeRule('suffix', 'action result', {'ie, iune'}),
            'ar':MorphemeRule('suffix', 'action taker/object of action', {'ar, ară'})
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
            'ul': MorphemeRule('ending', 'def.masc.sg', {'ul', 'l', 'u'}),
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
    
    def _remove_duplicates(self, decompositions: List[List[Tuple[str, MorphemeRule]]]) -> List[List[Tuple[str, MorphemeRule]]]:
        seen = set()
        unique_decompositions = []
        
        for decomp in decompositions:
            # Create a string representation of the decomposition
            decomp_str = str([(morpheme, rule.category, rule.meaning, rule.allomorphs) 
                            for morpheme, rule in decomp])
            
            if decomp_str not in seen:
                seen.add(decomp_str)
                unique_decompositions.append(decomp)
        
        return unique_decompositions
        
    def _find_prefix_matches(self, word: str) -> List[Tuple[List[Tuple[str, MorphemeRule]], str]]:
        """
        Find all possible prefix matches starting from the beginning of the word.
        Returns a list of tuples containing:
        - List of (morpheme, rule) pairs that were matched
        - Remaining word after removing those morphemes
        """
        matches = []
        # Try to find matches at the beginning
        for prefix, rule in self.prefixes.items():
            for allomorph in rule.allomorphs:
                if word.startswith(allomorph):
                    remaining = word[len(allomorph):]
                    # Recursively find other possible prefix matches
                    next_matches = self._find_prefix_matches_from_start(remaining)
                    
                    # Add current match to each possible combination
                    current_match = [(allomorph, rule)]
                    if next_matches:
                        for next_match_list, next_remaining in next_matches:
                            matches.append((current_match + next_match_list, next_remaining))
                    # Also add the current match alone as a possibility
                    matches.append((current_match, remaining))
        
        return matches if matches else [([], word)]
    
    def _find_suffix_matches(self, word: str, suffix_dict: Dict[str, MorphemeRule]) -> List[Tuple[List[Tuple[str, MorphemeRule]], str]]:
        """
        Find all possible suffix matches starting from the end of the word.
        Returns a list of tuples containing:
        - List of (morpheme, rule) pairs that were matched
        - Remaining word after removing those morphemes
        """
        matches = []
        # First try to find matches at the very end
        for suffix, rule in suffix_dict.items():
            for allomorph in rule.allomorphs:
                if word.endswith(allomorph):
                    remaining = word[:-len(allomorph)]
                    # Recursively find other possible matches from the same category
                    next_matches = self._find_suffix_matches(remaining, suffix_dict)
                    
                    # Add current match to each possible combination
                    current_match = [(allomorph, rule)]
                    if next_matches:
                        for next_match_list, next_remaining in next_matches:
                            matches.append((current_match + next_match_list, next_remaining))
                    # Also add the current match alone as a possibility
                    matches.append((current_match, remaining))
        
        return matches if matches else [([], word)]
    
    def decompose(self, word: str, pos: str) -> List[List[Tuple[str, MorphemeRule]]]:
        """
        Decompose a word into all possible morpheme combinations based on part of speech.
        Args:
            word: The word to decompose
            pos: Part of speech ('n' for noun, 'v' for verb)
        Returns:
            List of possible decompositions, where each decomposition is a list of (morpheme, rule) pairs
        """
        word = word.lower()
        all_decompositions = []

        # Step 1: Find all possible prefix combinations for both nouns and verbs
        prefix_results = self._find_prefix_matches(word)
        
        # Step 2: Process each prefix possibility
        for prefix_morphemes, after_prefixes in prefix_results:
            
            if pos == 'n':
                # Noun morphology: noun_suffixes -> plural_suffixes -> noun_endings
                
                # Start with rightmost morphemes (noun endings)
                ending_results = self._find_suffix_matches(after_prefixes, self.noun_endings)
                
                for ending_morphemes, after_endings in ending_results:
                    # Look for plural suffixes in what remains after removing endings
                    plural_results = self._find_suffix_matches(after_endings, self.plural_suffixes)
                    
                    for plural_morphemes, after_plurals in plural_results:
                        # Look for noun suffixes in what remains after removing plural markers
                        noun_suffix_results = self._find_suffix_matches(after_plurals, self.noun_suffixes)
                        
                        for noun_suffix_morphemes, remaining in noun_suffix_results:
                            # What remains after removing all suffixes must be the root
                            if remaining:
                                root_morpheme = [(remaining, MorphemeRule('root', 'root', {remaining}))]
                                
                                # Combine all morphemes in correct order:
                                # prefixes + root + noun_suffixes + plural_suffixes + endings
                                decomposition = (prefix_morphemes + 
                                            root_morpheme + 
                                            noun_suffix_morphemes +
                                            plural_morphemes + 
                                            ending_morphemes)
                                
                                all_decompositions.append(decomposition)
            
            elif pos == 'v':
                # Verb morphology: simpler, just prefixes -> root -> verb_suffixes
                
                # Look for verb suffixes
                verb_suffix_results = self._find_suffix_matches(after_prefixes, self.verb_suffixes)
                
                for verb_suffix_morphemes, remaining in verb_suffix_results:
                    # What remains after removing suffixes must be the root
                    if remaining:
                        root_morpheme = [(remaining, MorphemeRule('root', 'root', {remaining}))]
                        
                        # Combine morphemes in order:
                        # prefixes + root + verb_suffixes
                        decomposition = (prefix_morphemes +
                                    root_morpheme +
                                    verb_suffix_morphemes)
                        
                        all_decompositions.append(decomposition)
            
            else:
                raise ValueError(f"Unsupported part of speech: {pos}. Use 'n' for nouns or 'v' for verbs.")
        
        if not all_decompositions:
            # If no decompositions were found, treat the entire word as a root
            root_morpheme = [(word, MorphemeRule('root', 'root', {word}))]
            all_decompositions.append(root_morpheme)

        all_decompositions = self._remove_duplicates(all_decompositions)
        return all_decompositions
   
def test_morpheme_analyzer():
    analyzer = RomanianMorphemeFST()
    test_words = [
        ('lucrător', 'n'),      # lucr-ător (worker)
        ('nelucrând', 'v'),     # ne-lucr-ând (not working)
        ('făcător', 'n'),       # făc-ător (maker)
        ('scriitor', 'n'),      # scri-itor (writer)
        ('citește', 'v'),       # cit-ește (reads)
        ('prefăcut', 'v'),      # pre-făc-ut (pretended)
        ('lucrările', 'n'),     # lucr-ăr-i-le (the works)
        ('descoperire', 'n'),   # des-coper-ire (discovery)
    ]

    print("Romanian Morphological Analysis:")
    print("-" * 50)
    for word, pos in test_words:
        decompositions = analyzer.decompose(word, pos)
        print(f"\nWord: {word}")
        for i, decomposition in enumerate(decompositions, 1):
            print(f"Decomposition {i}:")
            for morpheme, rule in decomposition:
                print(f"  {morpheme}: {rule.category} - {rule.meaning}")

def run_morpheme_analyzer():
    analyzer = RomanianMorphemeFST()
    word = input("Enter the word you want to analyze: ")
    pos = input("What part of speech is the word you entered? (n/v): ")
    
    decompositions = analyzer.decompose(word, pos)
    
    print(f"\nPossible decompositions for '{word}':")
    for i, decomposition in enumerate(decompositions, 1):
        print(f"\nDecomposition {i}:")
        for morpheme, rule in decomposition:
            print(f"  {morpheme}: {rule.category} - {rule.meaning}")

if __name__ == "__main__":
    run_morpheme_analyzer()