import os
import requests
import json
import gzip
import shutil
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

def download_file(url, target_path):
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Saved to {target_path}")
        return True
    else:
        print(f"Failed to download. Status: {response.status_code}")
        return False

def setup_frequencies():
    """
    Downloads a curated Turkish word frequency list.
    Source: OpenSubtitles & GitHub Curated Lists
    """
    print("\n--- Setting up Valid Word Corpus ---")
    target_file = DATA_DIR / "tr_frequencies.json"
    
    if target_file.exists():
        print("Frequencies already exist. Skipping.")
        return

    # Using a known reliable source for frequency list (approx 50k words)
    # This URL is a placeholder for a real raw url. 
    # Since I cannot browse the web freely for a URL, I will create a seed list 
    # and then simulate the 'download' or tell user to download if really needed.
    # BUT, I can write a script that generates it TO START WITH from the old dictionary 
    # filtering it STRICTLY, or better yet, I will define a 'seed' list here 
    # to avoid empty start.
    
    # Actually, let's use a public raw URL if possible. 
    # Common repository: 'hermitdave/FrequencyWords'
    url = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/tr/tr_50k.txt"
    
    txt_path = DATA_DIR / "tr_50k.txt"
    if download_file(url, txt_path):
        # Convert to JSON structure
        words = {}
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ')
                if len(parts) == 2:
                    word, count = parts
                    # Basic filters
                    if len(word) > 1 and word.isalpha():
                         words[word] = int(count)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False)
        
        print(f"Converted to JSON. Total valid words: {len(words)}")
        os.remove(txt_path) # Cleanup

def setup_transformers():
    """
    Pre-downloads the BERT tokenizer and model.
    """
    print("\n--- Setting up AI Models (BERT) ---")
    try:
        from transformers import AutoTokenizer, AutoModelForMaskedLM
        model_name = "dbmdz/bert-base-turkish-cased"
        
        print(f"Loading/Downloading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForMaskedLM.from_pretrained(model_name)
        
        # Save locally to be sure
        model.save_pretrained(MODELS_DIR / "bert_tr")
        tokenizer.save_pretrained(MODELS_DIR / "bert_tr")
        print("Model saved locally.")
        
    except ImportError:
        print("Transformers library not installed. Please run 'pip install -r requirements.txt' first.")
    except Exception as e:
        print(f"Error checking models: {e}")

def setup_gpt2():
    """
    Downloads Turkish GPT-2 Model for text generation.
    """
    print("\n--- Setting up GenAI Model (GPT-2) ---")
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        # A good, lightweight Turkish GPT-2 model
        model_name = "redrussianarmy/gpt2-turkish-cased"
        
        print(f"Loading/Downloading {model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        target_dir = MODELS_DIR / "gpt2_tr"
        model.save_pretrained(target_dir)
        tokenizer.save_pretrained(target_dir)
        print("GPT-2 Model saved locally.")
        
    except Exception as e:
        print(f"Error downloading GPT-2: {e}")

if __name__ == "__main__":
    setup_frequencies()
    setup_transformers() # BERT (still useful for filling masks)
    setup_gpt2()         # GPT-2 (New!)
    print("\n[OK] Setup Complete!")
