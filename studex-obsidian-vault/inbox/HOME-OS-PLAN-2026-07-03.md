# STUDEX HOME OS — Home Assistant + OpenClaw Plan
**Created:** 2026-07-03
**Status:** Active Planning

---

## What We Found

**OpenClawHomeAssistant** — A Home Assistant add-on that runs OpenClaw inside Home Assistant OS.
- OpenClaw gateway runs inside Home Assistant
- Web terminal + landing page served in Home Assistant
- Connect any AI provider (OpenAI, Anthropic, etc.)
- Full access to all Home Assistant devices via the agent

**OpenClawHomeAssistantIntegration** — The bridge that lets OpenClaw agents control Home Assistant devices.
- Charlie/Naledi can now control your home directly
- "Turn on the lights" → Charlie → Home Assistant → device
- Wake-on-LAN support for any device
- Bluetooth device discovery and control

---

## What You Can Connect

| Device | Method | Control Available |
|--------|--------|-----------------|
| Apple HomePod | Home Assistant (Siri/HomeKit integration) | Volume, playback, Siri, scenes |
| Samsung TV | Home Assistant (SmartThings or IP control) | Power, volume, inputs, apps |
| Home Cameras | Home Assistant (generic IP camera integration) | Live feed, motion alerts, recording |
| Bluetooth Devices | Home Assistant + Bluetooth LE | Speakers, headphones, locks, sensors |
| LIFX / Hue Lights | Home Assistant | Power, color, brightness |
| Thermostats | Home Assistant | Temperature, schedules |
| Locks | Home Assistant (smart locks) | Lock/unlock, automations |
| MacBook Pro itself | Wake-on-LAN | Power on remotely via TailScale |

---

## Architecture

```
                    STUDEX OS (Mission Control — bl923ho8ctt3.space.minimax.io)
                                    │
                                    ↓
                    ┌───────────────────────────────────────┐
                    │   HOME ASSISTANT (MacBook Pro :8123)   │
                    │                                        │
                    │  ┌─────────────────────────────────┐ │
                    │  │  OpenClaw Add-on                │ │
                    │  │  Charlie → Home Assistant API    │ │
                    │  │  "Turn on TV" → HA → Samsung TV│ │
                    │  └─────────────────────────────────┘ │
                    │                                        │
                    │  Connected Devices:                   │
                    │  • HomePod (Siri/HomeKit)            │
                    │  • Samsung TV (IP control)           │
                    │  • Cameras (RTSP streams)            │
                    │  • Bluetooth (LE)                     │
                    └───────────────────────────────────────┘
                                    ↑
                                    │
                    TailScale VPN (macbook-pro-5.tailf7273b.ts.net)
                                    │
                            Orgo VM (us)
```

---

## Installation Steps

### Step 1 — Install Home Assistant on MacBook Pro

**Option A: Docker Desktop (Recommended)**
1. Install Docker Desktop from docker.com (free tier OK)
2. Enable Apple Silicon (Rosetta 2) for x86 containers
3. Run Home Assistant Container:
```bash
docker run -d \
  --name homeassistant \
  --privileged \
  --network=host \
  -e TZ=Africa/Johannesburg \
  -v ~/homeassistant/config:/config \
  --restart unless-stopped \
  homeassistant/home-assistant:stable
```

**Option B: Home Assistant Core (Python venv)**
```bash
pip3 install homeassistant
hass --open-ui
# Runs on http://localhost:8123
```

### Step 2 — Connect MacBook to TailScale (should already be done)
The MacBook should already be on `tailf7273b.ts.net`

### Step 3 — Access Home Assistant from Orgo VM
```bash
# From Orgo VM:
curl http://macbook-pro-5.tailf7273b.ts.net:8123
```

### Step 4 — Install OpenClaw Add-on in Home Assistant
1. Home Assistant → Settings → Add-ons → Add-on Store
2. Add repository: `https://github.com/techartdev/OpenClawHomeAssistant`
3. Install **OpenClaw Assistant**
4. Start the add-on

### Step 5 — Configure Home Assistant integrations
- **HomePod**: Settings → Devices → Add → Apple HomeKit
- **Samsung TV**: Settings → Devices → Add → Samsung SmartThings OR IP integration
- **Cameras**: Settings → Devices → Add → Generic IP Camera
- **Bluetooth**: Settings → Devices → Add → Bluetooth

### Step 6 — Add HOME page to STUDEX OS
- Embed Home Assistant at `http://macbook-pro-5.tailf7273b.ts.net:8123`
- Or use Home Assistant's iframe panel in the OS dashboard

---

## STUDEX OS — HOME Page Spec

```
┌─────────────────────────────────────────────────────────┐
│  STUDEX OS — HOME CONTROL                    [HH:MM UTC] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   🎵        │  │   📺        │  │   📹        │     │
│  │  HOMEPOD    │  │  SAMSUNG TV │  │  CAMERAS    │     │
│  │             │  │             │  │             │     │
│  │  ● Playing  │  │  ● ON       │  │  3 Online   │     │
│  │  Vol: 65%   │  │  HDMI 2     │  │  Motion: 0  │     │
│  │             │  │             │  │             │     │
│  │  [Vol +]    │  │  [Power]    │  │  [View]     │     │
│  │  [Vol -]    │  │  [Source]   │  │  [Arm]      │     │
│  │  [Play]     │  │  [Netflix]  │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   🔵        │  │   💡        │  │   🔊        │     │
│  │  BLUETOOTH  │  │  LIGHTS     │  │  MACBOOK    │     │
│  │             │  │             │  │             │     │
│  │  4 Devices  │  │  All: ON    │  │  ● Online   │     │
│  │  Connected   │  │  Lounge 80% │  │  Battery: 78%│     │
│  │             │  │             │  │             │     │
│  │  [Scan]     │  │  [All On]   │  │  [WOL]      │     │
│  │  [Devices]  │  │  [All Off]  │  │  [Screen]    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │  QUICK COMMANDS — Say it, Charlie does it        │    │
│  │  "Turn on the TV and set the thermostat"        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Wake-on-LAN (WOL) — Turn on MacBook Remotely

```
MacBook Pro: tailf7273b.ts.net
    │
    │ WOL packet via TailScale
    │
    ↓
MacBook Pro wakes up
    │
    │ Home Assistant detects online
    │
    ↓
Charlie: "MacBook Pro is online. Screen sharing available."
```

**Requirements:**
- MacBook Pro sleep settings: "Wake for network access" = ON
- Home Assistant MacBook card: shows battery, screen state
- TailScale WOL (newer versions support WOL over TailScale)

---

## Bluetooth Control via HA

Home Assistant can:
- Discover nearby Bluetooth devices
- Connect to Bluetooth speakers (audio routing)
- Read BLE sensor data (temperature, humidity)
- Control Bluetooth locks
- Send BLE commands to any paired device

---

## Next Steps

### Immediate (This Week)
1. [ ] Install Docker Desktop on MacBook Pro
2. [ ] Run Home Assistant Container
3. [ ] Access via http://localhost:8123
4. [ ] Create Home Assistant account
5. [ ] Connect HomePod via HomeKit
6. [ ] Connect Samsung TV via IP
7. [ ] Add OpenClaw add-on
8. [ ] Add HOME page to STUDEX OS

### Short-term
1. [ ] TailScale on Orgo VM (need auth key)
2. [ ] Charlie connects to Home Assistant API
3. [ ] "Hey Charlie, turn on the TV" works
4. [ ] MacBook WOL from Orgo VM

---

*Last updated: 2026-07-03 01:10 UTC*
