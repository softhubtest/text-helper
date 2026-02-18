"""
Context-Aware Suggestions
Cümle bağlamını analiz eder ve bağlama göre öneriler sunar
"""

from typing import List, Dict, Optional
import re

class ContextAnalyzer:
    """Cümle bağlamını analiz eder ve akıllı öneriler sunar"""
    
    def __init__(self):
        # Intent patterns - GENİŞLETİLMİŞ
        self.intent_patterns = {
            'greeting': [
                r'merhaba', r'selam', r'günaydın', r'iyi günler', r'iyi akşamlar',
                r'hoş geldin', r'hoşgeldin', r'hey', 'hi'
            ],
            'farewell': [
                r'güle güle', r'hoşça kal', r'baybay', r'görüşürüz', r'iyi geceler',
                r'kendine iyi bak'
            ],
            'question': [
                r'nasıl', r'neden', r'ne', r'kim', r'nere', r'kaç', r'hangi',
                r'\?', r'mi\?', r'mı\?', r'mu\?', r'mü\?', r'mısın', r'misin'
            ],
            'help': [
                r'yardım', r'yardımcı', r'destek', r'yardım et', r'bana yardım',
                r'olabilir', r'yapabilir', 'imdat', 'bakabilir'
            ],
            'order': [
                r'sipariş', r'siparişim', r'siparişiniz', r'order',
                r'takip', r'durum', 'getir', 'kurye'
            ],
            'cancel': [
                r'iptal', r'vazgeç', r'istemiyorum', r'iade', r'geri gönder'
            ],
            'confirm': [
                r'evet', r'tamam', r'onay', r'kabul', r'olur', r'peki', r'aynen'
            ],
            'reject': [
                r'hayır', r'olmaz', r'yok', r'red', r'kabul etmiyorum'
            ],
            'thanks': [
                r'teşekkür', r'sağol', r'minnettar', r'thanks', r'eyvallah', r'adamsın'
            ],
            'problem': [
                r'sorun', r'problem', r'hata', r'yanlış', r'çalışmıyor',
                r'bzuk', r'kötü', r'olmamış', r'şikayet'
            ],
            'information': [
                r'bilgi', r'bilgi al', r'bilgi ver', r'detay', r'açıkla',
                r'nedir', r'ne demek'
            ],
            'payment': [
                r'fatura', r'ödeme', r'ücret', r'fiyat', r'para', r'kart', r'taksit'
            ],
            'time': [
                r'zaman', r'saat', r'gün', r'bugün', r'yarın', r'ne zaman', r'süre'
            ],
            'location': [
                r'nerede', r'adres', r'konum', r'yer', r'yol', r'nereye'
            ],
            'customer_service': [
                r'sipariş', r'kargo', r'iade', r'fatura', r'destek', r'şikayet',
                r'yardım', r'müşteri', r'temsilci', r'kampanya', r'abonelik', r'tarife'
            ]
        }
        
        # Topic keywords – Genişletilmiş
        self.topic_keywords = {
            'customer_service': [
                'müşteri', 'hizmet', 'destek', 'temsilci', 'yardım', 'çağrı', 'şikayet',
                'sipariş', 'kargo', 'teslimat', 'iade', 'fatura', 'ödeme', 'kampanya',
                'abonelik', 'paket', 'tarife', 'numara', 'hat', 'şebeke', 'internet',
                'talep', 'bilgi', 'sorgulama', 'iptal', 'onay', 'memnuniyet', 'rica',
                'teşekkür', 'özür', 'danışman', 'merkezi', 'hattı', 'ticket', 'bilet'
            ],
            'technology': ['bilgisayar', 'telefon', 'yazılım', 'internet', 'wifi', 'kod', 'program'],
            'shopping': ['fiyat', 'ürün', 'sepet', 'satın', 'mağaza', 'market', 'ucuz', 'pahalı'],
            'order': ['sipariş', 'kargo', 'teslimat', 'iade', 'paket'],
            'financial': ['fatura', 'ödeme', 'borç', 'alacak', 'kredi', 'banka', 'para'],
            'technical': ['teknik', 'kurulum', 'ayar', 'yapılandırma', 'servis', 'tamir']
        }
        
        self.cs_boost_keywords = [
            'yardımcı', 'olabilirim', 'olabiliriz', 'destek', 'sipariş', 'kargo', 'iade',
            'fatura', 'kampanya', 'müşteri', 'temsilci', 'şikayet', 'teşekkür', 'rica',
            'bilgi', 'sorgulama', 'takip', 'durum', 'talep', 'çözüm', 'iptal', 'onay'
        ]
    
    def analyze(self, text: str) -> Dict:
        """Cümleyi analiz et ve detaylı bağlam bilgisi döndür"""
        if not text:
            return {}
            
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Intent detection
        intents = self._detect_intents(text_lower)
        
        # Topic detection
        topics = self._detect_topics(text_lower)
        
        # Sentence type
        sentence_type = self._detect_sentence_type(text_lower)
        
        # Context summary
        context = {
            'intents': intents,
            'topics': topics,
            'sentence_type': sentence_type,
            'word_count': len(words),
            'last_words': words[-3:] if len(words) >= 3 else words,
            'is_question': 'question' in intents or sentence_type == 'question',
            'is_greeting': 'greeting' in intents,
            'needs_help': 'help' in intents,
            'is_negative': 'problem' in intents or 'reject' in intents or 'cancel' in intents,
            'is_positive': 'thanks' in intents or 'confirm' in intents,
            'is_customer_service': 'customer_service' in intents or 'customer_service' in topics
        }
        
        return context
    
    def _detect_intents(self, text: str) -> List[str]:
        """Intent'leri tespit et"""
        detected = []
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(intent)
                    break 
        return detected
    
    def _detect_topics(self, text: str) -> List[str]:
        """Konuları tespit et"""
        detected = []
        for topic, keywords in self.topic_keywords.items():
            count = 0
            for keyword in keywords:
                if keyword in text:
                    count += 1
            if count > 0:
                detected.append(topic)
        return detected
    
    def _detect_sentence_type(self, text: str) -> str:
        """Cümle tipini tespit et"""
        if any(char in text for char in ['?', 'mi', 'mı', 'mu', 'mü', 'mısın', 'misin']):
            return 'question'
        elif any(word in text for word in ['lütfen', 'yap', 'et', 'ver', 'getir']):
            return 'command'
        elif any(word in text for word in ['teşekkür', 'sağol', 'thanks', 'eyvallah']):
            return 'thanks'
        elif any(word in text for word in ['hayır', 'yok', 'değil', 'olmaz']):
            return 'negative'
        else:
            return 'statement'
    
    def generate_smart_responses(self, context: Dict) -> List[Dict]:
        """Bağlama göre AKILLI hazır cevaplar/tamamlamalar üretir"""
        responses = []
        
        # 1. Giriş / Selamlaşma
        if context.get('is_greeting'):
            responses.extend([
                "Merhabalar, size nasıl yardımcı olabilirim?",
                "Selamlar, hoş geldiniz!",
                "Merhaba, bugün sizin için ne yapabilirim?"
            ])
            
        # 2. Yardım Talebi
        if context.get('needs_help'):
            responses.extend([
                "Elbette, size hemen yardımcı olayım.",
                "Hangi konuda desteğe ihtiyacınız var?",
                "Memnuniyetle yardımcı olurum, sorunuz nedir?"
            ])
            
        # 3. Sipariş / Kargo
        if 'order' in context.get('intents', []) or 'order' in context.get('topics', []):
            responses.extend([
                "Sipariş numaranızı alabilir miyim?",
                "Sipariş durumunuzu kontrol ediyorum.",
                "Kargonuz yola çıkmış durumda."
            ])
            
        # 4. Sorun / Şikayet
        if context.get('is_negative') or 'problem' in context.get('intents', []):
            responses.extend([
                "Yaşadığınız sorun için çok üzgünüm.",
                "Bu durumu hemen düzeltelim, lütfen detay verir misiniz?",
                "Teknik ekibimize iletiyorum, anlayışınız için teşekkürler."
            ])
            
        # 5. Onaylama
        if 'confirm' in context.get('intents', []):
            responses.extend([
                "Harika, işleminiz onaylandı.",
                "Tamamdır, kaydınızı aldım.",
                "Anlaşıldı, hemen ilgileniyorum."
            ])
            
        # 6. Teşekkür
        if 'thanks' in context.get('intents', []):
            responses.extend([
                "Rica ederim, her zaman bekleriz!",
                "Ne demek, görevimiz.",
                "Ben teşekkür ederim, iyi günler dilerim."
            ])
            
        # Formatla
        return [{'text': r, 'type': 'smart_response', 'score': 15.0, 'description': 'Akıllı Yanıt', 'source': 'context_ai'} for r in responses]

    def filter_suggestions_by_context(self, suggestions: List[Dict], context: Dict) -> List[Dict]:
        """Önerileri bağlama göre filtrele ve sırala - GELİŞMİŞ ALGORİTMA"""
        if not suggestions:
            return suggestions
        
        last_words = context.get('last_words', [])
        last_word = last_words[-1] if last_words else ''
        
        # Akıllı yanıtları ekle (eğer uygunsa)
        smart_responses = self.generate_smart_responses(context)
        if smart_responses:
             suggestions.extend(smart_responses)

        for sug in suggestions:
            score_boost = 0.0
            sug_text = sug.get('text', '').lower()
            
            # 1. Prefix Match (En Önemli)
            if last_word and len(last_word) >= 2:
                if sug_text.startswith(last_word):
                    score_boost += 15.0  # Çok yüksek bonus
                elif last_word in sug_text:
                    score_boost += 5.0
            
            # 2. Intent Matching
            for intent in context.get('intents', []):
                # Intent ile ilgili kelimeleri boostla
                 patterns = self.intent_patterns.get(intent, [])
                 # Basit bir kontrol: intent patterns içindeki kelimeler öneride geçiyor mu?
                 # (Regex listesi olduğu için tam eşleşme zor, basit kelime kontrolü yapalım)
                 if intent == 'help' and any(x in sug_text for x in ['yardım', 'destek', 'çözüm']):
                     score_boost += 5.0
                 if intent == 'greeting' and any(x in sug_text for x in ['merhaba', 'selam']):
                     score_boost += 5.0
            
            # 3. Topic Matching
            for topic in context.get('topics', []):
                topic_keywords = self.topic_keywords.get(topic, [])
                if any(keyword in sug_text for keyword in topic_keywords):
                    score_boost += 3.0
            
            # 4. Contextual Flow (Önceki kelimelere göre)
            # Örneğin "bir" den sonra "şey", "tane", "adet" gelir
            if last_word == 'bir':
                if sug_text in ['şey', 'tane', 'adet', 'defa', 'kere', 'az', 'çok']:
                    score_boost += 10.0
            if last_word == 'nasıl':
                if sug_text in ['yardımcı', 'bir', 'yani', 'oldu']:
                    score_boost += 10.0

            # Score'u güncelle
            if 'score' in sug:
                sug['score'] += score_boost
            else:
                sug['score'] = score_boost
        
        # Skora göre sırala
        suggestions.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return suggestions
    
    def get_contextual_suggestions(self, text: str, base_suggestions: List[Dict]) -> List[Dict]:
        """Bağlama göre önerileri döndür"""
        context = self.analyze(text)
        filtered = self.filter_suggestions_by_context(base_suggestions, context)
        
        # Context bilgisini ekle
        for sug in filtered:
            sug['context'] = {
                'intents': context.get('intents', []),
                'topics': context.get('topics', [])
            }
        
        return filtered

# Global instance
context_analyzer = ContextAnalyzer()
