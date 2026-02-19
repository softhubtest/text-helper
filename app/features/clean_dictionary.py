"""
Sözlük Temizleme Scripti (Gelişmiş Versiyon)
- Büyük/Küçük Ünlü Uyumu kurallarını uygular
- Fonotaktik (ses dizimi) kurallarını uygular
- Anlamsız permütasyonları ve sfaa, abadayıcu gibi kelimeleri temizler.
"""

import os
import re

def is_vowel(char):
    return char in "aeıioöuü"

def is_consonant(char):
    return char in "bcçdfgğhjklmnprsştvyz"

def follows_major_harmony(word):
    """Büyük Ünlü Uyumu: Kalınlık-İncelik"""
    vowels = [c for c in word if is_vowel(c)]
    if not vowels: return True # Sesli harf yoksa kural aranmaz (örn: spor - gerçi bu sözlükte olmamalı ama neyse)
    
    first_is_front = vowels[0] in "eiöü"
    for v in vowels[1:]:
        current_is_front = v in "eiöü"
        if first_is_front != current_is_front:
            # İstisnalar (anne, kardeş, elma vb.) - Ama permütasyonlarda bu kural katı uygulanmalı
            # Bu script anlamsız permütasyonları temizlemek için olduğu için katı modda çalıştıracağız.
            # Ancak bazı yaygın kelimeler istisna olabilir.
            # Şimdilik sadece çok bariz anlamsızlıkları elemek için %100 uygulayalım.
            return False
    return True


# Büyük Ünlü Uyumu istisnaları (Yaygın kullanılanlar)
DISHARMONIC_EXCEPTIONS = {
    "anne", "kardeş", "hangi", "hani", "elma", "şişman", "insan", "kitap", "kalem", "sabah",
    "fiyat", "ziyaret", "ticaret", "siyaset", "dakika", "hareket", "hakikat", "emanet", 
    "cesaret", "adalet", "ibadet", "kıyamet", "ganimet", "hikaye", "harita", "tarih",
    "tarif", "talih", "nasip", "sahip", "ahenk", "badem", "civar", "fidan", "gazete",
    "haber", "kader", "kahve", "taze", "meyve", "model", "bobin", "vites", "vagon",
    "ciğer", "limon", "pilot", "bira", "israf", "itiraf", "iftira", "ilham", "imha",
    "imkan", "inanç", "inkar", "insaf", "iptal", "isyan", "işgal", "ithal", "izan",
    "cami", "mani", "vali", "dahi", "kuzey", "güney", "tayin", "tahmin", "takvim",
    "tasvir", "tatil", "teklif", "teslim", "teşvik", "cisim", "çeşit", "mevsim",
    "sahil", "şehir", "mühim", "onur", "horoz", "konsol", "atlet", "metal", "torun",
    "topu", "kontrol", "alkol", "petrol", "futbol", "koro", "horon", "piyon", "bilyon",
    "kamyon", "lider", "final", "moral", "sistem", "program", "roket"
}

def check_last_transition_harmony(word):
    """
    Son iki sesli arasındaki uyumu kontrol eder.
    Sözlükteki 'root+suffix' hatalarını (örn: abadayı-ci) yakalamak için en etkili yöntemdir.
    """
    vowels = [c for c in word if is_vowel(c)]
    if len(vowels) < 2: return True
    
    last_vowel = vowels[-1]
    prev_vowel = vowels[-2]
    
    # İstisna Ekler Kontrolü
    if word.endswith(("yor", "ken", "ki", "gil", "mtırak")):
        return True
        
    # İstisna Kelimeler Kontrolü (Tam eşleşme veya kök eşleşmesi)
    if word in DISHARMONIC_EXCEPTIONS:
        return True
    
    # Bazı yaygın istisna köklerin türevlerini korumak için (örn: kitap -> kitapçı)
    # Eğer kelimenin kökü istisna listesindeyse ve son ek uyumluysa geçer.
    # Ancak burada basitçe son geçişe bakıyoruz. 'kitapçı' (a-ı) zaten uyumludur.
    # 'kitap' (i-a) uyumsuzdur, whitelist ile geçer.
    # 'kitapci' (a-i) uyumsuzdur, whitelist'te YOKTUR (kitap var, kitapci yok). REDDEDİLİR.
    # Bu mantık tam olarak istediğimiz şey!
    
    # Kalınlık-İncelik (Major Harmony)
    prev_is_front = prev_vowel in "eiöü"
    last_is_front = last_vowel in "eiöü"
    
    if prev_is_front != last_is_front:
        return False
        
    return True

def follows_major_harmony(word):
    """Büyük Ünlü Uyumu: Kalınlık-İncelik (Tüm kelime için)"""
    vowels = [c for c in word if is_vowel(c)]
    if not vowels: return True 
    
    first_is_front = vowels[0] in "eiöü"
    for v in vowels[1:]:
        current_is_front = v in "eiöü"
        if first_is_front != current_is_front:
            return False
    return True

