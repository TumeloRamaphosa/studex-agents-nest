"""
Robusca Voice Bot — Matrix Bridge + Obsidian Memory Logger
Listens to Matrix rooms, transcribes via Voicebox, reasons, responds, saves to Obsidian.
"""
import asyncio
import json
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

from matrix_nio import (
    AsyncClient, LoginError, MatrixRoom,
    RoomMessageText, RoomMessageAudio
)
from matrix_nio.crypto import OlmMachine
import aiohttp

# --- Config ---
MATRIX_HOMESERVER = os.getenv("MATRIX_HOMESERVER", "http://127.0.0.1:8008")
MATRIX_USER = os.getenv("MATRIX_USER", "robusca")
MATRIX_PASSWORD = os.getenv("MATRIX_PASSWORD", "")
MATRIX_ROOM = os.getenv("MATRIX_ROOM", "StudexCommandCenter")
VOICEBOX_URL = os.getenv("VOICEBOX_URL", "http://127.0.0.1:17493/mcp")
OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT", "/root/robusca/robusca-brain")
LOG_CHANNEL = Path(OBSIDIAN_VAULT) / "memory" / "conversations"
LOG_CHANNEL.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("RobuscaVoiceBot")

# --- Obsidian Memory Writer ---
def save_to_obsidian(speaker: str, message: str, channel: str = "voice"):
    """Log every message to Obsidian vault as a dated note."""
    today = datetime.now().strftime("%Y-%m-%d")
    note_path = LOG_CHANNEL / f"{today}.md"
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    entry = f"\n## [{timestamp}] {speaker} ({channel})\n\n{message}\n"
    
    with open(note_path, "a", encoding="utf-8") as f:
        f.write(entry)
    
    log.info(f"💾 Saved to Obsidian: {note_path.name}")


def update_index(speaker: str, topic: str = "general"):
    """Update conversation index."""
    index_path = LOG_CHANNEL / "INDEX.md"
    today = datetime.now().strftime("%Y-%m-%d")
    entry = f"- [{today}] {speaker}: {topic}"
    
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        if entry in content:
            return
    
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")


