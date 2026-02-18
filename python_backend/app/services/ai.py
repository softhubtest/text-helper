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
        """Fallback: Kapsamli Turkce kelime onerileri (Model olmadan yuksek kalite)"""
        suggestions = []
        words = text.split()
        last_word = words[-1].lower() if words else text.lower()
        
        # Kapsamli Turkce musteri hizmetleri pattern'leri
        patterns = {
            # A
            'aca': ['acaba', 'acaba nasıl', 'acaba ne zaman'],
            'aç': ['açık', 'açıklama', 'açıklamak istiyorum', 'açıkça belirtmek isterim'],
            'aci': ['acil', 'acil yardım', 'acil durum', 'acil olarak'],
            'ale': ['alerji', 'alerjik', 'alerji durumunda'],
            'ali': ['alındı', 'alındı bildirimi', 'alınmadı'],
            'alt': ['alternatif', 'alternatif çözüm', 'alternatif ürün'],
            'ana': ['anlaşılması', 'anladım', 'anlamıyorum', 'anlatabilir misiniz'],
            'ara': ['arama', 'arayabilirsiniz', 'aramak istiyorum', 'aranacak'],
            'asıl': ['asıl sorun', 'asıl mesele', 'asıl konu'],
            'ası': ['asıl mesele', 'asistan', 'asistanınız'],

            # B
            'bağ': ['bağlantı', 'bağlantı sorunu', 'bağlantı hatası', 'bağlantı kurulamıyor'],
            'bak': ['bakım', 'bakım hizmeti', 'bakmak istiyorum'],
            'bay': ['bayiler', 'bayiiniz', 'bayi noktaları'],
            'bek': ['bekliyorum', 'bekleme süresi', 'beklemek istemiyorum'],
            'bil': ['bilgi', 'bilgi almak istiyorum', 'bilgilendirme', 'bilmiyorum'],
            'bir': ['birkaç gün', 'birkaç saat', 'birkaç dakika', 'bir sorun yaşadım'],
            'böy': ['böyle bir durum', 'böyle olmamalı', 'böyle devam edemez'],
            'bun': ['bundan sonra', 'bunun için', 'bununla ilgili', 'bunun çözümü'],

            # C-Ç
            'can': ['canlı destek', 'canlı yardım', 'canlı görüşme'],
            'çal': ['çalışmıyor', 'çalışmıyor sistemde', 'çalışmayan ürün'],
            'çöz': ['çözüm', 'çözüm öneriniz', 'çözüm bekliyorum', 'çözülmedi'],

            # D
            'dan': ['danışmak istiyorum', 'danışma hattı'],
            'dep': ['depozito', 'depo', 'depolama'],
            'des': ['destek', 'destek almak istiyorum', 'destek hattı', 'destek ekibi'],
            'det': ['detaylı bilgi', 'detayları öğrenmek istiyorum'],
            'diy': ['diyorum ki', 'diyelim ki'],
            'dur': ['durum', 'durum sorgulama', 'durumum nedir'],

            # E
            'eks': ['eksik', 'eksik ürün', 'eksik parça', 'eksiklik var'],
            'ele': ['elektronik fatura', 'elektronik bildirim'],
            'ert': ['ertelendi', 'erteleme istiyorum'],
            'eso': ['esorgu', 'eş zamanlı'],

            # F
            'fat': ['fatura', 'fatura sorunu', 'fatura itirazı', 'fatura iptali'],
            'fiy': ['fiyat', 'fiyat bilgisi', 'fiyat listesi', 'fiyat farkı'],

            # G
            'gar': ['garanti', 'garanti kapsamı', 'garanti süresi', 'garanti belgesi'],
            'gec': ['gecikmeli', 'gecikme', 'gecikme nedeni', 'gecikme sorunu'],
            'gel': ['gelecek', 'gelecek mi', 'geliş tarihi', 'gelebilir misiniz'],
            'ger': ['gereken', 'gerekli belgeler', 'gereksinim', 'geri ödeme'],
            'gönd': ['gönderim', 'gönderildi', 'gönderim tarihi', 'gönderim takibi'],
            'gör': ['görüşmek istiyorum', 'görüşme talebi', 'görüştüm'],
            'güz': ['güzel', 'güzellik', 'güzel hizmet aldım'],

            # H
            'has': ['hasarlı', 'hasar', 'hasar tespiti', 'hasar bildirimi'],
            'hes': ['hesap', 'hesap bilgileri', 'hesabım kapalı', 'hesap açma'],
            'hız': ['hızlı', 'hızlı çözüm', 'hızlı dönüş'],
            'hiz': ['hizmet', 'hizmet kalitesi', 'hizmet bedeli', 'hizmet talebi'],

            # İ
            'iade': ['iade', 'iade talebi', 'iade ettim', 'iade süreci', 'iade edilmedi'],
            'ipa': ['iptal', 'iptal talebi', 'iptal ettim', 'iptal süreci'],
            'ist': ['istiyorum', 'istek', 'isteğim var', 'isteğimi iletmek istiyorum'],
            'iyi': ['iyiyim teşekkürler', 'iyi günler', 'iyi akşamlar'],

            # K
            'kal': ['kaldırma', 'kalite', 'kalite sorunu', 'kalitesiz ürün'],
            'kar': ['kargo', 'kargo takibi', 'kargo hasarı', 'kargo kayıp'],
            'kat': ['katılım', 'katılmak istiyorum'],
            'kay': ['kayıp', 'kayıt', 'kayıt numarası', 'kayıt olmak istiyorum'],
            'kod': ['kod', 'kod numarası', 'promosyon kodu'],
            'kon': ['konu', 'konuşmak istiyorum', 'konuyla ilgili'],
            'kul': ['kullanıcı', 'kullanım kılavuzu', 'kullanım sorunu', 'kullanıcı adı'],

            # M
            'man': ['mantık', 'mantıklı değil', 'manzara'],
            'mer': ['merhaba', 'merhaba, nasıl yardımcı olabilirim', 'merhaba, teşekkürler'],
            'müş': ['müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti', 'müşteri numarası'],

            # N
            'nas': ['nasıl', 'nasıl yardımcı olabilirim', 'nasıl bir sorun var'],
            'nere': ['nerede', 'nereye başvurabilirim', 'nereden alabilirim'],
            'num': ['numara', 'numaram nedir', 'numara değişikliği'],

            # O
            'ode': ['ödeme', 'ödeme yaptım', 'ödeme sorunu', 'ödeme onayı', 'ödeme iadesi'],
            'ola': ['olabilir mi', 'olası', 'olabildiğince hızlı'],
            'onay': ['onay', 'onaylandı mı', 'onay bekliyorum'],

            # P
            'par': ['parça', 'para iadesi', 'parça değişimi'],
            'pas': ['pasif', 'pasif hesap', 'pasoligim'],
            'pro': ['promosyon', 'promo kodu', 'problem'],

            # S
            'sağ': ['sağ olun', 'sağlık', 'sağ olun teşekkürler'],
            'ser': ['servis', 'servis talebi', 'servis noktası'],
            'sip': ['sipariş', 'siparişim', 'sipariş takibi', 'sipariş iptal', 'sipariş onayı'],
            'sor': ['sorun', 'sorunum var', 'sorunum çözülmedi', 'sorunu bildirmek istiyorum'],
            'şik': ['şikayet', 'şikayet etmek istiyorum', 'şikayetim var'],

            # T
            'tak': ['takip', 'takip numarası', 'takibini yapabilir miyim'],
            'tal': ['talep', 'talep açmak istiyorum', 'talebim var'],
            'tar': ['tarih', 'tarih değişikliği', 'tarifeler'],
            'tek': ['teknik destek', 'teknik sorun', 'tekrar', 'tekrar deniyorum'],
            'tel': ['telefon', 'telefon numarası', 'telefonda görüşebilir miyim'],
            'tes': ['teslimat', 'teslimat süresi', 'teslim alındı', 'teslim edilmedi'],
            'teş': ['teşekkür', 'teşekkürler', 'teşekkür ederim', 'teşekkür ederiz', 'teşekkürler iyi günler'],

            # U-Ü
            'ücr': ['ücretsiz', 'ücret iadesi', 'ücret bilgisi'],
            'ürü': ['ürün', 'ürün iadesi', 'ürün değişimi', 'ürün hasarlı', 'ürün bilgisi'],

            # Y
            'yar': ['yardım', 'yardımcı', 'yardımcı olabilir misiniz', 'yardım almak istiyorum'],
            'yer': ['yerine', 'yerinde inceleme', 'yetkili servis'],
            'yönet': ['yönetici', 'yöneticiye bağlar mısınız'],
            'yük': ['yükleme', 'yükleme sorunu'],

            # Z
            'zan': ['zannediyorum', 'zannetmiyorum'],
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
