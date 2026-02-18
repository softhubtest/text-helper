"""
Multi-Word Suggestions - Phrase Completion
- Phrase completion
- Template suggestions
- Context-aware phrases
"""

from typing import List, Dict
import re

class PhraseCompleter:
    """Cümle/ifade tamamlama"""
    
    def __init__(self, dictionary=None):
        """Dictionary: Sözlük referansı (opsiyonel) - son kelime için genel arama için"""
        self.dictionary = dictionary  # LargeTurkishDictionary veya benzeri
        # Phrase templates (context-aware)
        self.phrase_templates = {
            'greeting': {
                'merhaba nasıl': [
                    'yardımcı olabilirim',
                    'yardımcı olabiliriz',
                    'destek verebilirim',
                    'yardımcı olabilir misiniz'
                ],
                'merhaba': [
                    'nasıl yardımcı olabilirim',
                    'hoş geldiniz',
                    'size nasıl yardımcı olabilirim'
                ]
            },
            'customer_service': {
                'sipariş': [
                    'sipariş takibi',
                    'sipariş iptali',
                    'sipariş durumu',
                    'sipariş numarası',
                    'sipariş sorgulama'
                ],
                'ürün': [
                    'ürün bilgisi',
                    'ürün fiyatı',
                    'ürün stoku',
                    'ürün yorumları',
                    'ürün kategorisi'
                ],
                'al': [
                    'alışveriş',
                    'alıcı',
                    'alım',
                    'alış',
                    'alabilirim',
                    'alabilirsiniz',
                    'alabilir misiniz',
                    'alabilir miyim',
                    'alabilir misin',
                    'alabiliriz',
                    'alabilir',
                    'alıyorum',
                    'alıyorsunuz',
                    'alıyor',
                    'aldım',
                    'aldınız',
                    'aldı',
                    'alacağım',
                    'alacaksınız',
                    'alacak',
                    'alırsınız',
                    'alırım',
                    'alır'
                ],
                'müşteri': [
                    'müşteri hizmetleri',
                    'müşteri desteği',
                    'müşteri memnuniyeti',
                    'müşteri temsilcisi'
                ]
            },
            'technical': {
                'API': [
                    'API endpoint',
                    'API key',
                    'API documentation',
                    'API request',
                    'API response'
                ],
                'database': [
                    'database connection',
                    'database query',
                    'database schema',
                    'database backup'
                ]
            },
            'problem': {
                'sorun': [
                    'sorun çözümü',
                    'sorun bildirimi',
                    'sorun giderme',
                    'sorun raporu'
                ],
                'hata': [
                    'hata mesajı',
                    'hata raporu',
                    'hata çözümü',
                    'hata bildirimi'
                ]
            }
        }
        
        # Common phrase patterns (musteri hizmetleri + genel)
        self.common_phrases = [
            'yardımcı olabilirim', 'yardımcı olabiliriz', 'yardımcı olabilir misiniz',
            'destek verebilirim', 'bilgi verebilirim', 'çözüm bulabilirim',
            'sorun çözebilirim', 'takip edebilirim', 'kontrol edebilirim',
            'nasıl yardımcı olabilirim', 'size nasıl yardımcı olabilirim',
            'ne konuda yardımcı olabilirim', 'sipariş takibi', 'sipariş durumu',
            'sipariş sorgulama', 'kargo takibi', 'kargo durumu', 'iade talebi',
            'iade süreci', 'müşteri hizmetleri', 'müşteri desteği', 'teşekkür ederim',
            'teşekkürler', 'rica ederim', 'özür dilerim', 'kusura bakmayın',
        ]
        self._load_musteri_phrases()
    
    def _load_musteri_phrases(self):
        """musteri_hizmetleri_sozluk.txt'den 2+ kelimelik ifadeleri common_phrases'e ekle"""
        import os
        path = os.path.join(os.path.dirname(__file__), "musteri_hizmetleri_sozluk.txt")
        if not os.path.exists(path):
            return
        seen = set(self.common_phrases)
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if len(line.split()) >= 2 and line.lower() not in seen:
                    self.common_phrases.append(line)
                    seen.add(line.lower())
    
    def detect_context(self, text: str) -> str:
        """Context tespit et"""
        text_lower = text.lower()
        
        # Greeting
        if any(word in text_lower for word in ['merhaba', 'selam', 'günaydın', 'iyi günler']):
            return 'greeting'
        
        # Customer service
        if any(word in text_lower for word in ['sipariş', 'müşteri', 'ürün', 'kargo', 'teslimat']):
            return 'customer_service'
        
        # Technical
        if any(word in text_lower for word in ['api', 'endpoint', 'database', 'query', 'code']):
            return 'technical'
        
        # Problem
        if any(word in text_lower for word in ['sorun', 'hata', 'problem', 'çözüm']):
            return 'problem'
        
        return 'general'
    
    def complete_phrase(self, text: str, max_results: int = 10) -> List[Dict]:
        """Cümle tamamla - SON KELİME İÇİN ÖNERİ VER!"""
        results = []
        text_lower = text.lower().strip()
        words = text_lower.split()
        last_word = words[-1] if words else text_lower
        context = self.detect_context(text)
        
        # ÖNEMLİ: Eğer birden fazla kelime varsa, SON KELİME için öneriler ver!
        if len(words) > 1:
            # Önceki kelimeleri al (son kelime hariç)
            previous_words = ' '.join(words[:-1])
            
            # 0. ÖNCE: Son kelime için GENEL SÖZLÜK ARAMASI (HER KELİME İÇİN!)
            # Bu, template'lerde olmayan kelimeler için de çalışır!
            if self.dictionary and hasattr(self.dictionary, 'search'):
                try:
                    dict_results = self.dictionary.search(last_word, max_results=50)
                    for result in dict_results:
                        if isinstance(result, dict):
                            word = result.get('word', '')
                            score = result.get('score', 8.0)
                            frequency = result.get('frequency', 1)
                            
                            if word and word.lower() != last_word:
                                # ÖNCE: Sadece son kelime için öneriler (TEK KELİME - EN YÜKSEK ÖNCELİK!)
                                results.append({
                                    'text': word,
                                    'type': 'phrase',
                                    'score': 12.0 + (score / 10),  # EN YÜKSEK SKOR - genel sözlük!
                                    'description': f'Son kelime önerisi (sözlük, frekans: {frequency})',
                                    'source': 'phrase_completion',
                                    'context': context
                                })
                                
                                # SONRA: Birleşik öneri: "ürün al" + "alışveriş" → "ürün alışveriş"
                                full_phrase = f"{previous_words} {word}"
                                results.append({
                                    'text': full_phrase,
                                    'type': 'phrase',
                                    'score': 9.0 + (score / 20),  # Daha düşük skor - birleşik
                                    'description': f'Tam ifade (sözlük, frekans: {frequency})',
                                    'source': 'phrase_completion',
                                    'context': context
                                })
                except Exception as e:
                    print(f"[WARNING] Dictionary search hatasi (phrase_completion): {e}")
            
            # 1. Son kelime için template önerileri (ÖNCE TEK KELİME, SONRA BİRLEŞİK)
            if context in self.phrase_templates:
                templates = self.phrase_templates[context]
                
                # Son kelime için öneriler ara
                if last_word in templates:
                    for phrase in templates[last_word]:
                        # ÖNCE: Sadece son kelime için öneriler (TEK KELİME - YÜKSEK ÖNCELİK!)
                        results.append({
                            'text': phrase,
                            'type': 'phrase',
                            'score': 11.0,  # YÜKSEK SKOR - son kelime için tek kelime!
                            'description': f'Son kelime önerisi ({context})',
                            'source': 'phrase_completion',
                            'context': context
                        })
                        
                        # SONRA: Birleşik öneri: "ürün al" + "alışveriş" → "ürün alışveriş"
                        full_phrase = f"{previous_words} {phrase}"
                        results.append({
                            'text': full_phrase,
                            'type': 'phrase',
                            'score': 9.5,  # Daha düşük skor - birleşik
                            'description': f'Tam ifade ({context})',
                            'source': 'phrase_completion',
                            'context': context
                        })
            
            # 2. Son kelime için common phrases (ÖNCE TEK KELİME, SONRA BİRLEŞİK)
            for phrase in self.common_phrases:
                if phrase.startswith(last_word):
                    # ÖNCE: Sadece son kelime için öneriler (TEK KELİME)
                    results.append({
                        'text': phrase,
                        'type': 'phrase',
                        'score': 10.0,  # Yüksek skor - son kelime için tek kelime!
                        'description': 'Son kelime önerisi',
                        'source': 'phrase_completion',
                        'context': 'general'
                    })
                    
                    # SONRA: Birleşik öneri: "ürün al" + "alışveriş" → "ürün alışveriş"
                    full_phrase = f"{previous_words} {phrase}"
                    results.append({
                        'text': full_phrase,
                        'type': 'phrase',
                        'score': 8.5,  # Daha düşük skor - birleşik
                        'description': 'Yaygın ifade',
                        'source': 'phrase_completion',
                        'context': 'general'
                    })
        else:
            # TEK KELİME İSE: Normal template önerileri
            # 1. Template-based completion
            if context in self.phrase_templates:
                templates = self.phrase_templates[context]
                
                for key, phrases in templates.items():
                    # Eğer text bu key ile bitiyorsa veya key içeriyorsa
                    if text_lower.endswith(key) or (key in text_lower and len(words) == 1):
                        for phrase in phrases:
                            # Eğer text zaten phrase'in başlangıcını içeriyorsa, devamını öner
                            if phrase.startswith(text_lower.split()[-1] if text_lower.split() else ''):
                                full_phrase = phrase
                            else:
                                full_phrase = phrase
                            
                            results.append({
                                'text': full_phrase,
                                'type': 'phrase',
                                'score': 9.0,
                                'description': f'Tam ifade ({context})',
                                'source': 'phrase_completion',
                                'context': context
                            })
            
            # 2. Common phrases
            for phrase in self.common_phrases:
                if phrase.startswith(text_lower.split()[-1] if text_lower.split() else ''):
                    results.append({
                        'text': phrase,
                        'type': 'phrase',
                        'score': 8.0,
                        'description': 'Yaygın ifade',
                        'source': 'phrase_completion',
                        'context': 'general'
                    })
        
        # 3. Pattern-based completion
        # "merhaba nasıl" → "yardımcı olabilirim"
        if 'merhaba' in text_lower and 'nasıl' in text_lower:
            results.append({
                'text': 'yardımcı olabilirim',
                'type': 'phrase',
                'score': 9.5,
                'description': 'Selamlaşma tamamlama',
                'source': 'phrase_completion',
                'context': 'greeting'
            })
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for r in results:
            if r['text'] not in seen:
                seen.add(r['text'])
                unique_results.append(r)
        
        # Sort by score
        unique_results.sort(key=lambda x: x['score'], reverse=True)
        return unique_results[:max_results]
    
    def get_template_suggestions(self, word: str, context: str = None) -> List[str]:
        """Template önerileri al"""
        suggestions = []
        
        if context:
            if context in self.phrase_templates:
                templates = self.phrase_templates[context]
                if word.lower() in templates:
                    suggestions.extend(templates[word.lower()])
        else:
            # Tüm context'lerde ara
            for ctx, templates in self.phrase_templates.items():
                if word.lower() in templates:
                    suggestions.extend(templates[word.lower()])
        
        return list(set(suggestions))

# Global instance (dictionary referansı main.py'de geçilecek)
# phrase_completer = PhraseCompleter()  # Artık main.py'de oluşturuluyor
