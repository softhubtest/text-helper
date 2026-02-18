import sys
import os
import asyncio
from unittest.mock import MagicMock

# Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Mock FastAPI Request
class MockRequest:
    def __init__(self):
        self.client = MagicMock()
        self.client.host = "127.0.0.1"
        self.url = MagicMock()
        self.url.path = "/api/v1/predict"
        self.headers = {}

async def run_debug():
    print("Importing app...")
    try:
        from app.routers.prediction import predict
        from app.models.schemas import PredictionRequest
        
        req = PredictionRequest(
            text="merhaba ",
            context_message=None,
            max_suggestions=5,
            use_ai=True,
            use_search=True
        )
        
        print("Running predict...")
        response = await predict(req, MockRequest(), user_id="debug_user")
        print("Success!")
        print(response)
        
    except Exception as e:
        print("\nCRASH DETECTED:")
        import traceback
        with open("crash.log", "w") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_debug())
