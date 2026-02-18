# -*- coding: utf-8 -*-
"""Tüm doküman güncellemeleri: SISTEM_EKSIKLER, IPHONE_INCELEME, KALAN_EKSIKLER."""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")

# --- SISTEM_EKSIKLER_RAPORU.md ---
path_se = os.path.join(ROOT, "SISTEM_EKSIKLER_RAPORU.md")
with open(path_se, "r", encoding="utf-8") as f:
    se = f.read()

# 1.4 Giderildi
se = se.replace(
    "### 1.4 Öğrenme (`/learn`) frontend'den hiç çağrılmıyor\n\n- **Backend:**",
    "### 1.4 Öğrenme (`/learn`) frontend'den hiç çağrılmıyor → **Giderildi**\n\n- **Güncel:** `frontend_ultimate.js` içinde `learnMessage` → POST `/api/v1/learn` ile öğrenme tetikleniyor. Backend:"
)
se = se.replace(
    "- **Frontend:** `learnMessage` mesaj gönderince veya öneri seçilince **`/api/v1/process`** için POST atıyor; **`/api/v1/learn`** hiç kullanılmıyor.\n- **Sonuç:** Kullanıcı metinleri backend'e öğrenme olarak iletilmiyor; ngram / kullanıcı sözlüğü gelişmiyor.\n- **Öneri:** Mesaj gönderildiğinde (ve istenirse öneri seçildiğinde) ek olarak `POST /api/v1/learn` ile `{ \"text\": \"...\" }` gönderin. `learnMessage` içinde `/process` çağrısına ek olarak `/learn` çağrısı eklenebilir.",
    ""
)

# 2.1 Giderildi
se = se.replace(
    "### 2.1 Dokümanda olup projede olmayan .bat dosyaları\n\n- **`PRODUCTION_BASLAT.bat`** – Birçok dokümanda",
    "### 2.1 Dokümanda olup projede olmayan .bat dosyaları → **Giderildi**\n\n- **Güncel:** Projede **`PRODUCTION_BASLAT.bat`**, **`BASLAT.bat`**, **`TUM_OZELLIKLERLE_BASLAT.bat`**, `BASLAT_ULTIMATE.bat`, `DOCKER_BASLAT.bat`, `KELIME_TOPLA.bat` mevcut. Eski not: Birçok dokümanda"
)
se = se.replace(
    '"ana" başlatıcı olarak geçiyor; projede yok.\n- **`BASLAT.bat`**, **`TUM_OZELLIKLERLE_BASLAT.bat`** – `HANGI_BAT_DOSYASI.md` vb. içinde anlatılıyor; projede yok.\n\nMevcut olanlarla eşleştirme veya bu dosyaların oluşturulması gerekiyor.',
    "ana başlatıcı olarak geçiyordu; artık hepsi mevcut."
)

# 2.2 Giderildi
se = se.replace(
    "### 2.2 Port farkı\n\n- **Docs:** Bazı yerlerde `http://localhost:8000` ve `http://localhost:8000/docs` geçiyor.\n- **Uygulama:** `BASLAT_*.bat` ve `app/main.py` **8080** kullanıyor.\n- **Öneri:** Tüm dokümanlarda portu **8080** ile netleştirin.",
    "### 2.2 Port farkı → **Giderildi**\n\n- **Güncel:** Tüm dokümanlar ve uygulama **8080** kullanıyor; 8000 referansı yok."
)

# 3.1 Giderildi
se = se.replace(
    "### 3.1 `app/main.py` – Erişilemeyen kod ve tekrarlar\n\n- **Satır 61–63:** `read_index` içinde `return` sonrası ES kontrolü var; bu kod hiç çalışmaz:",
    "### 3.1 `app/main.py` – Erişilemeyen kod ve tekrarlar → **Giderildi**\n\n- **Güncel:** Mevcut `read_index` sadece `FileResponse` veya hata dönüyor; dead code yok. Eski not: `read_index` içinde return sonrası ES kontrolü vardı:"
)
se = se.replace(
    "- **Startup:** `from app.core.nlp_engine import nlp_engine` iki kez yazılmış (gereksiz tekrar).\n\n**Öneri:** Erişilemeyen ES kodunu kaldırın",
    "**Öneri:** (Giderildi – mevcut kod temiz.) Erişilemeyen ES kodu kaldırıldı"
)

