import os
import sys
import requests

# Fix encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_bedrock(api_key: str = None, model_name: str = "mistral.ministral-3-14b-instruct"):
    if not api_key:
        api_key = os.getenv("BEDROCK_API_KEY")
    
    if not api_key:
        print("[!] Loi: Chua cung cap API Key!")
        print("[*] Hay chay: python test_bedrock_mantle.py <YOUR_API_KEY>")
        return

    url = "https://bedrock-mantle.us-east-1.api.aws/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Project": "default",
        "Content-Type": "application/json"
    }

    # Danh sach cac model thu nghiem
    candidate_models = [
        model_name,
        "mistral.ministral-3-14b-instruct",
        "qwen.qwen3-next-80b-a3b",
        "openai.gpt-oss-120b"
    ]

    print(f"[*] Dang ket noi toi Bedrock Mantle Endpoint: {url}")
    print(f"[*] API Key: {api_key[:10]}...{api_key[-5:]}")
    
    for candidate in list(dict.fromkeys(candidate_models)):
        print(f"\n--- Dang thu nghiem Model: {candidate} ---")
        payload = {
            "model": candidate,
            "messages": [
                {
                    "role": "user",
                    "content": "Xin chao! Hay gioi thieu ngan gon ve ban than trong 1 cau tieng Viet."
                }
            ],
            "max_tokens": 150
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"[*] Status code: {res.status_code}")
            if res.status_code == 200:
                data = res.json()
                reply = data["choices"][0]["message"]["content"]
                print("[SUCCESS] Phan hoi THANH CONG tu Amazon Bedrock:")
                print(reply)
                return
            else:
                print(f"[!] Ket qua: {res.text}")
        except Exception as e:
            print(f"[ERROR] Loi ket noi: {e}")

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else None
    test_bedrock(key)
