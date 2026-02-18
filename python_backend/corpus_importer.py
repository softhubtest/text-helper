"""
Corpus Importer for TextHelper
Bu araç, elinizdeki herhangi bir metin dosyasını (Kitap, Wikipedia, Loglar)
tarayarak yeni kelimeler öğrenir ve sözlüğe ekler.

Kullanım:
    python corpus_importer.py "dosya_yolu.txt"
"""

import sys
import os
import json
import re
from collections import Counter

def clean_text(text):
    # Sadece Türkçe karakterler ve harfler kalsın
    text = text.lower()
    text = re.sub(r'[^a-zcCjwğüöşıİĞÜÖŞÇ\s]', '', text)
    return text

def import_corpus(file_path):
    print(f"📖 Dosya okunuyor: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ Dosya bulunamadı!")
        return

    # 1. Metni Oku
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp1254') as f:
                content = f.read()
        except:
            print("❌ Dosya kodlaması okunamadı (UTF-8 veya CP1254 değil).")
            return

    print(f"✅ Okunan karakter sayısı: {len(content)}")

    # 2. Temizle ve Kelimelere Ayır
    print("🧹 Metin temizleniyor...")
    cleaned = clean_text(content)
    words = cleaned.split()
    print(f"📊 Bulunan toplam kelime: {len(words)}")

    # 3. Frekans Analizi
    word_counts = Counter(words)
    print(f"🔍 Benzersiz kelime sayısı: {len(word_counts)}")

    # 4. Mevcut Sözlüğü Yükle
    current_dict_path = os.path.join("improvements", "turkish_dictionary.json")
    if not os.path.exists(current_dict_path):
        # Eğer yoksa yeni oluştur
        current_data = {"words": []}
    else:
        try:
            with open(current_dict_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            current_data = {"words": []}

    existing_words = set(current_data.get("words", []))
    print(f"📚 Mevcut sözlük boyutu: {len(existing_words)} kelime")

    # 5. Yeni Kelimeleri Ekle
    new_words_count = 0
    for word, count in word_counts.items():
        if word not in existing_words and len(word) > 1:
            if count > 1: # Sadece 1'den fazla geçenleri ekle (gürüntüyü azaltmak için)
                existing_words.add(word)
                new_words_count += 1
    
    # 6. Kaydet
    print(f"💾 Kaydediliyor... ({new_words_count} yeni kelime eklendi)")
    
    # Listeye çevir ve sırala
    sorted_words = sorted(list(existing_words))
    
    with open(current_dict_path, 'w', encoding='utf-8') as f:
        json.dump({"words": sorted_words}, f, ensure_ascii=False) # indent=0 for smaller size

    print("✅ İŞLEM TAMAMLANDI!")
    print(f"🚀 Yeni Sözlük Boyutu: {len(sorted_words)} kelime")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python corpus_importer.py <dosya_yolu>")
    else:
        import_corpus(sys.argv[1])
