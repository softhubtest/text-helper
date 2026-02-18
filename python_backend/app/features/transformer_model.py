"""
Gerçek Transformer Modeli Entegrasyonu
Türkçe BERT/GPT modelleri ile AI tahminleri
"""

import os
from typing import List, Optional
import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor

class RealTransformerModel:
    """Gerçek Transformer modeli"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        # Geçerli Türkçe modeller (fallback ile)
        # Geçerli modeller: gorkemgoknar/gpt2-small-turkish, ytu-ce-cosmos/turkish-gpt2, ytu-ce-cosmos/turkish-gpt2-large
        default_model = os.getenv("TRANSFORMER_MODEL", "gorkemgoknar/gpt2-small-turkish")
        self.model_name = default_model
        self.fallback_models = [
            "gorkemgoknar/gpt2-small-turkish",
            "ytu-ce-cosmos/turkish-gpt2",
            "gorkemgoknar/gpt2-turkish-writer"
        ]
        self.use_gpu = torch.cuda.is_available() and os.getenv("USE_GPU", "false").lower() == "true"
        
    async def load_model(self, timeout_seconds: int = 60):
        """Transformer modelini yükle (timeout ile - takılmayı önler)"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            print(f"[INFO] Transformer modeli yukleniyor: {self.model_name} (timeout: {timeout_seconds}s)")
            
            # Thread pool executor ile senkron işlemi asenkron yap
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            
            try:
                # Timeout ile yükleme
                await asyncio.wait_for(
                    loop.run_in_executor(executor, self._load_model_sync),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                print(f"[WARNING] Transformer yukleme timeout ({timeout_seconds}s) - atlaniyor")
                print("[INFO] Bellek yetersiz veya model cok buyuk - Transformer devre disi")
                self.model_loaded = False
                executor.shutdown(wait=False)
                return
            except Exception as e:
                executor.shutdown(wait=False)
                raise e
            finally:
                executor.shutdown(wait=False)
                
        except ImportError:
            print("[WARNING] transformers kutuphanesi kurulu degil")
            print("   Kurulum: pip install transformers torch")
            self.model_loaded = False
        except Exception as e:
            error_msg = str(e)
            if "not enough memory" in error_msg.lower() or "memory" in error_msg.lower():
                print(f"[WARNING] Bellek yetersiz: {error_msg}")
                print("[INFO] Transformer modelleri cok buyuk - Transformer devre disi")
            else:
                print(f"[WARNING] Transformer modeli yuklenemedi: {e}")
            # Fallback sistemine geç (daha kısa timeout)
            await self._try_fallback_models(timeout_seconds=30)
    
    def _load_model_sync(self):
        """Senkron model yükleme (ThreadPoolExecutor için)"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Tokenizer yükle
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Model yükle (daha az bellek kullanımı için)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.use_gpu else torch.float32,
            low_cpu_mem_usage=True,  # Daha az bellek kullan
            device_map="auto" if self.use_gpu else None
        )
        
        # INT8 Dynamic Quantization (CPU only - ~75% memory reduction)
        if not self.use_gpu:
            try:
                print("[INFO] INT8 quantization uygulanıyor (bellek tasarrufu)...")
                self.model = torch.quantization.quantize_dynamic(
                    self.model,
                    {torch.nn.Linear},
                    dtype=torch.qint8
                )
                print("[OK] INT8 quantization tamamlandı")
            except Exception as e:
                print(f"[WARNING] Quantization hatası (devam ediliyor): {e}")
        
        if self.use_gpu:
            self.model = self.model.cuda()
        self.model.eval()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model_loaded = True
        print(f"[OK] Transformer modeli hazir: {self.model_name} (GPU: {self.use_gpu})")
    
    async def _try_fallback_models(self, timeout_seconds: int = 30):
        """Fallback modelleri dene (kısa timeout)"""
        model_tried = self.model_name
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        
        for fallback_model in self.fallback_models:
            if fallback_model == model_tried:
                continue  # Zaten denendi
            try:
                print(f"[INFO] Fallback model deneniyor: {fallback_model} (timeout: {timeout_seconds}s)")
                self.model_name = fallback_model
                
                try:
                    await asyncio.wait_for(
                        loop.run_in_executor(executor, self._load_fallback_model, fallback_model),
                        timeout=timeout_seconds
                    )
                    print(f"[OK] Fallback model yuklendi: {self.model_name} (GPU: {self.use_gpu})")
                    executor.shutdown(wait=False)
                    return  # Başarılı
                except asyncio.TimeoutError:
                    print(f"[WARNING] {fallback_model} timeout ({timeout_seconds}s) - atlaniyor")
                    continue
                except Exception as e2:
                    error_msg = str(e2)
                    if "not enough memory" in error_msg.lower():
                        print(f"[WARNING] {fallback_model} - Bellek yetersiz, atlaniyor")
                    else:
                        print(f"[WARNING] {fallback_model} yuklenemedi: {e2}")
                    continue
            except Exception as e:
                print(f"[WARNING] {fallback_model} hatasi: {e}")
                continue
        
        executor.shutdown(wait=False)
        
        # Tüm modeller başarısız
        print("[WARNING] Tum Transformer modelleri yuklenemedi (bellek yetersiz veya timeout)")
        print("[INFO] Transformer kullanilmayacak, diger yontemler kullanilacak")
        print("[INFO] Sistem normal calisacak (sozluk, N-gram, vb.)")
        self.model_loaded = False
    
    def _load_fallback_model(self, model_name: str):
        """Fallback model yükleme (senkron)"""
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.use_gpu else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto" if self.use_gpu else None
        )
        if self.use_gpu:
            self.model = self.model.cuda()
        self.model.eval()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model_loaded = True
    
    async def predict(self, text: str, max_suggestions: int = 5) -> List[dict]:
        """AI ile tahmin yap"""
        if not self.model_loaded:
            return []
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )
            
            if self.use_gpu:
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=inputs['input_ids'].shape[1] + 20,
                    num_return_sequences=max_suggestions,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            suggestions = []
            seen = set()
            
            for output in outputs:
                # Decode
                generated_text = self.tokenizer.decode(output, skip_special_tokens=True)
                
                # Orijinal metni çıkar
                if generated_text.startswith(text):
                    continuation = generated_text[len(text):].strip()
                    words = continuation.split()
                    
                    if words:
                        next_word = words[0]
                        if next_word.lower() not in seen:
                            seen.add(next_word.lower())
                            suggestions.append({
                                'text': next_word,
                                'score': 9.5,
                                'type': 'ai_prediction',
                                'description': 'AI tahmini (Transformer)',
                                'source': 'transformer'
                            })
                            
                            if len(suggestions) >= max_suggestions:
                                break
            
            return suggestions
            
        except Exception as e:
            print(f"Transformer tahmin hatası: {e}")
            return []
    
    def get_model_info(self):
        """Model bilgileri"""
        return {
            "loaded": self.model_loaded,
            "model_name": self.model_name,
            "gpu_available": self.use_gpu,
            "parameters": sum(p.numel() for p in self.model.parameters()) if self.model else 0
        }

# Lazy Singleton Pattern - Load model only when first accessed
_transformer_model_instance = None

def get_transformer_model():
    """Get or create transformer model (lazy loading)"""
    global _transformer_model_instance
    if _transformer_model_instance is None:
        _transformer_model_instance = RealTransformerModel()
    return _transformer_model_instance

# Backwards compatibility - lazy proxy
class _LazyTransformerProxy:
    def __getattr__(self, name):
        instance = get_transformer_model()
        return getattr(instance, name)

transformer_model = _LazyTransformerProxy()
