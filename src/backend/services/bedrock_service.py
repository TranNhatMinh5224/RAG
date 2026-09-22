import json
import httpx
from core.config import settings

class BedrockResponse:
    def __init__(self, content: str):
        self.content = content

class BedrockChunk:
    def __init__(self, content: str):
        self.content = content

class BedrockMantleChat:
    """Adapter bất đồng bộ kết nối trực tiếp với Amazon Bedrock (Mantle Endpoint) chuẩn OpenAI format."""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        temperature: float = 0.1
    ):
        self.api_key = api_key or settings.BEDROCK_API_KEY
        raw_base = (base_url or settings.BEDROCK_BASE_URL).rstrip("/")
        if not raw_base.endswith("/chat/completions"):
            self.endpoint = f"{raw_base}/chat/completions"
        else:
            self.endpoint = raw_base
            
        self.model = model or settings.BEDROCK_MODEL or "mistral.ministral-3-14b-instruct"
        self.temperature = temperature
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Project": "default",
            "Content-Type": "application/json"
        }

    async def ainvoke(self, prompt, config=None):
        prompt_text = prompt if isinstance(prompt, str) else str(prompt)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 1500,
            "temperature": self.temperature
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(self.endpoint, headers=self.headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return BedrockResponse(content=content)
            else:
                raise RuntimeError(f"Bedrock Mantle Error {res.status_code}: {res.text[:300]}")

    async def astream(self, prompt, config=None):
        prompt_text = prompt if isinstance(prompt, str) else str(prompt)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "max_tokens": 1500,
            "temperature": self.temperature,
            "stream": True
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", self.endpoint, headers=self.headers, json=payload) as response:
                if response.status_code != 200:
                    # Fallback non-streaming
                    full_res = await self.ainvoke(prompt, config)
                    yield BedrockChunk(content=full_res.content)
                    return
                    
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and not line.startswith("data: [DONE]"):
                        try:
                            data = json.loads(line[6:])
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                yield BedrockChunk(content=delta)
                        except Exception:
                            pass
