import asyncio
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
FAL_KEY = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
HEADERS = {"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}

async def upload_file_to_fal(file_path: Path) -> str:
    """Upload media file to Fal storage."""
    mime = "video/mp4" if file_path.suffix == ".mp4" else "audio/mpeg"
    async with httpx.AsyncClient(timeout=60.0) as client:
        init_resp = await client.post(
            "https://rest.alpha.fal.ai/storage/upload/initiate",
            headers=HEADERS,
            json={"file_name": file_path.name, "content_type": mime},
        )
        if init_resp.status_code not in (200, 201):
            raise RuntimeError(f"Initiate upload failed: {init_resp.status_code} {init_resp.text}")
        data = init_resp.json()
        upload_url = data["upload_url"]
        file_url = data["file_url"]
        
        file_bytes = file_path.read_bytes()
        put_resp = await client.put(upload_url, headers={"Content-Type": mime}, content=file_bytes, timeout=120.0)
        if put_resp.status_code not in (200, 201, 204):
            raise RuntimeError(f"PUT failed: {put_resp.status_code}")
        return file_url

async def main():
    video_path = Path("storage/live_production/job_mass_dance_10s/kling_raw_10s.mp4")
    audio_path = Path("scratch/test_female_telugu.mp3")
    
    print("1. Uploading Kling video and female audio to Fal...")
    video_fal_url = await upload_file_to_fal(video_path)
    audio_fal_url = await upload_file_to_fal(audio_path)
    print("Video Fal URL:", video_fal_url)
    print("Audio Fal URL:", audio_fal_url)
    
    # Try fal-ai/sync-lipsync first (Sync Labs 2.0 is often faster and higher fidelity on full body videos)
    endpoint = "https://queue.fal.run/fal-ai/sync-lipsync"
    payload = {
        "video_url": video_fal_url,
        "audio_url": audio_fal_url,
    }
    print(f"2. Submitting to {endpoint}...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        sub = await client.post(endpoint, headers=HEADERS, json=payload)
        print("Submit status:", sub.status_code)
        sub_data = sub.json()
        print("Submit data:", sub_data)
        
        status_url = sub_data.get("status_url")
        response_url = sub_data.get("response_url")
        
        if not status_url:
            print("No status url!")
            return
            
        for i in range(60):
            await asyncio.sleep(4)
            s_resp = await client.get(status_url, headers=HEADERS)
            status = s_resp.json().get("status")
            print(f"Poll {i+1} ({i*4}s): status={status}")
            if status == "COMPLETED":
                res = await client.get(response_url, headers=HEADERS)
                res_data = res.json()
                print("Result data:", res_data)
                vid_url = res_data.get("video", {}).get("url")
                if vid_url:
                    out_lipsync = Path("storage/live_production/job_mass_dance_10s/lipsync_master_10s.mp4")
                    v_bytes = (await client.get(vid_url, timeout=60.0)).content
                    out_lipsync.write_bytes(v_bytes)
                    print(f"SUCCESS! Saved lipsynced video to {out_lipsync} ({len(v_bytes)} bytes)")
                    return
            elif status in ("FAILED", "CANCELLED"):
                print("Task failed:", s_resp.text)
                break

if __name__ == "__main__":
    asyncio.run(main())
