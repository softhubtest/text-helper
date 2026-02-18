from locust import HttpUser, task, between
import json

class TextHelperUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Simulate rapid typing
    
    @task
    def predict_fast(self):
        """Simulate fast typing (1-3 chars) hitting Trie/Cache"""
        self.client.post("/api/v1/predict", json={
            "text": "mer",
            "max_suggestions": 5,
            "use_ai": False # Fast path mainly
        })

    @task
    def predict_smart(self):
        """Simulate sentence completion hitting AI"""
        self.client.post("/api/v1/predict", json={
            "text": "Sipariş durumunu öğrenmek",
            "context_message": "Müşteri kargom nerede diye sordu",
            "max_suggestions": 5,
            "use_ai": True
        })

    @task
    def health_check(self):
        self.client.get("/api/v1/health")