def follows_minor_harmony(word):
    """Küçük Ünlü Uyumu: Düzlük-Yuvarlaklık"""
    vowels = [c for c in word if is_vowel(c)]
    if len(vowels) < 2: return True
    
    for i in range(len(vowels) - 1):
        v1 = vowels[i]
        v2 = vowels[i+1]
        
        # 1. Düzden sonra düz gelir (a,e,ı,i -> a,e,ı,i)
        if v1 in "aeıi":
            if v2 not in "aeıi":
                # İstisna: Şimdiki zaman eki -yor
                if v2 == 'o' and (word.endswith('yor') or 'yor' in word): continue
                return False
        
        # 2. Yuvarlaktan sonra ya düz-geniş (a,e) ya da yuvarlak-dar (u,ü) gelir
        if v1 in "oöuü":
            if v2 not in "aeuü":
                # İstisna: -yor
                if v2 == 'o' and (word.endswith('yor') or 'yor' in word): continue
                return False
    return True

def has_valid_phonotactics(word):
    """Ses Dizimi Kuralları"""
    
    # 1. Türkçe kelimeler (genellikle) iki sessizle başlamaz
    if len(word) > 2 and is_consonant(word[0]) and is_consonant(word[1]):
        allowed_starts = ["br", "tr", "kr", "sp", "st", "pr", "pl", "fl", "fr", "kl", "gr", "sm", "sk", "dr", "ch", "sh", "bl", "gl"]
        if not any(word.startswith(start) for start in allowed_starts):
           return False

    # 1.5. Aynı sesliyle başlama (aa, ee vs.)
    if len(word) > 2 and is_vowel(word[0]) and word[0] == word[1]:
        if word.startswith("aa") and not word.startswith("aaron"): 
             return False

    # 2. Üç sessiz yan yana gelmez
    if re.search(r'[bcçdfgğhjklmnprsştvyz]{3,}', word):
        allowed_clusters = ["ktr", "str", "nks", "rktr", "nst", "mstr", "ktr"]
        if not any(c in word for c in allowed_clusters):
             return False

    # 3. İkiden fazla aynı harf yan yana gelmez
    if re.search(r'(.)\1\1', word):
        return False
        
    return True

def is_valid_turkish_word(word):
    word = word.lower().strip()
    
    # Çok kısa kelimeler için whitelist
    if len(word) < 2: return False
    if len(word) == 2:
        allowed_2 = ["ab", "aç", "ad", "af", "ağ", "ah", "ak", "al", "an", "as", "aş", "at", "av", "ay", "az",
                     "bu", "şu", "o", "un", "su", "iş", "iz", "il", "in", "it", "of", "oh", "ol", "on", "ot", "oy",
                     "öl", "ön", "öz", "re", "se", "ta", "te", "ti", "us", "uz", "un", "ya", "ye", "ve"]
        return word in allowed_2

    # Karakter kontrolü
    if not re.match(r'^[a-zçğıöşü]+$', word):
        return False

    # 1. Fonotaktik Kontrol
    if not has_valid_phonotactics(word):
        return False

    # 2. Ünlü Uyumu Kontrolleri (DAHA DA GÜNCELLENDİ)
    # Strateji: 
    # - Küçük Ünlü Uyumu: KATIDIR. (sadece -yor ve bazı loanwordler hariç).
    # - Büyük Ünlü Uyumu: SADECE SON GEÇİŞ KONTROLÜ ile Hatalı Ekleri Yakala!
    
    if not follows_minor_harmony(word):
        if word not in DISHARMONIC_EXCEPTIONS:
             return False

    # SON GEÇİŞ KONTROLÜ (abadayı-ci temizliği için)
    # Eğer kelime istisna listesinde değilse, son sesli geçişi MUTLAKA uyumlu olmalı.
    if not check_last_transition_harmony(word):
         return False

    return True

def clean_dictionary():
    # txt dosyasını hedef alıyoruz
    input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "turkish_dictionary.txt")
    
    if not os.path.exists(input_file):
        print(f"Hata: {input_file} bulunamadı.")
        return

    print("Sözlük okunuyor...")
    with open(input_file, 'r', encoding='utf-8') as f:
        words = f.read().splitlines()

    print(f"Toplam kelime: {len(words)}")
    
    cleaned_words = []
    removed_count = 0
    
    # İlerlemeyi görmek için
    for word in words:
        word = word.strip()
        if not word: continue
        
        if is_valid_turkish_word(word):
            cleaned_words.append(word)
        else:
            removed_count += 1
            if removed_count < 20:
                print(f"Silinen: {word}")

    print(f"\nİşlem tamamlandı.")
    print(f"Kalan kelime: {len(cleaned_words)}")
    print(f"Silinen kelime: {removed_count}")
    
    # Dosyayı güncelle
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_words))

if __name__ == "__main__":
    clean_dictionary()
