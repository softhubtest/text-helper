import json
import os
from collections import defaultdict, Counter
from typing import Dict, List, Tuple

NGRAM_DATA_PATH = "data/user_ngrams.json"

class NgramEngine:
    def __init__(self, path: str = NGRAM_DATA_PATH):
        self.path = path
        # bigrams: maps 'word1' -> Counter({'word2': count, 'word3': count})
        self.bigrams: Dict[str, Counter] = defaultdict(Counter)
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Convert dict to defaultdict(Counter)
                    for key, val in data.items():
                        self.bigrams[key] = Counter(val)
                print(f"[NgramEngine] Loaded patterns for {len(self.bigrams)} context words.")
            except Exception as e:
                print(f"[NgramEngine] Error loading n-grams: {e}")
        else:
            self.bigrams = defaultdict(Counter)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.bigrams, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[NgramEngine] Error saving n-grams: {e}")

    def learn_sequence(self, sentence: str):
        """Learns bigrams from a finished sentence."""
        words = sentence.strip().split()
        if len(words) < 2:
            return

        # Simple Bigram Learning
        # "merhaba nasılsın" -> bigrams["merhaba"]["nasılsın"] += 1
        for i in range(len(words) - 1):
            w1 = words[i].lower()
            w2 = words[i+1].lower()
            self.bigrams[w1][w2] += 1
        
        self.save()

    def predict_next(self, current_word: str, limit: int = 3) -> List[Tuple[str, int]]:
        """Predicts likely next words based on the current word."""
        current_word = current_word.lower()
        if current_word in self.bigrams:
            # Returns [('nasılsın', 5), ('günaydın', 2)]
            return self.bigrams[current_word].most_common(limit)
        return []
