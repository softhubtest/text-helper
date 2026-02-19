import json
import os
from collections import Counter
from typing import Dict, List, Optional

USER_DICT_PATH = "data/user_dictionary.json"

class UserDictionary:
    def __init__(self, path: str = USER_DICT_PATH):
        self.path = path
        self.frequencies: Counter = Counter()
        self.load()

    def load(self):
        """Loads the user dictionary from disk."""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.frequencies = Counter(data)
                print(f"[UserDictionary] Loaded {len(self.frequencies)} custom words.")
            except Exception as e:
                print(f"[UserDictionary] Error loading dictionary: {e}")
                self.frequencies = Counter()
        else:
            print("[UserDictionary] No existing user dictionary found. Starting fresh.")
            self.frequencies = Counter()

    def save(self):
        """Saves the user dictionary to disk."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.frequencies, f, ensure_ascii=False, indent=2)
            # print("[UserDictionary] Saved successfully.") 
        except Exception as e:
            print(f"[UserDictionary] Error saving dictionary: {e}")

    def add_word(self, word: str):
        """Adds a word to the user dictionary or increments its count."""
        if not word or not word.strip():
            return
        
        word = word.lower().strip()
        self.frequencies[word] += 1
        self.save() # Auto-save on learn. In high-traffic, might want to batch this.

    def get_frequency(self, word: str) -> int:
        return self.frequencies.get(word.lower(), 0)

    def get_top_phrases(self, prefix: str, limit: int = 5) -> List[str]:
        """Returns top user words starting with prefix."""
        prefix = prefix.lower()
        matches = [
            (word, freq) for word, freq in self.frequencies.items() 
            if word.startswith(prefix)
        ]
        # Sort by frequency desc
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:limit]]
