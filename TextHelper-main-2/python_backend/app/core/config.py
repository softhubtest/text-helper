import os

class Settings:
    API_KEY = os.getenv("API_KEY", "texthelper-secret-key-2024")
    USE_TRANSFORMER = os.getenv("USE_TRANSFORMER", "false").lower() == "true"
    USE_ELASTICSEARCH = os.getenv("USE_ELASTICSEARCH", "false").lower() == "true"
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", None)
    ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", None)
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", None)

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_URL = os.getenv("REDIS_URL", None)
    ENABLE_HEAVY_FEATURES = os.getenv("ENABLE_HEAVY_FEATURES", "false").lower() == "true"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, "data")

settings = Settings()
