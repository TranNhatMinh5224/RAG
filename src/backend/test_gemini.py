import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI

async def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("KHÔNG TÌM THẤY GEMINI_API_KEY")
        return

    print("Đang khởi tạo Gemini 2.5 Flash...")
    try:
        llm = ChatGoogleGenerativeAI(
            temperature=0.1,
            google_api_key=api_key,
            model="gemini-2.5-flash"
        )
        print("Gửi câu hỏi thử nghiệm...")
        response = await llm.ainvoke("Xin chào, bạn là model nào?")
        print(f"Câu trả lời từ AI: {response.content}")
        print("Mọi thứ hoạt động HOÀN HẢO với gemini-2.5-pro!")
    except Exception as e:
        import traceback
        print(f"Lỗi: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini())
