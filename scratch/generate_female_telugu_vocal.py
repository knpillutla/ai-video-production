import asyncio
import os
import httpx
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

async def generate_female_vocal():
    key = os.getenv("SUNO_API_KEY")
    client = httpx.AsyncClient(timeout=60.0)
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "custom_mode": True,
        "prompt": "[Intro]\nహే... తయ్యారే తయ్యారే...\n[Chorus]\nపల్లెటూరి జాతరలో చిందేద్దాం రావే పిల్లా!\nడం డం డప్పుల మోతల్లో ఊగెద్దాం రావే భామా!",
        "tags": "Telugu folk mass, dappu beat, energetic female vocals, female playback singer, 138 bpm",
        "title": "Palletoori Jathara Female Vocal",
        "mv": "sonic-v5"
    }
    print("Submitting Suno generation for FEMALE Telugu vocals...")
    resp = await client.post("https://api.musicapi.ai/api/v1/sonic/create", headers=headers, json=body)
    print("Submit status:", resp.status_code)
    data = resp.json()
    print("Submit body:", data)
    task_id = data.get("task_id")
    if not task_id and isinstance(data.get("data"), dict):
        task_id = data["data"].get("task_id")
    elif not task_id and isinstance(data.get("data"), str):
        task_id = data["data"]
        
    print("Task ID:", task_id)
    if not task_id:
        return None
        
    poll_headers = {"Authorization": f"Bearer {key}"}
    for i in range(25):
        await asyncio.sleep(4)
        poll_resp = await client.get(f"https://api.musicapi.ai/api/v1/sonic/task/{task_id}", headers=poll_headers)
        p_data = poll_resp.json()
        print(f"Poll {i+1}: state={p_data.get('state')} / {poll_resp.status_code}")
        items = p_data.get("data")
        audio_url = None
        if isinstance(items, list) and items:
            audio_url = items[0].get("audio_url")
        elif isinstance(items, dict):
            audio_url = items.get("audio_url")
        elif p_data.get("audio_url"):
            audio_url = p_data.get("audio_url")
            
        if audio_url:
            print("FOUND AUDIO URL:", audio_url)
            out_file = Path("storage/live_production/job_mass_dance_10s/female_suno_vocal.mp3")
            out_file.parent.mkdir(parents=True, exist_ok=True)
            aud_bytes = (await client.get(audio_url, timeout=60.0)).content
            out_file.write_bytes(aud_bytes)
            print(f"Saved female vocal audio to {out_file} ({len(aud_bytes)} bytes)")
            return out_file
    return None

if __name__ == "__main__":
    asyncio.run(generate_female_vocal())
