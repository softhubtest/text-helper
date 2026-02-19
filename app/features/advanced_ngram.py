"""
Gelişmiş N-Gram Modeli
2-gram, 3-gram, 4-gram tabanlı tahminler
"""

from typing import List, Dict, Tuple
from collections import defaultdict
import json
import os
from datetime import datetime

class AdvancedNGramModel:
    """Gelişmiş N-gram modeli - cümle tamamlama için"""
    
    def __init__(self):
        self.bigrams = defaultdict(int)    # 2-gram: "merhaba nasıl" -> count
        self.trigrams = defaultdict(int)    # 3-gram: "merhaba nasıl yardımcı" -> count
        self.quadgrams = defaultdict(int)   # 4-gram: "merhaba nasıl yardımcı olabilirim" -> count
        
        self.word_followers = defaultdict(lambda: defaultdict(int))  # word -> {next_word: count}
        self.phrase_completions = defaultdict(lambda: defaultdict(int))  # phrase -> {completion: count}
        
        self.load_data()
        self._build_from_dictionary()
        self._load_musteri_hizmetleri_phrases()
    
    def _build_from_dictionary(self):
        """Sözlükten N-gram'ları oluştur"""
        # Yaygın Türkçe cümleler ve ifadeler
        common_phrases = [
            # Selamlaşma
            "merhaba nasıl yardımcı olabilirim",
            "merhaba nasıl yardımcı olabiliriz",
            "merhaba size nasıl yardımcı olabilirim",
            "merhaba hoş geldiniz nasıl yardımcı olabilirim",
            
            # Yardım
            "nasıl yardımcı olabilirim",
            "nasıl yardımcı olabiliriz",
            "size nasıl yardımcı olabilirim",
            "size nasıl yardımcı olabiliriz",
            "sana nasıl yardımcı olabilirim",
            
            # Teşekkür
            "teşekkür ederim",
            "teşekkürler",
            "çok teşekkür ederim",
            "teşekkür ediyorum",
            
            # Sipariş
            "sipariş takibi yapabilirim",
            "sipariş durumunu kontrol edebilirim",
            "sipariş bilgilerinizi alabilirim",
            
            # Müşteri
            "müşteri hizmetleri",
            "müşteri desteği",
            "müşteri memnuniyeti",
            
            # Soru
            "nasıl yapabilirim",
            "nasıl yapabiliriz",
            "nasıl olabilirim",
            "nasıl olabiliriz",
            
            # Bilgi
            "bilgi alabilirim",
            "bilgi verebilirim",
            "detaylı bilgi",
            
            # Problem
            "sorun çözebilirim",
            "problem çözebilirim",
            "yardımcı olabilirim",
        ]
        
        # Her cümleyi N-gram'lara ayır
        for phrase in common_phrases:
            words = phrase.lower().split()
            self._add_ngrams(words)
    
    def _load_musteri_hizmetleri_phrases(self):
        """musteri_hizmetleri_sozluk.txt'den 500+ ifade yukle"""
        path = os.path.join(os.path.dirname(__file__), "musteri_hizmetleri_sozluk.txt")
        if not os.path.exists(path):
            return
        count = 0
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                words = line.lower().split()
                if len(words) >= 2:
                    self._add_ngrams(words)
                    count += 1
                elif len(words) == 1:
                    pass
        if count:
            print(f"[OK] N-gram: musteri hizmetleri {count} ifade eklendi")
    
    def _add_ngrams(self, words: List[str]):
        """Cümleyi N-gram'lara ayır ve ekle"""
        if len(words) < 2:
            return
        
        # 2-gram
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            self.bigrams[bigram] += 1
            self.word_followers[words[i]][words[i+1]] += 1
        
        # 3-gram
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            self.trigrams[trigram] += 1
        
        # 4-gram
        for i in range(len(words) - 3):
            quadgram = f"{words[i]} {words[i+1]} {words[i+2]} {words[i+3]}"
            self.quadgrams[quadgram] += 1
        
        # Phrase completions
        for i in range(1, len(words)):
            prefix = " ".join(words[:i])
            completion = " ".join(words[i:])
            self.phrase_completions[prefix][completion] += 1
    
    def predict_next_word(self, context: str, max_results: int = 10) -> List[Dict]:
        """Bağlamdan sonraki kelimeyi tahmin et"""
        words = context.lower().strip().split()
        if not words:
            return []
        
        suggestions = []
        
        # 4-gram kullan (en spesifik)
        if len(words) >= 3:
            prefix = " ".join(words[-3:])
            completions = self.phrase_completions.get(prefix, {})
            for completion, count in sorted(completions.items(), key=lambda x: x[1], reverse=True)[:max_results]:
                next_word = completion.split()[0] if completion else ""
                if next_word:
                    suggestions.append({
                        'word': next_word,
                        'score': count * 10.0,
                        'type': 'ngram_4',
                        'description': f'4-gram tahmini (frekans: {count})',
                        'source': 'ngram'
                    })
        
        # 3-gram kullan
        if len(words) >= 2:
            prefix = " ".join(words[-2:])
            completions = self.phrase_completions.get(prefix, {})
            for completion, count in sorted(completions.items(), key=lambda x: x[1], reverse=True)[:max_results]:
                next_word = completion.split()[0] if completion else ""
                if next_word and next_word not in [s['word'] for s in suggestions]:
                    suggestions.append({
                        'word': next_word,
                        'score': count * 8.0,
                        'type': 'ngram_3',
                        'description': f'3-gram tahmini (frekans: {count})',
                        'source': 'ngram'
                    })
        
        # 2-gram kullan (en genel)
        if len(words) >= 1:
            last_word = words[-1]
            followers = self.word_followers.get(last_word, {})
            for next_word, count in sorted(followers.items(), key=lambda x: x[1], reverse=True)[:max_results]:
                if next_word not in [s['word'] for s in suggestions]:
                    suggestions.append({
                        'word': next_word,
                        'score': count * 6.0,
                        'type': 'ngram_2',
                        'description': f'2-gram tahmini (frekans: {count})',
                        'source': 'ngram'
                    })
        
        # Skora göre sırala ve duplikatları kaldır
        seen = set()
        unique_suggestions = []
        for sug in sorted(suggestions, key=lambda x: x['score'], reverse=True):
            if sug['word'] not in seen:
                seen.add(sug['word'])
                unique_suggestions.append(sug)
        
        return unique_suggestions[:max_results]
    
    def predict_phrase_completion(self, context: str, max_results: int = 5) -> List[str]:
        """Cümle tamamlama önerileri"""
        words = context.lower().strip().split()
        if not words:
            return []
        
        completions = []
        
        # 4-gram phrase completion
        if len(words) >= 3:
            prefix = " ".join(words[-3:])
            phrase_completions = self.phrase_completions.get(prefix, {})
            for completion, count in sorted(phrase_completions.items(), key=lambda x: x[1], reverse=True)[:max_results]:
                completions.append(completion)
        
        # 3-gram phrase completion
        if len(words) >= 2:
            prefix = " ".join(words[-2:])
            phrase_completions = self.phrase_completions.get(prefix, {})
            for completion, count in sorted(phrase_completions.items(), key=lambda x: x[1], reverse=True)[:max_results]:
                if completion not in completions:
                    completions.append(completion)
        
        return completions[:max_results]
    
    def learn_from_text(self, text: str):
        """Metinden öğren (real-time learning)"""
        words = text.lower().strip().split()
        if len(words) >= 2:
            self._add_ngrams(words)
            # Anında kaydet
            self.save_data()
    
    def save_data(self):
        """N-gram verilerini kaydet"""
        data_file = os.path.join(os.path.dirname(__file__), "ngram_data.json")
        try:
            data = {
                'bigrams': dict(self.bigrams),
                'trigrams': dict(self.trigrams),
                'quadgrams': dict(self.quadgrams),
                'word_followers': {k: dict(v) for k, v in self.word_followers.items()},
                'phrase_completions': {k: dict(v) for k, v in self.phrase_completions.items()},
                'last_updated': datetime.now().isoformat()
            }
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"N-gram data kaydetme hatasi: {e}")
    
    def load_data(self):
        """N-gram verilerini yükle"""
        data_file = os.path.join(os.path.dirname(__file__), "ngram_data.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bigrams = defaultdict(int, data.get('bigrams', {}))
                    self.trigrams = defaultdict(int, data.get('trigrams', {}))
                    self.quadgrams = defaultdict(int, data.get('quadgrams', {}))
                    self.word_followers = defaultdict(
                        lambda: defaultdict(int),
                        {k: defaultdict(int, v) for k, v in data.get('word_followers', {}).items()}
                    )
                    self.phrase_completions = defaultdict(
                        lambda: defaultdict(int),
                        {k: defaultdict(int, v) for k, v in data.get('phrase_completions', {}).items()}
                    )
                    print(f"[OK] N-gram modeli yuklendi: {len(self.bigrams)} bigram, {len(self.trigrams)} trigram")
            except Exception as e:
                print(f"N-gram data yukleme hatasi: {e}")
    
    def get_stats(self) -> Dict:
        """Model istatistikleri"""
        return {
            'bigrams': len(self.bigrams),
            'trigrams': len(self.trigrams),
            'quadgrams': len(self.quadgrams),
            'word_followers': len(self.word_followers),
            'phrase_completions': len(self.phrase_completions)
        }

# Global instance
advanced_ngram = AdvancedNGramModel()
