#!/usr/bin/env python3
"""
Generate Cinematic YouTube Subtitles (.srt, .vtt), High-CTR White Studio Thumbnail (4K, 720p),
and Full Publishing Package for The 4D Economic Power Master Cut (Gemini Aoede Voice).
"""

import sys
import math
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

from build_cinematic_10min_master import TIMELINE, get_media_duration

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "outputs"
FIG_DIR = OUT_DIR / "figures"
TEMP_DIR = ROOT / "build_temp_cinematic_4k"
SEGMENTS_DIR = TEMP_DIR / "segments"
DOC_BASE = Path(r"E:\Video Projects\Izhaan Intellect Video"
                 r"\The 4D Economic Power - Japan Bangladesh Documentary (Full Production Franchise)")
ASSETS_DIR = DOC_BASE / "04_Visual_Assets"

def format_timestamp_srt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def format_timestamp_vtt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    if millis >= 1000:
        millis = 999
    return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"

def split_text_into_sub_chunks(text: str, target_chunk_words: int = 8) -> list[str]:
    raw_sentences = re.split(r'(?<=[.?!,;])\s+', text)
    chunks = []
    for s in raw_sentences:
        s = s.strip()
        if not s:
            continue
        words = s.split()
        if len(words) <= target_chunk_words + 3:
            chunks.append(s)
        else:
            curr = []
            for w in words:
                curr.append(w)
                if len(curr) >= target_chunk_words:
                    chunks.append(" ".join(curr))
                    curr = []
            if curr:
                if len(curr) <= 3 and chunks:
                    chunks[-1] = chunks[-1] + " " + " ".join(curr)
                else:
                    chunks.append(" ".join(curr))
    return chunks

def generate_subtitles():
    """Build accurate .srt and .vtt subtitle tracks matching the Gemini female narration."""
    print("[Subtitles] Generating timecode-accurate cinematic subtitles...", flush=True)
    srt_entries = []
    vtt_entries = ["WEBVTT\n"]
    
    current_time = 0.0
    sub_index = 1
    
    for scene in TIMELINE:
        wav = SEGMENTS_DIR / f"{scene.scene_id}_voice_gemini.wav"
        dur_speech = scene.target_duration
        if wav.exists():
            dur_speech = get_media_duration(wav)
            scene_dur = round(dur_speech + 0.8, 2)
        else:
            scene_dur = scene.target_duration

        if not scene.narration_text.strip():
            current_time += scene_dur
            continue
        
        chunks = split_text_into_sub_chunks(scene.narration_text)
        total_chars = sum(len(c) for c in chunks)
        
        chunk_start = current_time
        for chunk in chunks:
            chunk_ratio = len(chunk) / max(total_chars, 1)
            chunk_dur = dur_speech * chunk_ratio
            chunk_end = chunk_start + chunk_dur
            
            srt_entries.append(
                f"{sub_index}\n"
                f"{format_timestamp_srt(chunk_start)} --> {format_timestamp_srt(chunk_end)}\n"
                f"{chunk}\n"
            )
            
            vtt_entries.append(
                f"{format_timestamp_vtt(chunk_start)} --> {format_timestamp_vtt(chunk_end)}\n"
                f"{chunk}\n"
            )
            
            sub_index += 1
            chunk_start = chunk_end
            
        current_time += scene_dur

    srt_path = OUT_DIR / "The_4D_Economic_Power_Cinematic_Master_4K.en.srt"
    vtt_path = OUT_DIR / "The_4D_Economic_Power_Cinematic_Master_4K.en.vtt"
    
    srt_path.write_text("\n".join(srt_entries), encoding="utf-8")
    vtt_path.write_text("\n".join(vtt_entries), encoding="utf-8")
    
    print(f"  [+] SRT Saved: {srt_path.name} ({len(srt_entries)} cues)", flush=True)
    print(f"  [+] VTT Saved: {vtt_path.name}", flush=True)
    return srt_path, vtt_path

