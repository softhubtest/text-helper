"""
WhatsApp/iPhone benzeri akıllı tamamlama - 1–2 karakter için öncelikli kelimeler.
"m" → merhaba, müşteri, ... / "n" → nasıl, ne, ... gibi alakalı, sık kullanılan öneriler.
"""

from typing import List, Dict

# Tek harf → müşteri hizmeti + günlük sık kullanılan kelimeler (öncelik sırası)
SMART_1CHAR: Dict[str, List[str]] = {
    "m": [
        "merhaba", "müşteri", "memnun", "mesaj", "müşteri hizmetleri", "memnuniyet",
        "merhabalar", "mümkün", "mümkünse", "memnuniyet", "müşteri desteği",
    ],
    "n": [
        "nasıl", "ne", "neden", "numara", "nasıl yardımcı olabilirim", "nerede",
        "ne zaman", "nasılsınız", "nasılsın", "niçin",
    ],
    "y": [
        "yardım", "yardımcı", "yardımcı olabilirim", "yapmak", "yapabilir",
        "yardımcı olabilir misiniz", "yapabilir misiniz", "evet", "yok",
    ],
    "t": [
        "teşekkürler", "teşekkür", "teşekkür ederim", "tamam", "tabii",
        "talep", "tarih", "teslimat", "tarife",
    ],
    "s": [
        "sipariş", "selam", "sipariş takibi", "sorun", "sağolun",
        "sipariş durumu", "size", "siparişim", "siparişiniz",
    ],
    "i": [
        "iyi", "iyi günler", "isterseniz", "istemiyorum", "istiyorum",
        "iade", "ilgili", "indirim", "iyi akşamlar", "iyi geceler",
    ],
    "h": [
        "hoş", "hoş geldiniz", "hoşgeldiniz", "hayır", "hangi", "hemen",
        "hat", "hesap", "hoşça kalın",
    ],
    "g": [
        "günaydın", "gün", "güzel", "görüşmek", "görüşürüz", "günler",
    ],
    "k": [
        "kargo", "kampanya", "kusura", "kusura bakmayın", "kontrol",
    ],
    "ö": [
        "özür", "özür dilerim", "önce", "ödemek", "ödeme", "önemli",
    ],
    "a": [
        "affedersiniz", "alışveriş", "ara", "arama", "açıklama", "adres",
        "almak", "anladım", "anlıyorum",
    ],
    "b": [
        "bilgi", "bir", "biraz", "bekleyin", "bay", "bayan", "bağlantı",
    ],
    "d": [
        "destek", "detay", "desteğiniz", "durum", "değişiklik",
    ],
    "e": [
        "evet", "elbette", "evet lütfen",
    ],
    "f": [
        "fatura", "fiyat", "fark", "form",
    ],
    "l": [
        "lütfen", "lütfen yardımcı olun", "link",
    ],
    "p": [
        "problem", "port", "paket", "promosyon",
    ],
    "r": [
        "rica", "rica ederim", "randevu",
    ],
    "u": [
        "ürün", "ürün bilgisi", "ücret", "üzgünüm",
    ],
    "ü": [
        "üzgünüm", "ürün", "ücret", "ünlü",
    ],
    "ç": [
        "çözüm", "çok", "çıkış", "çalışmak",
    ],
    "ş": [
        "şikayet", "şifre", "şube",
    ],
    "o": [
        "olur", "oldu", "olmak", "onun", "ona", "olarak", "olabilir",
    ],
}

# İki harf → daha spesifik tamamlamalar
SMART_2CHAR: Dict[str, List[str]] = {
    "me": ["merhaba", "merhabalar", "memnun", "müşteri", "mesaj", "mümkün", "müşteri hizmetleri"],
    "na": ["nasıl", "nasıl yardımcı olabilirim", "nasılsınız", "nasılsın", "numara"],
    "ya": ["yardım", "yardımcı", "yardımcı olabilirim", "yapmak", "yardımcı olabilir misiniz"],
    "te": ["teşekkürler", "teşekkür", "teşekkür ederim", "tamam", "teslimat", "talep"],
    "si": ["sipariş", "sipariş takibi", "sipariş durumu", "selam", "size", "siparişim"],
    "iy": ["iyi", "iyi günler", "iyi akşamlar", "iyi geceler"],
    "ha": ["hangi", "hayır", "hemen", "hangi konuda", "hat", "hesap", "hoşça kalın"],
    "ho": ["hoş", "hoş geldiniz", "hoşgeldiniz"],
    "ka": ["kargo", "kampanya", "kusura", "kusura bakmayın"],
    "öz": ["özür", "özür dilerim"],
    "af": ["affedersiniz", "affedersin"],
    "bi": ["bilgi", "bir", "biraz"],
    "de": ["destek", "detay", "değişiklik", "desteğiniz", "durum"],
    "ev": ["evet"],
    "fa": ["fatura", "fiyat"],
    "lü": ["lütfen", "lütfen yardımcı olun"],
    "ne": ["ne", "neden", "numara", "nerede", "ne zaman"],
    "ün": ["ürün", "ücret"],
    "çö": ["çözüm", "çok"],
    "şi": ["şikayet", "şifre"],
    "sa": ["sağolun", "sağ olun"],
    "an": ["anladım", "anlıyorum", "anlamadım"],
    "ar": ["ara", "arama", "arayabilirsiniz"],
    "in": ["indirim", "internet", "inceliyorum", "iptal"],
    "ip": ["iptal", "iptal etmek"],
    "so": ["sorun", "sorgulama", "sorun çözümü"],
    "ko": ["kontrol", "kontrol etmek", "kampanya"],
    "ge": ["güncelleme", "geri", "geri dönüş"],
    "ta": ["tamam", "tabii", "tabii ki", "tarih", "talep"],
    "bu": ["bu", "burada", "buraya", "bugün", "buna", "bundan"],
    "şu": ["şu", "şunu", "şöyle", "şimdi"],
    "ol": ["olur", "oldu", "olmak", "olacak", "olabilir"],
    "ve": ["ve"],
    "iç": ["için"],
    "ön": ["önce", "önemli", "öneri"],
    "al": ["almak", "alabilir", "alım", "alışveriş"],
    "so": ["sonra", "sorun", "sorgulama"],
    "gi": ["gibi", "girin", "giriş"],
    "da": ["daha", "da", "durum", "değişiklik"],
}