# 3.2 Giderildi
se = se.replace(
    "### 3.2 `nlp_engine.py` – `load_models` iki kez tanımlı\n\n- `load_models` iki def ile tanımlı; ikincisi birincisinin üzerine yazıyor. İlk blok fiilen dead code.\n- **Öneri:** Tek bir `load_models` tanımı bırakın; mantık tek yerde toplansın.",
    "### 3.2 `nlp_engine.py` – `load_models` iki kez tanımlı → **Giderildi**\n\n- **Güncel:** Tek bir `load_models` tanımı var."
)

# 3.3 Giderildi
se = se.replace(
    "### 3.3 `cache.py` – `get` içinde erişilemeyen `return`\n\n- `get` içinde `if self.use_redis: ... return ... else: return self.memory_cache.get(key)` sonrasında bir `return None` daha var; bu satıra hiç ulaşılmaz.\n- **Öneri:** Gereksiz `return None` satırını kaldırın.",
    "### 3.3 `cache.py` – `get` içinde erişilemeyen `return` → **Giderildi**\n\n- **Güncel:** Gereksiz `return None` kaldırıldı (Giderilen eksiklerde belirtildi)."
)

# 3.4 Giderildi
se = se.replace(
    "### 3.4 Frontend – `learnMessage` ve `/learn`\n\n- Yukarıda belirtildiği gibi `learnMessage` yalnızca `/process` kullanıyor; öğrenme için `/learn` kullanılmıyor. Bu hem mantık hem de amaçla uyumsuz.",
    "### 3.4 Frontend – `learnMessage` ve `/learn` → **Giderildi**\n\n- **Güncel:** `learnMessage` artık POST `/api/v1/learn` ile backend öğrenmeyi tetikliyor."
)

# Section 5 Checklist - replace by line numbers (curly quotes in file)
lines_se = se.splitlines(keepends=True)
# Find "## 5. Özet Checklist" and replace table (header + 11 rows)
for i, line in enumerate(lines_se):
    if "## 5. Özet Checklist" in line:
        # Replace next 14 lines (header + separator + 11 rows + blank)
        new_table_lines = [
            "| Konu | Durum | Not |\n",
            "|------|--------|--------|\n",
            "| `PRODUCTION_BASLAT.bat` | Var | Projede mevcut. |\n",
            "| `elasticsearch` paketi | Var | requirements.txt icinde elasticsearch>=7.17.0. |\n",
            "| `data/`, `tr_frequencies.json` | Ilk kurulumda yok (opsiyonel) | Fallback: turkish_dictionary.json. README'de ilk kurulum notu var. |\n",
            "| Frontend -> `/learn` | Var | learnMessage -> POST /api/v1/learn (frontend_ultimate.js). |\n",
            "| Docs ve .bat'ler | Uyumlu | Tum .bat dosyalari mevcut. |\n",
            "| Port | 8080 | Tum dokümanlarda 8080 kullaniliyor. |\n",
            "| Hybrid / Trie / Large Dict / Phrase completion | App'te | Trie, buyuk sozluk, iki asamali yanit, phrase completion pipeline'da. |\n",
            "| `main.py` erisilemeyen kod | Yok | Mevcut read_index temiz. |\n",
            "| `load_models` duplikasyonu | Yok | Tek tanim (nlp_engine). |\n",
            "| `cache.get` unreachable return | Giderildi | (Giderilen eksiklerde belirtildi.) |\n",
            "| Windows `--reload` | Bilgi | Batch'lerde reload kapatilabilir veya dokumante edilebilir. |\n",
            "\n",
        ]
        # Replace from i+2 (after ## and blank) for 14 lines
        start = i + 2
        end = min(start + 14, len(lines_se))
        lines_se[start:end] = new_table_lines
        se = "".join(lines_se)
        break

# Section 6 - replace by line numbers
lines_se = se.splitlines(keepends=True)
for i, line in enumerate(lines_se):
    if "## 6. Öncelik Sırası Önerisi" in line and "(güncel)" not in line:
        # Replace from this line through "Bu adımlar tamamlandığında"
        new_s6 = [
            "## 6. Öncelik Sırası Önerisi (güncel)\n",
            "\n",
            "1. ~~**Hemen:** `requirements.txt`'e `elasticsearch` ekleyin.~~ → **Yapıldı.**\n",
            "2. ~~**Hemen:** Frontend'de `/learn` ile öğrenmeyi bağlayın.~~ → **Yapıldı.**\n",
            "3. ~~**Kısa vadede:** PRODUCTION_BASLAT.bat ve port tutarlılığı.~~ → **Mevcut.**\n",
            "4. **İsteğe bağlı:** `data/` ve `tr_frequencies.json` için ilk kurulum adımı README'de netleştirildi (setup_ai notu).\n",
            "5. ~~**İsteğe bağlı:** Hybrid / Trie / Large Dict / Phrase completion app'e entegre.~~ → **Yapıldı.**\n",
            "\n",
            "Kritik eksikler giderildi; dokümantasyon güncel.\n",
        ]
        j = i + 1
        while j < len(lines_se) and "Bu adımlar tamamlandığında" not in lines_se[j]:
            j += 1
        end = j + 1 if j < len(lines_se) else len(lines_se)
        lines_se[i:end] = new_s6
        se = "".join(lines_se)
        break