def generate_cinematic_thumbnail():
    """Render a broadcast-grade, high-CTR White Studio documentary thumbnail."""
    print("[Thumbnail] Generating White Studio 4K & YouTube HD thumbnails...", flush=True)
    
    TW, TH = 3840, 2160
    # Clean White Studio Canvas (#FFFFFF)
    WHITE = (255, 255, 255)
    NAVY = (17, 24, 39)
    GREY_BORDER = (229, 231, 235)
    MUTED_GREY = (107, 114, 128)
    ROYAL_BLUE = (13, 110, 253)
    CRIMSON = (220, 38, 38)
    EMERALD = (22, 163, 74)

    im = Image.new("RGB", (TW, TH), WHITE)
    draw = ImageDraw.Draw(im)
    
    # Outer double border
    draw.rectangle([(60, 60), (TW - 60, TH - 60)], outline=GREY_BORDER, width=6)
    draw.rectangle([(80, 80), (TW - 80, TH - 80)], outline=(243, 244, 246), width=3)
    
    font_bold_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
    font_black_path = "C:\\Windows\\Fonts\\ariblk.ttf"
    
    try:
        f_pill = ImageFont.truetype(font_bold_path, 44)
        f_main = ImageFont.truetype(font_black_path, 150)
        f_sub = ImageFont.truetype(font_bold_path, 86)
        f_card_label = ImageFont.truetype(font_bold_path, 50)
        f_tag = ImageFont.truetype(font_bold_path, 42)
    except Exception:
        f_pill = f_main = f_sub = f_card_label = f_tag = ImageFont.load_default()

    # 1. Top Pill Badge: "IZHAAN INTELLECT  •  SPECIAL INVESTIGATION"
    pill_text = "IZHAAN INTELLECT  •  SPECIAL INVESTIGATION"
    pill_w = 1260
    pill_h = 86
    pill_x = (TW - pill_w) // 2
    pill_y = 100
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=43, fill=ROYAL_BLUE)
    draw.text((pill_x + pill_w//2, pill_y + pill_h//2), pill_text, fill=WHITE, font=f_pill, anchor="mm")

    # 2. Main Title: "JAPAN vs BANGLADESH"
    title_text = "JAPAN vs BANGLADESH"
    draw.text((TW // 2, 300), title_text, fill=NAVY, font=f_main, anchor="mm")

    # 3. Subtitle Hook: "THE $2.8 TRILLION CONVERGENCE"
    sub_text = "THE $2.8 TRILLION CONVERGENCE"
    draw.text((TW // 2, 430), sub_text, fill=CRIMSON, font=f_sub, anchor="mm")

    # Visual Cards Setup
    card_w, card_h = 1050, 1150
    card_y = 570
    
    def create_white_studio_card(img_path: Path, label: str, flag_text: str, border_color=ROYAL_BLUE):
        if not img_path.exists():
            return None
        src = Image.open(img_path).convert("RGBA")
        src_fitted = ImageOps.fit(src, (card_w, card_h - 160), method=Image.Resampling.LANCZOS)
        
        card = Image.new("RGBA", (card_w, card_h), (250, 250, 252, 255))
        card.paste(src_fitted, (0, 0))
        
        cdraw = ImageDraw.Draw(card)
        cdraw.rectangle([0, card_h - 160, card_w, card_h], fill=(255, 255, 255, 255))
        cdraw.line([(0, card_h - 160), (card_w, card_h - 160)], fill=GREY_BORDER, width=3)
        cdraw.text((card_w // 2, card_h - 105), label, fill=NAVY, font=f_card_label, anchor="mm")
        cdraw.text((card_w // 2, card_h - 45), flag_text, fill=MUTED_GREY, font=f_tag, anchor="mm")
        
        cdraw.rectangle([0, 0, card_w - 1, card_h - 1], outline=border_color, width=6)
        return card

    p_japan = ASSETS_DIR / "shinkansen_1964.jpg"
    card_japan = create_white_studio_card(p_japan, "JAPAN: 1946—1970", "POSTWAR CATCH-UP MIRACLE", border_color=ROYAL_BLUE)
    
    p_bd = ASSETS_DIR / "matarbari_deep_port.jpg"
    card_bd = create_white_studio_card(p_bd, "BANGLADESH: 2026—2046", "DEEP SEA PORT & ESCAPE VELOCITY", border_color=EMERALD)
    
    p_radar = FIG_DIR / "fig4_capability_radar.png"
    radar_w, radar_h = 1350, 1220
    radar_card = Image.new("RGBA", (radar_w, radar_h), (255, 255, 255, 255))
    if p_radar.exists():
        r_img = Image.open(p_radar).convert("RGBA")
        r_fitted = ImageOps.fit(r_img, (radar_w - 40, radar_h - 160), method=Image.Resampling.LANCZOS)
        radar_card.paste(r_fitted, (20, 20))
    rcdraw = ImageDraw.Draw(radar_card)
    rcdraw.rectangle([0, radar_h - 130, radar_w, radar_h], fill=ROYAL_BLUE)
    rcdraw.text((radar_w // 2, radar_h - 65), "9D STRUCTURAL CAPABILITY RADAR", fill=WHITE, font=f_card_label, anchor="mm")
    rcdraw.rectangle([0, 0, radar_w - 1, radar_h - 1], outline=ROYAL_BLUE, width=8)

    if card_japan:
        im.paste(card_japan, (150, card_y), card_japan)
    if card_bd:
        im.paste(card_bd, (TW - card_w - 150, card_y), card_bd)
    im.paste(radar_card, ((TW - radar_w) // 2, card_y - 40), radar_card)

    # Bottom Metric Ribbon
    ribbon_y = TH - 220
    ribbon_h = 130
    draw.rectangle([0, ribbon_y, TW, ribbon_y + ribbon_h], fill=(245, 247, 250))
    draw.line([(0, ribbon_y), (TW, ribbon_y)], fill=GREY_BORDER, width=4)
    
    badges = [
        "4K UHD WHITE STUDIO CUT",
        "5,000 MONTE CARLO DRAWS",
        "UN LDC 2026 GRADUATION",
        "GEMINI NEURAL NARRATION"
    ]
    spacing = TW // len(badges)
    for i, b in enumerate(badges):
        bx = spacing * i + spacing // 2
        draw.text((bx, ribbon_y + ribbon_h // 2), b, fill=NAVY, font=f_tag, anchor="mm")
        if i < len(badges) - 1:
            draw.line([(spacing * (i + 1), ribbon_y + 25), (spacing * (i + 1), ribbon_y + ribbon_h - 25)], fill=GREY_BORDER, width=3)

    thumb_4k = OUT_DIR / "The_4D_Economic_Power_Cinematic_Thumbnail_4K.png"
    im.save(thumb_4k, quality=95)
    print(f"  [+] White Studio 4K Thumbnail Saved: {thumb_4k.name} ({TW}x{TH})", flush=True)

    thumb_yt = OUT_DIR / "The_4D_Economic_Power_Cinematic_Thumbnail_YouTube.png"
    im_yt = im.resize((1280, 720), Image.Resampling.LANCZOS)
    im_yt.save(thumb_yt, quality=95)
    print(f"  [+] White Studio YouTube HD Thumbnail Saved: {thumb_yt.name} (1280x720)", flush=True)
    
    return thumb_4k, thumb_yt

def generate_publishing_package():
    """Create markdown metadata pack with updated chapter timestamps."""
    print("[Package] Writing YouTube publishing package...", flush=True)
    
    t = 0.0
    acts = {}
    for sc in TIMELINE:
        if sc.scene_id in ["s01_title_card", "s06_act1_card", "s13_act2_card", "s19_act3_card", "s24_act4_card", "s29_act5_card", "s36_outro", "s37_end_screen"]:
            acts[sc.scene_id] = t
        wav = SEGMENTS_DIR / f"{sc.scene_id}_voice_gemini.wav"
        if wav.exists():
            d = round(get_media_duration(wav) + 0.8, 2)
        else:
            d = sc.target_duration
        t += d

    def fmt_ts(sec: float) -> str:
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m:02d}:{s:02d}"

    doc = f"""# YouTube Publishing & SEO Package (Cinematic 4K White Studio Cut)
**Channel**: Izhaan Intellect (@IzhaanIntellect)  
**Video File**: `outputs/The_4D_Economic_Power_Cinematic_Master_4K.mp4`  
**Video Specs**: 3840x2160 (4K UHD), 30 FPS, Pure White Studio Canvas (#FFFFFF), 37 High-Velocity Scenes, Gemini Female Voice (Aoede), Orchestral Tension Score  
**Subtitles**: `The_4D_Economic_Power_Cinematic_Master_4K.en.srt` | `.en.vtt`  
**Thumbnail**: `outputs/The_4D_Economic_Power_Cinematic_Thumbnail_YouTube.png` (1280x720) & `Thumbnail_4K.png` (3840x2160)

---

## 1. High-CTR Video Title Options

### Option A (Recommended - Highest CTR & Algorithm Hook)
> **Can Bangladesh Replicate Japan's Miracle? The $2.8T Economic Convergence (2026–2046)**

### Option B (Analytical & Provocative)
> **The 2026 Precipice: Why Bangladesh Must Follow Japan's Industrial Playbook**

### Option C (Geopolitical & Academic)
> **Japan 1946 vs Bangladesh 2026: 5,000 Monte Carlo Simulations on Economic Superpower Status**

---

## 2. Optimized YouTube Description (Copy & Paste)

```markdown
In 1945, Tokyo was reduced to two million tons of smoking rubble. Western economists predicted Japan would remain permanently impoverished. Yet within 25 years, Japanese bullet trains were flying past Mount Fuji, and Japanese corporations dominated global markets.

Today, Bangladesh stands at an identical crossroads. In 2026, UN LDC graduation abruptly ends duty-free European market access, exposing garments to 8-12% tariffs. Compounded by banking NPLs and a sub-8% tax-to-GDP ratio, Bangladesh faces an invisible economic trapdoor.

Why did 88 out of 101 middle-income nations fail and get trapped since 1960? And how did Japan use MITI's 3 rules to pull off the greatest economic miracle in human history?

Using the 4D Economic Power Distribution Model (4D-EPDM) and 5,000 Monte Carlo simulations across 2026–2046, Izhaan Intellect presents an authoritative forensic investigation into structural complexity, maritime gravity, and the $2.8 Trillion reform dividend.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ VIDEO CHAPTERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{fmt_ts(acts.get("s01_title_card", 0.0))} - Prologue: The Ghost of 1945
{fmt_ts(acts.get("s06_act1_card", 45.0))} - Act I: The 2026 Precipice & The Trapdoor
{fmt_ts(acts.get("s13_act2_card", 130.0))} - Act II: The 87% Failure Rate & Complexity Chasm
{fmt_ts(acts.get("s19_act3_card", 225.0))} - Act III: The Secret Japanese Playbook (The MITI Triad)
{fmt_ts(acts.get("s24_act4_card", 315.0))} - Act IV: The Closing Demographic Window (2026–2038)
{fmt_ts(acts.get("s29_act5_card", 390.0))} - Act V: The $2.8 Trillion Horizon & Matarbari Mega Port
{fmt_ts(acts.get("s36_outro", 460.0))} - Outro: The Verdict & Subscribe

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 INTERACTIVE SIMULATOR & RESEARCH DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Live Interactive Web Simulator: https://rbr48.github.io/4d-epdm
• Open-Source GitHub Repository: https://github.com/rbr48/4d-epdm
• Complete Research Audit: https://github.com/rbr48/4d-epdm/blob/main/RESEARCH_PAPER_AND_DISSERTATION_CHAPTER.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔬 METHODOLOGICAL CITATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Hausmann, R. & Hidalgo, C. (2009). The Building Blocks of Economic Complexity. PNAS.
2. Johnson, C. (1982). MITI and the Japanese Miracle. Stanford University Press.
3. World Bank & UNCTAD (2024). Structural Transformation and LDC Graduation Reports.
4. Eichengreen, B., Park, D., & Shin, K. (2014). Growth Slowdowns Redux: Middle-Income Trap.

#BangladeshEconomy #Japan #EconomicDevelopment #Geopolitics #4DEPDM #IzhaanIntellect #Macroeconomics #IndustrialPolicy #Matarbari
```

---

## 3. SEO Tags & Search Keywords (500-Character Block)

```text
Bangladesh economy, Japan economic miracle, 4D economic power, economic complexity index, middle income trap, Bangladesh 2026 LDC graduation, Matarbari deep sea port, Padma bridge, MITI industrial policy, Monte Carlo simulation macroeconomics, Bangladesh GDP 2046, Izhaan Intellect, Ricardo Hausmann, Asian Tigers, structural transformation, garments export tariffs, economic superpower blueprint, development economics
```

---

## 4. Pinned Comment Template

```text
📊 Explore the interactive simulation engine: What policy sequence do you believe is most urgent for Bangladesh as it graduates from LDC status in 2026? 
Test the live 9D capability model yourself at https://rbr48.github.io/4d-epdm and let us know your scenario projections in the comments below!
```
"""
    pkg_path = OUT_DIR / "YOUTUBE_CINEMATIC_PUBLISHING_PACKAGE.md"
    pkg_path.write_text(doc, encoding="utf-8")
    print(f"  [+] Publishing Package Saved: {pkg_path.name}", flush=True)
    return pkg_path

if __name__ == "__main__":
    generate_subtitles()
    generate_cinematic_thumbnail()
    generate_publishing_package()
    print("All cinematic publishing assets successfully built!", flush=True)
