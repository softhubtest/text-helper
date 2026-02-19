"""
Relevance Filter - İlgisiz Önerileri Filtrele
Kalite iyileştirme için ilgisiz önerileri çıkar.
iPhone benzeri: yaygın kelimeler (hangi, merhaba, nasıl vb.) asla filtrelenmez.
"""

from typing import List, Dict, Set
import re
from collections import Counter

try:
    from common_words import is_common, first_word_common
    _common_words_available = True
except ImportError:
    _common_words_available = False
    is_common = lambda w: False
    first_word_common = lambda t: False


class RelevanceFilter:
    """İlgisiz önerileri filtrele"""
    
    def __init__(self):
        # ALKALI ÖNERİLER İÇİN: Minimum relevance score artırıldı (daha alakalı öneriler)
        self.min_relevance_score = 0.3  # Minimum relevance score (artırıldı - alakasız önerileri filtrele)
    
    def filter_irrelevant(
        self,
        suggestions: List[Dict],
        context: str,
        max_results: int = 50
    ) -> List[Dict]:
        """İlgisiz önerileri çıkar"""
        if not suggestions:
            return []
        
        context_lower = context.lower()
        context_words = set(re.findall(r'\b[çğıöşüÇĞIİÖŞÜa-zA-Z]{2,}\b', context_lower))
        
        scored_suggestions = []
        
        for suggestion in suggestions:
            # WhatsApp/iPhone: öncelikli önerileri (smart_completions) asla filtreleme
            if suggestion.get('source') == 'smart_completions':
                scored_suggestions.append({**suggestion, 'relevance_score': 1.0})
                continue
            suggestion_text = suggestion.get('text', '') or suggestion.get('word', '')
            # iPhone benzeri: yaygın kelimeleri (hangi, merhaba, nasıl vb.) asla filtreleme
            if _common_words_available and suggestion_text:
                st = suggestion_text.strip()
                if (" " not in st and is_common(st)) or first_word_common(st):
                    scored_suggestions.append({**suggestion, 'relevance_score': 1.0})
                    continue
            if not suggestion_text:
                continue
            
            suggestion_lower = suggestion_text.lower()
            suggestion_words = set(re.findall(r'\b[çğıöşüÇĞIİÖŞÜa-zA-Z]{2,}\b', suggestion_lower))
            
            # Relevance score hesapla
            relevance_score = self._calculate_relevance(
                context_words,
                suggestion_words,
                context_lower,
                suggestion_lower
            )
            
            # ALKALI ÖNERİLER İÇİN: Minimum relevance kontrolü (daha katı)
            if relevance_score < self.min_relevance_score:
                continue  # İlgisiz öneri, atla (alkalı öneriler için)
            
            # ALKALI ÖNERİLER İÇİN: Relevance skorunu daha fazla önem ver
            original_score = suggestion.get('score', 0.0)
            # Relevance score daha yüksek ağırlık (alkalı öneriler için)
            combined_score = (original_score * 0.5) + (relevance_score * 10.0 * 0.5)
            
            scored_suggestions.append({
                **suggestion,
                'score': combined_score,
                'relevance_score': relevance_score
            })
        
        # Skora göre sırala
        scored_suggestions.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_suggestions[:max_results]
    
    def _calculate_relevance(
        self,
        context_words: Set[str],
        suggestion_words: Set[str],
        context_lower: str,
        suggestion_lower: str
    ) -> float:
        """Relevance score hesapla (0-1) - ALKALI ÖNERİLER İÇİN İYİLEŞTİRİLDİ"""
        # Tek harf için prefix match kontrolü
        if len(context_lower.strip()) <= 1:
            # Tek harf için prefix match yeterli ama daha katı
            if suggestion_lower.startswith(context_lower.strip()):
                return 0.9  # Yüksek relevance (artırıldı)
            return 0.2  # Düşük relevance (filtreleme yap)
        
        if not context_words or not suggestion_words:
            return 0.3  # Düşük relevance (önceden: 0.5)
        
        # ALKALI ÖNERİLER İÇİN: Son kelimeye odaklan (en önemli!)
        context_words_list = context_lower.split()
        context_last_word = context_words_list[-1] if context_words_list else ''
        
        # 1. SON KELİME PREFIX MATCH (EN ÖNEMLİ - 40% ağırlık)
        # "ürün al" yazınca "al" ile başlayan öneriler öncelikli
        if context_last_word and len(context_last_word) >= 2:
            if suggestion_lower.startswith(context_last_word):
                prefix_match = 1.0  # Mükemmel match
            elif context_last_word in suggestion_lower:
                prefix_match = 0.7  # İyi match
            else:
                prefix_match = 0.0  # Match yok
        else:
            prefix_match = 0.5  # Son kelime çok kısa
        
        # 2. KELİME ÖRTÜŞMESİ (30% ağırlık)
        overlap = len(context_words & suggestion_words)
        overlap_score = overlap / max(len(context_words), len(suggestion_words), 1)
        
        # 3. SEMANTIC SIMILARITY (20% ağırlık)
        semantic_score = self._simple_semantic_similarity(context_words, suggestion_words)
        
        # 4. DOMAIN UYUMU (10% ağırlık)
        domain_score = self._domain_match_score(context_lower, suggestion_lower)
        
        # ALKALI ÖNERİLER İÇİN: Ağırlıklı toplam (prefix match öncelikli)
        relevance = (
            prefix_match * 0.4 +      # Son kelime prefix match (EN ÖNEMLİ)
            overlap_score * 0.3 +     # Kelime örtüşmesi
            semantic_score * 0.2 +     # Semantic similarity
            domain_score * 0.1         # Domain uyumu
        )
        
        return min(relevance, 1.0)
    
    def _simple_semantic_similarity(self, context_words: Set[str], suggestion_words: Set[str]) -> float:
        """Basit semantic similarity (kelime benzerliği) - ALKALI ÖNERİLER İÇİN İYİLEŞTİRİLDİ"""
        if not context_words or not suggestion_words:
            return 0.2  # Düşük similarity (önceden: 0.5)
        
        # Ortak kelimeler
        common = context_words & suggestion_words
        if common:
            return 0.8  # Yüksek similarity (artırıldı)
        
        # ALKALI ÖNERİLER İÇİN: Prefix benzerliği kontrolü (daha katı)
        similarity = 0.0
        for cw in context_words:
            if len(cw) >= 3:  # En az 3 harf
                for sw in suggestion_words:
                    # Prefix match (daha katı)
                    if sw.startswith(cw[:min(4, len(cw))]) or cw.startswith(sw[:min(4, len(sw))]):
                        similarity += 0.3  # Artırıldı: 0.1 -> 0.3
                    # İçeriyor mu kontrolü
                    elif cw in sw or sw in cw:
                        similarity += 0.2
        
        return min(similarity, 1.0)
    
    def _domain_match_score(self, context: str, suggestion: str) -> float:
        """Domain uyumu skoru – müşteri hizmetleri tabanı: CS geniş ve öncelikli"""
        domain_keywords = {
            'customer_service': [
                'müşteri', 'hizmet', 'destek', 'yardım', 'sipariş', 'ürün', 'kargo', 'iade',
                'fatura', 'kampanya', 'abonelik', 'paket', 'tarife', 'şikayet', 'temsilci',
                'çağrı', 'talep', 'bilgi', 'sorgulama', 'iptal', 'onay', 'rica', 'teşekkür',
                'özür', 'olabilirim', 'olabiliriz', 'takip', 'durum', 'çözüm', 'memnuniyet'
            ],
            'technical': ['api', 'endpoint', 'database', 'code', 'yazılım', 'sistem'],
            'sales': ['satış', 'fiyat', 'indirim', 'kampanya', 'sepet', 'alışveriş']
        }
        
        context_lower = context.lower()
        suggestion_lower = suggestion.lower()
        
        context_domain = None
        for domain, keywords in domain_keywords.items():
            if any(kw in context_lower for kw in keywords):
                context_domain = domain
                break
        
        if not context_domain:
            return 0.5
        
        suggestion_keywords = domain_keywords.get(context_domain, [])
        if any(kw in suggestion_lower for kw in suggestion_keywords):
            return 1.0
        return 0.3
    
    def remove_duplicates(self, suggestions: List[Dict]) -> List[Dict]:
        """Duplicate ve benzer önerileri çıkar"""
        if not suggestions:
            return []
        
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            suggestion_text = suggestion.get('text', '') or suggestion.get('word', '')
            if not suggestion_text:
                continue
            
            suggestion_lower = suggestion_text.lower().strip()
            
            # Exact duplicate kontrolü
            if suggestion_lower in seen:
                continue
            
            # Benzer kelime kontrolü (Levenshtein distance için hazır)
            is_similar = False
            for seen_text in seen:
                if self._is_similar(suggestion_lower, seen_text):
                    is_similar = True
                    break
            
            if is_similar:
                continue
            
            seen.add(suggestion_lower)
            unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _is_similar(self, word1: str, word2: str, threshold: float = 0.8) -> bool:
        """İki kelime benzer mi? (basit versiyon)"""
        if word1 == word2:
            return True
        
        # Uzunluk farkı çok büyükse benzer değil
        if abs(len(word1) - len(word2)) > max(len(word1), len(word2)) * 0.5:
            return False
        
        # Prefix match
        min_len = min(len(word1), len(word2))
        if min_len >= 3:
            prefix_match = word1[:3] == word2[:3]
            if prefix_match and abs(len(word1) - len(word2)) <= 2:
                return True
        
        # Levenshtein distance için hazır (şimdilik basit)
        # Gerçek implementasyon için python-Levenshtein kullanılabilir
        return False

# Global instance
relevance_filter = RelevanceFilter()