with open(path_se, "w", encoding="utf-8") as f:
    f.write(se)
print("SISTEM_EKSIKLER_RAPORU.md güncellendi.")

# --- IPHONE_SEVIYESI_INCELEME.md ---
path_inc = os.path.join(ROOT, "docs", "IPHONE_SEVIYESI_INCELEME.md")
with open(path_inc, "r", encoding="utf-8") as f:
    inc = f.read()

# Section 2 - replace table by line numbers (curly quotes in file)
lines_inc = inc.splitlines(keepends=True)
for i, line in enumerate(lines_inc):
    if "## 2. Eksik veya İyileştirilebilir" in line:
        # Find table start (next non-blank after header)
        start = i + 2
        while start < len(lines_inc) and "| Konu | Öncelik |" not in lines_inc[start]:
            start += 1
        if start >= len(lines_inc):
            break
        # Find table end (blank line or next ##)
        end = start + 1
        while end < len(lines_inc) and (lines_inc[end].strip().startswith("|") or lines_inc[end].strip() == ""):
            end += 1
        new_inc_table = [
            "| Konu | Öncelik | Açıklama |\n",
            "|------|---------|----------|\n",
            "| **IPHONE doc girişi** | Tamamlandı | Giriş paragrafı güncel duruma göre güncellendi (iPhone'a yakın, Trie, phrase completion API'de). |\n",
            "| **Health'te Trie bilgisi** | Tamamlandı | `/health` cevabında `trie_ready` ve `trie_words` eklendi. |\n",
            "| **Phrase completion API** | Tamamlandı | improvements/phrase_completion.py routes üzerinden lazy load; WebSocket enhanced ve HTTP /process içinde kullanılıyor. |\n",
            "| **WebSocket phase + input eşleşmesi** | Tamamlandı | Frontend'de _lastWsRequestText ile enhanced yanıtı sadece aynı input için uygulanıyor. |\n",
            "| **Varsayılan WebSocket** | Bilgi | Frontend useWebSocket: false – çoğu kullanım HTTP. İki aşamalı his için WS açılabilir. |\n",
            "| **SISTEM_EKSIKLER_RAPORU** | Tamamlandı | Bölüm 2.3 ve checklist güncellendi; Trie, Large Dict, phrase completion app'te. |\n",
        ]
        lines_inc[start:end] = new_inc_table
        inc = "".join(lines_inc)
        break

# Section 3 - phrase completion
inc = inc.replace(
    "| Çok güçlü bağlam / cümle tahmini | N-gram + BERT var; phrase completion API'de yok |",
    "| Çok güçlü bağlam / cümle tahmini | N-gram + BERT + phrase completion API'de |"
)

# Section 4 Sonuç
inc = inc.replace(
    "**Büyük oranda yakın.** Trie, büyük sözlük, iki aşamalı yanıt, öğrenme, önbellek ve UX öğeleri (ghost text, Tab/ok, debounce, işlem süresi) mevcut. Eksikler çoğunlukla **doküman tutarlılığı**, **health bilgisi**, **phrase completion'ın API'ye alınması** ve **isteğe bağlı frontend iyileştirmeleri**.",
    "**Büyük oranda yakın.** Trie, büyük sözlük, iki aşamalı yanıt, phrase completion API, öğrenme, önbellek, health trie bilgisi ve UX öğeleri (ghost text, Tab/ok, debounce, phase/input eşleşmesi, işlem süresi) mevcut. Doküman güncellemeleri tamamlandı."
)
inc = inc.replace(
    "- **Eklenmesi gereken kritik bir şey var mı?**  \n  **Hayır.** Trie ve iki aşamalı sistem çalışıyor. İsterseniz:\n  1. `IPHONE_SEVIYESI_DEGERLENDIRME.md` girişini güncel duruma göre düzeltin.\n  2. `/health` cevabına `trie_ready` ekleyin.\n  3. `SISTEM_EKSIKLER_RAPORU.md` 2.3'ü \"Trie ve Large Dict artık app'te\" diye güncelleyin.\n  4. (Opsiyonel) Frontend'de WebSocket `phase` + input eşleşmesi; (opsiyonel) phrase completion'ı API'ye bağlayın.\n\nBu inceleme, mevcut koda ve dokümana göre yapılmıştır.",
    "- **Eklenmesi gereken kritik bir şey var mı?**  \n  **Hayır.** Tüm maddeler tamamlandı: IPHONE girişi, health trie, phrase completion API, WebSocket phase/input, SISTEM_EKSIKLER güncellemesi.\n\nBu inceleme, mevcut koda ve dokümana göre güncellenmiştir."
)

