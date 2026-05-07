import httpx
import json
from app.core.config import settings

async def call_llm(prompt: str, system: str = "", temperature: float = 0.1) -> str:
    if settings.LLM_PROVIDER == "groq":
        return await _call_groq(prompt, system, temperature)
    elif settings.LLM_PROVIDER == "ollama":
        return await _call_ollama(prompt, system, temperature)
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")


async def _call_groq(prompt: str, system: str, temperature: float) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2048,
                "response_format": {"type": "json_object"},
            }
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_ollama(prompt: str, system: str, temperature: float) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
                "options": {"temperature": temperature}
            }
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]