import os
from google import genai
from dotenv import load_dotenv

def check_available_models():
    # Load API Key từ file .env
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("KHÔNG TÌM THẤY GEMINI_API_KEY trong file .env!")
        return

    print("Đang truy xuất danh sách các Model mà API Key của bạn được phép sử dụng...")
    print("-" * 50)
    try:
        client = genai.Client(api_key=api_key)
        available_models = []
        for m in client.models.list():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
                print(f"✔️ {m.name}")
                
        print("-" * 50)
        
        # Chọn model phù hợp nhất cho RAG
        if "models/gemini-1.5-flash" in available_models or "models/gemini-1.5-flash-latest" in available_models:
            print("\n👉 KẾT LUẬN: Đề xuất sử dụng 'gemini-1.5-flash'. Đây là model miễn phí, siêu nhanh và hoàn hảo cho hệ thống RAG.")
        elif "models/gemini-1.5-pro" in available_models:
            print("\n👉 KẾT LUẬN: Đề xuất sử dụng 'gemini-1.5-pro'.")
        else:
            print("\n👉 KẾT LUẬN: Hãy chọn một model có chữ 'gemini' trong danh sách trên.")
            
    except Exception as e:
        print(f"Lỗi khi truy xuất danh sách model: {e}")

if __name__ == "__main__":
    check_available_models()
