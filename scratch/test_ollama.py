import sys
import os
import asyncio

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, 'c:/Users/Minh/Desktop/My-Project/RAG/src/backend')
from langchain_ollama import ChatOllama
from core.config import settings

async def main():
    print(f"Connecting to Ollama at {settings.OLLAMA_BASE_URL} with model {settings.OLLAMA_MODEL}...")
    llm = ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0.1
    )
    res = await llm.ainvoke("Xin chào! Hãy giới thiệu bạn là ai và tóm tắt ngắn gọn 1 câu về Deep Learning trong y tế.")
    print("\n--- PHẢN HỒI TỪ QWEN 2.5:7B ---")
    print(res.content)
    print("---------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
