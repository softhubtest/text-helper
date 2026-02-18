import os
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM

def download_model():
    model_name = "ytu-ce-cosmos/turkish-gpt2-medium"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")
    target_dir = os.path.join(models_dir, "turkish-gpt2-medium")

    print(f"Model indiriliyor: {model_name}...")
    print(f"Hedef klasor: {target_dir}")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    try:
        print("Tokenizer indiriliyor...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.save_pretrained(target_dir)

        print("Model indiriliyor (bu biraz zaman alabilir)...")
        model = AutoModelForCausalLM.from_pretrained(model_name)
        model.save_pretrained(target_dir)

        print("--------------------------------------------------")
        print("BASARILI: Model indirildi ve kaydedildi.")
        print(f"Konum: {target_dir}")
        print("Sistem artik bu modeli offline kullanabilir.")
        print("--------------------------------------------------")
    
    except Exception as e:
        print(f"HATA: Model indirilemedi! {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_model()
