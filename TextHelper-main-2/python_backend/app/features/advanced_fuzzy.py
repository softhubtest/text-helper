"""
Gelişmiş Fuzzy Matching
- Phonetic matching (ses benzerliği)
- Türkçe karakter varyasyonları
- Klavye yakınlığı
- Multi-algorithm fusion
"""

import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher

class AdvancedFuzzyMatcher:
    """Gelişmiş fuzzy matching - çoklu algoritma"""
    
    def __init__(self):
        # Türkçe karakter mapping
        self.turkish_char_map = {
            'ı': ['i', 'ı'],
            'i': ['ı', 'i'],
            'ş': ['s', 'ş'],
            's': ['ş', 's'],
            'ğ': ['g', 'ğ'],
            'g': ['ğ', 'g'],
            'ü': ['u', 'ü'],
            'u': ['ü', 'u'],
            'ö': ['o', 'ö'],
            'o': ['ö', 'o'],
            'ç': ['c', 'ç'],
            'c': ['ç', 'c']
        }
        
        # Klavye yakınlık matrisi (QWERTY Türkçe)
        self.keyboard_proximity = {
            'q': ['a', 'w'],
            'w': ['q', 'e', 's', 'a'],
            'e': ['w', 'r', 'd', 's'],
            'r': ['e', 't', 'f', 'd'],
            't': ['r', 'y', 'g', 'f'],
            'y': ['t', 'u', 'h', 'g'],
            'u': ['y', 'ı', 'j', 'h'],
            'ı': ['u', 'i', 'k', 'j'],
            'i': ['ı', 'o', 'l', 'k'],
            'o': ['i', 'p', 'ş', 'l'],
            'p': ['o', 'ğ', 'ü', 'ş'],
            'ğ': ['p', 'ü'],
            'ü': ['ğ', 'ö', 'ç', 'ş'],
            'a': ['q', 's', 'w'],
            's': ['a', 'd', 'w', 'e'],
            'd': ['s', 'f', 'e', 'r'],
            'f': ['d', 'g', 'r', 't'],
            'g': ['f', 'h', 't', 'y'],
            'h': ['g', 'j', 'y', 'u'],
            'j': ['h', 'k', 'u', 'ı'],
            'k': ['j', 'l', 'ı', 'i'],
            'l': ['k', 'ş', 'i', 'o'],
            'ş': ['l', 'ü', 'o', 'p'],
            'z': ['x'],
            'x': ['z', 'c'],
            'c': ['x', 'v', 'ç'],
            'ç': ['c', 'v', 'ö'],
            'v': ['c', 'b', 'ç'],
            'b': ['v', 'n'],
            'n': ['b', 'm'],
            'm': ['n', 'ö'],
            'ö': ['m', 'ç', 'ü']
        }
    
    def phonetic_similarity(self, word1: str, word2: str) -> float:
        """Ses benzerliği hesapla"""
        # Basit phonetic matching
        # Türkçe için ses benzerliği kuralları
        word1_clean = word1.lower().replace('h', '').replace('ğ', 'g')
        word2_clean = word2.lower().replace('h', '').replace('ğ', 'g')
        
        # Vowel similarity
        vowels1 = re.sub(r'[^aeıioöuü]', '', word1_clean)
        vowels2 = re.sub(r'[^aeıioöuü]', '', word2_clean)
        
        if not vowels1 or not vowels2:
            return 0.0
        
        similarity = SequenceMatcher(None, vowels1, vowels2).ratio()
        return similarity
    
    def turkish_char_variations(self, word: str) -> List[str]:
        """Türkçe karakter varyasyonlarını üret"""
        variations = [word]
        
        for char, alternatives in self.turkish_char_map.items():
            if char in word.lower():
                for alt in alternatives:
                    if alt != char:
                        variant = word.lower().replace(char, alt)
                        if variant not in variations:
                            variations.append(variant)
        
        return variations
    
    def keyboard_proximity_score(self, word1: str, word2: str) -> float:
        """Klavye yakınlığı skoru"""
        if len(word1) != len(word2):
            return 0.0
        
        score = 0.0
        for i, (c1, c2) in enumerate(zip(word1.lower(), word2.lower())):
            if c1 == c2:
                score += 1.0
            elif c1 in self.keyboard_proximity and c2 in self.keyboard_proximity[c1]:
                score += 0.7
            elif c2 in self.keyboard_proximity and c1 in self.keyboard_proximity[c2]:
                score += 0.7
        
        return score / len(word1) if word1 else 0.0
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Levenshtein distance hesapla"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def jaro_winkler_similarity(self, s1: str, s2: str) -> float:
        """Jaro-Winkler similarity"""
        if s1 == s2:
            return 1.0
        
        # Jaro similarity
        match_window = max(len(s1), len(s2)) // 2 - 1
        if match_window < 0:
            match_window = 0
        
        s1_matches = [False] * len(s1)
        s2_matches = [False] * len(s2)
        
        matches = 0
        transpositions = 0
        
        for i in range(len(s1)):
            start = max(0, i - match_window)
            end = min(i + match_window + 1, len(s2))
            
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break
        
        if matches == 0:
            return 0.0
        
        k = 0
        for i in range(len(s1)):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
        
        jaro = (matches / len(s1) + matches / len(s2) + (matches - transpositions / 2) / matches) / 3.0
        
        # Winkler modification
        prefix = 0
        for i in range(min(len(s1), len(s2), 4)):
            if s1[i] == s2[i]:
                prefix += 1
            else:
                break
        
        winkler = jaro + (0.1 * prefix * (1 - jaro))
        return winkler
    
    def match(self, word: str, candidates: List[str], max_results: int = 10) -> List[Dict]:
        """Fuzzy matching yap"""
        results = []
        word_lower = word.lower()
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            
            # 1. Exact match
            if word_lower == candidate_lower:
                results.append({
                    'word': candidate,
                    'score': 10.0,
                    'method': 'exact',
                    'confidence': 1.0
                })
                continue
            
            # 2. Levenshtein distance
            lev_dist = self.levenshtein_distance(word_lower, candidate_lower)
            max_len = max(len(word_lower), len(candidate_lower))
            lev_score = 1.0 - (lev_dist / max_len) if max_len > 0 else 0.0
            
            # 3. Jaro-Winkler similarity
            jaro_score = self.jaro_winkler_similarity(word_lower, candidate_lower)
            
            # 4. Phonetic similarity
            phonetic_score = self.phonetic_similarity(word_lower, candidate_lower)
            
            # 5. Keyboard proximity
            keyboard_score = self.keyboard_proximity_score(word_lower, candidate_lower)
            
            # 6. Turkish character variations
            turkish_bonus = 0.0
            variations = self.turkish_char_variations(word_lower)
            if candidate_lower in variations:
                turkish_bonus = 0.3
            
            # Combined score (weighted)
            # Combined score (weighted)
            # Tuning: Increase phonetic weight for better "sounds like" matching (mrb -> merhaba)
            combined_score = (
                lev_score * 0.25 +
                jaro_score * 0.25 +
                phonetic_score * 0.30 + # Increased from 0.20
                keyboard_score * 0.15 +
                turkish_bonus
            )
            
            # Abbreviation Bonus (e.g. mrb -> merhaba)
            # If word is short (len<=4) and candidate contains all chars in order
            if len(word_lower) <= 4 and len(candidate_lower) > len(word_lower):
                is_abbrev = True
                last_idx = -1
                for char in word_lower:
                    idx = candidate_lower.find(char, last_idx + 1)
                    if idx == -1:
                        is_abbrev = False
                        break
                    last_idx = idx
                
                if is_abbrev:
                    combined_score += 0.2 # Significant bonus
            
            # Normalize to 0-10 range
            final_score = combined_score * 10.0
            
            if final_score > 0.3:  # Threshold
                results.append({
                    'word': candidate,
                    'score': final_score,
                    'method': 'fuzzy',
                    'confidence': combined_score,
                    'levenshtein': lev_score,
                    'jaro': jaro_score,
                    'phonetic': phonetic_score,
                    'keyboard': keyboard_score
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def correct_typo(self, word: str, dictionary: List[str]) -> str:
        """Yazım hatasını düzelt"""
        matches = self.match(word, dictionary, max_results=1)
        if matches and matches[0]['confidence'] > 0.7:
            return matches[0]['word']
        return word

# Global instance
advanced_fuzzy = AdvancedFuzzyMatcher()
