"""
Simulates the camera vision device pushing inspection results over the
websocket. Useful for testing the backend + frontend before real hardware
is wired up.

Usage:
    python simulator.py --url ws://localhost:8000/ws/ingest --device CAM-01 --rate 1.0
"""
import argparse
import asyncio
import base64
import datetime as dt
import json
import random

import websockets
import websockets.exceptions as ws_exc

SKUS = [
    {"skuId": 1, "sku": "SKU-001"},
    {"skuId": 2, "sku": "SKU-002"},
    {"skuId": 3, "sku": "SKU-003"},
    {"skuId": 4, "sku": "SKU-004"},
]

# 1x1 px transparent PNG, just so the image field is non-empty for testing.
TINY_PNG_B64 = base64.b64encode(
    bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000a49444154789c6360000002000100ffff03000006"
        "0005570a2eab0000000049454e44ae426082"
    )
).decode()


async def run(url: str, device: str, rate: float):
    seq = 0
    async with websockets.connect(url) as ws:
        print(f"Connected to {url} as {device}")
        while True:
            seq += 1
            sku = random.choice(SKUS)
            verdict = "PASS" if random.random() > 0.05 else "FAIL"
            message = {
                "device": device,
                "seq": seq,
                "tsUtc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "verdict": verdict,
                "sku": sku["sku"],
                "skuId": sku["skuId"],
                "qty": 1,
                "score": round(random.uniform(0.85, 0.99), 2),
                "image": {
                    "mime": "image/png",
                    "width": 1,
                    "height": 1,
                    "bytes": len(TINY_PNG_B64),
                    "base64": TINY_PNG_B64,
                },
            }
            await ws.send(json.dumps(message))
            try:
                ack = await asyncio.wait_for(ws.recv(), timeout=2)
                print(f"seq={seq} sku={sku['sku']} verdict={verdict} -> {ack}")
            except asyncio.TimeoutError:
                print(f"seq={seq} sent, no ack received (timeout)")

            await asyncio.sleep(1.0 / rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="ws://localhost:8000/ws/ingest")
    parser.add_argument("--device", default="CAM-01")
    parser.add_argument("--rate", type=float, default=1.0, help="messages per second")
    args = parser.parse_args()

    try:
        asyncio.run(run(args.url, args.device, args.rate))
    except (KeyboardInterrupt, ws_exc.ConnectionClosed):
        print("Stopped.")
