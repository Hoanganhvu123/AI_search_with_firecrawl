import httpx
import asyncio
import os

MODELS_TO_TEST = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "llama3-8b-8192",          # Groq
    "mixtral-8x7b-32768",      # Groq
    "llama3-8b",               # Groq / Cerebras
    "mistral-tiny",            # Mistral
    "mistral-small-latest",    # Mistral
    "openai/gpt-3.5-turbo",    # OpenRouter
    "anthropic/claude-3-haiku",# OpenRouter
    "meta/llama3-8b-instruct", # NVIDIA NIM
]

async def test_models():
    async with httpx.AsyncClient(timeout=10.0) as client:
        for model in MODELS_TO_TEST:
            print(f"Testing model: {model} ...", end=" ")
            try:
                resp = await client.post(
                    "http://localhost:3001/v1/chat/completions",
                    json={"model": model, "messages": [{"role": "user", "content": "Say 'hello'"}]},
                    headers={"Authorization": f"Bearer {os.getenv('FREELLM_API_KEY', 'freellmapi-dummy-key')}"}
                )
                if resp.status_code == 200:
                    print("[OK] SUCCESS!")
                    print("Response:", resp.json()["choices"][0]["message"]["content"])
                    return model  # Stop on first success
                else:
                    print(f"[FAILED] ({resp.status_code})")
                    print("Error:", resp.text)
            except Exception as e:
                print(f"[ERROR]: {e}")

if __name__ == "__main__":
    asyncio.run(test_models())