# 3 karakter → daha da spesifik (mer→merhaba, nas→nasıl, han→hangi ...)
SMART_3CHAR: Dict[str, List[str]] = {
    "mer": ["merhaba", "merhabalar", "müşteri"],
    "han": ["hangi", "hangi konuda", "hangi konuda destek almak istersiniz", "hangi konuda yardımcı olabilirim", "hanım", "handan"],
    "nas": ["nasıl", "nasıl yardımcı olabilirim", "nasılsınız", "nasılsın"],
    "yar": ["yardım", "yardımcı", "yardımcı olabilirim", "yardımcı olabilir misiniz"],
    "teş": ["teşekkürler", "teşekkür", "teşekkür ederim"],
    "sip": ["sipariş", "sipariş takibi", "sipariş durumu", "siparişiniz"],
    "iyi": ["iyi", "iyi günler", "iyi akşamlar", "iyi geceler"],
    "hoş": ["hoş", "hoş geldiniz", "hoşgeldiniz"],
    "kar": ["kargo", "kampanya"],
    "özü": ["özür", "özür dilerim"],
    "aff": ["affedersiniz", "affedersin"],
    "bil": ["bilgi"],
    "des": ["destek", "detay"],
    "eve": ["evet"],
    "fat": ["fatura", "fiyat"],
    "lüt": ["lütfen"],
    "tam": ["tamam", "tabii"],
    "ürü": ["ürün", "ücret"],
    "çöz": ["çözüm", "çok"],
    "şik": ["şikayet", "şifre"],
    "sağ": ["sağolun", "sağ olun"],
    "ind": ["indirim", "internet"],
    "ipt": ["iptal"],
    "sor": ["sorun", "sorgulama"],
    "kon": ["kontrol", "kampanya"],
    "gün": ["güncelleme", "günaydın"],
    "içi": ["için"],
    "çok": ["çok"],
    "olm": ["olmak", "olur", "oldu"],
    "gör": ["görüşmek", "görüşürüz", "gördüm"],
    "ist": ["isterseniz", "istiyorum", "istemiyorum"],
    "şey": ["şey"],
    "var": ["var"],
    "yok": ["yok", "yoksa"],
    "yap": ["yapmak", "yapabilir"],
    "gel": ["gelmek", "geldi", "gelir"],
    "git": ["gitmek", "gitti"],
    "son": ["sonra", "sonuç"],
    "gib": ["gibi"],
    "kad": ["kadar"],
    "dah": ["daha"],
    "önc": ["önce"],
}

# 4 karakter – iPhone: "hang" → "hangi" vb.
SMART_4CHAR: Dict[str, List[str]] = {
    "hang": ["hangi", "hangi konuda", "hangi konuda destek almak istersiniz", "hangi konuda yardımcı olabilirim"],
    "merh": ["merhaba", "merhabalar"],
    "nası": ["nasıl", "nasılsınız", "nasılsın", "nasıl yardımcı olabilirim"],
    "yard": ["yardım", "yardımcı", "yardımcı olabilirim"],
    "teşe": ["teşekkürler", "teşekkür", "teşekkür ederim"],
    "sipa": ["sipariş", "sipariş takibi", "sipariş durumu", "siparişiniz"],
    "için": ["için"],
    "oldu": ["oldu"],
    "görü": ["görüşmek", "görüşürüz"],
    "iste": ["isterseniz", "istiyorum", "istemiyorum"],
    "önce": ["önce"],
    "nere": ["nerede", "nereye"],
    "gibi": ["gibi"],
    "kadar": ["kadar"],
    "daha": ["daha"],
}


def get_smart_completions(prefix: str, max_results: int = 24) -> List[Dict]:
    """
    Prefix 1–4 karakterse öncelikli tamamlamaları döner.
    iPhone gibi: "han" → hangi, "mer" → merhaba, "hang" → hangi, ...
    """
    if not prefix or len(prefix) > 4:
        return []
    p = prefix.lower().strip()
    out: List[Dict] = []
    maps = [(1, SMART_1CHAR), (2, SMART_2CHAR), (3, SMART_3CHAR), (4, SMART_4CHAR)]
    for n, m in maps:
        if len(p) != n or p not in m:
            continue
        for i, w in enumerate(m[p][:max_results]):
            if w.startswith(p):
                out.append({
                    "word": w,
                    "score": 15.0 - (i * 0.25),
                    "frequency": 100,
                    "type": "smart_completion",
                    "description": "Öneri (öncelikli)",
                    "source": "smart_completions",
                })
        break
    return out[:max_results]
