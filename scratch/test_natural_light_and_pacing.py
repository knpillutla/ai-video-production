import asyncio
import httpx
from pathlib import Path
from PIL import Image
import numpy as np

FAL_KEY = "82b43aa4-6d10-44ef-940f-f43ac2562224:fb1f36b10bf499206772af7efc421258"

async def generate_natural_daylight_image():
    endpoint = "https://queue.fal.run/fal-ai/flux/dev"
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "Ultra-photorealistic 4K cinematic portrait, 24-year-old skinny beautiful South Indian Telugu woman, "
        "radiant natural smile, crisp natural open-air daylight, balanced 5600K soft daylight lighting, "
        "authentic natural skin tones, zero artificial yellow tint, zero lens flare blowout, "
        "traditional crimson and cream silk festive attire, fresh white jasmine flowers in hair, "
        "dancing pose in rustic village open courtyard with terracotta pots and clean neutral sky"
    )
    payload = {
        "prompt": prompt,
        "image_size": "landscape_16_9",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }
    print("Generating natural daylight image via Fal Flux Dev...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        # submit
        sub = await client.post(endpoint, headers=headers, json=payload)
        sub_data = sub.json()
        status_url = sub_data.get("status_url")
        resp_url = sub_data.get("response_url")
        print(f"Submitted request: {sub_data.get('request_id')}")

        for _ in range(30):
            await asyncio.sleep(2)
            s = await client.get(status_url, headers=headers)
            if s.json().get("status") == "COMPLETED":
                res = await client.get(resp_url, headers=headers)
                data = res.json()
                img_url = data["images"][0]["url"]
                print(f"Generated Image URL: {img_url}")
                
                # download and analyze
                out_path = Path("scratch/analysis/natural_dance_flux.jpg")
                img_resp = await client.get(img_url)
                out_path.write_bytes(img_resp.content)
                
                img = Image.open(out_path).convert("RGB")
                arr = np.array(img, dtype=np.float32)
                r = arr[:, :, 0].mean()
                g = arr[:, :, 1].mean()
                b = arr[:, :, 2].mean()
                yellow_cast = ((r + g) / 2.0) - b
                print(f"Color Metrics: R={r:.1f}, G={g:.1f}, B={b:.1f}")
                print(f"Warmth / Yellow Cast Index: {yellow_cast:.1f} (Old was +61.2)")
                print(f"Saved to: {out_path}")
                return img_url, str(out_path)

if __name__ == "__main__":
    asyncio.run(generate_natural_daylight_image())
