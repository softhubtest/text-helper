"""
Gelişmiş Ranking Algoritması
Machine Learning tabanlı sıralama
"""

from typing import List, Dict
from datetime import datetime
import math
import sys
import os

# Support Dictionary Import
sys.path.append(os.path.join(os.path.dirname(__file__)))
try:
    from support_dictionary import is_support_term, is_brand_name
    SUPPORT_DICT_AVAILABLE = True
except ImportError:
    SUPPORT_DICT_AVAILABLE = False
    is_support_term = lambda x: False
    is_brand_name = lambda x: False

class AdvancedRanking:
    """Gelişmiş ranking algoritması"""
    
    def __init__(self):
        # Feature weights (ML öğrenme ile optimize edilebilir)
        self.weights = {
            'frequency': 0.25,      # Kelime frekansı
            'user_preference': 0.20,  # Kullanıcı tercihi
            'context_relevance': 0.25, # Bağlam uyumu
            'typo_distance': 0.15,    # Yazım hatası mesafesi
            'time_decay': 0.10,       # Zaman bazlı azalma
            'source_quality': 0.05    # Kaynak kalitesi
        }
        
        # Click-through tracking
        self.ctr_data = {}  # {suggestion_text: {clicks, impressions}}
    
    def rank_suggestions(
        self,
        suggestions: List[Dict],
        context: Dict = None,
        user_id: str = None,
        input_text: str = None
    ) -> List[Dict]:
        """Önerileri gelişmiş algoritma ile sırala"""
        if not suggestions:
            return []
        
        # Her öneri için feature'ları hesapla
        for sug in suggestions:
            features = self._extract_features(sug, context, user_id, input_text)
            score = self._calculate_ml_score(features)
            sug['ml_score'] = score
            sug['features'] = features
        
        # ML score'a göre sırala
        suggestions.sort(key=lambda x: x.get('ml_score', 0), reverse=True)
        
        return suggestions
    
    def _extract_features(self, suggestion: Dict, context: Dict, user_id: str, input_text: str) -> Dict:
        """Feature extraction"""
        text = suggestion.get('text', '').lower()
        base_score = suggestion.get('score', 0)
        
        features = {
            # 1. Frequency feature
            'frequency': min(base_score / 10.0, 1.0),
            
            # 2. User preference (eğer varsa)
            'user_preference': self._get_user_preference(user_id, text) if user_id else 0.0,
            
            # 3. Context relevance
            'context_relevance': self._calculate_context_relevance(text, context) if context else 0.5,
            
            # 4. Typo distance
            'typo_distance': self._calculate_typo_similarity(input_text, text) if input_text else 0.5,
            
            # 5. Time decay (yeni öneriler daha iyi)
            'time_decay': 1.0,  # Şimdilik sabit
            
            # 6. Source quality
            'source_quality': self._get_source_quality(suggestion.get('source', '')),
            
            # 7. Click-through rate
            'ctr': self._get_ctr(text),
            
            # 8. Length penalty (çok uzun kelimeler cezalandırılır)
            'length_penalty': 1.0 - (len(text) / 50.0) if len(text) > 20 else 1.0,
            
            # Raw text for domain checks
            'text_raw': text
        }
        
        return features
    
    def _calculate_ml_score(self, features: Dict) -> float:
        """Machine Learning score hesapla"""
        score = 0.0
        
        # Weighted sum
        score += features.get('frequency', 0) * self.weights['frequency']
        score += features.get('user_preference', 0) * self.weights['user_preference']
        score += features.get('context_relevance', 0) * self.weights['context_relevance']
        score += features.get('typo_distance', 0) * self.weights['typo_distance']
        score += features.get('time_decay', 0) * self.weights['time_decay']
        score += features.get('source_quality', 0) * self.weights['source_quality']
        
        # CTR bonus
        ctr = features.get('ctr', 0)
        if ctr > 0:
            score += ctr * 0.15
        
        # DOMAIN SPECIFIC BOOST (Müşteri Hizmetleri)
        if SUPPORT_DICT_AVAILABLE:
            text = features.get('text_raw', '') # Text'i feature'dan almamız lazım
            
            # 1. Brand Filter (Yasaklı Markalar)
            if is_brand_name(text):
                score *= 0.1 # Cezalandır (%90 düşür)
                
            # 2. Domain Boost (Destek Terimleri)
            elif is_support_term(text):
                score *= 3.0 # Ödüllendir (3x)
        
        # Length penalty
        score *= features.get('length_penalty', 1.0)
        
        # Normalize to 0-10 range
        return min(score * 10, 10.0)
    
    def _get_user_preference(self, user_id: str, text: str) -> float:
        """Kullanıcı tercihini al (ML learning'den)"""
        try:
            from ml_learning import ml_learning
            if ml_learning and user_id in ml_learning.user_preferences:
                user_prefs = ml_learning.user_preferences[user_id]
                count = user_prefs.get(text.lower(), 0)
                # Normalize: 0-1 arası
                return min(count / 10.0, 1.0)
        except:
            pass
        return 0.0
    
    def _calculate_context_relevance(self, text: str, context: Dict) -> float:
        """Bağlam uyumunu hesapla"""
        if not context:
            return 0.5
        
        relevance = 0.0
        
        # Intent matching
        intents = context.get('intents', [])
        if 'help' in intents and any(word in text for word in ['olabilirim', 'yardımcı', 'destek']):
            relevance += 0.4
        if 'question' in intents and any(word in text for word in ['evet', 'hayır', 'tabii']):
            relevance += 0.3
        if 'greeting' in intents and any(word in text for word in ['merhaba', 'selam']):
            relevance += 0.3
        
        # Topic matching
        topics = context.get('topics', [])
        topic_keywords = {
            'customer_service': ['müşteri', 'hizmet', 'destek'],
            'order': ['sipariş', 'kargo', 'teslimat'],
            'product': ['ürün', 'fiyat', 'kampanya']
        }
        for topic in topics:
            keywords = topic_keywords.get(topic, [])
            if any(keyword in text for keyword in keywords):
                relevance += 0.2
        
        return min(relevance, 1.0)
    
    def _calculate_typo_similarity(self, input_text: str, suggestion: str) -> float:
        """Yazım hatası benzerliği"""
        if not input_text or not suggestion:
            return 0.5
        
        # Basit Levenshtein benzerliği
        def levenshtein_ratio(s1: str, s2: str) -> float:
            if not s1 or not s2:
                return 0.0
            max_len = max(len(s1), len(s2))
            if max_len == 0:
                return 1.0
            
            # Basit karakter benzerliği
            common = sum(1 for c in s1 if c in s2)
            return common / max_len
        
        return levenshtein_ratio(input_text.lower(), suggestion.lower())
    
    def _get_source_quality(self, source: str) -> float:
        """Kaynak kalitesi - smart_completions / phrase en ustte"""
        quality_map = {
            'smart_completions': 1.0,
            'transformer': 0.95,
            'phrase_completion': 0.95,
            'ngram': 0.9,
            'advanced_ngram': 0.9,
            'trie_index': 0.88,
            'elasticsearch': 0.82,
            'large_dictionary_direct': 0.8,
            'dictionary': 0.75,
            'local_dictionary': 0.75,
            'domain_dictionaries': 0.85,
            'spellcheck': 0.6,
        }
        return quality_map.get(source, 0.5)
    
    def _get_ctr(self, text: str) -> float:
        """Click-through rate"""
        if text not in self.ctr_data:
            return 0.0
        
        data = self.ctr_data[text]
        impressions = data.get('impressions', 1)
        clicks = data.get('clicks', 0)
        
        if impressions == 0:
            return 0.0
        
        return clicks / impressions
    
    def record_click(self, suggestion_text: str):
        """Tıklamayı kaydet (real-time learning)"""
        if suggestion_text not in self.ctr_data:
            self.ctr_data[suggestion_text] = {'clicks': 0, 'impressions': 0}
        
        self.ctr_data[suggestion_text]['clicks'] += 1
    
    def record_impression(self, suggestion_text: str):
        """Gösterimi kaydet"""
        if suggestion_text not in self.ctr_data:
            self.ctr_data[suggestion_text] = {'clicks': 0, 'impressions': 0}
        
        self.ctr_data[suggestion_text]['impressions'] += 1
    
    def update_weights(self, new_weights: Dict):
        """Ağırlıkları güncelle (ML öğrenme ile)"""
        self.weights.update(new_weights)

# Global instance
advanced_ranking = AdvancedRanking()
