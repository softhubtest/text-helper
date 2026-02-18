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
        from huggingface_hub import snapshot_download
        
        print(f"Model indiriliyor (Memory Optimized): {model_name}...")
        
        # OOM Hatası Önlemi: Modeli RAM'e yüklemeden direkt diske indir
        snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            local_dir_use_symlinks=False,  # Dosyaları direkt kopyala
            resume_download=True
        )

        print("--------------------------------------------------")
        print("BASARILI: Model indirildi ve kaydedildi.")
        print(f"Konum: {target_dir}")
        print("--------------------------------------------------")
    
    except Exception as e:
        print(f"HATA: Model indirilemedi! {e}")
        # Hata olsa bile devam et (uygulama çökmesin, sadece AI kapanır)
        pass

if __name__ == "__main__":
    download_model()
