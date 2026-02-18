"""
Advanced Context-Aware Completion System
Context analizi ve tamamlama sistemi
"""

from typing import List, Dict, Optional, Tuple
import re
from collections import defaultdict

class AdvancedContextCompleter:
    """Context analizi ve tamamlama"""
    
    def __init__(self, dictionary=None):
        # Sozluk referansi (opsiyonel)
        self.dictionary = dictionary
        
        # Domain tespiti için anahtar kelimeler
        self.domain_keywords = {
            'customer_service': [
                'müşteri', 'hizmet', 'destek', 'yardım', 'sorun', 'problem',
                'sipariş', 'ürün', 'kargo', 'teslimat', 'iade', 'değişim',
                'fatura', 'ödeme', 'hesap', 'kayıt', 'üyelik'
            ],
            'technical': [
                'api', 'endpoint', 'database', 'query', 'code', 'program',
                'yazılım', 'uygulama', 'sistem', 'sunucu', 'server', 'hosting',
                'domain', 'ssl', 'https', 'http', 'json', 'xml'
            ],
            'sales': [
                'satış', 'fiyat', 'indirim', 'kampanya', 'promosyon', 'kupon',
                'sepet', 'alışveriş', 'ödeme', 'kredi', 'kart', 'nakit'
            ],
            'general': []
        }
        
        # Gramer kurallari
        self.grammar_rules = {
            'verb_endings': ['mak', 'mek', 'acak', 'ecek', 'ıyor', 'iyor', 'uyor', 'üyor'],
            'noun_endings': ['lık', 'lik', 'luk', 'lük', 'cı', 'ci', 'cu', 'cü'],
            'adjective_endings': ['lı', 'li', 'lu', 'lü', 'sız', 'siz', 'suz', 'süz']
        }
    
    def analyze_full_context(self, text: str) -> Dict[str, any]:
        # Cumle baglami analizi
        words = text.lower().split()
        
        analysis = {
            'domain': self._detect_domain(text),
            'last_words': words[-3:] if len(words) >= 3 else words,
            'word_count': len(words),
            'grammar_structure': self._analyze_grammar_structure(words),
            'intent': self._detect_intent(text),
            'last_word': words[-1] if words else '',
            'previous_words': ' '.join(words[:-1]) if len(words) > 1 else ''
        }
        
        return analysis
    
    def _detect_domain(self, text: str) -> str:
        # Domain tespiti
        text_lower = text.lower()
        
        for domain, keywords in self.domain_keywords.items():
            if domain == 'general':
                continue
            for keyword in keywords:
                if keyword in text_lower:
                    return domain
        
        return 'general'
    
    def _analyze_grammar_structure(self, words: List[str]) -> Dict[str, any]:
        """Gramer yapısını analiz et"""
        if not words:
            return {}
        
        last_word = words[-1]
        structure = {
            'last_word_type': self._detect_word_type(last_word),
            'needs_verb': self._needs_verb(words),
            'needs_noun': self._needs_noun(words),
            'needs_adjective': self._needs_adjective(words)
        }
        
        return structure
    
    def _detect_word_type(self, word: str) -> str:
        """Kelime tipini tespit et"""
        if any(word.endswith(ending) for ending in self.grammar_rules['verb_endings']):
            return 'verb'
        elif any(word.endswith(ending) for ending in self.grammar_rules['noun_endings']):
            return 'noun'
        elif any(word.endswith(ending) for ending in self.grammar_rules['adjective_endings']):
            return 'adjective'
        return 'unknown'
    
    def _needs_verb(self, words: List[str]) -> bool:
        """Fiil gerekiyor mu?"""
        if not words:
            return False
        
        last_word = words[-1]
        # Son kelime isim ise fiil gerekiyor olabilir
        if self._detect_word_type(last_word) == 'noun':
            return True
        
        # "nasıl", "ne", "neden" gibi soru kelimelerinden sonra fiil gerekiyor
        question_words = ['nasıl', 'ne', 'neden', 'niçin', 'kim', 'nerede', 'ne zaman']
        if any(qw in words for qw in question_words):
            return True
        
        return False
    
    def _needs_noun(self, words: List[str]) -> bool:
        """İsim gerekiyor mu?"""
        if not words:
            return True  # Boşsa isim başlayabilir
        
        last_word = words[-1]
        # Son kelime fiil ise isim gerekiyor olabilir
        if self._detect_word_type(last_word) == 'verb':
            return True
        
        # "bir", "bu", "şu" gibi belirteçlerden sonra isim gerekiyor
        determiners = ['bir', 'bu', 'şu', 'o', 'her', 'tüm', 'bazı']
        if any(det in words for det in determiners):
            return True
        
        return False
    
    def _needs_adjective(self, words: List[str]) -> bool:
        """Sıfat gerekiyor mu?"""
        if not words:
            return False
        
        last_word = words[-1]
        # "çok", "daha", "en" gibi zarflardan sonra sıfat gerekiyor
        adverbs = ['çok', 'daha', 'en', 'pek', 'oldukça', 'fazla']
        if any(adv in words for adv in adverbs):
            return True
        
        return False
    
    def _detect_intent(self, text: str) -> str:
        """Kullanıcı intent (niyet) tespit et"""
        text_lower = text.lower()
        
        # Soru intent
        if any(word in text_lower for word in ['nasıl', 'ne', 'neden', 'niçin', 'kim', 'nerede', 'ne zaman', 'hangi']):
            return 'question'
        
        # İstek intent
        if any(word in text_lower for word in ['istiyorum', 'istiyoruz', 'istiyorsun', 'istiyorsunuz', 'istiyor', 'lütfen']):
            return 'request'
        
        # Bilgi intent
        if any(word in text_lower for word in ['bilgi', 'açıkla', 'anlat', 'söyle', 'göster']):
            return 'information'
        
        # Yardım intent
        if any(word in text_lower for word in ['yardım', 'destek', 'yardımcı', 'yardım et']):
            return 'help'
        
        return 'general'
    
    def suggest_with_grammar_check(self, text: str, suggestions: List[Dict]) -> List[Dict]:
        """Gramer uyumlu öneriler"""
        analysis = self.analyze_full_context(text)
        grammar_structure = analysis.get('grammar_structure', {})
        
        scored_suggestions = []
        
        for suggestion in suggestions:
            suggestion_text = suggestion.get('text', '') or suggestion.get('word', '')
            if not suggestion_text:
                continue
            
            score = suggestion.get('score', 0.0)
            suggestion_type = self._detect_word_type(suggestion_text.lower())
            
            # Gramer uyumu bonusu
            grammar_bonus = 0.0
            
            if grammar_structure.get('needs_verb') and suggestion_type == 'verb':
                grammar_bonus = 2.0
            elif grammar_structure.get('needs_noun') and suggestion_type == 'noun':
                grammar_bonus = 2.0
            elif grammar_structure.get('needs_adjective') and suggestion_type == 'adjective':
                grammar_bonus = 2.0
            
            # Gramer uyumsuzluğu cezası
            if grammar_structure.get('needs_verb') and suggestion_type != 'verb':
                grammar_bonus = -1.0
            elif grammar_structure.get('needs_noun') and suggestion_type != 'noun':
                grammar_bonus = -0.5
            
            scored_suggestions.append({
                **suggestion,
                'score': score + grammar_bonus,
                'grammar_match': grammar_bonus > 0
            })
        
        # Skora göre sırala
        scored_suggestions.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_suggestions
    
    def suggest_with_semantic_similarity(self, text: str, suggestions: List[Dict]) -> List[Dict]:
        """Anlamsal benzerlik ile öneri"""
        analysis = self.analyze_full_context(text)
        domain = analysis.get('domain', 'general')
        intent = analysis.get('intent', 'general')
        last_word = analysis.get('last_word', '')
        
        scored_suggestions = []
        
        for suggestion in suggestions:
            suggestion_text = suggestion.get('text', '') or suggestion.get('word', '')
            if not suggestion_text:
                continue
            
            score = suggestion.get('score', 0.0)
            semantic_bonus = 0.0
            
            # Domain uyumu
            suggestion_lower = suggestion_text.lower()
            domain_keywords = self.domain_keywords.get(domain, [])
            if any(keyword in suggestion_lower for keyword in domain_keywords):
                semantic_bonus += 1.5
            
            # Intent uyumu
            if intent == 'question' and any(qw in suggestion_lower for qw in ['nasıl', 'ne', 'neden']):
                semantic_bonus += 1.0
            elif intent == 'request' and any(rw in suggestion_lower for rw in ['istiyorum', 'lütfen', 'yapabilir']):
                semantic_bonus += 1.0
            elif intent == 'help' and any(hw in suggestion_lower for hw in ['yardım', 'destek', 'yardımcı']):
                semantic_bonus += 1.0
            
            # Son kelime ile benzerlik (basit - Levenshtein distance için hazır)
            if last_word and suggestion_lower.startswith(last_word):
                semantic_bonus += 1.0
            
            scored_suggestions.append({
                **suggestion,
                'score': score + semantic_bonus,
                'semantic_match': semantic_bonus > 0
            })
        
        # Skora göre sırala
        scored_suggestions.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_suggestions
    
    def complete_with_full_context(self, text: str, max_results: int = 50) -> List[Dict]:
        """Tam context analizi ile tamamlama"""
        analysis = self.analyze_full_context(text)
        last_word = analysis.get('last_word', '')
        previous_words = analysis.get('previous_words', '')
        
        results = []
        
        # 1. Son kelime için sözlük araması
        if self.dictionary and hasattr(self.dictionary, 'search') and last_word:
            try:
                dict_results = self.dictionary.search(last_word, max_results=max_results)
                for result in dict_results:
                    if isinstance(result, dict):
                        word = result.get('word', '')
                        score = result.get('score', 8.0)
                        
                        if word and word.lower() != last_word:
                            # Son kelime onerileri (oncelikli)
                            results.append({
                                'text': word,
                                'type': 'dictionary',
                                'score': 15.0 + (score / 10),
                                'description': f'Sozluk onerisi',
                                'source': 'context',
                                'last_word_match': True
                            })
                            
                            # SONRA: Birleşik öneri (daha düşük öncelik)
                            if previous_words:
                                full_phrase = f"{previous_words} {word}"
                                results.append({
                                    'text': full_phrase,
                                    'type': 'phrase',
                                    'score': 10.0 + (score / 20),  # Daha düşük skor
                                    'description': f'Tam ifade (sözlük)',
                                    'source': 'advanced_context',
                                    'last_word_match': False
                                })
            except Exception as e:
                print(f"[WARNING] Dictionary search hatasi (advanced_context): {e}")
        
        # 2. Gramer kontrolü ile filtrele
        if results:
            results = self.suggest_with_grammar_check(text, results)
        
        # 3. Semantic similarity ile skorla
        if results:
            results = self.suggest_with_semantic_similarity(text, results)
        

        # 4. Son kelime önerilerine öncelik ver
        results.sort(
            key=lambda x: (
                x.get('last_word_match', False),  # Önce last_word_match=True olanlar
                x.get('score', 0)  # Sonra skora göre
            ),
            reverse=True
        )
        
        return results[:max_results]

    # Eklenen Regex Pattern Özellikleri (ContextAnalyzer'dan aktarıldı)
    def generate_smart_responses(self, text: str) -> List[Dict]:
        """Hazır, akıllı yanıtlar üret"""
        text_lower = text.lower()
        responses = []
        
        # 1. Selamlaşma
        if any(x in text_lower for x in ['merhaba', 'selam', 'günaydın', 'iyi günler']):
            responses.extend([
                "Merhabalar, size nasıl yardımcı olabilirim?",
                "Selamlar, hoş geldiniz!",
                "Merhaba, bugün sizin için ne yapabilirim?"
            ])
            
        # 2. Yardım
        if any(x in text_lower for x in ['yardım', 'destek', 'yapabilirim']):
            responses.extend([
                "Hangi konuda desteğe ihtiyacınız var?",
                "Size nasıl yardımcı olabilirim?",
                "Sorunuzu detaylandırabilir misiniz?"
            ])
            
        # 3. Teşekkür
        if any(x in text_lower for x in ['teşekkür', 'sağol']):
            responses.extend([
                "Rica ederim, iyi günler dilerim.",
                "Ne demek, her zaman bekleriz."
            ])
            
        # 4. Sipariş/Kargo
        if any(x in text_lower for x in ['sipariş', 'kargo', 'teslimat']):
            responses.extend([
                "Sipariş numaranızı alabilir miyim?",
                "Kargo takibi için takip numaranız nedir?",
                "Sipariş durumunuzu kontrol ediyorum."
            ])

        return [{'text': r, 'type': 'smart_response', 'score': 20.0, 'description': 'Akıllı Yanıt', 'source': 'context_ai'} for r in responses]

# Global instance
advanced_context_completer = AdvancedContextCompleter()
