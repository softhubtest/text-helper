"""
Streaming Loader for Huge Dictionary
Uses ijson to load 1GB+ JSON files without memory crash.
"""
import ijson
import os

class StreamingDictionaryLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.words = [] # Keep top frequent words in memory
        self.total_count = 0
        
    def load(self, max_memory_words=500000):
        print(f"[STREAM] Sozluk araniyor: {self.filepath}")
        if not os.path.exists(self.filepath):
            print("[STREAM] Dosya yok.")
            return []
            
        print("[STREAM] Yukleme basladi (Streaming)...")
        # ijson ile streaming okuma
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                # 'words.item' -> words arrayindeki her bir item
                objects = ijson.items(f, 'words.item')
                
                count = 0
                for word in objects:
                    count += 1
                    if count <= max_memory_words:
                        self.words.append(word)
                
                self.total_count = count
                print(f"[STREAM] Yukleme bitti. Hafizaya alinan: {len(self.words)} / Toplam: {self.total_count}")
                return self.words
        except Exception as e:
            print(f"[STREAM] Hata: {e}")
            return []

if __name__ == "__main__":
    # Test
    loader = StreamingDictionaryLoader(os.path.join("improvements", "turkish_dictionary.json"))
    loader.load()
