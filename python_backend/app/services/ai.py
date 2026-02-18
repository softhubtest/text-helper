import os
from typing import List
from app.models.schemas import Suggestion
from app.core.config import settings
from app.core.logs import logger

# Global import for optional dependencies
try:
    from transformer_model import transformer_model
    REAL_TRANSFORMER_AVAILABLE = True
except ImportError:
    REAL_TRANSFORMER_AVAILABLE = False
    transformer_model = None

class TransformerPredictor:
    """AI tabanlı tahminler için Transformer modeli"""
    
    def __init__(self):
        self.model_loaded = False
        self.model = None
        self.tokenizer = None
        self.use_transformer = settings.USE_TRANSFORMER
        
    async def load_model(self):
        """Transformer modelini yükle"""
        # Model varsa kullan
        if REAL_TRANSFORMER_AVAILABLE and transformer_model:
            await transformer_model.load_model()
            self.model_loaded = transformer_model.model_loaded
            if self.model_loaded:
                logger.info("Model yuklendi")
                return
        
        # Fallback (sadece model yoksa)
        if not self.use_transformer and not self.model_loaded:
            logger.info("Model devre disi")
            return
            
        try:
            # Hugging Face transformers
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            logger.info("Model yukleniyor...")
            # GPT-2 modeli
            model_name = "ytu-ce-cosmos/turkish-gpt2-medium"
            
            # Local model check
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            local_model_path = os.path.join(base_dir, "models", "turkish-gpt2-medium")
            
            if os.path.exists(local_model_path):
                logger.info(f"Offline model bulundu: {local_model_path}")
                model_name = local_model_path
            else:
                logger.info(f"Offline model bulunamadi, internetten indirilecek: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=os.path.exists(local_model_path))
            self.model = AutoModelForCausalLM.from_pretrained(model_name, local_files_only=os.path.exists(local_model_path))
            self.model.eval()  # Evaluation mode
            
            self.model_loaded = True
            logger.info("Model hazir")
        except ImportError:
            logger.warning("transformers eksik (pip install transformers torch)")
            self.model_loaded = False
        except Exception as e:
            logger.warning(f"Model yuklenemedi: {e}")
            self.model_loaded = False
    
    async def predict(self, text: str, max_suggestions: int = 5) -> List[Suggestion]:
        """AI ile tahmin yap"""
        # Model varsa kullan
        if REAL_TRANSFORMER_AVAILABLE and transformer_model and transformer_model.model_loaded:
            results = await transformer_model.predict(text, max_suggestions)
            return [Suggestion(**r) for r in results]
        
        if not self.model_loaded:
            return self._fallback_predictions(text, max_suggestions)
        
        try:
            import torch
            # Gerçek transformer tahmini
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs['input_ids'].shape[1] + 20,
                    num_return_sequences=max_suggestions,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            suggestions = []
            for output in outputs:
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                # Son kelimeyi al
                last_word = generated_text.split()[-1] if generated_text.split() else ""
                
                if last_word and last_word not in [s.text for s in suggestions]:
                    suggestions.append(Suggestion(
                        text=last_word,
                        type="ai_prediction",
                        score=9.5,
                        description="AI tahmini (Transformer)",
                        source="transformer"
                    ))
            
            return suggestions[:max_suggestions]
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            return self._fallback_predictions(text, max_suggestions)
    
    def _fallback_predictions(self, text: str, max_suggestions: int) -> List[Suggestion]:
        """Fallback: Basit kurallar"""
        suggestions = []
        words = text.split()
        last_word = words[-1].lower() if words else text.lower()
        
        # Türkçe pattern'ler
        patterns = {
            'man': ['mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal'],
            'nas': ['nasıl', 'nasıl yardımcı', 'nasıl olabilirim', 'nasıl yapabilirim'],
            'mer': ['merhaba', 'merhaba size', 'merhaba nasıl', 'merhaba hoş'],
            'teş': ['teşekkür', 'teşekkürler', 'teşekkür ederim', 'teşekkür ederiz'],
            'yar': ['yardım', 'yardımcı', 'yardımcı olabilirim', 'yardım etmek'],
            'müs': ['müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti'],
            'sip': ['sipariş', 'siparişiniz', 'sipariş takibi', 'sipariş durumu'],
            'ara': ['ara', 'araba', 'arama', 'aramak', 'arayabilirsiniz'],
            'aç': ['açık', 'açmak', 'açıklama', 'açıklamak', 'açıklayabilirim'],
        }
        
        prefix = last_word[:3] if len(last_word) >= 3 else last_word
        if prefix in patterns:
            for word in patterns[prefix][:max_suggestions]:
                suggestions.append(Suggestion(
                    text=word,
                    type="ai_prediction",
                    score=9.0,
                    description="AI tahmini (Pattern)",
                    source="transformer"
                ))
        
        return suggestions

transformer_predictor = TransformerPredictor()
