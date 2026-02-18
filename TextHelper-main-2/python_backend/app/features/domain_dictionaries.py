"""
Domain-Specific Dictionaries
- Customer service dictionary
- Technical dictionary
- E-commerce dictionary
- Dynamic loading
"""

from typing import List, Dict, Optional
import os
import json

class DomainDictionaryManager:
    """Domain-specific sözlük yöneticisi"""
    
    def __init__(self):
        self.domains = {
            'customer_service': self._get_customer_service_dict(),
            'technical': self._get_technical_dict(),
            'ecommerce': self._get_ecommerce_dict(),
            'general': []
        }
    
    def _get_customer_service_dict(self) -> Dict[str, List[str]]:
        """Müşteri hizmetleri sözlüğü"""
        return {
            'sipariş': [
                'sipariş takibi', 'sipariş iptali', 'sipariş durumu',
                'sipariş numarası', 'sipariş sorgulama', 'sipariş bilgisi',
                'sipariş güncelleme', 'sipariş iade', 'sipariş değişim'
            ],
            'müşteri': [
                'müşteri hizmetleri', 'müşteri desteği', 'müşteri memnuniyeti',
                'müşteri temsilcisi', 'müşteri danışmanı', 'müşteri ilişkileri',
                'müşteri şikayeti', 'müşteri önerisi'
            ],
            'ürün': [
                'ürün bilgisi', 'ürün fiyatı', 'ürün stoku', 'ürün yorumları',
                'ürün kategorisi', 'ürün özellikleri', 'ürün garantisi'
            ],
            'kargo': [
                'kargo takibi', 'kargo durumu', 'kargo adresi', 'kargo ücreti',
                'kargo süresi', 'kargo teslimat', 'kargo iptali'
            ],
            'iade': [
                'iade talebi', 'iade süreci', 'iade koşulları', 'iade formu',
                'iade onayı', 'iade takibi'
            ],
            'destek': [
                'destek almak', 'destek talebi', 'destek ekibi', 'destek hattı',
                'teknik destek', 'müşteri desteği'
            ],
            'yardım': [
                'yardımcı olabilirim', 'yardım almak', 'yardım merkezi',
                'yardım dokümantasyonu'
            ],
            'şikayet': [
                'şikayet bildirimi', 'şikayet formu', 'şikayet takibi',
                'şikayet çözümü'
            ],
            'memnuniyet': [
                'memnuniyet anketi', 'memnuniyet değerlendirmesi',
                'memnuniyet geri bildirimi'
            ]
        }
    
    def _get_technical_dict(self) -> Dict[str, List[str]]:
        """Teknik terimler sözlüğü"""
        return {
            'API': [
                'API endpoint', 'API key', 'API documentation', 'API request',
                'API response', 'API authentication', 'API rate limit',
                'API version', 'API integration'
            ],
            'database': [
                'database connection', 'database query', 'database schema',
                'database backup', 'database restore', 'database migration',
                'database index', 'database optimization'
            ],
            'endpoint': [
                'endpoint URL', 'endpoint method', 'endpoint parameter',
                'endpoint response', 'endpoint authentication'
            ],
            'query': [
                'query string', 'query parameter', 'query optimization',
                'query result', 'query execution'
            ],
            'code': [
                'code review', 'code deployment', 'code repository',
                'code documentation', 'code testing'
            ],
            'error': [
                'error handling', 'error message', 'error log',
                'error debugging', 'error resolution'
            ],
            'server': [
                'server configuration', 'server response', 'server error',
                'server log', 'server maintenance'
            ],
            'authentication': [
                'authentication token', 'authentication method',
                'authentication key', 'authentication flow'
            ]
        }
    
    def _get_ecommerce_dict(self) -> Dict[str, List[str]]:
        """E-ticaret sözlüğü"""
        return {
            'ürün': [
                'ürün bilgisi', 'ürün fiyatı', 'ürün stoku', 'ürün yorumları',
                'ürün kategorisi', 'ürün özellikleri', 'ürün garantisi',
                'ürün resimleri', 'ürün videosu'
            ],
            'sepet': [
                'sepet içeriği', 'sepet tutarı', 'sepet temizleme',
                'sepet güncelleme', 'sepet kontrolü'
            ],
            'ödeme': [
                'ödeme yöntemi', 'ödeme onayı', 'ödeme bilgisi',
                'ödeme güvenliği', 'ödeme iptali'
            ],
            'fatura': [
                'fatura bilgisi', 'fatura adresi', 'fatura düzenleme',
                'fatura indirme', 'fatura gönderme'
            ],
            'kampanya': [
                'kampanya kodu', 'kampanya indirimi', 'kampanya süresi',
                'kampanya koşulları', 'kampanya kullanımı'
            ],
            'indirim': [
                'indirim kodu', 'indirim oranı', 'indirim uygulama',
                'indirim geçerliliği'
            ],
            'kargo': [
                'kargo takibi', 'kargo durumu', 'kargo adresi',
                'kargo ücreti', 'kargo süresi', 'kargo teslimat'
            ],
            'teslimat': [
                'teslimat adresi', 'teslimat süresi', 'teslimat takibi',
                'teslimat onayı', 'teslimat güncelleme'
            ]
        }
    
    def detect_domain(self, text: str) -> str:
        """Domain tespit et"""
        text_lower = text.lower()
        
        # Customer service keywords
        cs_keywords = ['sipariş', 'müşteri', 'destek', 'yardım', 'şikayet', 'memnuniyet', 'iade']
        if any(keyword in text_lower for keyword in cs_keywords):
            return 'customer_service'
        
        # Technical keywords
        tech_keywords = ['api', 'endpoint', 'database', 'query', 'code', 'server', 'error']
        if any(keyword in text_lower for keyword in tech_keywords):
            return 'technical'
        
        # E-commerce keywords
        ecom_keywords = ['ürün', 'sepet', 'ödeme', 'fatura', 'kampanya', 'indirim', 'kargo', 'teslimat']
        if any(keyword in text_lower for keyword in ecom_keywords):
            return 'ecommerce'
        
        return 'general'
    
    def get_domain_dict(self, domain: str) -> Dict[str, List[str]]:
        """Domain sözlüğünü al"""
        return self.domains.get(domain, {})
    
    def get_suggestions(self, word: str, context: Optional[str] = None, max_results: int = 10) -> List[Dict]:
        """Domain'e özel öneriler al"""
        results = []
        
        # Domain tespit et
        if context:
            domain = context
        else:
            domain = self.detect_domain(word)
        
        # Domain sözlüğünden önerileri al
        domain_dict = self.get_domain_dict(domain)
        word_lower = word.lower()
        
        if word_lower in domain_dict:
            suggestions = domain_dict[word_lower]
            for i, suggestion in enumerate(suggestions[:max_results]):
                results.append({
                    'text': suggestion,
                    'type': 'domain',
                    'score': 9.0 - (i * 0.1),
                    'description': f'{domain} sözlüğü',
                    'source': f'domain_{domain}',
                    'domain': domain
                })
        
        # Prefix match
        for key, suggestions in domain_dict.items():
            if key.startswith(word_lower) and key != word_lower:
                for suggestion in suggestions[:3]:
                    results.append({
                        'text': suggestion,
                        'type': 'domain',
                        'score': 8.0,
                        'description': f'{domain} sözlüğü (prefix match)',
                        'source': f'domain_{domain}',
                        'domain': domain
                    })
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for r in results:
            if r['text'] not in seen:
                seen.add(r['text'])
                unique_results.append(r)
        
        # Sort by score
        unique_results.sort(key=lambda x: x['score'], reverse=True)
        return unique_results[:max_results]
    
    def add_custom_domain(self, domain: str, dictionary: Dict[str, List[str]]):
        """Özel domain ekle"""
        self.domains[domain] = dictionary

# Global instance
domain_manager = DomainDictionaryManager()
