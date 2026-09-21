import asyncio
import os
import sys
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

async def upload_file_to_fal(file_path: Path) -> str:
    mime = "video/mp4" if file_path.suffix == ".mp4" else "audio/mpeg"
    async with httpx.AsyncClient(timeout=60.0) as client:
        init_resp = await client.post(
            "https://rest.alpha.fal.ai/storage/upload/initiate",
            headers=HEADERS,
            json={"file_name": file_path.name, "content_type": mime},
        )
        data = init_resp.json()
        upload_url = data["upload_url"]
        file_url = data["file_url"]
        
        file_bytes = file_path.read_bytes()
        put_resp = await client.put(upload_url, headers={"Content-Type": mime}, content=file_bytes, timeout=60.0)
        print(f"Uploaded {file_path.name} ({len(file_bytes)} bytes) -> {file_url}", flush=True)
        return file_url

async def run_lipsync():
    video_path = Path("scratch/kling_720p_for_lipsync.mp4")
    audio_path = Path("scratch/female_dance_song_10s.mp3")
    
    print("1. Uploading assets to Fal...", flush=True)
    v_url = await upload_file_to_fal(video_path)
    a_url = await upload_file_to_fal(audio_path)
    
    # Try fal-ai/sync-lipsync
    endpoint = "https://queue.fal.run/fal-ai/sync-lipsync"
    payload = {"video_url": v_url, "audio_url": a_url}
    print(f"2. Submitting to {endpoint}...", flush=True)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        sub_data = sub.json()
        print("Submit response:", sub_data, flush=True)
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")
        
        if not status_url:
            print("Failed to get status URL!", flush=True)
            return False
            
        for i in range(45):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            s_json = s_resp.json()
            status = s_json.get("status")
            print(f"Poll {i+1} ({i*4}s): {status}", flush=True)
            if status == "COMPLETED":
                res = await client.get(response_url, headers=HEADERS)
                res_data = res.json()
                print("Result payload:", res_data, flush=True)
                vid_url = res_data.get("video", {}).get("url")
                if vid_url:
                    out_lipsync = Path("scratch/female_lipsynced_raw.mp4")
                    v_bytes = (await client.get(vid_url, timeout=60.0)).content
                    out_lipsync.write_bytes(v_bytes)
                    print(f"SAVED LIPSYNC VIDEO: {out_lipsync} ({len(v_bytes)} bytes)", flush=True)
                    return True
            elif status in ("FAILED", "CANCELLED"):
                print("Task failed:", s_json, flush=True)
                return False
    return False

if __name__ == "__main__":
    asyncio.run(run_lipsync())
