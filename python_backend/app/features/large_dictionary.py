"""
Büyük Türkçe Sözlük - 50,000+ Kelime
"""

import json
import os
import re
from typing import List, Dict

class LargeTurkishDictionary:
    """Büyük Türkçe sözlük yöneticisi"""
    
    def __init__(self):
        self.words = []
        self.word_frequencies = {}
        self.categories = {}
        self.prefix_index = {}  # ilk harf -> o harfle baslayan kelimeler (1-char arama icin)
        self.load_dictionary()
    
    def load_dictionary(self):
        """Sözlüğü yükle (Streaming ile)"""
        # JSON dosyasından yükle
        dict_file = os.path.join(os.path.dirname(__file__), "turkish_dictionary.json")
        
        # Streaming Loader kullan
        try:
            # sys.path hack to import from parent/sibling if needed
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(__file__))) 
            from streaming_loader import StreamingDictionaryLoader
            
            if os.path.exists(dict_file):
                loader = StreamingDictionaryLoader(dict_file)
                # Sadece en popüler 500k kelimeyi RAM'e al (kalanı diskte veya search ile bul)
                self.words = loader.load(max_memory_words=600000)
                
                if not self.words:
                     # Fallback
                     self.words = self._get_default_words()
                     
                self._calculate_frequencies()
                print(f"[OK] Buyuk sozluk (Stream) yuklendi: {len(self.words)} kelime (RAM)")
            else:
                 # Varsayılan sözlük
                self.words = self._get_default_words()
                self._calculate_frequencies()
                print(f"[OK] Varsayilan sozluk yuklendi: {len(self.words)} kelime")
                
        except Exception as e:
            print(f"Sözlük yükleme hatası (Stream): {e}, varsayılan kullanılıyor")
            self.words = self._get_default_words()
            self._calculate_frequencies()
            
        self._build_prefix_index()
    
    def _build_prefix_index(self):
        """1 karakter arama icin: ilk harfe gore kelime indexi"""
        self.prefix_index = {}
        for w in self.words:
            if not w or len(w) < 2:
                continue
            c = w[0].lower()
            if c not in self.prefix_index:
                self.prefix_index[c] = []
            self.prefix_index[c].append(w)
    
    def _get_default_words(self) -> List[str]:
        """Varsayılan kelime listesi (genişletilmiş)"""
        return [
            # Mantık kelimeleri (genişletilmiş)
            'mantık', 'mantıklı', 'mantıksız', 'mantıken', 'mantıksal', 'mantıkça',
            'mantıkçı', 'mantıksallık', 'mantıksızca', 'mantıklılık',
            
            # Merhaba ve selamlaşma (genişletilmiş)
            'merhaba', 'merhaba size', 'merhaba nasıl', 'merhaba hoş', 'merhabalar',
            'selam', 'selamlar', 'selamun aleyküm', 'hoş geldiniz', 'hoş geldin',
            'hoşgeldiniz', 'hoşgeldin', 'günaydın', 'iyi günler', 'iyi akşamlar',
            'iyi geceler', 'merhaba nasılsınız', 'merhaba nasılsın',
            
            # Teşekkür (genişletilmiş)
            'teşekkür', 'teşekkürler', 'teşekkür ederim', 'teşekkür ederiz',
            'teşekkür ediyorum', 'teşekkür ediyoruz', 'teşekkürler ederim',
            'sağolun', 'sağ olun', 'sağol', 'sağ ol', 'minnettarım', 'minnettarız',
            
            # Yardım (genişletilmiş)
            'yardım', 'yardımcı', 'yardımcı olabilirim', 'yardım etmek',
            'yardımcı olmak', 'destek', 'destek olmak', 'destek vermek',
            'yardım edebilirim', 'yardımcı olabiliriz', 'destek verebilirim',
            'yardım istiyorum', 'yardıma ihtiyacım var',
            
            # Müşteri (genişletilmiş)
            'müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti',
            'müşteri temsilcisi', 'müşteri danışmanı', 'müşteri ilişkileri',
            'müşteri hizmeti', 'müşteri desteği', 'müşteri sorunları',
            
            # Sipariş (genişletilmiş)
            'sipariş', 'siparişiniz', 'sipariş takibi', 'sipariş durumu',
            'sipariş vermek', 'sipariş almak', 'sipariş iptal', 'sipariş iptali',
            'sipariş numarası', 'sipariş sorgulama', 'sipariş bilgisi',
            
            # Ara (genişletilmiş)
            'ara', 'araba', 'arama', 'aramak', 'arayabilirsiniz', 'arayabilirim',
            'arama yapmak', 'arama sonuçları', 'arama motoru', 'arama yap',
            'arama yapabilir misiniz', 'arama yapabilir miyim',
            
            # Aç (genişletilmiş)
            'açık', 'açmak', 'açıklama', 'açıklamak', 'açıklayabilirim',
            'açıklayabilir misiniz', 'açıklayabilir misin', 'açıklama yapmak',
            'açıklama istiyorum', 'açıklama yapabilir misiniz',
            
            # Nasıl (genişletilmiş)
            'nasıl', 'nasıl yardımcı', 'nasıl olabilirim', 'nasıl yapabilirim',
            'nasıl yapılır', 'nasıl kullanılır', 'nasıl çalışır', 'nasıl yapıyoruz',
            'nasıl yapabilirsiniz', 'nasıl yardımcı olabilirim',
            
            # Diğer yaygın kelimeler (genişletilmiş)
            'iyi', 'kötü', 'güzel', 'büyük', 'küçük', 'yeni', 'eski',
            'yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek', 'vermek', 'almak',
            'sorun', 'problem', 'çözüm', 'bilgi', 'detay', 'fiyat', 'ücret',
            'ürün', 'hizmet', 'kargo', 'teslimat', 'iade', 'değişim',
            'garanti', 'kampanya', 'indirim', 'ödeme', 'fatura', 'fiyat',
            'müşteri', 'destek', 'yardım', 'bilgi', 'sorun', 'çözüm',
            
            # A ile başlayan kelimeler (GENİŞLETİLMİŞ)
            'a', 'ab', 'acaba', 'acele', 'aç', 'açık', 'açıklama', 'açıklamak', 'açmak', 'açılış', 'açılım',
            'ad', 'ada', 'adam', 'adım', 'adres', 'af', 'affetmek', 'ağ', 'ağaç', 'ağır', 'ağlamak', 'ağrı',
            'ah', 'ak', 'akıl', 'akıllı', 'akşam', 'al', 'ala', 'alacak', 'alışveriş', 'almak', 'alt',
            'altın', 'ama', 'amca', 'ana', 'anlamak', 'anne', 'anlatmak', 'anlaşma', 'anı', 'ara',
            'araba', 'arama', 'aramak', 'arayış', 'arkadaş', 'artık', 'artırmak', 'as', 'asker', 'at',
            'ata', 'atmak', 'av', 'ay', 'aya', 'ayak', 'aydın', 'ayrı', 'az', 'azalmak',
            
            # B ile başlayan kelimeler
            'baba', 'babam', 'baba', 'bacı', 'bağ', 'bağlamak', 'bahçe', 'bak', 'bakmak', 'bana',
            'bank', 'bankacı', 'barış', 'bas', 'basit', 'baş', 'başarı', 'başarmak', 'başka', 'bat',
            'battı', 'bay', 'bayan', 'bazı', 'be', 'bekle', 'beklemek', 'belge', 'belki', 'ben',
            'bence', 'benim', 'beraber', 'beri', 'bes', 'beş', 'bet', 'bey', 'beyaz', 'bi',
            'bile', 'bilgi', 'bilgim', 'bilgisayar', 'bilinmeyen', 'bilmek', 'bin', 'bir', 'biraz',
            'birçok', 'biri', 'birkaç', 'birşey', 'bit', 'bitirmek', 'biz', 'bizim', 'boş', 'bu',
            'bura', 'burada', 'buraya', 'burayı', 'bütün', 'buyur', 'buz',
            
            # C ile başlayan kelimeler (GENİŞLETİLMİŞ)
            'c', 'ca', 'cadde', 'cahil', 'can', 'canım', 'canlı', 'canlılık', 'canlısı', 'caz',
            'ce', 'cebim', 'cebir', 'cehennem', 'ceket', 'celal', 'cem', 'cemal', 'cenaze', 'cennet',
            'cep', 'cephe', 'cer', 'cereyan', 'cerrah', 'cesaret', 'cevap', 'cevaplamak', 'cevher', 'ci',
            'cibinlik', 'ciddi', 'ciddiyet', 'cihan', 'cik', 'ciklet', 'cila', 'cilt', 'cimri', 'cin',
            'cins', 'cinsel', 'cinsiyet', 'cir', 'cirit', 'cisim', 'civa', 'ciz', 'cizgi', 'co',
            'cocuk', 'coğrafya', 'coşku', 'coşmak', 'cömert', 'cor', 'cora', 'corba', 'cos', 'cosku',
            'cu', 'cuma', 'cumartesi', 'cumhur', 'cumhuriyet', 'cun', 'cunta', 'cup', 'cuval', 'cuz',
            'cü', 'cüce', 'cümle', 'cüret', 'cüzdan',
            
            # D ile başlayan kelimeler
            'da', 'daha', 'dahi', 'daima', 'dakika', 'dal', 'dalgın', 'dam', 'damar', 'dan',
            'dans', 'dar', 'dara', 'dargın', 'dart', 'das', 'data', 'dava', 'davet', 'day',
            'dayanmak', 'de', 'dede', 'dedi', 'dedim', 'defa', 'değer', 'değil', 'değirmen', 'deh',
            'del', 'deli', 'delik', 'demek', 'demir', 'den', 'deneme', 'deniz', 'denk', 'der',
            'derece', 'dergi', 'derin', 'ders', 'des', 'destek', 'detay', 'dev', 'deva', 'devam',
            'devlet', 'di', 'dil', 'dilek', 'din', 'dinle', 'dinlemek', 'dip', 'direk', 'dir',
            'direkt', 'dis', 'dış', 'dışarı', 'diş', 'do', 'doğa', 'doğru', 'doğum', 'dok',
            'doktor', 'dokunmak', 'dol', 'dolu', 'dom', 'don', 'dondurma', 'dop', 'dor', 'dos',
            'dosya', 'dot', 'doy', 'doz', 'du', 'dudak', 'duh', 'dul', 'dum', 'dun',
            'dün', 'dur', 'durmak', 'dus', 'dut', 'duy', 'duymak', 'duygu', 'düz', 'düzen',
            'dünya', 'düş', 'düşmek', 'düşünce', 'düşünmek',
            
            # E ile başlayan kelimeler
            'e', 'eb', 'ec', 'ed', 'ede', 'eden', 'eder', 'ediyor', 'ef', 'eg',
            'eh', 'ek', 'ekmek', 'el', 'elbette', 'ele', 'elektrik', 'elma', 'em', 'emek',
            'emekli', 'en', 'en iyi', 'enerji', 'engel', 'ep', 'er', 'erken', 'erkek', 'ert',
            'ertesi', 'es', 'esas', 'eser', 'eski', 'et', 'etmek', 'ev', 'eve', 'evet',
            'evim', 'evlat', 'ey', 'eylem',
            
            # F ile başlayan kelimeler
            'fa', 'fabrika', 'fakir', 'fal', 'falan', 'far', 'fark', 'farklı', 'fas', 'fat',
            'fatura', 'fa', 'fazla', 'fe', 'felaket', 'fen', 'fer', 'fes', 'fet', 'fi',
            'fidan', 'fikir', 'fil', 'film', 'fin', 'fir', 'firma', 'fis', 'fit', 'fo',
            'fok', 'fon', 'form', 'for', 'fos', 'fot', 'fotoğraf', 'fu', 'fuar', 'fuk',
            'ful', 'fun', 'fur', 'fus', 'fut', 'futbol',
            
            # G ile başlayan kelimeler
            'ga', 'gaz', 'gazete', 'ge', 'gece', 'geç', 'geçmiş', 'gel', 'gelmek', 'gen',
            'genç', 'geniş', 'ger', 'gerçek', 'ges', 'get', 'gez', 'gezmek', 'gi', 'gibi',
            'gid', 'gitmek', 'giz', 'gizli', 'go', 'gol', 'gon', 'gor', 'gos', 'got',
            'göz', 'görmek', 'göster', 'göstermek', 'gü', 'güç', 'güçlü', 'gül', 'gülmek', 'gün',
            'güneş', 'güzel', 'güzellik',
            
            # H ile başlayan kelimeler
            'ha', 'haber', 'hadi', 'hak', 'haklı', 'hal', 'hala', 'halk', 'ham', 'han',
            'hangi', 'hani', 'hap', 'har', 'harcamak', 'has', 'hat', 'hata', 'hatırlamak', 'hav',
            'hava', 'hay', 'hayal', 'hayat', 'hayır', 'hayvan', 'haz', 'hazır', 'he', 'hed',
            'hediye', 'hem', 'hemen', 'hen', 'henüz', 'hep', 'hepsi', 'her', 'herkes', 'hes',
            'hesap', 'hey', 'heyecan', 'hi', 'hiç', 'hikaye', 'hil', 'him', 'hin', 'hip',
            'hir', 'his', 'hissetmek', 'hit', 'ho', 'hoca', 'hod', 'hol', 'hom', 'hon',
            'hop', 'hor', 'hos', 'hot', 'hoş', 'hoşgeldiniz', 'hu', 'hukuk', 'hul', 'hum',
            'hun', 'hup', 'hur', 'hus', 'hut', 'huzur',
            
            # I-İ ile başlayan kelimeler
            'ı', 'ılık', 'ısı', 'ışık', 'i', 'ib', 'ic', 'id', 'ide', 'ideal',
            'idrak', 'if', 'ifade', 'ig', 'ih', 'ihmal', 'ii', 'ij', 'ik', 'ikinci',
            'il', 'ilaç', 'ile', 'ileri', 'ilgili', 'ilk', 'im', 'imkan', 'in', 'ince',
            'indir', 'indirmek', 'insan', 'ip', 'ir', 'is', 'iş', 'işte', 'it', 'itaat',
            'iyi', 'iz', 'izle', 'izlemek',
            
            # J ile başlayan kelimeler
            'ja', 'jandarma', 'je', 'jel', 'ji', 'jim', 'jo', 'jok', 'jor', 'jos',
            'jot', 'ju', 'jul', 'jum', 'jun', 'jup', 'jur', 'jus', 'jut',
            
            # K ile başlayan kelimeler
            'ka', 'kadın', 'kafa', 'kah', 'kahve', 'kal', 'kalmak', 'kalp', 'kam', 'kan',
            'kana', 'kap', 'kapı', 'kar', 'kara', 'kardeş', 'karşı', 'kas', 'kaş', 'kat',
            'katılmak', 'kav', 'kay', 'kaybetmek', 'kayıt', 'kaz', 'kazanmak', 'ke', 'kelime', 'ken',
            'kendi', 'kent', 'ker', 'kes', 'kesmek', 'ket', 'key', 'ki', 'kim', 'kime',
            'kimse', 'kir', 'kı', 'kısa', 'kız', 'kızmak', 'kl', 'kla', 'klan', 'kle',
            'kli', 'klo', 'kloz', 'ko', 'koc', 'koca', 'kod', 'kol', 'kolay', 'kom',
            'komşu', 'kon', 'konu', 'konuşmak', 'kop', 'kor', 'korkmak', 'kos', 'kot', 'kov',
            'koş', 'koşmak', 'ku', 'kul', 'kulak', 'kum', 'kur', 'kural', 'kurt', 'kus',
            'kuş', 'kut', 'kutu', 'kuv', 'kuy', 'kuz', 'kü', 'küçük', 'kül', 'kültür',
            
            # L ile başlayan kelimeler
            'la', 'lab', 'lac', 'lad', 'laf', 'lag', 'lah', 'lak', 'lal', 'lam',
            'lamba', 'lan', 'lang', 'lap', 'lar', 'las', 'lat', 'lau', 'lav', 'law',
            'lay', 'laz', 'le', 'leb', 'lec', 'led', 'lef', 'leg', 'leh', 'lek',
            'lem', 'len', 'leng', 'lep', 'ler', 'les', 'let', 'lev', 'lew', 'lex',
            'ley', 'lez', 'li', 'lib', 'lic', 'lid', 'lif', 'lig', 'lih', 'lik',
            'lim', 'lin', 'ling', 'lip', 'lir', 'lis', 'lit', 'liv', 'liw', 'lix',
            'liy', 'liz', 'lo', 'lob', 'loc', 'lod', 'lof', 'log', 'loh', 'lok',
            'lom', 'lon', 'long', 'lop', 'lor', 'los', 'lot', 'lou', 'lov', 'low',
            'loy', 'loz', 'lu', 'lub', 'luc', 'lud', 'luf', 'lug', 'luh', 'luk',
            'lum', 'lun', 'lung', 'lup', 'lur', 'lus', 'lut', 'luu', 'luv', 'luw',
            'lux', 'luy', 'luz', 'lü', 'lük', 'lüm', 'lün', 'lüp', 'lür', 'lüs',
            'lüt', 'lüv', 'lüw', 'lüx', 'lüy', 'lüz',
            
            # M ile başlayan kelimeler
            'ma', 'mab', 'mac', 'mad', 'maf', 'mag', 'mah', 'mak', 'mal', 'mam',
            'man', 'mantık', 'mantıklı', 'map', 'mar', 'mas', 'masa', 'mat', 'mau', 'mav',
            'mavi', 'may', 'maz', 'me', 'meb', 'mec', 'med', 'mef', 'meg', 'meh',
            'mek', 'mel', 'mem', 'men', 'meng', 'mep', 'mer', 'merhaba', 'mes', 'mesaj',
            'met', 'meu', 'mev', 'mew', 'mex', 'mey', 'mez', 'mi', 'mib', 'mic', 'mid',
            'mif', 'mig', 'mih', 'mik', 'mil', 'mim', 'min', 'ming', 'mip', 'mir',
            'mis', 'mit', 'miu', 'miv', 'miw', 'mix', 'miy', 'miz', 'mo', 'mob', 'moc',
            'mod', 'mof', 'mog', 'moh', 'mok', 'mol', 'mom', 'mon', 'mong', 'mop', 'mor',
            'mos', 'mot', 'mou', 'mov', 'mow', 'mox', 'moy', 'moz', 'mu', 'mub', 'muc',
            'mud', 'muf', 'mug', 'muh', 'muk', 'mul', 'mum', 'mun', 'mung', 'mup', 'mur',
            'mus', 'mut', 'muu', 'muv', 'muw', 'mux', 'muy', 'muz', 'mü', 'müb', 'müc',
            'müd', 'müf', 'müg', 'müh', 'mük', 'mül', 'müm', 'mün', 'müng', 'müp', 'mür',
            'müs', 'müşteri', 'müt', 'müu', 'müv', 'müw', 'müx', 'müy', 'müz',
            
            # N ile başlayan kelimeler
            'na', 'nab', 'nac', 'nad', 'naf', 'nag', 'nah', 'nak', 'nal', 'nam',
            'nan', 'nap', 'nar', 'nas', 'nasıl', 'nat', 'nau', 'nav', 'naw', 'nax',
            'nay', 'naz', 'ne', 'neb', 'nec', 'ned', 'nef', 'neg', 'neh', 'nek',
            'nel', 'nem', 'nen', 'neng', 'nep', 'ner', 'nes', 'net', 'neu', 'nev',
            'new', 'nex', 'ney', 'nez', 'ni', 'nib', 'nic', 'nid', 'nif', 'nig',
            'nih', 'nik', 'nil', 'nim', 'nin', 'ning', 'nip', 'nir', 'nis', 'nit',
            'niu', 'niv', 'niw', 'nix', 'niy', 'niz', 'no', 'nob', 'noc', 'nod',
            'nof', 'nog', 'noh', 'nok', 'nol', 'nom', 'non', 'nong', 'nop', 'nor',
            'nos', 'not', 'nou', 'nov', 'now', 'nox', 'noy', 'noz', 'nu', 'nub',
            'nuc', 'nud', 'nuf', 'nug', 'nuh', 'nuk', 'nul', 'num', 'nun', 'nung',
            'nup', 'nur', 'nus', 'nut', 'nuu', 'nuv', 'nuw', 'nux', 'nuy', 'nuz',
            
            # O-Ö ile başlayan kelimeler
            'o', 'ob', 'oc', 'od', 'of', 'og', 'oh', 'ok', 'okul', 'ol',
            'olmak', 'om', 'on', 'ona', 'ondan', 'onlar', 'onun', 'op', 'or', 'ora',
            'orada', 'oran', 'oraya', 'os', 'ot', 'otobüs', 'ou', 'ov', 'ow', 'ox',
            'oy', 'oyun', 'oz', 'ö', 'öb', 'öc', 'öd', 'öf', 'ög', 'öh', 'ök',
            'öl', 'ölmek', 'öm', 'ön', 'önce', 'önder', 'öp', 'ör', 'örmek', 'ös',
            'öt', 'öu', 'öv', 'övmek', 'öw', 'öx', 'öy', 'öz', 'özel', 'özlemek',
            
            # P ile başlayan kelimeler
            'pa', 'pab', 'pac', 'pad', 'paf', 'pag', 'pah', 'pak', 'pal', 'pam',
            'pan', 'pap', 'par', 'para', 'pas', 'pat', 'pau', 'pav', 'paw', 'pax',
            'pay', 'paz', 'pe', 'peb', 'pec', 'ped', 'pef', 'peg', 'peh', 'pek',
            'pel', 'pem', 'pen', 'peng', 'pep', 'per', 'pes', 'pet', 'peu', 'pev',
            'pew', 'pex', 'pey', 'pez', 'pi', 'pib', 'pic', 'pid', 'pif', 'pig',
            'pih', 'pik', 'pil', 'pim', 'pin', 'ping', 'pip', 'pir', 'pis', 'pit',
            'piu', 'piv', 'piw', 'pix', 'piy', 'piz', 'po', 'pob', 'poc', 'pod',
            'pof', 'pog', 'poh', 'pok', 'pol', 'pom', 'pon', 'pong', 'pop', 'por',
            'pos', 'pot', 'pou', 'pov', 'pow', 'pox', 'poy', 'poz', 'pu', 'pub',
            'puc', 'pud', 'puf', 'pug', 'puh', 'puk', 'pul', 'pum', 'pun', 'pung',
            'pup', 'pur', 'pus', 'put', 'puu', 'puv', 'puw', 'pux', 'puy', 'puz',
            
            # R ile başlayan kelimeler
            'ra', 'rab', 'rac', 'rad', 'raf', 'rag', 'rah', 'rak', 'ral', 'ram',
            'ran', 'rap', 'rar', 'ras', 'rat', 'rau', 'rav', 'raw', 'rax', 'ray',
            'raz', 're', 'reb', 'rec', 'red', 'ref', 'reg', 'reh', 'rek', 'rel',
            'rem', 'ren', 'reng', 'rep', 'rer', 'res', 'ret', 'reu', 'rev', 'rew',
            'rex', 'rey', 'rez', 'ri', 'rib', 'ric', 'rid', 'rif', 'rig', 'rih',
            'rik', 'ril', 'rim', 'rin', 'ring', 'rip', 'rir', 'ris', 'rit', 'riu',
            'riv', 'riw', 'rix', 'riy', 'riz', 'ro', 'rob', 'roc', 'rod', 'rof',
            'rog', 'roh', 'rok', 'rol', 'rom', 'ron', 'rong', 'rop', 'ror', 'ros',
            'rot', 'rou', 'rov', 'row', 'rox', 'roy', 'roz', 'ru', 'rub', 'ruc',
            'rud', 'ruf', 'rug', 'ruh', 'ruk', 'rul', 'rum', 'run', 'rung', 'rup',
            'rur', 'rus', 'rut', 'ruu', 'ruv', 'ruw', 'rux', 'ruy', 'ruz',
            
            # S-Ş ile başlayan kelimeler
            'sa', 'sab', 'sac', 'sad', 'saf', 'sag', 'sah', 'sak', 'sal', 'sam',
            'san', 'sap', 'sar', 'sas', 'sat', 'sau', 'sav', 'saw', 'sax', 'say',
            'saz', 'se', 'seb', 'sec', 'sed', 'sef', 'seg', 'seh', 'sek', 'sel',
            'sem', 'sen', 'seng', 'sep', 'ser', 'ses', 'set', 'seu', 'sev', 'sevmek',
            'sew', 'sex', 'sey', 'sez', 'si', 'sib', 'sic', 'sid', 'sif', 'sig',
            'sih', 'sik', 'sil', 'sim', 'sin', 'sing', 'sip', 'sir', 'sis', 'sit',
            'siu', 'siv', 'siw', 'six', 'siy', 'siz', 'so', 'sob', 'soc', 'sod',
            'sof', 'sog', 'soh', 'sok', 'sol', 'som', 'son', 'song', 'sop', 'sor',
            'sorun', 'sos', 'sot', 'sou', 'sov', 'sow', 'sox', 'soy', 'soz', 'su',
            'sub', 'suc', 'sud', 'suf', 'sug', 'suh', 'suk', 'sul', 'sum', 'sun',
            'sung', 'sup', 'sur', 'sus', 'sut', 'suu', 'suv', 'suw', 'sux', 'suy',
            'suz', 'sü', 'süb', 'süc', 'süd', 'süf', 'süg', 'süh', 'sük', 'sül',
            'süm', 'sün', 'süng', 'süp', 'sür', 'sürmek', 'süs', 'süt', 'süu', 'süv',
            'süw', 'süx', 'süy', 'süz', 'ş', 'şa', 'şab', 'şac', 'şad', 'şaf',
            'şag', 'şah', 'şak', 'şal', 'şam', 'şan', 'şap', 'şar', 'şas', 'şat',
            'şau', 'şav', 'şaw', 'şax', 'şay', 'şaz', 'şe', 'şeb', 'şec', 'şed',
            'şef', 'şeg', 'şeh', 'şek', 'şel', 'şem', 'şen', 'şeng', 'şep', 'şer',
            'şes', 'şet', 'şeu', 'şev', 'şew', 'şex', 'şey', 'şez', 'şi', 'şib',
            'şic', 'şid', 'şif', 'şig', 'şih', 'şik', 'şil', 'şim', 'şin', 'şing',
            'şip', 'şir', 'şis', 'şit', 'şiu', 'şiv', 'şiw', 'şix', 'şiy', 'şiz',
            'şo', 'şob', 'şoc', 'şod', 'şof', 'şog', 'şoh', 'şok', 'şol', 'şom',
            'şon', 'şong', 'şop', 'şor', 'şos', 'şot', 'şou', 'şov', 'şow', 'şox',
            'şoy', 'şoz', 'şu', 'şub', 'şuc', 'şud', 'şuf', 'şug', 'şuh', 'şuk',
            'şul', 'şum', 'şun', 'şung', 'şup', 'şur', 'şus', 'şut', 'şuu', 'şuv',
            'şuw', 'şux', 'şuy', 'şuz',
            
            # T ile başlayan kelimeler
            'ta', 'tab', 'tac', 'tad', 'taf', 'tag', 'tah', 'tak', 'tal', 'tam',
            'tan', 'tap', 'tar', 'tas', 'tat', 'tau', 'tav', 'taw', 'tax', 'tay',
            'taz', 'te', 'teb', 'tec', 'ted', 'tef', 'teg', 'teh', 'tek', 'tel',
            'tem', 'ten', 'teng', 'tep', 'ter', 'tes', 'teşekkür', 'tet', 'teu', 'tev',
            'tew', 'tex', 'tey', 'tez', 'ti', 'tib', 'tic', 'tid', 'tif', 'tig',
            'tih', 'tik', 'til', 'tim', 'tin', 'ting', 'tip', 'tir', 'tis', 'tit',
            'tiu', 'tiv', 'tiw', 'tix', 'tiy', 'tiz', 'to', 'tob', 'toc', 'tod',
            'tof', 'tog', 'toh', 'tok', 'tol', 'tom', 'ton', 'tong', 'top', 'tor',
            'tos', 'tot', 'tou', 'tov', 'tow', 'tox', 'toy', 'toz', 'tu', 'tub',
            'tuc', 'tud', 'tuf', 'tug', 'tuh', 'tuk', 'tul', 'tum', 'tun', 'tung',
            'tup', 'tur', 'tus', 'tut', 'tutmak', 'tuu', 'tuv', 'tuw', 'tux', 'tuy',
            'tuz',
            
            # U-Ü ile başlayan kelimeler
            'u', 'ub', 'uc', 'ud', 'uf', 'ug', 'uh', 'uk', 'ul', 'um',
            'un', 'una', 'undan', 'unlar', 'unun', 'up', 'ur', 'ura', 'uran', 'uraya',
            'us', 'ut', 'utobüs', 'uu', 'uv', 'uw', 'ux', 'uy', 'uyun', 'uz',
            'ü', 'üb', 'üc', 'üd', 'üf', 'üg', 'üh', 'ük', 'ül', 'ülmek',
            'üm', 'ün', 'ünce', 'ünder', 'üp', 'ür', 'ürmek', 'üs', 'üt', 'üu',
            'üv', 'üvmek', 'üw', 'üx', 'üy', 'üz', 'üzel', 'üzlemek',
            
            # V ile başlayan kelimeler
            'va', 'vab', 'vac', 'vad', 'vaf', 'vag', 'vah', 'vak', 'val', 'vam',
            'van', 'vap', 'var', 'vas', 'vat', 'vau', 'vav', 'vaw', 'vax', 'vay',
            'vaz', 've', 'veb', 'vec', 'ved', 'vef', 'veg', 'veh', 'vek', 'vel',
            'vem', 'ven', 'veng', 'vep', 'ver', 'vermek', 'ves', 'vet', 'veu', 'vev',
            'vew', 'vex', 'vey', 'vez', 'vi', 'vib', 'vic', 'vid', 'vif', 'vig',
            'vih', 'vik', 'vil', 'vim', 'vin', 'ving', 'vip', 'vir', 'vis', 'vit',
            'viu', 'viv', 'viw', 'vix', 'viy', 'viz', 'vo', 'vob', 'voc', 'vod',
            'vof', 'vog', 'voh', 'vok', 'vol', 'vom', 'von', 'vong', 'vop', 'vor',
            'vos', 'vot', 'vou', 'vov', 'vow', 'vox', 'voy', 'voz', 'vu', 'vub',
            'vuc', 'vud', 'vuf', 'vug', 'vuh', 'vuk', 'vul', 'vum', 'vun', 'vung',
            'vup', 'vur', 'vus', 'vut', 'vuu', 'vuv', 'vuw', 'vux', 'vuy', 'vuz',
            
            # Y ile başlayan kelimeler
            'ya', 'yab', 'yac', 'yad', 'yaf', 'yag', 'yah', 'yak', 'yal', 'yam',
            'yan', 'yap', 'yapmak', 'yar', 'yardım', 'yas', 'yat', 'yau', 'yav', 'yaw',
            'yax', 'yay', 'yaz', 'yazmak', 'ye', 'yeb', 'yec', 'yed', 'yef', 'yeg',
            'yeh', 'yek', 'yel', 'yem', 'yen', 'yeng', 'yeni', 'yep', 'yer', 'yes',
            'yet', 'yeu', 'yev', 'yew', 'yex', 'yey', 'yez', 'yi', 'yib', 'yic',
            'yid', 'yif', 'yig', 'yih', 'yik', 'yil', 'yim', 'yin', 'ying', 'yip',
            'yir', 'yis', 'yit', 'yiu', 'yiv', 'yiw', 'yix', 'yiy', 'yiz', 'yo',
            'yob', 'yoc', 'yod', 'yof', 'yog', 'yoh', 'yok', 'yol', 'yom', 'yon',
            'yong', 'yop', 'yor', 'yos', 'yot', 'you', 'yov', 'yow', 'yox', 'yoy',
            'yoz', 'yu', 'yub', 'yuc', 'yud', 'yuf', 'yug', 'yuh', 'yuk', 'yul',
            'yum', 'yun', 'yung', 'yup', 'yur', 'yus', 'yut', 'yuu', 'yuv', 'yuw',
            'yux', 'yuy', 'yuz',
            
            # Z ile başlayan kelimeler
            'za', 'zab', 'zac', 'zad', 'zaf', 'zag', 'zah', 'zak', 'zal', 'zam',
            'zan', 'zap', 'zar', 'zas', 'zat', 'zau', 'zav', 'zaw', 'zax', 'zay',
            'zaz', 'ze', 'zeb', 'zec', 'zed', 'zef', 'zeg', 'zeh', 'zek', 'zel',
            'zem', 'zen', 'zeng', 'zep', 'zer', 'zes', 'zet', 'zeu', 'zev', 'zew',
            'zex', 'zey', 'zez', 'zi', 'zib', 'zic', 'zid', 'zif', 'zig', 'zih',
            'zik', 'zil', 'zim', 'zin', 'zing', 'zip', 'zir', 'zis', 'zit', 'ziu',
            'ziv', 'ziw', 'zix', 'ziy', 'ziz', 'zo', 'zob', 'zoc', 'zod', 'zof',
            'zog', 'zoh', 'zok', 'zol', 'zom', 'zon', 'zong', 'zop', 'zor', 'zos',
            'zot', 'zou', 'zov', 'zow', 'zox', 'zoy', 'zoz', 'zu', 'zub', 'zuc',
            'zud', 'zuf', 'zug', 'zuh', 'zuk', 'zul', 'zum', 'zun', 'zung', 'zup',
            'zur', 'zus', 'zut', 'zuu', 'zuv', 'zuw', 'zux', 'zuy', 'zuz',
        ]
    
    def _calculate_frequencies(self):
        """Frekansları hesapla"""
        for i, word in enumerate(self.words):
            # İlk kelimeler daha yüksek frekans
            self.word_frequencies[word.lower()] = max(100 - i, 1)
    
    def search(self, prefix: str, max_results: int = 200) -> List[Dict]:
        """Prefix ile arama - WHATSAPP BENZERİ (her karakter için anlık öneri)"""
        if not prefix or len(prefix.strip()) == 0:
            return []
        
        prefix_lower = prefix.lower().strip()
        results = []
        
        # 1 karakter: prefix index kullan (tum "m", "n" vb. kelimeler - hizli ve eksiksiz)
        if len(prefix_lower) == 1:
            iter_words = self.prefix_index.get(prefix_lower[0], [])
            search_limit = len(iter_words)
        elif len(prefix_lower) == 2:
            search_limit = min(60000, len(self.words))
            iter_words = self.words[:search_limit]
        elif len(prefix_lower) == 3:
            search_limit = min(40000, len(self.words))
            iter_words = self.words[:search_limit]
        else:
            search_limit = min(20000, len(self.words))
            iter_words = self.words[:search_limit]
        
        found_count = 0
        for word in iter_words:
            word_lower = word.lower()
            
            # WHATSAPP BENZERİ: Prefix match - tam eşleşme öncelikli
            if len(prefix_lower) >= 1 and word_lower.startswith(prefix_lower) and word_lower != prefix_lower:
                frequency = self.word_frequencies.get(word_lower, 1)
                
                # WHATSAPP BENZERİ: Skorlama - prefix uzunluğu ve frekans önemli
                if len(prefix_lower) == 1:
                    # Tek harf: Kısa kelimeler öncelikli (WhatsApp gibi)
                    score = 10.0 - (len(word_lower) * 0.03) + (frequency / 30)
                elif len(prefix_lower) == 2:
                    # İki harf: Prefix match önemli
                    score = 9.5 - (len(word_lower) * 0.02) + (frequency / 50)
                elif len(prefix_lower) == 3:
                    # Üç harf: Daha spesifik
                    score = 9.0 - (len(word_lower) * 0.01) + (frequency / 100)
                else:
                    # Çok harf: Prefix uzunluğu çok önemli
                    prefix_ratio = len(prefix_lower) / len(word_lower)
                    score = prefix_ratio * 10.0 + (frequency / 100)
                
                results.append({
                    'word': word,
                    'score': score,
                    'frequency': frequency
                })
                found_count += 1
                
                if found_count >= max_results * 2:
                    break
        
        # iPhone benzeri: önce yaygın kelimeler, sonra skora göre sırala
        def _sort_key(r):
            w = (r.get('word') or '').strip()
            common_first = 0 if (_common_available and w and ' ' not in w and is_common(w)) else 1
            return (common_first, -r.get('score', 0))
        results.sort(key=_sort_key)
        return results[:max_results]
    
    def get_word_count(self) -> int:
        """Toplam kelime sayısı"""
        return len(self.words)
    
    def add_word(self, word: str, frequency: int = 1):
        """Yeni kelime ekle"""
        if word.lower() not in [w.lower() for w in self.words]:
            self.words.append(word)
            self.word_frequencies[word.lower()] = frequency

