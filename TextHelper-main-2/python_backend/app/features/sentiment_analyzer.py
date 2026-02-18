"""
Sentiment Analysis
- Positive/Negative/Neutral detection
- Emotion detection
- Sentiment-based suggestions
"""

from typing import Dict, List
import re

class SentimentAnalyzer:
    """Sentiment analiz"""
    
    def __init__(self):
        # Positive keywords
        self.positive_keywords = [
            'mutlu', 'harika', 'mükemmel', 'güzel', 'iyi', 'başarı',
            'teşekkür', 'sağol', 'minnettar', 'sevinç', 'neşe',
            'başarılı', 'harika', 'süper', 'müthiş', 'fantastik'
        ]
        
        # Negative keywords
        self.negative_keywords = [
            'üzgün', 'kötü', 'sorun', 'hata', 'problem', 'şikayet',
            'sinir', 'kızgın', 'hayal kırıklığı', 'başarısız',
            'kötü', 'berbat', 'dehşet', 'felaket'
        ]
        
        # Emotion keywords
        self.emotion_keywords = {
            'happy': ['mutlu', 'sevinç', 'neşe', 'gülümseme'],
            'sad': ['üzgün', 'keder', 'hüzün', 'ağlamak'],
            'angry': ['kızgın', 'sinir', 'öfke', 'kızmak'],
            'excited': ['heyecan', 'coşku', 'heyecanlı'],
            'grateful': ['teşekkür', 'minnettar', 'sağol'],
            'worried': ['endişe', 'kaygı', 'merak']
        }
    
    def analyze(self, text: str) -> Dict:
        """Sentiment analiz yap"""
        text_lower = text.lower()
        
        # Positive score
        positive_score = sum(1 for word in self.positive_keywords if word in text_lower)
        
        # Negative score
        negative_score = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Determine sentiment
        if positive_score > negative_score:
            sentiment = 'positive'
            confidence = min(positive_score / 3.0, 1.0)
        elif negative_score > positive_score:
            sentiment = 'negative'
            confidence = min(negative_score / 3.0, 1.0)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        # Detect emotion
        detected_emotions = []
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': positive_score,
            'negative_score': negative_score,
            'emotions': detected_emotions,
            'is_positive': sentiment == 'positive',
            'is_negative': sentiment == 'negative',
            'is_neutral': sentiment == 'neutral'
        }
    
    def get_sentiment_based_suggestions(self, text: str, sentiment: Dict) -> List[str]:
        """Sentiment'e göre öneriler"""
        suggestions = []
        
        if sentiment['is_positive']:
            suggestions.extend(['harika', 'mükemmel', 'ne güzel', 'çok iyi'])
        elif sentiment['is_negative']:
            suggestions.extend(['üzgünüm', 'destek', 'yardım', 'çözüm'])
        else:
            suggestions.extend(['tamam', 'anladım', 'devam'])
        
        return suggestions

# Global instance
sentiment_analyzer = SentimentAnalyzer()
