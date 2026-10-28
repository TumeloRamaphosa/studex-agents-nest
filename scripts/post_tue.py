import urllib.request
import urllib.error
import urllib.parse
import json
import os

FH_TOKEN = os.environ.get("FEEDHIVE_API_KEY", "")
FH_BASE = "https://api.feedhive.com"

# Upload media first
image_path = "/workspace/images/africa-pillar-tue.png"
if os.path.exists(image_path):
    print(f"Uploading media: {image_path}")
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    filename = "africa-pillar-tue.png"
    mime = "image/png"
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + image_data + f"\r\n--{boundary}--\r\n".encode()
    
    upload_req = urllib.request.Request(
        f"{FH_BASE}/v1/media/upload",
        data=body,
        headers={
            "Authorization": f"Bearer {FH_TOKEN}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(upload_req, timeout=15) as resp:
            upload_result = json.loads(resp.read().decode())
            media_url = upload_result.get("media_url", "")
            print(f"Upload success: {media_url}")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"Upload HTTP {e.code}: {err_body[:300]}")
        media_url = ""
    except Exception as e:
        print(f"Upload error: {e}")
        media_url = ""
else:
    print("Image not found")
    media_url = ""

# Schedule post
post_content = """Africa is not the future.

Africa is the present.

Six of the world's ten fastest-growing economies are African. Mobile money has over 50% adoption across the continent. And 85% of all employment in Africa runs through the informal economy — a world where speed, trust, and mobility define how business gets done.

At Studex, we're building for this reality.

Our Rwanda hub gives us a launchpad into the African tech ecosystem — not to bring solutions FROM elsewhere, but to build technology that solves HOW African businesses actually operate.

Our Super Agents handle multi-currency transactions, cross-border compliance, and mobile payment integrations — natively. No adaptors. No workarounds. Just seamless operations at African scale.

The opportunity isn't in Africa.

The opportunity IS Africa.

And we're here to build it.

👉 Partner with us: @agent.studexmeat.com

#StudexGM #AfricanTech #Rwanda #SuperAgents #AgenticAI"""

publish_at = "2026-09-29T07:00:00Z"  # 09:00 SAST = 07:00 UTC

schedule_payload = {
    "content": post_content,
    "media_urls": [media_url] if media_url else [],
    "platforms": ["facebook", "twitter", "instagram", "linkedin"],
    "publish_at": publish_at
}

print(f"\nScheduling post for {publish_at}")
print(f"Content length: {len(post_content)} chars")

schedule_req = urllib.request.Request(
    f"{FH_BASE}/v1/posts/schedule",
    data=json.dumps(schedule_payload).encode(),
    headers={
        "Authorization": f"Bearer {FH_TOKEN}",
        "Content-Type": "application/json",
    },
    method="POST"
)
try:
    with urllib.request.urlopen(schedule_req, timeout=15) as resp:
        schedule_result = json.loads(resp.read().decode())
        print(f"Schedule success: {json.dumps(schedule_result)}")
        post_id = schedule_result.get("id", "UNKNOWN")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"Schedule HTTP {e.code}: {err_body[:500]}")
    post_id = "FAILED"
except Exception as e:
    print(f"Schedule error: {e}")
    post_id = "FAILED"

print(f"\nRESULT: post_id={post_id}, media_url={media_url}")
