import os
from typing import List, Optional
from app.models.schemas import Suggestion
from app.core.config import settings
from app.core.logs import logger

# ============================================================
# Musteri Hizmetleri Kelime Listesi Yukleyici
# ============================================================

def _load_customer_service_words() -> List[str]:
    """customer_service_words.txt dosyasini yukle"""
    words = []
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        word_file = os.path.join(data_dir, "customer_service_words.txt")
        if os.path.exists(word_file):
            with open(word_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        words.append(line)
            logger.info(f"Musteri hizmetleri kelime listesi yuklendi: {len(words)} girdi")
        else:
            logger.warning(f"Kelime listesi bulunamadi: {word_file}")
    except Exception as e:
        logger.error(f"Kelime listesi yuklenemedi: {e}")
    return words

# Uygulama baslangicinda bir kez yukle
CUSTOMER_SERVICE_WORDS: List[str] = _load_customer_service_words()

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
            
            # Model yükleme (Memory Optimized)
            import torch
            from torch.quantization import quantize_dynamic
            
            logger.info(f"Model yukleniyor: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=os.path.exists(local_model_path))
            
            # 1. Adım: Modeli CPU'ya normal yükle (low_cpu_mem_usage ile RAM spike engelle)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, 
                local_files_only=os.path.exists(local_model_path),
                low_cpu_mem_usage=True
            )
            
            # 2. Adım: Dynamic Quantization (Boyutu yariya indirir: 32-bit -> 8-bit)
            logger.info("Model optimize ediliyor (Quantization)...")
            self.model = quantize_dynamic(
                self.model, {torch.nn.Linear}, dtype=torch.qint8
            )
            
            # 3. Adım: Thread sayisini sinirla (CPU verimliligi)
            torch.set_num_threads(2)
            
            self.model.eval()  # Evaluation mode
            
            self.model_loaded = True
            logger.info("Model hazir (Ozgur surum icin optimize edildi)")
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
        """
        3 katmanli akilli eslestirme motoru:
          1. Son kelime -> ifadenin ILK kelimesinin basiyla esles (yuksek skor)
          2. Son 2 kelime -> tam ifadenin basiyla esles       (en yuksek skor)
          3. Son kelime -> ifade icindeki HERHANGI bir kelimede ara (substring)
        Bu sayede cumlenin ortasindaki bir kelimeyi yazinca da oneri gelir.
        """
        suggestions_set = []
        seen = set()
        text_lower = text.lower().strip()
        words = text_lower.split()
        last_word = words[-1] if words else text_lower

        # KATMAN 1: Son kelime -> ifadenin ilk kelimesinin basi
        if len(last_word) >= 2:
            for entry in CUSTOMER_SERVICE_WORDS:
                entry_lower = entry.lower()
                first_word_of_entry = entry_lower.split()[0]
                if first_word_of_entry.startswith(last_word) and entry not in seen:
                    seen.add(entry)
                    score = 9.0 + min(len(last_word) * 0.15, 0.9)
                    suggestions_set.append((entry, score))

        # KATMAN 2: Son 2 kelime -> tam ifade basi
        if len(words) >= 2:
            phrase_prefix = " ".join(words[-2:])
            for entry in CUSTOMER_SERVICE_WORDS:
                if entry.lower().startswith(phrase_prefix) and entry not in seen:
                    seen.add(entry)
                    suggestions_set.append((entry, 9.95))

        # KATMAN 3: Son kelime -> ifade icindeki herhangi bir kelimenin basi
        if len(last_word) >= 3:
            for entry in CUSTOMER_SERVICE_WORDS:
                if entry in seen:
                    continue
                entry_words = entry.lower().split()
                if any(w.startswith(last_word) for w in entry_words):
                    seen.add(entry)
                    suggestions_set.append((entry, 8.5))

        # Skora gore sirala, esit skorlarda alfabe sirasi
        suggestions_set.sort(key=lambda x: (-x[1], x[0]))

        return [
            Suggestion(
                text=text_val,
                type="ai_prediction",
                score=round(score, 1),
                description="Musteri Hizmetleri Onerileri",
                source="dictionary"
            )
            for text_val, score in suggestions_set[:max_suggestions]
        ]

transformer_predictor = TransformerPredictor()
