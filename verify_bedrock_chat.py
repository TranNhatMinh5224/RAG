import asyncio
import os
import sys
from pathlib import Path

# Fix encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add src/backend to sys.path
backend_dir = Path(__file__).resolve().parent / "src" / "backend"
sys.path.insert(0, str(backend_dir))

from core.config import settings

async def verify_bedrock_chat():
    from services.bedrock_service import BedrockMantleChat
    chat = BedrockMantleChat(
        api_key=settings.BEDROCK_API_KEY,
        base_url=settings.BEDROCK_BASE_URL,
        model=settings.BEDROCK_MODEL
    )
    print(f"[*] Testing Bedrock ainvoke with model: {chat.model}...")
    res = await chat.ainvoke("Chào bạn, hãy giới thiệu ngắn gọn trong 1 câu.")
    print(f"[SUCCESS] Result: {res.content}")

    print("\n[*] Testing Bedrock astream...")
    print("[STREAM START] ", end="", flush=True)
    async for chunk in chat.astream("Đếm từ 1 đến 5 bằng tiếng Việt."):
        print(chunk.content, end="", flush=True)
    print("\n[STREAM END]")

if __name__ == "__main__":
    asyncio.run(verify_bedrock_chat())
