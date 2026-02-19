"""
Smart Templates
- Context-aware templates
- Dynamic variable filling
- Template suggestions
"""

from typing import List, Dict, Optional
import re

class SmartTemplateManager:
    """Akıllı şablon yöneticisi"""
    
    def __init__(self):
        # Template kategorileri
        self.templates = {
            'customer_service': {
                'sipariş': [
                    'Sipariş #{{order_id}} durumu: {{status}}',
                    'Sipariş {{order_id}} için {{action}}',
                    'Sipariş numarası: {{order_id}}',
                    'Sipariş {{order_id}} takibi'
                ],
                'müşteri': [
                    'Müşteri {{customer_name}} için {{action}}',
                    'Müşteri desteği: {{issue}}',
                    'Müşteri memnuniyeti: {{rating}}'
                ],
                'ürün': [
                    'Ürün {{product_id}} bilgisi: {{info}}',
                    'Ürün {{product_id}} fiyatı: {{price}}',
                    'Ürün {{product_id}} stoku: {{stock}}'
                ]
            },
            'technical': {
                'api': [
                    'API endpoint: {{endpoint}}',
                    'API key: {{api_key}}',
                    'API request: {{method}} {{url}}',
                    'API response: {{status_code}}'
                ],
                'database': [
                    'Database query: {{query}}',
                    'Database connection: {{host}}:{{port}}',
                    'Database backup: {{backup_name}}'
                ],
                'error': [
                    'Error: {{error_message}}',
                    'Error code: {{error_code}}',
                    'Error resolution: {{solution}}'
                ]
            },
            'greeting': {
                'merhaba': [
                    'Merhaba {{name}}, nasıl yardımcı olabilirim?',
                    'Merhaba, size nasıl yardımcı olabilirim?',
                    'Merhaba {{name}}, hoş geldiniz!'
                ]
            }
        }
        
        # Template variables
        self.variables = {
            'order_id': ['12345', '67890', 'ORDER-001'],
            'customer_name': ['Ahmet', 'Ayşe', 'Müşteri'],
            'product_id': ['PROD-001', 'PROD-002'],
            'status': ['hazırlanıyor', 'kargoda', 'teslim edildi'],
            'action': ['takip', 'iptal', 'güncelleme'],
            'name': ['Değerli', 'Sayın']
        }
    
    def detect_context(self, text: str) -> str:
        """Context tespit et"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['sipariş', 'müşteri', 'ürün']):
            return 'customer_service'
        elif any(word in text_lower for word in ['api', 'database', 'error']):
            return 'technical'
        elif any(word in text_lower for word in ['merhaba', 'selam']):
            return 'greeting'
        
        return 'general'
    
    def fill_template(self, template: str) -> str:
        """Template'i doldur"""
        result = template
        
        # Variable replacement
        for var_name, values in self.variables.items():
            pattern = r'\{\{' + var_name + r'\}\}'
            if re.search(pattern, result):
                # İlk değeri kullan (gerçek uygulamada context'ten alınır)
                replacement = values[0] if values else var_name
                result = re.sub(pattern, replacement, result)
        
        return result
    
    def get_templates(self, text: str, max_results: int = 5) -> List[Dict]:
        """Template önerileri al"""
        results = []
        text_lower = text.lower()
        context = self.detect_context(text)
        
        if context in self.templates:
            templates = self.templates[context]
            
            # Kelime bazlı template
            for key, template_list in templates.items():
                if key in text_lower:
                    for i, template in enumerate(template_list[:max_results]):
                        filled = self.fill_template(template)
                        results.append({
                            'text': filled,
                            'type': 'template',
                            'score': 9.5 - (i * 0.1),
                            'description': f'Şablon ({context})',
                            'source': 'smart_templates',
                            'template': template,
                            'context': context
                        })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:max_results]
    
    def add_template(self, context: str, key: str, template: str):
        """Yeni template ekle"""
        if context not in self.templates:
            self.templates[context] = {}
        if key not in self.templates[context]:
            self.templates[context][key] = []
        self.templates[context][key].append(template)

# Global instance
smart_template_manager = SmartTemplateManager()
