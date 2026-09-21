import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_musicapi():
    key = os.getenv("SUNO_API_KEY")
    client = httpx.AsyncClient(timeout=30.0)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "custom_mode": True,
        "prompt": "[Chorus]\nసుర్రుమంటదిరో సుర్రుమంటదిరో పల్లెటూరి జాతర రేగిందిరో!",
        "tags": "Telugu folk mass, dappu beat, high energy",
        "title": "Surrumantadiro Test",
        "mv": "sonic-v5"
    }
    resp = await client.post("https://api.musicapi.ai/api/v1/sonic/create", headers=headers, json=body)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text)

asyncio.run(test_musicapi())
