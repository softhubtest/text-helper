"""
Medium Dictionary for Fallback Suggestions
Basic Turkish vocabulary + Customer Service phrases
"""

MEDIUM_DICTIONARY_WORDS = [
    # Selamlaşma / Greeting
    "merhaba", "merhabalar", "selam", "selamlar", "iyi günler", "iyi akşamlar", "iyi geceler",
    "günaydın", "hoş geldiniz", "hoş bulduk", "nasılsınız", "iyiyim",
    
    # Müşteri Hizmetleri Genel
    "müşteri", "hizmet", "hizmetleri", "temsilci", "temsilcisi", "destek", "yardım",
    "çözüm", "talep", "şikayet", "öneri", "memnuniyet", "anket", "iletişim",
    "bağlanmak", "görüşmek", "konuşmak", "bekliyorum", "bekleme", "sırada",
    
    # Sipariş & Kargo
    "sipariş", "kargo", "teslimat", "paket", "gönderi", "ürün", "sepet", "stok",
    "takip", "durum", "nerede", "hazırlanıyor", "yolda", "dağıtımda", "ulaşmadı",
    "gecikme", "adres", "teslim", "almadım", "gelmedi", "iade", "değişim",
    "hasarlı", "eksik", "yanlış", "kusurlu", "bozuk", "garanti",
    
    # Ödeme & Fatura
    "fatura", "ödeme", "ücret", "fiyat", "tutar", "borç", "bakiye", "kredi",
    "kart", "havale", "eft", "taksit", "peşin", "nakit", "iade", "para",
    "hesap", "dekont", "makbuz", "kampanya", "indirim", "kupon", "kod",
    
    # Teknik & Hesap
    "giriş", "şifre", "parola", "unuttum", "yenileme", "güncelleme", "hata",
    "sorun", "çalışmıyor", "açılmıyor", "dondu", "yavaş", "internet", "bağlantı",
    "uygulama", "web", "sitesi", "mobil", "telefon", "bilgisayar", "tablet",
    "profil", "ayarlar", "bildirim", "sms", "email", "posta", "onay",
    
    # Eylemler / Verbs
    "yapmak", "etmek", "olmak", "istemek", "almak", "vermek", "gitmek", "gelmek",
    "bakmak", "görmek", "duymak", "bilmek", "sanmak", "durmak", "kalkmak",
    "başlamak", "bitirmek", "sormak", "cevaplamak", "yazmak", "okumak",
    "iptal", "onaylamak", "reddetmek", "beklemek", "acele", "kontrol",
    
    # Soru Kelimeleri
    "nasıl", "ne", "neden", "niçin", "kim", "hangi", "nerede", "nereye",
    "kaç", "kaçta", "ne zaman", "mı", "mi", "mu", "mü",
    
    # Zaman
    "şimdi", "hemen", "bugün", "yarın", "dün", "sabah", "öğle", "akşam",
    "gece", "hafta", "ay", "yıl", "süre", "dakika", "saat", "gün",
    
    # Bağlaçlar ve Diğerleri
    "ve", "veya", "ile", "ama", "fakat", "ancak", "çünkü", "bu", "şu", "o",
    "için", "gibi", "kadar", "dha", "daha", "en", "çok", "az", "biraz",
    "lütfen", "teşekkür", "rica", "tabii", "peki", "tamam", "olur", "evet", "hayır"
]

class MediumDictionary:
    """Orta ölçekli yedek sözlük"""
    
    def __init__(self):
        self.words = sorted(list(set(MEDIUM_DICTIONARY_WORDS)))
        
    def search(self, prefix: str, max_results: int = 20) -> list:
        """Prefix'e göre arama yap"""
        if not prefix:
            return []
            
        prefix_lower = prefix.lower().strip()
        results = []
        
        for word in self.words:
            word_lower = word.lower()
            
            # Tam prefix eşleşmesi
            if word_lower.startswith(prefix_lower):
                score = 10.0
                
                # Uzunluk farkı cezası (kısa kelimeler öne çıksın diye değil, yakın uzunluktakiler)
                len_diff = len(word_lower) - len(prefix_lower)
                score -= len_diff * 0.1
                
                results.append({
                    'word': word,
                    'score': max(1.0, score),
                    'source': 'medium_dictionary'
                })
                
        # Skora göre sırala
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]

# Global instance
medium_dictionary = MediumDictionary()