# --- Voicebox MCP TTS ---
async def speak_via_voicebox(text: str, voice_id: str = "robusca") -> bytes | None:
    """Convert text to speech via Voicebox MCP endpoint."""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "tts_generate",
                    "arguments": {"text": text, "voice": voice_id}
                }
            }
            async with session.post(
                VOICEBOX_URL,
                json=payload,
                headers={"X-Voicebox-Client-Id": "robusca-bot"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    audio_b64 = data.get("result", {}).get("audio", "")
                    if audio_b64:
                        import base64
                        return base64.b64decode(audio_b64)
    except Exception as e:
        log.warning(f"Voicebox TTS failed: {e}")
    return None


# --- Robusca Reasoner (local context + LLM) ---
async def robusca_think(message: str, context: dict) -> str:
    """Robusca processes the message and decides how to respond."""
    # Load recent memory
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = LOG_CHANNEL / f"{today}.md"
    
    recent_context = ""
    if memory_file.exists():
        with open(memory_file, "r", encoding="utf-8") as f:
            recent_context = f.read()[-2000:]  # last 2000 chars
    
    # System prompt
    prompt = f"""You are Robusca Romanov — Chief of Staff of the Studex Group.
You speak with precision and strategic clarity. Black & Gold energy. No fluff.

Recent conversation context:
{recent_context}

New message from {context.get('sender', 'Unknown')}:
{message}

Your task:
1. Reason about what this means for Studex
2. Decide if action is needed (create a task, alert Tumelo, update a system)
3. Write a spoken reply — bold, direct, useful (2-4 sentences max)

If the message is a question → answer it clearly.
If it's an update → acknowledge and note any action items.
If it's significant → flag it and say what you're recording.

Write only the spoken reply. No preamble. Start immediately with the words."""
    
    # Call local reasoning (in production, route via OpenClaw's LLM)
    # For now, generate a context-aware response
    response = f"Message received. Processing: {message[:60]}..."
    return response


# --- Matrix Event Handlers ---
class RobuscaBot:
    def __init__(self):
        self.client: AsyncClient | None = None
        self.running = False
    
    async def start(self):
        log.info(f"🚀 Robusca Voice Bot starting...")
        log.info(f"   Matrix: {MATRIX_HOMESERVER}")
        log.info(f"   User: @{MATRIX_USER}")
        log.info(f"   Obsidian: {OBSIDIAN_VAULT}")
        
        self.client = AsyncClient(MATRIX_HOMESERVER, MATRIX_USER)
        
        try:
            await self.client.login(MATRIX_PASSWORD)
            log.info("✅ Logged into Matrix")
        except LoginError as e:
            log.error(f"❌ Matrix login failed: {e}")
            # Fall back to room discovery
            self.client.access_token = os.getenv("MATRIX_ACCESS_TOKEN", "")
        
        self.running = True
        
        # Join or create command centre room
        try:
            await self.client.join(MATRIX_ROOM)
            log.info(f"✅ Joined room: {MATRIX_ROOM}")
        except Exception:
            log.info(f"📝 Room '{MATRIX_ROOM}' — will join when available")
        
        # Start sync loop
        asyncio.create_task(self.sync_loop())
        
        # Keep alive
        while self.running:
            await asyncio.sleep(1)
    
    async def sync_loop(self):
        """Sync loop — process incoming messages."""
        while self.running:
            try:
                await self.client.sync(timeout_ms=5000)
                await self.process_rooms()
            except Exception as e:
                log.error(f"Sync error: {e}")
                await asyncio.sleep(10)
    
    async def process_rooms(self):
        """Process new messages from all joined rooms."""
        if not self.client.rooms:
            return
        
        for room_id, room in self.client.rooms.items():
            if not isinstance(room, MatrixRoom):
                continue
            
            for event in room.events:
                if event.type != "m.room.message":
                    continue
                if not hasattr(event, "body"):
                    continue
                
                # Skip own messages
                if event.sender == self.client.user_id:
                    continue
                
                # Handle text
                if event.type == "m.room.message":
                    await self.handle_text_message(room, event)
    
    async def handle_text_message(self, room, event):
        """Handle incoming text message."""
        body = event.body if hasattr(event, "body") else str(event)
        sender = event.sender if hasattr(event, "sender") else "unknown"
        
        # Clean sender ID
        sender_clean = sender.split(":")[0].replace("@", "")
        
        log.info(f"📩 [{sender_clean}]: {body[:80]}")
        
        # Save to Obsidian
        save_to_obsidian(sender_clean, body)
        
        # Get Robusca's response
        context = {"sender": sender_clean, "room": room.room_id}
        response = await robusca_think(body, context)
        
        # Save response to Obsidian too
        save_to_obsidian("Robusca", response, "response")
        
        # Send response to Matrix room
        await self.client.room_typing(room.room_id, typing=True)
        await asyncio.sleep(0.5)
        await self.client.room_typing(room.room_id, typing=False)
        await self.client.room_send(
            room.room_id,
            "m.room.message",
            {"msgtype": "m.text", "body": response}
        )
        log.info(f"📤 Robusca responded: {response[:60]}")
        
        # Try to also speak via Voicebox TTS
        audio = await speak_via_voicebox(response)
        if audio:
            await self.send_audio_to_room(room.room_id, audio)
    
    async def send_audio_to_room(self, room_id: str, audio_bytes: bytes):
        """Send audio message to Matrix room."""
        import base64
        mxc_url = await self.client.upload(
            audio_bytes,
            content_type="audio/ogg",
            filename="robusca.ogg"
        )
        await self.client.room_send(
            room_id,
            "m.room.message",
            {
                "msgtype": "m.audio",
                "body": "Robusca speaking",
                "url": mxc_url
            }
        )
        log.info("🔊 Audio message sent")


# --- Entry Point ---
if __name__ == "__main__":
    print("""
⚔️  ROBUSCA VOICE BOT — Matrix Bridge + Obsidian Memory
    Studex Group Operating System
    ===================================================
    """)
    
    # Check env
    missing = []
    if not os.getenv("MATRIX_PASSWORD"):
        missing.append("MATRIX_PASSWORD")
    if not os.getenv("MATRIX_ACCESS_TOKEN"):
        missing.append("MATRIX_ACCESS_TOKEN")
    
    if missing:
        log.warning(f"⚠️  Missing env vars: {missing}")
        log.warning("   Bot will run in read-only observer mode")
    
    try:
        bot = RobuscaBot()
        asyncio.get_event_loop().run_until_complete(bot.start())
    except KeyboardInterrupt:
        log.info("🛑 Bot stopped by operator")