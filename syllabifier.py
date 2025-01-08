import re
from typing import List

class RomanianSyllabifier:
    def __init__(self):
        # Define Romanian vowels (including special characters)
        self.vowels = set('aăâeioîuү')
        
        # Define Romanian consonants
        self.consonants = set('bcdfghjklmnpqrsștțvwxz')
        
        # Romanian diphthongs
        self.diphthongs = {
            'ea', 'eo', 'eu', 'ia', 'ie', 'ii', 'io', 'iu',
            'îi', 'oa', 'ua', 'uă', 'ue', 'ui', 'uo'
        }
        
        # Romanian triphthongs
        self.triphthongs = {
            'eai', 'eau', 'iai', 'iau', 'iei', 'ioa', 'oai'
        }
        
        # Romanian consonant clusters that shouldn't be split
        self.consonant_clusters = {
            'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr',
            'pl', 'pr', 'sc', 'sk', 'sl', 'sm', 'sn', 'sp', 'st',
            'șt', 'tr', 'vr', 'zl', 'zn', 'zv'
        }

    def is_vowel(self, char: str) -> bool:
        """Check if a character is a Romanian vowel."""
        return char.lower() in self.vowels

    def is_diphthong(self, chars: str) -> bool:
        """Check if a sequence of characters forms a Romanian diphthong."""
        return chars.lower() in self.diphthongs

    def is_triphthong(self, chars: str) -> bool:
        """Check if a sequence of characters forms a Romanian triphthong."""
        return chars.lower() in self.triphthongs

    def find_syllable_boundaries(self, word: str) -> List[str]:
        """Split a word into syllables using Romanian syllabification rules."""
        word = word.lower()
        syllables = []
        current_syllable = ""
        i = 0
        
        while i < len(word):
            current_syllable += word[i]
            
            # Check for triphthongs
            if (i + 2 < len(word) and 
                word[i:i+3] in self.triphthongs):
                current_syllable += word[i+1] + word[i+2]
                i += 2
                syllables.append(current_syllable)
                current_syllable = ""
                i += 1
                continue
            
            # Check for diphthongs
            if (i + 1 < len(word) and 
                word[i:i+2] in self.diphthongs):
                current_syllable += word[i+1]
                i += 1
                syllables.append(current_syllable)
                current_syllable = ""
                i += 1
                continue
            
            # If we're not at the end of the word
            if i + 1 < len(word):
                # VCV pattern
                if (self.is_vowel(word[i]) and 
                    not self.is_vowel(word[i + 1]) and 
                    i + 2 < len(word) and 
                    self.is_vowel(word[i + 2])):
                    syllables.append(current_syllable)
                    current_syllable = ""
                
                # VCCV pattern
                elif (self.is_vowel(word[i]) and 
                      not self.is_vowel(word[i + 1]) and 
                      i + 2 < len(word) and 
                      not self.is_vowel(word[i + 2])):
                    if (i + 2 < len(word) and 
                        word[i + 1:i + 3] in self.consonant_clusters):
                        syllables.append(current_syllable)
                        current_syllable = ""
                    elif i + 2 < len(word):
                        current_syllable += word[i + 1]
                        syllables.append(current_syllable)
                        current_syllable = ""
                        i += 1
            
            i += 1
        
        # Add any remaining letters to the final syllable
        if current_syllable:
            syllables.append(current_syllable)
        
        return syllables

    def syllabify(self, word: str) -> str:
        """Return the word with syllables separated by hyphens."""
        return '-'.join(self.find_syllable_boundaries(word))


def test_romanian_syllabifier():
    syllabifier = RomanianSyllabifier()
    test_words = [
        'familie',    # fa-mi-li-e
        'școală',     # școa-lă
        'frumos',     # fru-mos
        'copil',      # co-pil
        'băiat',      # bă-iat
        'împreună',   # îm-pre-u-nă
        'european',   # eu-ro-pe-an
        'automat',    # au-to-mat
        'iarnă',      # iar-nă
        'România'     # Ro-mâ-ni-a
    ]
    
    print("Romanian Syllabification Examples:")
    print("-" * 40)
    for word in test_words:
        syllabified = syllabifier.syllabify(word)
        print(f"{word}: {syllabified}")


if __name__ == "__main__":
    test_romanian_syllabifier()