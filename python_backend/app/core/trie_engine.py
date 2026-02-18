"""
Trie (Prefix Tree) Engine - Ultra hızlı prefix arama.
iPhone/WhatsApp benzeri: O(prefix) arama, linear scan yok.
"""

from typing import List, Dict, Optional


class TrieNode:
    """Trie düğümü."""

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end = False
        self.words: List[str] = []
        self.frequency = 0


class TrieEngine:
    """Trie tabanlı prefix arama - büyük sözlükte milisaniye altı his."""

    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word: str, frequency: int = 1) -> None:
        word_lower = word.lower().strip()
        if not word_lower:
            return
        node = self.root
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
        """Prefix ile arama - O(prefix + k) where k = sonuç sayısı."""
        if not prefix:
            return []
        prefix_lower = prefix.lower().strip()
        node = self.root
        for char in prefix_lower:
            if char not in node.children:
                return []
            node = node.children[char]
        results: List[Dict] = []
        self._collect(node, prefix_lower, results, max_results * 3)
        # Frekans ve prefix uzunluğuna göre skor (yaygın kelimeler önce)
        for r in results:
            w = r.get("word", "")
            pre_len = len(prefix_lower)
            ratio = (pre_len / len(w)) if w else 0
            freq = r.get("frequency", 0)
            r["score"] = (ratio * 10.0) + (freq / 100.0)
        results.sort(key=lambda x: (-x.get("score", 0), -x.get("frequency", 0)))
        return results[:max_results]

    def _collect(
        self,
        node: TrieNode,
        prefix: str,
        results: List[Dict],
        limit: int,
    ) -> None:
        if len(results) >= limit:
            return
        if node.is_end:
            for word in node.words:
                if len(results) >= limit:
                    return
                results.append({
                    "word": word,
                    "frequency": node.frequency,
                    "source": "trie",
                })
        for _, child in sorted(node.children.items()):
            if len(results) >= limit:
                return
            self._collect(child, prefix, results, limit)

    def build_from_frequency_dict(self, freq_dict: Dict[str, int]) -> None:
        """frequency_dict (word -> count) ile Trie oluştur."""
        self.root = TrieNode()
        self.word_count = 0
        for word, count in freq_dict.items():
            self.insert(word, count)
        print(f"[Trie] Ready: {self.word_count:,} words (prefix search < ~50 ms target)")

    def get_stats(self) -> Dict:
        def count_nodes(n: TrieNode) -> int:
            return 1 + sum(count_nodes(c) for c in n.children.values())
        return {
            "word_count": self.word_count,
            "node_count": count_nodes(self.root),
        }
