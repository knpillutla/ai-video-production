import asyncio
import httpx
from pathlib import Path
import subprocess, imageio_ffmpeg

headers = {'Authorization': 'Key 82b43aa4-6d10-44ef-940f-f43ac2562224:fb1f36b10bf499206772af7efc421258'}
status_url = 'https://queue.fal.run/fal-ai/sync-lipsync/requests/01a0c14a-d81d-7e51-8a97-7b7e8053a996/status'
response_url = 'https://queue.fal.run/fal-ai/sync-lipsync/requests/01a0c14a-d81d-7e51-8a97-7b7e8053a996'

async def poll():
    print("Resuming polling for Suno Lipsync request...", flush=True)
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(60):
            await asyncio.sleep(5)
            r = await client.get(status_url, headers=headers)
            status = r.json().get('status')
            print(f"Poll {i+1} ({i*5}s): {status}", flush=True)
            if status == 'COMPLETED':
                res = await client.get(response_url, headers=headers)
                vid_url = res.json().get('video', {}).get('url')
                if vid_url:
                    out_raw = Path('scratch/suno_lipsynced_raw.mp4')
                    v_bytes = (await client.get(vid_url, timeout=90.0)).content
                    out_raw.write_bytes(v_bytes)
                    print(f"SUCCESS: Downloaded raw lipsync video ({len(v_bytes)} bytes)", flush=True)
                    
                    exe = imageio_ffmpeg.get_ffmpeg_exe()
                    final_4k = Path('storage/live_production/job_mass_dance_10s/telugu_female_lipsync_dance_4k_master.mp4')
                    cmd = [
                        exe, '-y',
                        '-i', str(out_raw),
                        '-vf', 'scale=3840:2160:flags=lanczos',
                        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-r', '30',
                        '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                        str(final_4k)
                    ]
                    subprocess.run(cmd, check=True)
                    print(f"4K Broadcast Master with PURE SUNO MUSIC Ready: {final_4k} ({final_4k.stat().st_size} bytes)", flush=True)
                    return
            elif status in ('FAILED', 'CANCELLED'):
                print("Failed:", r.text, flush=True)
                return

if __name__ == '__main__':
    asyncio.run(poll())
