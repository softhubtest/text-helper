# 🚀 TextHelper Pro Mode - Railway Kurulum Rehberi

TextHelper "Pro Mode" (Python Backend + AI + Redis + Elasticsearch) Vercel üzerinde çalışmaz, ancak **Railway** üzerinde mükemmel çalışır. Yaptığım kod güncellemeleri sayesinde sisteminiz artık Railway ile tam uyumludur.

Bu rehberi adım adım takip ederek projenizi canlıya alabilirsiniz.

---

## 1. Hazırlık: GitHub'a Yükleme

Railway, kodunuzu doğrudan GitHub'dan çeker.
1.  Bu projeyi (yaptığım değişikliklerle birlikte) GitHub'a yükleyin (`git push`).
2.  Repo'nuzun gizli veya herkese açık olması fark etmez.

---

## 2. Railway Projesi Oluşturma

1.  [railway.app](https://railway.app/) adresine gidin ve GitHub ile giriş yapın.
2.  **"New Project"** -> **"Empty Project"** seçeneğine tıklayın.
3.  Bu proje sizin ana panonuz olacak.

---

## 3. Redis (Önbellek) Ekleme

Pro Mode, hız için Redis'e ihtiyaç duyar.
1.  Proje panosunda boş bir yere sağ tıklayın veya "New" butonuna basın.
2.  **Database** -> **Redis** seçin.
3.  Railway bir Redis servisi oluşturacaktır.

---

## 4. Backend (Sizin Kodunuz) Ekleme

1.  Proje panosunda tekrar "New" butonuna basın.
2.  **GitHub Repo** seçeneğine tıklayın.
3.  `TextHelper` reponuzu listeden seçin.
4.  **"Add Variables"** (Değişken Ekle) diyerek bekleyin (Hemen deploy etmeyin).

### ⚙️ Ayarlar (Settings)

Eklediğiniz servise tıklayın ve şu ayarları yapın:

**Build Command:** (Boş bırakın, Dockerfile otomatik algılanır)
**Start Command:** (Boş bırakın, Dockerfile içindeki komut kullanılır)

**Root Directory:**
Eğer `Dockerfile` dosyanız `python_backend` klasörü içindeyse (ki öyle):
*   **Settings** -> **Root Directory** kısmına `/python_backend` yazın.

---

## 5. Çevresel Değişkenler (Variables)

Backend servisinizin **Variables** sekmesine gelin. Railway, Redis'i otomatik olarak bağlayabilir ancak biz garanti olsun diye elle girelim.

Şu değişkenleri ekleyin:

| Değişken Adı | Değer | Açıklama |
| :--- | :--- | :--- |
| `API_KEY` | `texthelper-secret-key-2024` | (İstediğiniz bir şifre yapın) |
| `Use_Transformer` | `true` | AI modellerini açar |
| `Use_Elasticsearch` | `true` | Elasticsearch aramasını açar |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Railway bunu otomatik tamamlar (Reference seçin) |

---

## 6. Elasticsearch (Zorlu Kısım)

"Pro Mode" için Elasticsearch gereklidir. Railway'de iki seçeneğiniz var:

### Seçenek A: Railway Üzerinde Docker Image (Kolay ama Ücretli Olabilir)
Railway RAM konusunda hassastır. Elasticsearch çok RAM yer (>1GB).
1.  Projede "New" -> "Docker Image" seçin.
2.  Image adı: `docker.elastic.co/elasticsearch/elasticsearch:7.17.9`
3.  Oluşan servisin **Variables** kısmına şunları ekleyin:
    *   `discovery.type` = `single-node`
    *   `xpack.security.enabled` = `false`
    *   `ES_JAVA_OPTS` = `-Xms512m -Xmx512m` (RAM kullanımını sınırlar)
4.  Bu servisin "Internal Domain" adresini alın (örn: `elasticsearch.railway.internal`).
5.  **Backend servisinizin** Variables kısmına geri dönün ve ekleyin:
    *   `ELASTICSEARCH_HOST` = `http://elasticsearch.railway.internal:9200` (Kendi internal adresiniz)

### Seçenek B: Harici Servis (Önerilen)
Bonsai.io veya Elastic Cloud gibi yönetilen bir servis kullanıyorsanız:
*   Backend değişkenlerine `ELASTICSEARCH_URL` ekleyin (örn: `https://user:pass@host.com:9200`). Kodunuz bunu artık destekliyor.

---

## 7. Deploy ve Test

1.  Tüm ayarlar bittiğinde Backend servisini **"Deploy"** (veya Redeploy) edin.
2.  Logs sekmesinden yapılandırmayı izleyin. "Model indiriliyor" aşaması biraz sürebilir.
3.  Deploy başarılı olduğunda Railway size bir `Generated Domain` (örn: `texthelper-production.up.railway.app`) verecektir (Settings -> Networking altında).
4.  Bu adresi kopyalayın.

---

## 8. Frontend Bağlantısı

Son adım olarak Frontend kodunuzdaki (HTML/JS) API adresini güncellemelisiniz.

1.  `js/frontend_ultimate.js` dosyasını açın.
2.  `http://localhost:8080` yerine Railway'in verdiği adresi (örn: `https://texthelper-production.up.railway.app`) yazın.
3.  Frontend'i Vercel'e deploy edin.

🎉 **Tebrikler!** Artık Pro Mode özellikli yapay zekanız bulutta çalışıyor.