with open(path_inc, "w", encoding="utf-8") as f:
    f.write(inc)
print("IPHONE_SEVIYESI_INCELEME.md güncellendi.")

# --- KALAN_EKSIKLER.md ---
path_ke = os.path.join(ROOT, "docs", "KALAN_EKSIKLER.md")
with open(path_ke, "r", encoding="utf-8") as f:
    ke = f.read()

ke = ke.replace(
    "## Hâlâ eksik veya iyileştirilebilir\n\n| Konu | Öncelik | Açıklama |\n|------|---------|----------|\n| **data/ ve tr_frequencies.json ilk kurulum** | Düşük | `data/` ve `tr_frequencies.json` varsayılan kurulumda yok; `turkish_dictionary.json` fallback kullanılıyor. README'de `setup_ai.py` notu var. İsterseniz \"İlk kurulum\" adımını daha net yazabilirsiniz. |\n| **SISTEM_EKSIKLER_RAPORU Checklist (Bölüm 5)** | Doküman | Checklist hâlâ \"PRODUCTION_BASLAT ❌ Yok\", \"elasticsearch ❌ yok\", \"/learn ❌ Çağrı yok\", \"Hybrid/Trie ❌ yok\" diyor. Bunlar giderildi; tabloyu güncellemek faydalı olur. |\n| **docs/IPHONE_SEVIYESI_INCELEME.md Bölüm 2 tablosu** | Doküman | \"Eksik veya İyileştirilebilir\" tablosunda IPHONE girişi, Health, Phrase completion, WebSocket phase, SISTEM_EKSIKLER hâlâ \"eksik/opsiyonel\" yazıyor. Hepsi tamamlandı; tabloyu \"Tamamlandı\" olarak güncellemek tutarlılık sağlar. |\n| **FastAPI lifespan** | Opsiyonel | `on_event(\"startup\")` çalışıyor; ileride `lifespan` context manager'a geçilebilir (FastAPI önerisi). |\n| **getContextFromLastMessage** | Opsiyonel | `.message.incoming` arıyor; arayüzde sadece `.outgoing` olabilir; context boş kalabilir. Kritik değil. |",
    "## Hâlâ eksik veya iyileştirilebilir\n\n| Konu | Öncelik | Açıklama |\n|------|---------|----------|\n| **data/ ve tr_frequencies.json ilk kurulum** | ✅ Dokümante edildi | README'de \"İlk kurulum (opsiyonel – büyük sözlük)\" adımı netleştirildi; fallback açıklandı. |\n| **SISTEM_EKSIKLER_RAPORU Checklist (Bölüm 5)** | ✅ Güncellendi | Checklist ve Bölüm 6 güncel duruma çekildi. |\n| **docs/IPHONE_SEVIYESI_INCELEME.md Bölüm 2 tablosu** | ✅ Güncellendi | Tüm maddeler \"Tamamlandı\" olarak işaretlendi. |\n| **FastAPI lifespan** | Opsiyonel | `on_event(\"startup\")` çalışıyor; ileride `lifespan` kullanılabilir. |\n| **getContextFromLastMessage** | Opsiyonel | `.message.incoming` arıyor; arayüzde sadece `.outgoing` olabilir; context boş kalabilir. Kritik değil. |"
)
ke = ke.replace(
    "## Özet\n\n- **Kritik eksik yok.**",
    "## Özet\n\n- **Kritik eksik yok.** Tüm doküman güncellemeleri (SISTEM_EKSIKLER checklist/1.4/2.1/2.2/3.x/6, IPHONE_INCELEME tablo/Sonuç, README ilk kurulum) yapıldı.\n- **Önceki durum:**"
)

with open(path_ke, "w", encoding="utf-8") as f:
    f.write(ke)
print("KALAN_EKSIKLER.md güncellendi.")
print("Done.")