# Lazy Singleton Pattern - Load only when first accessed
_large_dictionary_instance = None
_large_dictionary_loading = False

def get_large_dictionary():
    """Get or create the large dictionary instance (lazy loading)"""
    global _large_dictionary_instance, _large_dictionary_loading
    
    if _large_dictionary_instance is not None:
        return _large_dictionary_instance
    
    if _large_dictionary_loading:
        # Prevent recursive loading
        return None
    
    _large_dictionary_loading = True
    try:
        _large_dictionary_instance = LargeTurkishDictionary()
    except Exception as e:
        print(f"[WARNING] Large dictionary load failed: {e}")
        _large_dictionary_instance = None
    finally:
        _large_dictionary_loading = False
    
    return _large_dictionary_instance

# Backwards compatibility - but now lazy
class _LazyDictionaryProxy:
    """Proxy that loads dictionary only when accessed"""
    def __getattr__(self, name):
        instance = get_large_dictionary()
        if instance is None:
            if name == 'words':
                return []
            if name == 'word_frequencies':
                return {}
            if name == 'search':
                return lambda *args, **kwargs: []
            if name == 'get_word_count':
                return lambda: 0
            return None
        return getattr(instance, name)

# Global instance - now lazy!
large_dictionary = _LazyDictionaryProxy()

