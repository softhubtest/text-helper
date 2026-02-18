"""
Security Improvements
- Rate limiting
- Input validation
- Authentication/Authorization
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import re

class SecurityManager:
    """Güvenlik yöneticisi"""
    
    def __init__(self):
        # Rate limiting: IP -> requests
        self.rate_limit_store: Dict[str, list] = defaultdict(list)
        self.rate_limit_max = 100  # requests per minute
        self.rate_limit_window = 60  # seconds
        
        # Blocked IPs
        self.blocked_ips = set()
        
        # API keys (basit implementasyon)
        self.api_keys = {}
    
    def check_rate_limit(self, ip: str) -> bool:
        """Rate limit kontrolü"""
        if ip in self.blocked_ips:
            return False
        
        now = datetime.now()
        # Eski kayıtları temizle
        self.rate_limit_store[ip] = [
            req_time for req_time in self.rate_limit_store[ip]
            if (now - req_time).total_seconds() < self.rate_limit_window
        ]
        
        # Limit kontrolü
        if len(self.rate_limit_store[ip]) >= self.rate_limit_max:
            self.blocked_ips.add(ip)
            return False
        
        # Yeni isteği kaydet
        self.rate_limit_store[ip].append(now)
        return True
    
    def validate_input(self, text: str) -> tuple[bool, Optional[str]]:
        """Input validation"""
        if not text:
            return True, None
        
        # SQL injection patterns
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|;|\*|/\*|\*/)",
            r"(\b(UNION|OR|AND)\s+\d+\s*=\s*\d+)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "SQL injection attempt detected"
        
        # XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "XSS attempt detected"
        
        # Length check
        if len(text) > 10000:  # Max 10KB
            return False, "Input too long"
        
        return True, None
    
    def sanitize_input(self, text: str) -> str:
        """Input sanitization"""
        # HTML tags kaldır
        text = re.sub(r'<[^>]+>', '', text)
        # Script tags kaldır
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        # JavaScript events kaldır
        text = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
        return text
    
    def check_api_key(self, api_key: Optional[str]) -> bool:
        """API key kontrolü"""
        if not api_key:
            return False
        return api_key in self.api_keys
    
    def add_api_key(self, api_key: str, user_id: str):
        """API key ekle"""
        self.api_keys[api_key] = user_id
    
    def unblock_ip(self, ip: str):
        """IP engelini kaldır"""
        self.blocked_ips.discard(ip)
        if ip in self.rate_limit_store:
            del self.rate_limit_store[ip]
    
    def get_rate_limit_info(self, ip: str) -> Dict:
        """Rate limit bilgisi"""
        now = datetime.now()
        recent_requests = [
            req_time for req_time in self.rate_limit_store.get(ip, [])
            if (now - req_time).total_seconds() < self.rate_limit_window
        ]
        
        return {
            'ip': ip,
            'requests_count': len(recent_requests),
            'limit': self.rate_limit_max,
            'window_seconds': self.rate_limit_window,
            'blocked': ip in self.blocked_ips,
            'remaining': max(0, self.rate_limit_max - len(recent_requests))
        }

# Global instance
security_manager = SecurityManager()
