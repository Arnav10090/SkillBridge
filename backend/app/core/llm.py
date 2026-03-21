import httpx, json
from app.core.config import settings

async def call_llm(prompt: str, system: str = "", temperature: float = 0.1) -> str:
    """Unified LLM caller — works with Ollama or OpenAI."""

    if settings.LLM_PROVIDER == "ollama":
        return await _call_ollama(prompt, system, temperature)
    elif settings.LLM_PROVIDER == "openai":
        return await _call_openai(prompt, system, temperature)
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")


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


async def _call_openai(prompt: str, system: str, temperature: float) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"}
    )
    return resp.choices[0].message.content