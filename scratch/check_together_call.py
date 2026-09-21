import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_flux():
    key = os.getenv("TOGETHER_API_KEY")
    client = httpx.AsyncClient(timeout=30.0)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": "black-forest-labs/FLUX.1-schnell",
        "prompt": "4K photo of Swiss Alps in the rain",
        "width": 1344,
        "height": 768,
        "steps": 4,
        "n": 1,
        "response_format": "url",
    }
    resp = await client.post("https://api.together.xyz/v1/images/generations", headers=headers, json=body)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)

asyncio.run(test_flux())
