"""
Machine Learning Ogrenme Sistemi
Kullanici davranisindan ogrenir
"""

from typing import List, Dict
from collections import defaultdict
import json
import os
from datetime import datetime
from app.features.redis_cache import cache

class MLLearningSystem:
    """ML tabanlı ogrenme sistemi - Redis Destekli"""
    
    def __init__(self):
        # Redis prefix'leri
        self.PREFIX_PREF = "ml:pref"
        self.PREFIX_CTX = "ml:ctx" 
        self.PREFIX_COOC = "ml:cooc"
        
        # Local memory cache (Redis yavaşlarsa veya çökerse)
        self.local_preferences = defaultdict(lambda: defaultdict(int))
        self.local_context = defaultdict(lambda: defaultdict(int))
        self.local_cooccurrence = defaultdict(lambda: defaultdict(int))
        
        # Eğer Redis yoksa diskten yükle (Fallback)
        if not cache or not cache.available:
            self.load_local_data()
    
    def learn_from_interaction(
        self,
        user_id: str,
        input_text: str,
        selected_suggestion: str,
        context: str = ""
    ):
        """Kullanıcı etkileşiminden öğren (Redis + Async)"""
        try:
            # 1. Kullanici Tercihleri (Redis Hash)
            if cache and cache.available:
                # Key: ml:pref:{user_id} -> Field: {suggestion} -> Value: count
                cache.client.hincrby(f"{self.PREFIX_PREF}:{user_id}", selected_suggestion, 1)
            else:
                self.local_preferences[user_id][selected_suggestion] += 1
            
            # 2. Bağlam Pattern'leri (Redis Hash)
            if context and cache and cache.available:
                # Context kısa olmalı ki key çok büyümesin
                short_ctx = context.strip().lower()[:50] 
                cache.client.hincrby(f"{self.PREFIX_CTX}:{short_ctx}", selected_suggestion, 1)
                # TTL ekle (Bağlam verisi 30 gün kalsın)
                cache.client.expire(f"{self.PREFIX_CTX}:{short_ctx}", 30 * 24 * 60 * 60)
            elif context:
                self.local_context[context][selected_suggestion] += 1
            
            # 3. Kelime birlikte kullanımı (Redis Hash)
            words = input_text.split()
            if len(words) > 1:
                for i in range(len(words) - 1):
                    w1, w2 = words[i], words[i+1]
                    if cache and cache.available:
                        cache.client.hincrby(f"{self.PREFIX_COOC}:{w1}", w2, 1)
                    else:
                        self.local_cooccurrence[w1][w2] += 1
            
            # Redis yoksa locale kaydet
            if not cache or not cache.available:
                self.save_local_data()
                
        except Exception as e:
            print(f"ML learning hatasi: {e}")

    def get_personalized_suggestions(
        self,
        user_id: str,
        text: str,
        base_suggestions: List[str]
    ) -> List[Dict]:
        """Kişiselleştirilmiş öneriler (Redis'ten hızlı okuma)"""
        personalized = []
        
        try:
            # Redis'ten kullanıcının tüm tercihlerini çek (Tek komut)
            user_prefs = {}
            if cache and cache.available:
                user_prefs = cache.client.hgetall(f"{self.PREFIX_PREF}:{user_id}")
                # Byte -> Int conversion
                user_prefs = {k: int(v) for k, v in user_prefs.items()}
            else:
                user_prefs = self.local_preferences.get(user_id, {})

            # Kullanıcı tercihlerine göre skorla
            for suggestion in base_suggestions:
                base_score = 1.0
                user_pref = user_prefs.get(suggestion, 0)
                
                # Kullanıcı tercihi bonusu
                personalized_score = base_score + (user_pref * 0.5)
                
                personalized.append({
                    'text': suggestion,
                    'score': personalized_score,
                    'personalized': user_pref > 0
                })
        except Exception as e:
            print(f"Personalization error: {e}")
            # Fallback
            return [{'text': s, 'score': 1.0, 'personalized': False} for s in base_suggestions]
        
        # Skora göre sırala
        personalized.sort(key=lambda x: x['score'], reverse=True)
        return personalized
    
    def predict_next_word(self, context: str) -> List[str]:
        """Bağlamdan sonraki kelimeyi tahmin et"""
        words = context.split()
        if not words:
            return []
        
        last_word = words[-1].lower()
        next_words = {}
        
        try:
            if cache and cache.available:
                next_words = cache.client.hgetall(f"{self.PREFIX_COOC}:{last_word}")
                next_words = {k: int(v) for k, v in next_words.items()}
            else:
                next_words = self.local_cooccurrence.get(last_word, {})
        except Exception:
            return []
        
        # En sık kullanılanları döndür
        sorted_words = sorted(
            next_words.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [word for word, count in sorted_words[:5]]
    
    def save_local_data(self):
        """Yedek: Yerel JSON'a kaydet"""
        data_file = os.path.join(os.path.dirname(__file__), "ml_learning_data.json")
        try:
            data = {
                'user_preferences': dict(self.local_preferences),
                'context_patterns': dict(self.local_context),
                'word_cooccurrence': {k: dict(v) for k, v in self.local_cooccurrence.items()},
                'last_updated': datetime.now().isoformat()
            }
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_local_data(self):
        """Yedek: Yerel JSON'dan yükle"""
        data_file = os.path.join(os.path.dirname(__file__), "ml_learning_data.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.local_preferences = defaultdict(lambda: defaultdict(int), {k: defaultdict(int, v) for k, v in data.get('user_preferences', {}).items()})
                    self.local_context = defaultdict(lambda: defaultdict(int), {k: defaultdict(int, v) for k, v in data.get('context_patterns', {}).items()})
                    self.local_cooccurrence = defaultdict(lambda: defaultdict(int), {k: defaultdict(int, v) for k, v in data.get('word_cooccurrence', {}).items()})
            except Exception:
                pass

# Global instance
ml_learning = MLLearningSystem()
