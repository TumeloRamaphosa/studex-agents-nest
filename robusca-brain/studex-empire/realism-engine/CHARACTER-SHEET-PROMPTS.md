# Character Sheet Prompts — Realism Engine v2
**For use with Naledi content agent (Emily face + Realism Stack)**
**Source:** Emily + Naledi Calendar (Notion)

---

## 🔑 Core Principle
> "Photographic identity sheet" replaces "character reference sheet"
> "Contact sheet" replaces "model turnaround"
> Natural posture replaces A-pose
> Identity consistency without mechanical perfection
> Explicit suppression of CG language

---

## 1️⃣ Photorealistic Character Identity Sheet (Using a Reference Image)

**Prompt**

Create a **photorealistic multi-angle photographic identity sheet** based **strictly** on the uploaded reference image.

- Match the **exact real-world appearance** of the person: facial structure, proportions, skin texture, age, asymmetry, and natural imperfections.
- The result must look like **real photography of a real human**, not a digital character or 3D asset.
- Use a **simple, neutral background**, similar to a studio or indoor wall.
- The overall feeling should be **documentary and natural**, not stylized or cinematic.

**Layout**

- **Two horizontal rows**, presented as a clean photo contact sheet.
    - **Top row:** four full-body photographs of the same person:
        1. Facing the camera
        2. Left-facing profile
        3. Right-facing profile
        4. Facing away from the camera
    - **Bottom row:** three close-up photographic portraits:
        1. Facing the camera
        2. Left-facing profile
        3. Right-facing profile

**Pose & Body Language**

- The subject stands **naturally and casually**, as a real person would when asked to stand still.
- No exaggerated stance, no rigid pose, no symmetry.
- Subtle, natural weight distribution and relaxed posture.
- Shoulders relaxed, arms resting naturally at the sides.

**Consistency & Accuracy**

- Maintain **strong identity consistency** across all images.
- Preserve natural human asymmetry.
- Proportions must remain realistic and consistent without looking mechanically aligned.
- The subject should feel like the *same person photographed multiple times*, not a replicated model.

**Lighting & Camera**

- Soft, neutral, real-world lighting (similar to window light or soft studio light).
- No dramatic, cinematic, or stylized lighting.
- Natural shadows with gentle falloff.
- Realistic camera perspective and lens behavior.

**Critical constraints**

- ❌ Not a 3D render
- ❌ Not CGI
- ❌ Not a game character
- ❌ Not stylized
- ❌ Not a model turnaround

---

## 2️⃣ Photorealistic Character Identity Sheet (No Reference Image)

**Prompt**

Create a **photorealistic photographic identity sheet** of the following person:

**[INSERT REALISTIC HUMAN DESCRIPTION HERE]**

- The subject must look like a **real human photographed in the real world**.
- Avoid any stylized, animated, or synthetic appearance.
- Use a **simple neutral background**, similar to an ID or documentary shoot.

**Layout**

- **Two horizontal rows**, presented as a photo contact sheet.
    - **Top row:** four full-body photographs:
        1. Facing the camera
        2. Left-facing profile
        3. Right-facing profile
        4. Facing away
    - **Bottom row:** three close-up portraits:
        1. Facing the camera
        2. Left-facing profile
        3. Right-facing profile

**Pose & Presence**

- Natural stance, relaxed posture.
- No posing for presentation.
- Subtle variation in head angle and body balance, like multiple photos taken moments apart.

**Lighting & Finish**

- Soft, neutral, realistic lighting.
- No stylization, no dramatic contrast.
- The final result should resemble **real reference photography**, not a character asset.

---

## 3️⃣ Changing Wardrobe (Photorealistic Edit)

**Prompt**

Use the **same photographic identity sheet** as reference.

- Maintain the **exact same person**: face, body, age, proportions, posture, and expression.
- Change **only** the clothing to the following:

**[INSERT OUTFIT DESCRIPTION OR REFERENCE IMAGE]**

**Constraints**

- The clothing must behave like real fabric on a real body.
- No change to lighting, camera angle, or body posture.
- The person should still feel like the same individual photographed on the same day, just wearing different clothes.
- No stylization, no CGI look, no character redesign.

---

## ⚡ Nano Banana Short Prompts (Optimised)

### Identity Sheet (with ref)
```
photographic identity sheet, [uploaded reference], contact sheet layout,
two rows, four full-body + three close-up portraits, neutral background,
natural relaxed posture, soft studio lighting, documentary feel,
real human photographed multiple times, NOT CGI NOT 3D render NOT game asset
```

### Identity Sheet (without ref)
```
photorealistic identity sheet, [description], contact sheet layout,
two rows, neutral background, natural stance relaxed posture,
soft window light, documentary photography, real world human,
NOT animated NOT stylized NOT character asset
```

### Wardrobe Change
```
same person as reference identity sheet, change clothing only to [description],
identical face body posture lighting, real fabric behavior,
same day same shoot just different clothes, NOT CGI NOT redesign
```

---

## 🧪 Stress-Test Prompt (Validate Realism)

```
Create a photorealistic identity sheet of [description].
Now take the same person and place them in:
1. A busy Johannesburg CBD street
2. A dusty farm marketplace
3. A luxury restaurant table
4. A gym changing room
Same person. Same face. All four scenes must look like real photographs
taken on different days with different clothing. NOT composited. NOT CG.
```

---

## 🎬 Video Identity Continuity Prompt

```
Maintain exact character identity across all video frames.
Use the photographic identity sheet as the consistency anchor.
Every frame must show the same real human being photographed naturally.
Consistent: face structure, skin texture, body proportions, posture, age.
Variation allowed: clothing, lighting, environment, head angle.
Forbidden: style shift, age change, facial drift, CG look.
```

---

## 📅 Naledi Calendar Integration

These prompts are used by the Naledi content agent when:
- Creating new Emily character assets for campaigns
- Generating content for specific calendar events (Global Markets, promotions)
- Maintaining visual consistency across Instagram, TikTok, Facebook
- Post-campaign UGC using the Realism Stack face

**Notion reference:** Emily + Naledi Calendar
**Agent responsible:** Naledi Brain (content) + Realism Engine