import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")

async def check_endpoints():
    headers = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
    endpoints = [
        "https://queue.fal.run/fal-ai/latentsync",
        "https://queue.fal.run/fal-ai/sync-lipsync",
    ]
    async with httpx.AsyncClient() as client:
        for ep in endpoints:
            # Send an empty options or check if endpoint responds
            try:
                resp = await client.post(ep, headers=headers, json={})
                print(f"Endpoint {ep}: status {resp.status_code}, text: {resp.text[:100]}")
            except Exception as e:
                print(f"Endpoint {ep} error: {e}")

if __name__ == "__main__":
    asyncio.run(check_endpoints())
