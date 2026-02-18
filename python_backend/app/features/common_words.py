"""
iPhone benzeri yaygın kelime önceliklendirmesi.
Sözlük/trie sonuçlarında "hangi", "merhaba", "nasıl" gibi sık kullanılan kelimeler
her zaman nadir kelimelerden (handelier, hanımcık vb.) önce gelir.
"""

import os
from typing import Set, FrozenSet

# Yüklenen set (lazy)
_COMMON_WORDS: Set[str] = set()
_LOADED = False


def _collect_smart_completion_words() -> Set[str]:
    """Smart completions'taki tüm kelime ve ifadelerden tek kelimeleri topla."""
    out: Set[str] = set()
    try:
        from smart_completions import (
            SMART_1CHAR, SMART_2CHAR, SMART_3CHAR, SMART_4CHAR
        )
        for m in (SMART_1CHAR, SMART_2CHAR, SMART_3CHAR, SMART_4CHAR):
            for words in m.values():
                for w in words:
                    for part in w.split():
                        if len(part) >= 2 and part.isalpha():
                            out.add(part.lower())
    except Exception:
        pass
    return out


def _load_musteri_single_words() -> Set[str]:
    """musteri_hizmetleri_sozluk.txt'ten tek kelimeleri al."""
    out: Set[str] = set()
    path = os.path.join(os.path.dirname(__file__), "musteri_hizmetleri_sozluk.txt")
    if not os.path.exists(path):
        return out
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.split("#")[0].strip()
                if not line:
                    continue
                for part in line.split():
                    if len(part) >= 2 and part.isalpha():
                        out.add(part.lower())
    except Exception:
        pass
    return out


# Türkçe en sık kullanılan kelimeler (iPhone/WhatsApp tarzı öncelik)
_CURATED_COMMON = frozenset([
    "bir", "bu", "şu", "o", "için", "ile", "var", "yok", "çok", "iyi", "kötü",
    "ne", "nasıl", "hangi", "evet", "hayır", "da", "de", "ki", "mi", "mı", "mu", "mü",
    "gibi", "kadar", "daha", "en", "az", "hiç", "hep", "hemen", "sonra", "önce",
    "şimdi", "bugün", "yarın", "dün", "burada", "orada", "nerede", "nereye",
    "niçin", "neden", "ne zaman", "kim", "kime", "hangisi", "ben", "sen", "biz", "siz",
    "onlar", "benim", "senin", "onun", "bizim", "sizin", "onların",
    "olmak", "etmek", "yapmak", "gelmek", "gitmek", "almak", "vermek", "demek",
    "istemek", "bilmek", "görmek", "duymak", "söylemek", "konuşmak", "düşünmek",
    "bulmak", "beklemek", "olur", "oldu", "olacak", "eder", "etti", "yapar", "yaptı",
    "gelir", "geldi", "gider", "gitti", "alır", "aldı", "verir", "verdi",
    "lütfen", "tabii", "elbette", "acaba", "belki", "zaten", "henüz", "mutlaka",
    "özellikle", "genellikle", "bazen", "her", "tüm", "bütün", "herkes", "şey",
    "iş", "konu", "durum", "sorun", "problem", "çözüm", "bilgi", "detay", "yardım",
    "destek", "sipariş", "ürün", "kargo", "fatura", "fiyat", "ücret", "kampanya",
    "indirim", "iade", "teslimat", "müşteri", "mesaj", "numara", "adres", "hesap",
    "talep", "iptal", "onay", "kontrol", "sorgulama", "güncelleme", "değişiklik",
    "kayıt", "giriş", "çıkış", "şifre", "güvenlik", "teşekkür", "teşekkürler",
    "merhaba", "selam", "günaydın", "hoş", "hoşgeldiniz", "üzgünüm", "özür",
    "rica", "affedersiniz", "kusura", "sağolun", "anladım", "tamam", "pek",
    "biraz", "biraz", "birçok", "birkaç", "bazı", "hiçbir", "herhangi",
    "neden", "niye", "nasılsınız", "nasılsın", "nerede", "nereye", "neyse",
    "demek", "demi", "falan", "gibi", "kadar", "daha", "en", "ile", "ve", "veya",
    "ama", "fakat", "ancak", "çünkü", "eğer", "ise", "ki", "için", "göre",
    "hakkında", "sonra", "önce", "şimdi", "henüz", "artık", "yine", "tekrar",
    "sadece", "yalnızca", "özel", "genel", "doğru", "yanlış", "kolay", "zor",
    "iyi", "kötü", "güzel", "büyük", "küçük", "yeni", "eski", "uzun", "kısa",
    "hızlı", "yavaş", "erken", "geç", "çok", "az", "fazla", "eksik", "yeterli",
    "mümkün", "imkansız", "gerek", "lazım", "şart", "zorunlu", "serbest",
    "açık", "kapalı", "hazır", "beklemede", "tamamlandı", "devam", "bitmiş",
    "görüşmek", "görüşürüz", "hoşça", "kalın", "iyi günler", "iyi akşamlar",
    "handan", "hanım", "handelier", "hanımcık",  # han* tamamlamaları – hangi öncelikli ama diğerleri de set’te
])


def _ensure_loaded() -> None:
    global _LOADED, _COMMON_WORDS
    if _LOADED:
        return
    _COMMON_WORDS = set(_CURATED_COMMON)
    _COMMON_WORDS |= _collect_smart_completion_words()
    _COMMON_WORDS |= _load_musteri_single_words()
    # Nadir/aykırı kelimeleri çıkar – iPhone’da "hangi" önce, "handelier" vb. öne çıkmasın
    for rare in ("handelier", "hanımcık", "hanım hanımcık"):
        _COMMON_WORDS.discard(rare)
    _LOADED = True


def is_common(word: str) -> bool:
    """Kelime yaygın Türkçe kelime setinde mi? (iPhone tarzı öncelik için)"""
    if not word or len(word) < 2:
        return False
    _ensure_loaded()
    return word.lower().strip() in _COMMON_WORDS


def get_common_set() -> FrozenSet[str]:
    """Yaygın kelime setini döndür (read-only)."""
    _ensure_loaded()
    return frozenset(_COMMON_WORDS)


def first_word_common(text: str) -> bool:
    """İfadenin ilk kelimesi yaygın mı? (örn. 'hangi konuda...' -> hangi)"""
    if not text:
        return False
    parts = text.strip().split()
    return bool(parts) and is_common(parts[0])
