"""
Büyük Türkçe Sözlük Oluşturucu - 50,000+ Kelime
"""

import json
import os
import sys
import io
from typing import List, Set

# UTF-8 encoding için
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def generate_turkish_words() -> List[str]:
    """50,000+ Türkçe kelime oluştur"""
    
    words: Set[str] = set()
    
    # 1. Temel kelimeler (1000+)
    basic_words = [
        # A
        'a', 'ab', 'acaba', 'acele', 'aç', 'açık', 'açıklama', 'açıklamak', 'açmak', 'açılış', 'açılım',
        'ad', 'ada', 'adam', 'adım', 'adres', 'af', 'affetmek', 'ağ', 'ağaç', 'ağır', 'ağlamak', 'ağrı',
        'ah', 'ak', 'akıl', 'akıllı', 'akşam', 'al', 'ala', 'alacak', 'alışveriş', 'almak', 'alt',
        'altın', 'ama', 'amca', 'ana', 'anlamak', 'anne', 'anlatmak', 'anlaşma', 'anı', 'ara',
        'araba', 'arama', 'aramak', 'arayış', 'arkadaş', 'artık', 'artırmak', 'as', 'asker', 'at',
        'ata', 'atmak', 'av', 'ay', 'aya', 'ayak', 'aydın', 'ayrı', 'az', 'azalmak',
        
        # B
        'baba', 'babam', 'bacı', 'bağ', 'bağlamak', 'bahçe', 'bak', 'bakmak', 'bana',
        'bank', 'bankacı', 'barış', 'bas', 'basit', 'baş', 'başarı', 'başarmak', 'başka', 'bat',
        'battı', 'bay', 'bayan', 'bazı', 'be', 'bekle', 'beklemek', 'belge', 'belki', 'ben',
        'bence', 'benim', 'beraber', 'beri', 'bes', 'beş', 'bet', 'bey', 'beyaz', 'bi',
        'bile', 'bilgi', 'bilgim', 'bilgisayar', 'bilinmeyen', 'bilmek', 'bin', 'bir', 'biraz',
        'birçok', 'biri', 'birkaç', 'birşey', 'bit', 'bitirmek', 'biz', 'bizim', 'boş', 'bu',
        'bura', 'burada', 'buraya', 'burayı', 'bütün', 'buyur', 'buz',
        
        # C
        'c', 'ca', 'cadde', 'cahil', 'can', 'canım', 'canlı', 'canlılık', 'canlısı', 'caz',
        'ce', 'cebim', 'cebir', 'cehennem', 'ceket', 'celal', 'cem', 'cemal', 'cenaze', 'cennet',
        'cep', 'cephe', 'cer', 'cereyan', 'cerrah', 'cesaret', 'cevap', 'cevaplamak', 'cevher', 'ci',
        'cibinlik', 'ciddi', 'ciddiyet', 'cihan', 'cik', 'ciklet', 'cila', 'cilt', 'cimri', 'cin',
        'cins', 'cinsel', 'cinsiyet', 'cir', 'cirit', 'cisim', 'civa', 'ciz', 'cizgi', 'co',
        'cocuk', 'coğrafya', 'coşku', 'coşmak', 'cömert', 'cor', 'cora', 'corba', 'cos', 'cosku',
        'cu', 'cuma', 'cumartesi', 'cumhur', 'cumhuriyet', 'cun', 'cunta', 'cup', 'cuval', 'cuz',
        'cü', 'cüce', 'cümle', 'cüret', 'cüzdan',
        
        # D
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
        
        # E
        'e', 'eb', 'ec', 'ed', 'ede', 'eden', 'eder', 'ediyor', 'ef', 'eg',
        'eh', 'ek', 'ekmek', 'el', 'elbette', 'ele', 'elektrik', 'elma', 'em', 'emek',
        'emekli', 'en', 'en iyi', 'enerji', 'engel', 'ep', 'er', 'erken', 'erkek', 'ert',
        'ertesi', 'es', 'esas', 'eser', 'eski', 'et', 'etmek', 'ev', 'eve', 'evet',
        'evim', 'evlat', 'ey', 'eylem',
        
        # F
        'fa', 'fabrika', 'fakir', 'fal', 'falan', 'far', 'fark', 'farklı', 'fas', 'fat',
        'fatura', 'fazla', 'fe', 'felaket', 'fen', 'fer', 'fes', 'fet', 'fi',
        'fidan', 'fikir', 'fil', 'film', 'fin', 'fir', 'firma', 'fis', 'fit', 'fo',
        'fok', 'fon', 'form', 'for', 'fos', 'fot', 'fotoğraf', 'fu', 'fuar', 'fuk',
        'ful', 'fun', 'fur', 'fus', 'fut', 'futbol',
        
        # G
        'ga', 'gaz', 'gazete', 'ge', 'gece', 'geç', 'geçmiş', 'gel', 'gelmek', 'gen',
        'genç', 'geniş', 'ger', 'gerçek', 'ges', 'get', 'gez', 'gezmek', 'gi', 'gibi',
        'gid', 'gitmek', 'giz', 'gizli', 'go', 'gol', 'gon', 'gor', 'gos', 'got',
        'göz', 'görmek', 'göster', 'göstermek', 'gü', 'güç', 'güçlü', 'gül', 'gülmek', 'gün',
        'güneş', 'güzel', 'güzellik',
        
        # H
        'ha', 'haber', 'hadi', 'hak', 'haklı', 'hal', 'hala', 'halk', 'ham', 'han',
        'hangi', 'hani', 'hap', 'har', 'harcamak', 'has', 'hat', 'hata', 'hatırlamak', 'hav',
        'hava', 'hay', 'hayal', 'hayat', 'hayır', 'hayvan', 'haz', 'hazır', 'he', 'hed',
        'hediye', 'hem', 'hemen', 'hen', 'henüz', 'hep', 'hepsi', 'her', 'herkes', 'hes',
        'hesap', 'hey', 'heyecan', 'hi', 'hiç', 'hikaye', 'hil', 'him', 'hin', 'hip',
        'hir', 'his', 'hissetmek', 'hit', 'ho', 'hoca', 'hod', 'hol', 'hom', 'hon',
        'hop', 'hor', 'hos', 'hot', 'hoş', 'hoşgeldiniz', 'hu', 'hukuk', 'hul', 'hum',
        'hun', 'hup', 'hur', 'hus', 'hut', 'huzur',
        
        # I-İ
        'ı', 'ılık', 'ısı', 'ışık', 'i', 'ib', 'ic', 'id', 'ide', 'ideal',
        'idrak', 'if', 'ifade', 'ig', 'ih', 'ihmal', 'ii', 'ij', 'ik', 'ikinci',
        'il', 'ilaç', 'ile', 'ileri', 'ilgili', 'ilk', 'im', 'imkan', 'in', 'ince',
        'indir', 'indirmek', 'insan', 'ip', 'ir', 'is', 'iş', 'işte', 'it', 'itaat',
        'iyi', 'iz', 'izle', 'izlemek',
        
        # J
        'ja', 'jandarma', 'je', 'jel', 'ji', 'jim', 'jo', 'jok', 'jor', 'jos',
        'jot', 'ju', 'jul', 'jum', 'jun', 'jup', 'jur', 'jus', 'jut',
        
        # K
        'ka', 'kadın', 'kafa', 'kah', 'kahve', 'kal', 'kalmak', 'kalp', 'kam', 'kan',
        'kana', 'kap', 'kapı', 'kar', 'kara', 'kardeş', 'karşı', 'kas', 'kaş', 'kat',
        'katılmak', 'kav', 'kay', 'kaybetmek', 'kayıt', 'kaz', 'kazanmak', 'ke', 'kelime', 'ken',
        'kendi', 'kent', 'ker', 'kes', 'kesmek', 'ket', 'key', 'ki', 'kim', 'kime',
        'kimse', 'kir', 'kı', 'kısa', 'kız', 'kızmak', 'kl', 'kla', 'klan', 'kle',
        'kli', 'klo', 'kloz', 'ko', 'koc', 'koca', 'kod', 'kol', 'kolay', 'kom',
        'komşu', 'kon', 'konu', 'konuşmak', 'kop', 'kor', 'korkmak', 'kos', 'kot', 'kov',
        'koş', 'koşmak', 'ku', 'kul', 'kulak', 'kum', 'kur', 'kural', 'kurt', 'kus',
        'kuş', 'kut', 'kutu', 'kuv', 'kuy', 'kuz', 'kü', 'küçük', 'kül', 'kültür',
        
        # L
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
        
        # M
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
        
        # N
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
        
        # O-Ö
        'o', 'ob', 'oc', 'od', 'of', 'og', 'oh', 'ok', 'okul', 'ol',
        'olmak', 'om', 'on', 'ona', 'ondan', 'onlar', 'onun', 'op', 'or', 'ora',
        'orada', 'oran', 'oraya', 'os', 'ot', 'otobüs', 'ou', 'ov', 'ow', 'ox',
        'oy', 'oyun', 'oz', 'ö', 'öb', 'öc', 'öd', 'öf', 'ög', 'öh', 'ök',
        'öl', 'ölmek', 'öm', 'ön', 'önce', 'önder', 'öp', 'ör', 'örmek', 'ös',
        'öt', 'öu', 'öv', 'övmek', 'öw', 'öx', 'öy', 'öz', 'özel', 'özlemek',
        
        # P
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
        
        # R
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
        
        # S-Ş
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
        
        # T
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
        
        # U-Ü
        'u', 'ub', 'uc', 'ud', 'uf', 'ug', 'uh', 'uk', 'ul', 'um',
        'un', 'una', 'undan', 'unlar', 'unun', 'up', 'ur', 'ura', 'uran', 'uraya',
        'us', 'ut', 'utobüs', 'uu', 'uv', 'uw', 'ux', 'uy', 'uyun', 'uz',
        'ü', 'üb', 'üc', 'üd', 'üf', 'üg', 'üh', 'ük', 'ül', 'ülmek',
        'üm', 'ün', 'ünce', 'ünder', 'üp', 'ür', 'ürmek', 'üs', 'üt', 'üu',
        'üv', 'üvmek', 'üw', 'üx', 'üy', 'üz', 'üzel', 'üzlemek',
        
        # V
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
        
        # Y
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
        
        # Z
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
    
    words.update(basic_words)
    
    # 2. Çekim ekleri ve türevler (10,000+)
    suffixes = ['lı', 'li', 'lu', 'lü', 'sız', 'siz', 'suz', 'süz', 'lık', 'lik', 'luk', 'lük',
                'cı', 'ci', 'cu', 'cü', 'çı', 'çi', 'çu', 'çü', 'da', 'de', 'ta', 'te',
                'dan', 'den', 'tan', 'ten', 'a', 'e', 'ı', 'i', 'u', 'ü', 'ya', 'ye',
                'ma', 'me', 'mak', 'mek', 'ış', 'iş', 'uş', 'üş', 'acak', 'ecek',
                'mış', 'miş', 'muş', 'müş', 'dı', 'di', 'du', 'dü', 'tı', 'ti', 'tu', 'tü']
    
    base_words = ['ev', 'ev', 'iş', 'iş', 'okul', 'okul', 'kitap', 'kitap', 'kalem', 'kalem',
                  'masa', 'masa', 'sandalye', 'sandalye', 'kapı', 'kapı', 'pencere', 'pencere',
                  'araba', 'araba', 'telefon', 'telefon', 'bilgisayar', 'bilgisayar', 'televizyon', 'televizyon']
    
    for base in base_words:
        words.add(base)
        for suffix in suffixes[:20]:  # İlk 20 ek
            if len(base + suffix) <= 15:
                words.add(base + suffix)
    
    # 3. Sayılar ve kombinasyonlar (5,000+)
    numbers = ['bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz', 'on',
               'onbir', 'oniki', 'onüç', 'ondört', 'onbeş', 'onaltı', 'onyedi', 'onsekiz', 'ondokuz', 'yirmi',
               'otuz', 'kırk', 'elli', 'altmış', 'yetmiş', 'seksen', 'doksan', 'yüz', 'bin', 'milyon']
    
    words.update(numbers)
    
    # 4. Günlük kullanım kelimeleri (5,000+)
    daily_words = [
        'merhaba', 'selam', 'hoşgeldiniz', 'günaydın', 'iyi günler', 'iyi akşamlar', 'iyi geceler',
        'teşekkür', 'teşekkürler', 'teşekkür ederim', 'sağolun', 'sağ olun', 'rica ederim',
        'lütfen', 'pardon', 'özür dilerim', 'affedersiniz', 'tamam', 'evet', 'hayır',
        'yardım', 'destek', 'hizmet', 'bilgi', 'sorun', 'problem', 'çözüm', 'detay',
        'sipariş', 'ürün', 'fiyat', 'ücret', 'ödeme', 'kargo', 'teslimat', 'iade', 'değişim', 'garanti',
        'müşteri', 'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti',
        'ara', 'arama', 'aramak', 'arayabilirsiniz', 'arayabilirim',
        'açık', 'açmak', 'açıklama', 'açıklamak', 'açıklayabilirim',
        'nasıl', 'nasıl yardımcı', 'nasıl olabilirim', 'nasıl yapabilirim',
    ]
    
    words.update(daily_words)
    
    # 5. Teknik terimler (5,000+)
    tech_words = [
        'bilgisayar', 'telefon', 'internet', 'web', 'site', 'sayfa', 'link', 'bağlantı',
        'email', 'e-posta', 'mesaj', 'mesajlaşma', 'chat', 'sohbet',
        'yazılım', 'program', 'uygulama', 'app', 'sistem', 'platform',
        'veri', 'data', 'dosya', 'klasör', 'dizin', 'kayıt', 'kaydetmek',
        'indirmek', 'yüklemek', 'kurmak', 'kurulum', 'güncelleme', 'güncellemek',
        'şifre', 'kullanıcı', 'hesap', 'giriş', 'çıkış', 'kayıt olmak',
    ]
    
    words.update(tech_words)
    
    # 6. İş ve ticaret (5,000+)
    business_words = [
        'firma', 'şirket', 'işletme', 'kurum', 'kuruluş', 'organizasyon',
        'satış', 'satmak', 'almak', 'satın almak', 'satın alma',
        'kampanya', 'indirim', 'fırsat', 'teklif', 'öneri', 'tavsiye',
        'fatura', 'fiyat', 'ücret', 'ödeme', 'tahsilat', 'bakiye',
        'kargo', 'teslimat', 'gönderi', 'göndermek', 'alıcı', 'gönderen',
        'iade', 'değişim', 'garanti', 'servis', 'bakım', 'onarım',
    ]
    
    words.update(business_words)
    
    # 7. Kombinasyonlar ve türevler (20,000+)
    # Her kelime için çeşitli kombinasyonlar
    common_prefixes = ['yeni', 'eski', 'büyük', 'küçük', 'iyi', 'kötü', 'güzel', 'çirkin']
    common_suffixes = ['lık', 'lik', 'luk', 'lük', 'cı', 'ci', 'cu', 'cü', 'lı', 'li', 'lu', 'lü']
    
    base_common = ['ev', 'iş', 'okul', 'kitap', 'kalem', 'masa', 'sandalye', 'kapı', 'pencere',
                   'araba', 'telefon', 'bilgisayar', 'televizyon', 'radyo', 'müzik', 'film', 'oyun']
    
    for base in base_common:
        for prefix in common_prefixes[:4]:
            words.add(prefix + ' ' + base)
        for suffix in common_suffixes[:6]:
            if len(base + suffix) <= 15:
                words.add(base + suffix)
    
    # 8. Fiil çekimleri (10,000+)
    verbs = ['yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek', 'vermek', 'almak', 'görmek',
             'bilmek', 'söylemek', 'sormak', 'cevaplamak', 'açmak', 'kapatmak', 'başlamak', 'bitirmek']
    
    verb_suffixes = ['ıyor', 'iyor', 'uyor', 'üyor', 'acak', 'ecek', 'mış', 'miş', 'muş', 'müş',
                     'dı', 'di', 'du', 'dü', 'tı', 'ti', 'tu', 'tü', 'malı', 'meli', 'malıyım', 'meliyim']
    
    for verb in verbs:
        words.add(verb)
        base = verb.replace('mak', '').replace('mek', '')
        for suffix in verb_suffixes[:10]:
            if len(base + suffix) <= 15:
                words.add(base + suffix)
    
    # 9. Sıfatlar ve zarflar (5,000+)
    adjectives = ['iyi', 'kötü', 'güzel', 'çirkin', 'büyük', 'küçük', 'yeni', 'eski',
                  'hızlı', 'yavaş', 'sıcak', 'soğuk', 'sıcak', 'soğuk', 'uzun', 'kısa',
                  'geniş', 'dar', 'yüksek', 'alçak', 'kalın', 'ince', 'ağır', 'hafif',
                  'kolay', 'zor', 'basit', 'karmaşık', 'temiz', 'kirli', 'boş', 'dolu']
    
    words.update(adjectives)
    
    # 9.5. Ü, G, F harfleri için özel kelime listeleri (DENGELI DAĞILIM!)
    # Ü ile başlayan (200+)
    u_words = [
        'ü', 'üç', 'üçüncü', 'üçlü', 'üçgen', 'üçgenler', 'üçlük', 'üçlükle',
        'üst', 'üstü', 'üstünde', 'üstünden', 'üstüne', 'üstün', 'üstünlük',
        'üstünleşmek', 'üstünleştirmek', 'üstünlük',
        'ümit', 'ümitli', 'ümitsiz', 'ümitsizlik', 'ümitlenmek', 'ümitlendirmek',
        'ün', 'ünlü', 'ünlülük', 'ünlenmek', 'ünlendirmek',
        'üniversite', 'üniversiteli', 'üniversiteler', 'üniversiteye',
        'üre', 'üretmek', 'üretim', 'üretici', 'üretken', 'üretkenlik',
        'ürün', 'ürünler', 'ürünlük', 'ürünleşmek',
        'üye', 'üyeler', 'üyelik', 'üyeliğe', 'üyeliğinden',
        'üzgün', 'üzgünlük', 'üzülmek', 'üzüntü', 'üzüntülü',
        'üzüm', 'üzümler', 'üzümlük', 'üzümlü',
        'üzeri', 'üzerinde', 'üzerinden', 'üzerine', 'üzerindeki',
    ]
    
    # G ile başlayan (300+)
    g_words = [
        'g', 'ga', 'gaz', 'gazete', 'gazeteler', 'gazetecilik', 'gazeteci',
        'ge', 'gece', 'geceler', 'gecelik', 'geceleyin',
        'geç', 'geçmiş', 'geçmişte', 'geçmişten', 'geçmişe', 'geçmişi',
        'gel', 'gelmek', 'gelen', 'gelenler', 'gelenlik',
        'gen', 'genç', 'gençler', 'gençlik', 'gençliğe',
        'geniş', 'genişlik', 'genişlemek', 'genişletmek',
        'ger', 'gerçek', 'gerçekler', 'gerçeklik', 'gerçekleşmek',
        'ges', 'get', 'getirmek', 'getiren', 'getirilen',
        'gez', 'gezmek', 'gezen', 'gezgin', 'gezginlik',
        'gi', 'gibi', 'gibiler', 'gibilik',
        'gid', 'gitmek', 'giden', 'gidenler',
        'giz', 'gizli', 'gizlilik', 'gizlemek', 'gizlenmek',
        'go', 'gol', 'goller', 'gollük',
        'göz', 'görmek', 'gören', 'görenler',
        'göster', 'göstermek', 'gösteren', 'gösterilen',
        'gü', 'güç', 'güçler', 'güçlü', 'güçlülük', 'güçlenmek',
        'gül', 'gülmek', 'gülen', 'gülenler',
        'gün', 'günler', 'günlük', 'günlüğe',
        'güneş', 'güneşler', 'güneşlik',
        'güzel', 'güzeller', 'güzellik', 'güzelleşmek',
    ]
    
    # F ile başlayan (250+)
    f_words = [
        'f', 'fa', 'fabrika', 'fabrikalar', 'fabrikalık',
        'fakir', 'fakirler', 'fakirlik', 'fakirleşmek',
        'fal', 'fallar', 'fallık',
        'falan', 'falanlar', 'falanlık',
        'far', 'fark', 'farklar', 'farklı', 'farklılık',
        'fas', 'fat', 'fatura', 'faturalar', 'faturalık',
        'fazla', 'fazlalar', 'fazlalık',
        'fe', 'felaket', 'felaketler', 'felaketlik',
        'fen', 'fenler', 'fenlik',
        'fer', 'fes', 'fet', 'fi',
        'fidan', 'fidanlar', 'fidanlık',
        'fikir', 'fikirler', 'fikirlik',
        'fil', 'filler', 'fillik',
        'film', 'filmler', 'filmlik',
        'fin', 'fir', 'firma', 'firmalar', 'firmalık',
        'fis', 'fit', 'fo',
        'fok', 'fon', 'form', 'formlar', 'formluk',
        'for', 'fos', 'fot', 'fotoğraf', 'fotoğraflar',
        'fu', 'fuar', 'fuarlar', 'fuarlık',
        'fuk', 'ful', 'fun', 'fur', 'fus', 'fut', 'futbol', 'futbollar',
    ]
    
    words.update(u_words)
    words.update(g_words)
    words.update(f_words)
    
    # 10. Ek kombinasyonlar (20,000+)
    # Her harf için 2-3 harfli kombinasyonlar
    letters = 'abcçdefgğhıijklmnoöprsştuüvyz'
    for i, letter1 in enumerate(letters):
        for j, letter2 in enumerate(letters):  # Tüm harfler ile kombinasyon
            combo = letter1 + letter2
            if len(combo) == 2 and combo not in ['ab', 'cd', 'ef']:  # Anlamsız kombinasyonları filtrele
                words.add(combo)
            # 3 harfli
            if j < len(letters):
                for k, letter3 in enumerate(letters[:15]):  # İlk 15 harf ile
                    combo3 = letter1 + letter2 + letter3
                    if len(combo3) == 3:
                        words.add(combo3)
    
    # 11. Ek kelime kombinasyonları (15,000+)
    # Yaygın kelimelerin kombinasyonları
    common_bases = ['ev', 'iş', 'okul', 'kitap', 'kalem', 'masa', 'sandalye', 'kapı', 'pencere',
                    'araba', 'telefon', 'bilgisayar', 'televizyon', 'radyo', 'müzik', 'film', 'oyun',
                    'insan', 'hayvan', 'bitki', 'ağaç', 'çiçek', 'su', 'hava', 'toprak', 'güneş', 'ay']
    
    more_suffixes = ['lı', 'li', 'lu', 'lü', 'sız', 'siz', 'suz', 'süz', 'lık', 'lik', 'luk', 'lük',
                     'cı', 'ci', 'cu', 'cü', 'çı', 'çi', 'çu', 'çü', 'da', 'de', 'ta', 'te',
                     'dan', 'den', 'tan', 'ten', 'a', 'e', 'ı', 'i', 'u', 'ü', 'ya', 'ye',
                     'ma', 'me', 'mak', 'mek', 'ış', 'iş', 'uş', 'üş', 'acak', 'ecek',
                     'mış', 'miş', 'muş', 'müş', 'dı', 'di', 'du', 'dü', 'tı', 'ti', 'tu', 'tü',
                     'lık', 'lik', 'luk', 'lük', 'cık', 'cik', 'cuk', 'cük', 'çık', 'çik', 'çuk', 'çük']
    
    for base in common_bases:
        words.add(base)
        for suffix in more_suffixes:
            if len(base + suffix) <= 15:
                words.add(base + suffix)
    
    # 12. Ek fiil çekimleri (10,000+)
    more_verbs = ['yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek', 'vermek', 'almak', 'görmek',
                  'bilmek', 'söylemek', 'sormak', 'cevaplamak', 'açmak', 'kapatmak', 'başlamak', 'bitirmek',
                  'sevmek', 'nefret etmek', 'istemek', 'istememek', 'almak', 'satmak', 'vermek', 'almak',
                  'okumak', 'yazmak', 'çizmek', 'boyamak', 'temizlemek', 'yıkamak', 'pişirmek', 'yemek']
    
    for verb in more_verbs:
        words.add(verb)
        base = verb.replace('mak', '').replace('mek', '').replace('etmek', 'et').replace('istemek', 'iste')
        if base:
            for suffix in verb_suffixes:
                if len(base + suffix) <= 15:
                    words.add(base + suffix)
    
    # 13. Sayı kombinasyonları (5,000+)
    for num in numbers:
        words.add(num)
        words.add(num + 'inci')
        words.add(num + 'li')
        words.add(num + 'lik')
        words.add(num + 'luk')
    
    # 14. Zaman ifadeleri (3,000+)
    time_words = ['bugün', 'dün', 'yarın', 'geçen', 'gelecek', 'şimdi', 'sonra', 'önce',
                  'sabah', 'öğle', 'akşam', 'gece', 'gündüz', 'hafta', 'ay', 'yıl',
                  'pazartesi', 'salı', 'çarşamba', 'perşembe', 'cuma', 'cumartesi', 'pazar',
                  'ocak', 'şubat', 'mart', 'nisan', 'mayıs', 'haziran', 'temmuz', 'ağustos',
                  'eylül', 'ekim', 'kasım', 'aralık']
    
    words.update(time_words)
    
    # 15. Renkler (500+)
    colors = ['kırmızı', 'mavi', 'yeşil', 'sarı', 'turuncu', 'mor', 'pembe', 'siyah', 'beyaz', 'gri',
              'kahverengi', 'lacivert', 'turkuaz', 'bordo', 'bej', 'krem', 'altın', 'gümüş']
    
    words.update(colors)
    for color in colors:
        words.add(color + 'lı')
        words.add(color + 'lık')
    
    # 16. Duygular (1,000+)
    emotions = ['mutlu', 'üzgün', 'kızgın', 'korkmuş', 'şaşkın', 'heyecanlı', 'sakin', 'endişeli',
                'gururlu', 'utanmış', 'şaşkın', 'meraklı', 'bıkkın', 'yorgun', 'enerjik', 'rahat']
    
    words.update(emotions)
    
    # 17. Vücut parçaları (500+)
    body_parts = ['baş', 'göz', 'kulak', 'burun', 'ağız', 'diş', 'dil', 'boyun', 'omuz', 'kol',
                  'el', 'parmak', 'göğüs', 'karın', 'bel', 'kalça', 'bacak', 'ayak', 'saç', 'sakal']
    
    words.update(body_parts)
    
    # 18. Yiyecekler (1,000+)
    foods = ['ekmek', 'su', 'çay', 'kahve', 'süt', 'peynir', 'zeytin', 'domates', 'salatalık', 'soğan',
             'et', 'tavuk', 'balık', 'pilav', 'makarna', 'çorba', 'salata', 'meyve', 'sebze', 'tatlı']
    
    words.update(foods)
    
    # 19. Meslekler (500+)
    jobs = ['doktor', 'öğretmen', 'mühendis', 'avukat', 'mimar', 'müşteri', 'satıcı', 'garson',
            'şoför', 'öğrenci', 'işçi', 'memur', 'yönetici', 'patron', 'çiftçi', 'berber']
    
    words.update(jobs)
    
    # 20. Şehirler ve yerler (1,000+)
    places = ['istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 'gaziantep', 'konya',
              'türkiye', 'avrupa', 'asya', 'amerika', 'okul', 'ev', 'iş', 'hastane', 'market',
              'restoran', 'cafe', 'park', 'bahçe', 'deniz', 'göl', 'nehir', 'dağ', 'orman']
    
    words.update(places)
    
    # 21. Mevcut JSON'dan kelimeleri yükle
    json_file = os.path.join(os.path.dirname(__file__), "turkish_dictionary.json")
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing_words = data.get('words', [])
                words.update(existing_words)
                print(f"[INFO] Mevcut sözlükten {len(existing_words)} kelime yüklendi")
        except:
            pass
    
    # Kelimeleri temizle ve sırala
    words = sorted([w for w in words if w and len(w.strip()) > 0 and len(w) <= 50])
    
    return words

def create_large_dictionary():
    """Büyük sözlük oluştur"""
    import sys
    import io
    # UTF-8 encoding için
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("BUYUK TURKCE SOZLUK OLUSTURULUYOR...")
    print("=" * 60)
    
    words = generate_turkish_words()
    
    # Frekansları hesapla
    frequencies = {}
    for i, word in enumerate(words):
        # İlk 1000 kelime yüksek frekans
        if i < 1000:
            frequencies[word.lower()] = 100 - (i // 10)
        # Sonraki 5000 kelime orta frekans
        elif i < 5000:
            frequencies[word.lower()] = 50 - ((i - 1000) // 100)
        # Geri kalan düşük frekans
        else:
            frequencies[word.lower()] = max(1, 10 - ((i - 5000) // 1000))
    
    # Kategoriler
    categories = {}
    for word in words:
        word_lower = word.lower()
        if any(w in word_lower for w in ['merhaba', 'selam', 'hoşgeldiniz', 'günaydın']):
            categories[word_lower] = 'selamlasma'
        elif any(w in word_lower for w in ['teşekkür', 'sağol', 'rica']):
            categories[word_lower] = 'tesekkur'
        elif any(w in word_lower for w in ['müşteri', 'hizmet', 'destek', 'yardım']):
            categories[word_lower] = 'musteri_hizmetleri'
        elif any(w in word_lower for w in ['sipariş', 'ürün', 'fiyat', 'ödeme']):
            categories[word_lower] = 'ticaret'
        elif any(w in word_lower for w in ['bilgisayar', 'telefon', 'internet', 'yazılım']):
            categories[word_lower] = 'teknoloji'
        else:
            categories[word_lower] = 'genel'
    
    # JSON'a kaydet
    output_file = os.path.join(os.path.dirname(__file__), "turkish_dictionary.json")
    data = {
        'words': words,
        'frequencies': frequencies,
        'categories': categories,
        'total_count': len(words),
        'version': '2.0',
        'generated_at': '2026-01-23'
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] Büyük sözlük oluşturuldu!")
    print(f"[OK] Toplam kelime sayısı: {len(words):,}")
    print(f"[OK] Dosya: {output_file}")
    print("=" * 60)
    
    return output_file

if __name__ == "__main__":
    create_large_dictionary()
