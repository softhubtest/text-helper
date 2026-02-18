"""
ML-Based Ranking System
Machine Learning tabanlı öneri sıralama - piyasanın en iyisi için
"""

from typing import List, Dict, Optional
import json
import os
from collections import defaultdict
from datetime import datetime
import numpy as np

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    try:
        import lightgbm as lgb
        LIGHTGBM_AVAILABLE = True
    except ImportError:
        LIGHTGBM_AVAILABLE = False

class MLRankingSystem:
    """ML tabanlı ranking sistemi"""
    
    def __init__(self):
        self.model = None
        self.model_trained = False
        self.feature_names = [
            'word_frequency',
            'context_match',
            'user_preference',
            'domain_match',
            'grammar_match',
            'semantic_similarity',
            'length_score',
            'recency_score'
        ]
        self.user_selections = defaultdict(lambda: defaultdict(int))
        self.load_data()
    
    def extract_features(self, suggestion: Dict, context: Dict, user_id: str = "default") -> List[float]:
        """Öneri için feature'ları çıkar"""
        features = []
        
        # 1. Kelime frekansı (0-1 normalize)
        frequency = suggestion.get('frequency', 1)
        features.append(min(frequency / 100.0, 1.0))
        
        # 2. Context uyumu (0-1)
        context_match = 1.0 if suggestion.get('context_match', False) else 0.0
        features.append(context_match)
        
        # 3. Kullanıcı tercihi (0-1 normalize)
        suggestion_text = suggestion.get('text', '') or suggestion.get('word', '')
        user_pref = self.user_selections[user_id].get(suggestion_text.lower(), 0)
        features.append(min(user_pref / 10.0, 1.0))
        
        # 4. Domain uyumu (0-1)
        domain_match = 1.0 if suggestion.get('domain_match', False) else 0.0
        features.append(domain_match)
        
        # 5. Gramer uyumu (0-1)
        grammar_match = 1.0 if suggestion.get('grammar_match', False) else 0.0
        features.append(grammar_match)
        
        # 6. Semantic similarity (0-1)
        semantic_score = suggestion.get('semantic_score', 0.0)
        features.append(min(semantic_score / 10.0, 1.0))
        
        # 7. Uzunluk skoru (kısa kelimeler öncelikli - 0-1)
        word_length = len(suggestion_text)
        length_score = 1.0 - min(word_length / 20.0, 1.0)
        features.append(length_score)
        
        # 8. Güncellik skoru (şimdilik 0.5 - zamanla öğrenilecek)
        recency_score = 0.5
        features.append(recency_score)
        
        return features
    
    def train_ranking_model(self, training_data: Optional[List[Dict]] = None):
        """Ranking modeli eğit"""
        if not XGBOOST_AVAILABLE and not LIGHTGBM_AVAILABLE:
            print("[WARNING] XGBoost veya LightGBM kurulu değil")
            print("   Kurulum: pip install xgboost veya pip install lightgbm")
            return False
        
        # Eğer training data yoksa, basit bir model oluştur
        if training_data is None:
            # Basit heuristik model (gerçek training data ile değiştirilebilir)
            print("[INFO] Basit ranking modeli oluşturuluyor...")
            self.model_trained = True
            return True
        
        try:
            # Feature extraction
            X = []
            y = []
            
            for sample in training_data:
                features = sample.get('features', [])
                label = sample.get('label', 0)  # 1 = seçildi, 0 = seçilmedi
                
                if len(features) == len(self.feature_names):
                    X.append(features)
                    y.append(label)
            
            if len(X) < 10:
                print("[WARNING] Yetersiz training data - basit model kullanılacak")
                self.model_trained = True
                return True
            
            # Model eğitimi
            if XGBOOST_AVAILABLE:
                self.model = xgb.XGBRanker(
                    objective='rank:pairwise',
                    learning_rate=0.1,
                    max_depth=6,
                    n_estimators=100
                )
                self.model.fit(X, y, group=[len(X)])
            elif LIGHTGBM_AVAILABLE:
                import lightgbm as lgb
                train_data = lgb.Dataset(X, label=y, group=[len(X)])
                self.model = lgb.train(
                    {'objective': 'lambdarank', 'metric': 'ndcg'},
                    train_data,
                    num_boost_round=100
                )
            
            self.model_trained = True
            print("[OK] ML ranking modeli eğitildi")
            return True
            
        except Exception as e:
            print(f"[WARNING] Model eğitimi hatası: {e}")
            self.model_trained = True  # Basit model kullan
            return False
    
    def rank_suggestions(
        self,
        suggestions: List[Dict],
        context: Dict,
        user_id: str = "default"
    ) -> List[Dict]:
        """ML ile sırala"""
        if not suggestions:
            return []
        
        # Feature extraction
        scored_suggestions = []
        
        for suggestion in suggestions:
            features = self.extract_features(suggestion, context, user_id)
            
            # ML model ile skorla (varsa)
            if self.model_trained and self.model is not None:
                try:
                    if XGBOOST_AVAILABLE:
                        ml_score = self.model.predict([features])[0]
                    elif LIGHTGBM_AVAILABLE:
                        ml_score = self.model.predict([features])[0]
                    else:
                        ml_score = 0.0
                except:
                    ml_score = 0.0
            else:
                # Basit heuristik skorlama (ML model yoksa)
                ml_score = self._heuristic_score(features)
            
            # Orijinal skor ile ML skorunu birleştir
            original_score = suggestion.get('score', 0.0)
            combined_score = (original_score * 0.4) + (ml_score * 10.0 * 0.6)
            
            scored_suggestions.append({
                **suggestion,
                'score': combined_score,
                'ml_score': ml_score,
                'features': features
            })
        
        # Skora göre sırala
        scored_suggestions.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_suggestions
    
    def _heuristic_score(self, features: List[float]) -> float:
        """Basit heuristik skorlama (ML model yoksa)"""
        if len(features) != len(self.feature_names):
            return 0.0
        
        # Ağırlıklı toplam
        weights = [0.15, 0.20, 0.15, 0.10, 0.10, 0.15, 0.10, 0.05]
        
        score = sum(f * w for f, w in zip(features, weights))
        return score
    
    def learn_from_selection(
        self,
        user_id: str,
        selected_suggestion: str,
        context: Dict
    ):
        """Kullanıcı seçiminden öğren"""
        suggestion_lower = selected_suggestion.lower()
        self.user_selections[user_id][suggestion_lower] += 1
        
        # Real-time learning: Anında kaydet
        self.save_data()
    
    def save_data(self):
        """Verileri kaydet"""
        data_file = os.path.join(os.path.dirname(__file__), 'ml_ranking_data.json')
        
        try:
            data = {
                'user_selections': {
                    user_id: dict(selections)
                    for user_id, selections in self.user_selections.items()
                },
                'model_trained': self.model_trained,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] ML ranking data kaydetme hatası: {e}")
    
    def load_data(self):
        """Verileri yükle"""
        data_file = os.path.join(os.path.dirname(__file__), 'ml_ranking_data.json')
        
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    user_selections = data.get('user_selections', {})
                    for user_id, selections in user_selections.items():
                        self.user_selections[user_id] = defaultdict(int, selections)
                    
                    self.model_trained = data.get('model_trained', False)
            except Exception as e:
                print(f"[WARNING] ML ranking data yükleme hatası: {e}")

# Global instance
ml_ranking = MLRankingSystem()
