import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_fal_flux():
    key = os.getenv("FAL_KEY")
    client = httpx.AsyncClient(timeout=30.0)
    headers = {"Authorization": f"Key {key}", "Content-Type": "application/json"}
    body = {
        "prompt": "4K photo of Swiss Alps in the rain, Seealpsee",
        "image_size": "landscape_16_9",
        "num_inference_steps": 4,
        "num_images": 1,
        "enable_safety_checker": False
    }
    # Test queue or sync endpoint
    resp = await client.post("https://fal.run/fal-ai/flux/schnell", headers=headers, json=body)
    print("STATUS:", resp.status_code)
    print("BODY:", resp.text[:300])

asyncio.run(test_fal_flux())
