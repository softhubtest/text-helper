import os
import sys

def download_model():
    """
    Railway free tier'da hafiza limiti nedeniyle buyuk modeller indirilemez.
    Bu script uygulamanin AI modeli olmadan baslamasini saglar.
    Uygulama veri tabani (N-gram, Sozluk) ile calisir.
    """
    model_name = "ytu-ce-cosmos/turkish-gpt2-medium"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")
    target_dir = os.path.join(models_dir, "turkish-gpt2-medium")

    print(f"Model kontrol: {target_dir}")

    # Zaten indirilmisse tekrar indirme
    if os.path.exists(target_dir) and len(os.listdir(target_dir)) > 3:
        print("Model zaten mevcut, atlanıyor.")
        return

    # Ortam degiskenini kontrol et - kullanici modeli etkinlestirmek istiyorsa
    force_download = os.getenv("FORCE_MODEL_DOWNLOAD", "false").lower() == "true"
    
    if not force_download:
        print("--------------------------------------------------")
        print("INFO: Model indirme atlanıyor (RAM limiti nedeniyle).")
        print("INFO: Uygulama N-gram + Sozluk ile calisacak.")
        print("INFO: Modeli etkinlestirmek icin FORCE_MODEL_DOWNLOAD=true set edin.")
        print("--------------------------------------------------")
        return

    # FORCE_MODEL_DOWNLOAD=true ise dene (odemeli plan vs)  
    try:
        from huggingface_hub import snapshot_download
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        print(f"Model indiriliyor: {model_name}...")
        snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            max_workers=1
        )
        print(f"BASARILI: Model indirildi -> {target_dir}")
    
    except Exception as e:
        print(f"UYARI: Model indirilemedi: {e}")
        print("Uygulama dictionary modunda devam edecek.")

if __name__ == "__main__":
    download_model()
