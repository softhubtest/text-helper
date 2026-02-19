"""
Emoji Suggestions
- Context-aware emoji
- Sentiment-based emoji
- Smart emoji selection
"""

from typing import List, Dict
import re

class EmojiSuggester:
    """Emoji önerileri"""
    
    def __init__(self):
        # Emoji kategorileri
        self.emoji_categories = {
            'greeting': ['👋', '😊', '🙂', '👋🏻', '👋🏼'],
            'thanks': ['🙏', '❤️', '👍', '😊', '🙏🏻'],
            'happy': ['😄', '😊', '😃', '🎉', '✨', '🌟'],
            'sad': ['😢', '😔', '😞', '💔'],
            'excited': ['🎉', '🔥', '💯', '✨', '🚀'],
            'love': ['❤️', '💕', '😍', '🥰', '💖'],
            'support': ['💪', '🤝', '🙌', '👍'],
            'question': ['❓', '🤔', '💭'],
            'success': ['✅', '🎯', '🏆', '⭐'],
            'warning': ['⚠️', '❗', '🔔'],
            'customer_service': ['💬', '📞', '✉️', '📧'],
            'technical': ['⚙️', '🔧', '💻', '🔌'],
            'ecommerce': ['🛒', '💰', '📦', '🚚']
        }
        
        # Kelime-emoji mapping
        self.word_emoji_map = {
            'merhaba': ['👋', '😊', '🙂'],
            'selam': ['👋', '🙂'],
            'teşekkür': ['🙏', '❤️', '👍'],
            'sağol': ['🙏', '👍'],
            'mutlu': ['😄', '😊', '🎉'],
            'üzgün': ['😢', '😔'],
            'harika': ['🎉', '🔥', '✨'],
            'yardım': ['💪', '🤝', '🙌'],
            'destek': ['💪', '🤝'],
            'sipariş': ['📦', '🛒'],
            'ürün': ['🛒', '📦'],
            'kargo': ['🚚', '📦'],
            'api': ['💻', '⚙️'],
            'database': ['💾', '🔧'],
            'sorun': ['⚠️', '❗'],
            'hata': ['❌', '⚠️'],
            'başarı': ['✅', '🎯']
        }
    
    def detect_sentiment(self, text: str) -> str:
        """Basit sentiment tespiti"""
        text_lower = text.lower()
        
        # Positive keywords
        positive = ['mutlu', 'harika', 'mükemmel', 'güzel', 'iyi', 'başarı', 'teşekkür', 'sağol']
        if any(word in text_lower for word in positive):
            return 'positive'
        
        # Negative keywords
        negative = ['üzgün', 'kötü', 'sorun', 'hata', 'problem', 'şikayet']
        if any(word in text_lower for word in negative):
            return 'negative'
        
        # Neutral
        return 'neutral'
    
    def detect_context(self, text: str) -> str:
        """Context tespit et"""
        text_lower = text.lower()
        
        # Greeting
        if any(word in text_lower for word in ['merhaba', 'selam', 'günaydın']):
            return 'greeting'
        
        # Thanks
        if any(word in text_lower for word in ['teşekkür', 'sağol', 'minnettar']):
            return 'thanks'
        
        # Customer service
        if any(word in text_lower for word in ['sipariş', 'müşteri', 'destek']):
            return 'customer_service'
        
        # Technical
        if any(word in text_lower for word in ['api', 'endpoint', 'database']):
            return 'technical'
        
        # E-commerce
        if any(word in text_lower for word in ['ürün', 'sepet', 'kargo']):
            return 'ecommerce'
        
        return 'general'
    
    def suggest_emojis(self, text: str, max_results: int = 5) -> List[Dict]:
        """Emoji önerileri"""
        results = []
        text_lower = text.lower()
        
        # 1. Word-based emoji
        for word, emojis in self.word_emoji_map.items():
            if word in text_lower:
                for emoji in emojis[:2]:
                    results.append({
                        'text': emoji,
                        'type': 'emoji',
                        'score': 9.0,
                        'description': f'Emoji ({word})',
                        'source': 'emoji_suggestions'
                    })
        
        # 2. Context-based emoji
        context = self.detect_context(text)
        if context in self.emoji_categories:
            for emoji in self.emoji_categories[context][:3]:
                results.append({
                    'text': emoji,
                    'type': 'emoji',
                    'score': 8.5,
                    'description': f'Emoji ({context})',
                    'source': 'emoji_suggestions'
                })
        
        # 3. Sentiment-based emoji
        sentiment = self.detect_sentiment(text)
        if sentiment == 'positive':
            for emoji in self.emoji_categories['happy'][:2]:
                results.append({
                    'text': emoji,
                    'type': 'emoji',
                    'score': 8.0,
                    'description': 'Emoji (positive)',
                    'source': 'emoji_suggestions'
                })
        elif sentiment == 'negative':
            for emoji in self.emoji_categories['sad'][:2]:
                results.append({
                    'text': emoji,
                    'type': 'emoji',
                    'score': 8.0,
                    'description': 'Emoji (negative)',
                    'source': 'emoji_suggestions'
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

# Global instance
emoji_suggester = EmojiSuggester()
