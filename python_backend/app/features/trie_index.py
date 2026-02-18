"""
Trie (Prefix Tree) Index - Ultra Hızlı Arama
Performans iyileştirme için prefix tree veri yapısı.
iPhone benzeri: yaygın kelimeler önce sıralanır.
"""

from typing import List, Dict, Optional, Set
from collections import defaultdict

try:
    from app.features.common_words import is_common
    _trie_common_available = True
except ImportError:
    _trie_common_available = False
    is_common = lambda w: False

class TrieNode:
    """Trie node"""
    
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.words = []  # Bu node'da biten kelimeler
        self.frequency = 0

class TrieIndex:
    """Trie (Prefix Tree) index - çok hızlı prefix arama"""
    
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
    
    def insert(self, word: str, frequency: int = 1):
        """Kelime ekle"""
        node = self.root
        word_lower = word.lower()
        
        for char in word_lower:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end = True
        if word not in node.words:
            node.words.append(word)
        node.frequency = max(node.frequency, frequency)
        self.word_count += 1
    
    def search(self, prefix: str, max_results: int = 120) -> List[Dict]:
        """Prefix ile arama - WHATSAPP BENZERİ (çok hızlı, her karakter için)"""
        if not prefix:
            return []
        
        prefix_lower = prefix.lower().strip()
        node = self.root
        
        # WHATSAPP BENZERİ: Prefix'e kadar git (her karakter için)
        for char in prefix_lower:
            if char not in node.children:
                return []  # Prefix bulunamadı
            node = node.children[char]
        
        # WHATSAPP BENZERİ: Bu node'dan başlayarak tüm kelimeleri topla
        results = []
        self._collect_words(node, prefix_lower, results, max_results * 3)
        
        # Frekans ve prefix uzunluğuna göre skor
        for result in results:
            word = result.get('word', '')
            prefix_ratio = len(prefix_lower) / len(word) if word else 0
            frequency = result.get('frequency', 0)
            result['score'] = (prefix_ratio * 10.0) + (frequency / 100)
        
        # iPhone benzeri: önce yaygın kelimeler, sonra skora göre
        def _trie_sort_key(r):
            w = (r.get('word') or '').strip()
            common_first = 0 if (_trie_common_available and w and ' ' not in w and is_common(w)) else 1
            return (common_first, -r.get('score', 0))
        results.sort(key=_trie_sort_key)
        return results[:max_results]
    
    def _collect_words(self, node: TrieNode, prefix: str, results: List[Dict], max_results: int):
        """Node'dan tüm kelimeleri topla - WHATSAPP BENZERİ (DFS, hızlı)"""
        if len(results) >= max_results:
            return
        
        # WHATSAPP BENZERİ: Bu node'da biten kelimeler (öncelikli)
        if node.is_end:
            for word in node.words:
                if len(results) >= max_results:
                    return
                
                # WHATSAPP BENZERİ: Skor - prefix uzunluğu ve frekans önemli
                prefix_ratio = len(prefix) / len(word) if word else 0
                score = (prefix_ratio * 10.0) + (node.frequency / 50)
                
                results.append({
                    'word': word,
                    'score': score,
                    'frequency': node.frequency,
                    'type': 'dictionary',
                    'description': f'Sözlük (frekans: {node.frequency})',
                    'source': 'trie_index'
                })
        
        # WHATSAPP BENZERİ: Çocuk node'ları ziyaret et (alfabetik sıra - hızlı)
        for char, child_node in sorted(node.children.items()):
            if len(results) >= max_results:
                return
            self._collect_words(child_node, prefix + char, results, max_results)
    
    def build_from_words(self, words: List[str], frequencies: Optional[Dict[str, int]] = None):
        """Kelime listesinden Trie oluştur"""
        self.root = TrieNode()
        self.word_count = 0
        
        frequencies = frequencies or {}
        
        print(f"[INFO] Trie index oluşturuluyor: {len(words):,} kelime...")
        
        for word in words:
            frequency = frequencies.get(word.lower(), 1)
            self.insert(word, frequency)
        
        print(f"[OK] Trie index hazır: {self.word_count:,} kelime")
    
    def get_stats(self) -> Dict:
        """Trie istatistikleri"""
        def count_nodes(node: TrieNode) -> int:
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        
        return {
            'word_count': self.word_count,
            'node_count': count_nodes(self.root),
            'memory_efficient': True
        }

# Global instance
trie_index = TrieIndex()
