from typing import Optional
from app.core.logs import logger

class SpellChecker:
    """Yazım düzeltme - Lazy loading ile bellek hatası önleme"""
    
    def __init__(self):
        self.speller = None
        self.available = False
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization - sadece gerektiğinde yükle"""
        if self._initialized:
            return
        
        self._initialized = True
        
        try:
            from autocorrect import Speller
            # Türkçe model yüklemeyi dene
            try:
                self.speller = Speller(lang='tr')
                self.available = True
                logger.info("Yazim duzeltme aktif (autocorrect)")
            except MemoryError:
                logger.warning("autocorrect bellek hatasi - yazim duzeltme devre disi")
                self.available = False
            except Exception as e:
                logger.warning(f"autocorrect yukleme hatasi: {e}")
                self.available = False
        except ImportError:
            self.available = False
            logger.warning("autocorrect kurulu degil: pip install autocorrect")
    
    async def check(self, word: str) -> Optional[str]:
        """Yazım hatasını düzelt"""
        # Lazy initialization
        if not self._initialized:
            self._initialize()
        
        if not self.available or not self.speller or len(word) <= 3:
            return None
        
        try:
            corrected = self.speller(word)
            return corrected if corrected != word else None
        except MemoryError:
            # Bellek hatası durumunda devre dışı bırak
            self.available = False
            return None
        except Exception:
            return None

spell_checker = SpellChecker()
