import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def poll_task(task_id):
    key = os.getenv("SUNO_API_KEY")
    client = httpx.AsyncClient(timeout=30.0)
    headers = {"Authorization": f"Bearer {key}"}
    for i in range(15):
        await asyncio.sleep(4)
        resp = await client.get(f"https://api.musicapi.ai/api/v1/sonic/task/{task_id}", headers=headers)
        print(f"POLL {i+1}: status={resp.status_code}, body={resp.text[:300]}")
        data = resp.json()
        # check if succeeded
        if data.get("state") in ("succeeded", "success") or "audio_url" in str(data):
            print("SUCCESS! Audio found!")
            break

asyncio.run(poll_task("f07964c3-38b8-455b-ac15-4131a2713f3b"))
