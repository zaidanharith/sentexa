import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[2]))

from ml.model.config import CHECKPOINT_DIR, HF_MODEL

def main():
    load_dotenv()
    
    hf_token = os.getenv("HF_TOKEN")
    hf_model = os.getenv("HF_MODEL", HF_MODEL)
    
    print("=" * 60)
    print("Sentexa ML Model Downloader for Production Deployment")
    print("-" * 60)
    print(f"Target Model ID: {hf_model}")
    print(f"Destination:     {CHECKPOINT_DIR}")
    
    if not hf_model:
        print("[-] Error: HF_MODEL is not set. Please configure it in your environment or .env file.")
        sys.exit(1)
        
    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        from huggingface_hub import login
    except ImportError:
        print("[-] Error: Hugging Face 'transformers' or 'huggingface_hub' is not installed.")
        print("    Please run: pip install transformers huggingface_hub torch")
        sys.exit(1)
        
    if hf_token:
        print("[+] Found HF_TOKEN in environment. Authenticating with Hugging Face...")
        try:
            login(token=hf_token)
            print("[✓] Hugging Face authentication successful.")
        except Exception as e:
            print(f"[!] Warning: HF authentication failed, attempting public download. Details: {e}")
    else:
        print("[*] No HF_TOKEN found in environment. Attempting public repository download...")

    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n[+] Downloading tokenizer for {hf_model}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(hf_model, token=hf_token if hf_token else None)
        tokenizer.save_pretrained(str(CHECKPOINT_DIR))
        print(f"[✓] Tokenizer saved successfully to {CHECKPOINT_DIR}")
    except Exception as e:
        print(f"[-] Error downloading tokenizer: {e}")
        sys.exit(1)
        
    print(f"\n[+] Downloading model weights for {hf_model} (this may take a few minutes)...")
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            hf_model, 
            token=hf_token if hf_token else None,
            low_cpu_mem_usage=True
        )
        model.save_pretrained(str(CHECKPOINT_DIR))
        print(f"[✓] Model weights saved successfully to {CHECKPOINT_DIR}")
    except Exception as e:
        print(f"[-] Error downloading model weights: {e}")
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("[✓] Model pre-download complete! The container is ready for offline/isolated inference.")
    print("=" * 60)

if __name__ == "__main__":
    main()
