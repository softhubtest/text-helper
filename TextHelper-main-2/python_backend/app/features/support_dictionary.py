"""
Müşteri Hizmetleri ve Destek Sözlüğü (Domain Specific)
Marka bağımsız, genel destek terimlerini içerir.
"""

# Genel Müşteri Hizmetleri Kalıpları
SUPPORT_PHRASES = [
    # Açılış / Selamlaşma
    "merhaba size nasıl yardımcı olabilirim",
    "nasıl yardımcı olabilirim",
    "size nasıl destek olabilirim",
    "merhaba hoş geldiniz",
    "iyi günler dilerim",
    
    # Kapanış
    "başka bir arzunuz var mı",
    "başka bir sorunuz var mı",
    "yardımcı olabileceğim başka bir konu var mı",
    "iyi günler dileriz",
    "keyifli alışverişler dileriz",
    "sağlıklı günler dileriz",
    
    # Anlama / Onay
    "anladım kontrol ediyorum",
    "sizi çok iyi anlıyorum",
    "hemen kontrol ediyorum",
    "lütfen hatta kalınız",
    "kısa bir süre bekleteceğim",
]

# Anahtar Kelimeler (Yüksek Öncelik - 3x Boost)
SUPPORT_KEYWORDS = {
    # Genel İşlemler
    "yardım", "destek", "bilgi", "talep", "şikayet", "öneri",
    "işlem", "başvuru", "iptal", "iade", "değişim", "onay",
    
    # E-Ticaret
    "sipariş", "kargo", "teslimat", "paket", "ürün", "stok",
    "sepet", "ödeme", "fatura", "kampanya", "indirim", "kupon",
    "beden", "renk", "adres", "teslim", "takip", "numarası",
    
    # Telekomünikasyon
    "tarife", "paket", "internet", "dakika", "sms", "fatura",
    "borç", "alacak", "tl", "bakiye", "yükleme", "hat",
    "numara", "taşıma", "iptal", "dondurma", "nakil", "devir",
    "kota", "aşım", "hız", "fiber", "modem", "kurulum",
}

# Yasaklı Marka İsimleri (Filtrelenecek)
BRAND_NAMES = {
    "vodafone", "turkcell", "türk telekom", "bimcell", "pttcell",
    "trendyol", "hepsiburada", "amazon", "n11", "çiçeksepeti",
    "getir", "yemeksepeti", "migros", "carrefour", "şok", "bim", "a101",
    "apple", "samsung", "huawei", "xiaomi", "oppo",
    "nike", "adidas", "puma", "zara", "mango", "lc waikiki", "defacto"
}

def is_support_term(word: str) -> bool:
    """Kelime destek terimi mi?"""
    return word.lower() in SUPPORT_KEYWORDS

def is_brand_name(word: str) -> bool:
    """Kelime marka ismi mi?"""
    return word.lower() in BRAND_NAMES
