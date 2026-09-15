#!/usr/bin/env python3
"""
Hollywood/Netflix-Grade 4K Cinematic YouTube Documentary Builder (<10 Minutes)
=============================================================================
Channel: Izhaan Intellect
Title: The 4D Economic Power: Japan vs Bangladesh ($2.8T Convergence)

Production Specs:
- Resolution: 3840 x 2160 (4K UHD), 30 FPS Progressive
- Aspect Ratio: 2.39:1 Anamorphic Cinema Letterbox on 4K Canvas
- Color Grade: Teal-Orange Cinema Balance + S-Curves + 35mm Film Grain
- Audio: High-Fidelity Neural Narration + Continuous Multi-Track BGM Score (with Auto-Ducking)
- Master Target Duration: ~9 Minutes 10 Seconds (Strictly < 600 Seconds)
"""

import os
import sys
import math
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "outputs"
FIG_DIR = OUT_DIR / "figures"
TEMP_DIR = ROOT / "build_temp_cinematic_4k"
TEMP_DIR.mkdir(exist_ok=True)
SEGMENTS_DIR = TEMP_DIR / "segments"
SEGMENTS_DIR.mkdir(exist_ok=True)

DOC_BASE = Path(r"E:\Video Projects\Izhaan Intellect Video"
                 r"\The 4D Economic Power - Japan Bangladesh Documentary (Full Production Franchise)")
ASSETS_DIR = DOC_BASE / "04_Visual_Assets"
BGM_DIR = Path(r"E:\Video Projects\Izhaan Intellect Video"
               r"\The Domino Effect - Global Risk 4D Documentary (Full Production Franchise)\05_BGM")

FINAL_VIDEO = OUT_DIR / "The_4D_Economic_Power_Cinematic_Master_4K.mp4"

# 4K UHD Cinematic Specs
W, H = 3840, 2160
FPS = 30
VOICE = "en-US-ChristopherNeural"

VISIBLE_H = round(W / 2.39)          # ~1607 (2.39:1 cinema)
BAR_H = (H - VISIBLE_H) // 2         # ~277px top + bottom black bars

# Cinema Filters
COLOR_GRADE = (
    "colorbalance=rs=-0.06:gs=-0.02:bs=0.12:"
    "rm=0.03:gm=-0.01:bm=0.05:"
    "rh=0.10:gh=0.02:bh=-0.04,"
    "curves=m='0/0.04 0.25/0.22 0.5/0.50 0.75/0.80 1/0.96',"
    "eq=saturation=0.90:contrast=1.04:brightness=0.01,"
    "vignette=PI/5"
)

LETTERBOX = (
    f"drawbox=y=0:w=iw:h={BAR_H}:c=black:t=fill,"
    f"drawbox=y=ih-{BAR_H}:w=iw:h={BAR_H}:c=black:t=fill"
)

GRAIN = "noise=c0s=3:c0f=t+u"

# Encoder options
SEG_ENCODER = "libx264"
SEG_OPTS = ["-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-g", str(FPS * 2)]

@dataclass
class CinematicScene:
    scene_id: str
    scene_type: str           # "title", "image", "video"
    source_asset: str         # Filename in ASSETS_DIR or FIG_DIR
    duration: float = 0.0     # Duration in seconds (for image/title)
    trim_start: float = 0.0   # For video clips
    trim_end: float = 0.0     # For video clips
    title_main: str = ""
    title_sub: str = ""
    zoom_dir: str = "in"      # "in", "out", "none"
    pan_dir: str = "center"   # "center", "left", "right", "up", "down"
    narration_text: str = ""

    @property
    def actual_duration(self) -> float:
        if self.scene_type == "video":
            return self.trim_end - self.trim_start
        return self.duration

    @property
    def video_file(self) -> Path:
        return SEGMENTS_DIR / f"{self.scene_id}_v4k.mp4"

    @property
    def audio_file(self) -> Path:
        return SEGMENTS_DIR / f"{self.scene_id}_audio.mp3"


# ═══════════════════════════════════════════════════════════════════════
# 5-ACT CINEMATIC TIMELINE (Target: ~9m 10s Total = 550s)
# ═══════════════════════════════════════════════════════════════════════

TIMELINE: List[CinematicScene] = [
    # ─── PROLOGUE: THE CONVERGENCE PREMISE (45s) ──────────────────────
    CinematicScene(
        scene_id="s00_title_hook",
        scene_type="title",
        source_asset="",
        duration=6.0,
        title_main="THE 4D ECONOMIC POWER",
        title_sub="JAPAN · BANGLADESH · THE $2.8 TRILLION CONVERGENCE",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s01_tokyo_ruins",
        scene_type="image",
        source_asset="tokyo_1945_ruins.jpg",
        duration=11.0,
        zoom_dir="out", pan_dir="left",
        narration_text=(
            "In 1946, Tokyo lay in pulverized ashes. Per capita income was one-fifth of the United States. "
            "Conventional economics wrote Japan off as permanently impoverished."
        )
    ),
    CinematicScene(
        scene_id="s02_shinkansen",
        scene_type="image",
        source_asset="shinkansen_1964.jpg",
        duration=13.0,
        zoom_dir="in", pan_dir="right",
        narration_text=(
            "Yet within twenty-five years, Japan engineered an industrial catch-up without historical precedent. "
            "It proved that national wealth is not governed by resource endowment, but by structural capability."
        )
    ),
    CinematicScene(
        scene_id="s03_matarbari_intro",
        scene_type="image",
        source_asset="matarbari_deep_port.jpg",
        duration=15.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "Today, Bangladesh stands at an identical historical crossroads. As UN LDC graduation approaches in 2026, "
            "it must make a defining choice: slide into the middle-income trap, or execute the Japanese playbook."
        )
    ),

    # ─── ACT I: THE 2026 PRECIPICE & TRIPLE CLIFF (102s) ──────────────
    CinematicScene(
        scene_id="s04_act1_card",
        scene_type="title",
        source_asset="",
        duration=4.0,
        title_main="ACT I",
        title_sub="THE 2026 PRECIPICE & THE TRIPLE CLIFF",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s05_complexity_chasm",
        scene_type="image",
        source_asset="fig2_economic_complexity_chasm.png",
        duration=16.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "On headline GDP, Bangladesh appears as a fast-growing frontier market. But inspect structural capabilities, "
            "and Bangladesh scores just 22 points on the Economic Power Index, trapped far behind Vietnam at 54 and Japan at 72. "
            "Over 84 percent of export revenue remains locked in low-complexity garments."
        )
    ),
    CinematicScene(
        scene_id="s06_mid_income_trap_video",
        scene_type="video",
        source_asset="Forecasting_the_Middle-Income_Trap__Inside_the_4D-EPDM_Architec_Clean.mp4",
        trim_start=0.0, trim_end=62.0,
        narration_text=(
            "In 2026, United Nations LDC graduation terminates duty-free European access, subjecting exports to eight to twelve "
            "percent tariffs. Compounded by banking sector non-performing loans and a tax-to-GDP ratio stuck below eight percent, "
            "the sovereign state faces severe liquidity constraints right as global competition intensifies."
        )
    ),
    CinematicScene(
        scene_id="s07_plate01_investment",
        scene_type="image",
        source_asset="plate_01_investment_comparison.png",
        duration=10.0,
        zoom_dir="in", pan_dir="left",
        narration_text=(
            "Historical precedent is brutal. Out of one hundred and one middle-income economies in 1960, only thirteen escaped "
            "the trap. All thirteen methodically climbed the ladder of product complexity."
        )
    ),
    CinematicScene(
        scene_id="s08_plate02_trade",
        scene_type="image",
        source_asset="plate_02_trade_openness_plunge.png",
        duration=10.0,
        zoom_dir="out", pan_dir="right",
        narration_text=(
            "Heavy capital investment alone cannot save an economy if institutional governance and domestic fiscal depth fail to materialize."
        )
    ),

    # ─── ACT II: THE ANATOMY OF A CATCH-UP MIRACLE (105s) ─────────────
    CinematicScene(
        scene_id="s09_act2_card",
        scene_type="title",
        source_asset="",
        duration=4.0,
        title_main="ACT II",
        title_sub="THE JAPANESE MIRACLE: POSTWAR RUIN TO INDUSTRIAL SUPERPOWER",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s10_japan_arch_video",
        scene_type="video",
        source_asset="The_Japanese_Development_Architecture_for_Bangladesh_Clean.mp4",
        trim_start=0.0, trim_end=75.0,
        narration_text=(
            "How did Japan achieve the impossible? Under MITI, the state enforced disciplined export conditions. Subsidies "
            "were strictly tied to foreign market penetration. Postal savings were channeled directly into heavy steel, "
            "shipbuilding, and deep logistics. The state did not pick winners; it enforced competitive discipline."
        )
    ),
    CinematicScene(
        scene_id="s11_takeoff_blueprint",
        scene_type="image",
        source_asset="The_Bangladesh_Takeoff_Architecture_page_01.png",
        duration=13.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "Japan methodically progressed from basic cotton textiles in the 1950s, to heavy steel in the 1960s, to electronics "
            "and robotics in the 1970s. Each technological phase funded the human capital needed for the next."
        )
    ),
    CinematicScene(
        scene_id="s12_takeoff_p02",
        scene_type="image",
        source_asset="The_Bangladesh_Takeoff_Architecture_page_02.png",
        duration=13.0,
        zoom_dir="out", pan_dir="left",
        narration_text=(
            "This sequential ladder is the missing architecture for South Asia. Developing nations cannot bypass physical manufacturing "
            "to jump straight into service economies without hollow domestic supply chains."
        )
    ),

    # ─── ACT III: THE 9D CAPABILITY MATRIX BEYOND GDP (97s) ───────────
    CinematicScene(
        scene_id="s13_act3_card",
        scene_type="title",
        source_asset="",
        duration=4.0,
        title_main="ACT III",
        title_sub="THE 9D CAPABILITY MATRIX: BEYOND HEADLINE GDP",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s14_radar_matrix",
        scene_type="image",
        source_asset="fig4_capability_radar.png",
        duration=16.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "To model this transition, our research team developed the 4D-EPDM framework, tracking nine structural dimensions: "
            "physical capital, human capital, technology depth, institutions, demographic dividend, complexity, maritime gravity, "
            "social cohesion, and domestic fiscal mobilization."
        )
    ),
    CinematicScene(
        scene_id="s15_science_video",
        scene_type="video",
        source_asset="4D-EPDM__The_Science_of_Economic_Forecasting_Clean.mp4",
        trim_start=0.0, trim_end=60.0,
        narration_text=(
            "Standard macroeconomic models assume smooth factor substitution. But 4D-EPDM accounts for real-world institutional friction, "
            "governance decay, and geopolitical supply chain shocks. The capability radar pinpoints exactly where structural failure occurs."
        )
    ),
    CinematicScene(
        scene_id="s16_demographic_clock",
        scene_type="image",
        source_asset="fig1_demographic_dividend.png",
        duration=17.0,
        zoom_dir="in", pan_dir="left",
        narration_text=(
            "And the demographic clock is relentless. Japan became wealthy before its society aged in the 1990s. Bangladesh's golden "
            "demographic window closes around 2038. The nation has twelve years to build high-productivity industry before demographic "
            "aging sets in."
        )
    ),

    # ─── ACT IV: 5,000 MONTE CARLO TRAJECTORIES (105s) ────────────────
    CinematicScene(
        scene_id="s17_act4_card",
        scene_type="title",
        source_asset="",
        duration=4.0,
        title_main="ACT IV",
        title_sub="2026 TO 2046: 5,000 MONTE CARLO TRAJECTORIES",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s18_fan_charts",
        scene_type="image",
        source_asset="fig3_bangladesh_2045_fan_charts.png",
        duration=16.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "Simulating five thousand stochastic paths over the next twenty years reveals a stark divergence. Under status quo inertia, "
            "capability plateaus at thirty-six by 2046, locked in middle-income stagnation. But under the Resilient 4D-Plus reform pathway, "
            "capability surges to 56.4, surpassing present-day Vietnam."
        )
    ),
    CinematicScene(
        scene_id="s19_monetary_dividend",
        scene_type="image",
        source_asset="fig5_macro_monetary_projections.png",
        duration=18.0,
        zoom_dir="in", pan_dir="right",
        narration_text=(
            "The monetary reform dividend is staggering. Integrated reform creates a 4.9 trillion dollar PPP economy by 2046, "
            "generating 320 billion dollars in annual domestic tax revenue. That extra 160 billion dollars every year eliminates "
            "dangerous foreign debt dependency."
        )
    ),
    CinematicScene(
        scene_id="s20_opensource_video",
        scene_type="video",
        source_asset="The_Open-Source_Economic_Miracle_Clean.mp4",
        trim_start=0.0, trim_end=67.0,
        narration_text=(
            "Every equation, parameter distribution, and econometric backcast in 4D-EPDM is open-source and pre-registered. Across "
            "twenty-one historical stress tests, the model maintained a 0.94 calibration score, giving policymakers rigorous empirical clarity."
        )
    ),

    # ─── ACT V: THE FOUR-PHASE ROADMAP & TAKEOFF (98s) ─────────────────
    CinematicScene(
        scene_id="s21_act5_card",
        scene_type="title",
        source_asset="",
        duration=4.0,
        title_main="ACT V",
        title_sub="THE FOUR-PHASE STRATEGIC ROADMAP (2026–2046)",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s22_matarbari_deep",
        scene_type="image",
        source_asset="matarbari_deep_port.jpg",
        duration=14.0,
        zoom_dir="out", pan_dir="left",
        narration_text=(
            "The escape from the middle-income trap follows four synchronized phases. Phase One: 2026 to 2028, auditing non-performing "
            "loans and digitizing tax collection. Phase Two: 2028 to 2032, commissioning the Matarbari Deep Sea Port to allow direct mother-vessel "
            "transshipment, cutting European transit times by half."
        )
    ),
    CinematicScene(
        scene_id="s23_2045_blueprint_video",
        scene_type="video",
        source_asset="The_2045_Blueprint__Bangladesh_and_the_4D_Transformation_Clean.mp4",
        trim_start=0.0, trim_end=65.0,
        narration_text=(
            "Phase Three scales industrial clusters into consumer electronics, active pharmaceutical ingredients, and green chemicals. "
            "Phase Four shifts fiscal revenue into technical vocational training, turning youth demographics into high-productivity automation."
        )
    ),
    CinematicScene(
        scene_id="s24_padma_modern",
        scene_type="image",
        source_asset="padma_bridge_modern.jpg",
        duration=11.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "Japan demonstrated that economic superpower status does not require natural resources. It requires institutional discipline, "
            "relentless technological upgrade, and strategic courage. For Bangladesh, the 2026 to 2046 window is the final opportunity."
        )
    ),
    CinematicScene(
        scene_id="s25_end_card",
        scene_type="title",
        source_asset="",
        duration=8.0,
        title_main="IZHAAN INTELLECT SPECIAL INVESTIGATION",
        title_sub="INTERACTIVE SIMULATOR: RBR48.GITHUB.IO/4D-EPDM · SUBSCRIBE",
        narration_text=""
    ),
]


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def resolve_asset_path(filename: str) -> Path:
    p1 = FIG_DIR / filename
    if p1.exists():
        return p1
    p2 = ASSETS_DIR / filename
    if p2.exists():
        return p2
    raise FileNotFoundError(f"Cannot resolve asset: {filename}")

def get_media_duration(file_path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


# ═══════════════════════════════════════════════════════════════════════
# PHASE 1: AUDIO SYNTHESIS & CONTINUOUS SCORE AUTO-DUCKING
# ═══════════════════════════════════════════════════════════════════════

async def generate_narration_audio(scene: CinematicScene) -> Path:
    """Generate or retrieve clean neural narration audio."""
    if not scene.narration_text.strip():
        # Generate silent audio file matching duration
        silent_path = SEGMENTS_DIR / f"{scene.scene_id}_audio.mp3"
        if not silent_path.exists():
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anullsrc=r=48000:cl=stereo:d={scene.actual_duration}",
                "-c:a", "libmp3lame", "-b:a", "192k",
                str(silent_path)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return silent_path

    audio_path = SEGMENTS_DIR / f"{scene.scene_id}_audio.mp3"
    if audio_path.exists() and audio_path.stat().st_size > 1000:
        return audio_path

    import edge_tts
    communicate = edge_tts.Communicate(scene.narration_text, VOICE)
    await communicate.save(str(audio_path))
    return audio_path

def build_master_audio(rendered_scenes: List[CinematicScene], total_video_dur: float) -> Path:
    """Concatenate voice tracks, crossfade 4-track BGM score, and apply sidechain ducking."""
    print("\n[Phase 1] Building Master Soundtrack with Auto-Ducking...")
    mastered_audio = TEMP_DIR / "mastered_soundtrack.wav"
    if mastered_audio.exists() and mastered_audio.stat().st_size > 1000000:
        print(f"  [+] Master Audio Cached: {mastered_audio.name} ({get_media_duration(mastered_audio):.2f}s)")
        return mastered_audio
    
    # 1. Padded Voiceover Segments matching exact scene visual durations
    voice_concat_txt = TEMP_DIR / "voice_concat.txt"
    with open(voice_concat_txt, "w", encoding="utf-8") as f:
        for sc in rendered_scenes:
            raw_audio = sc.audio_file
            padded_wav = SEGMENTS_DIR / f"{sc.scene_id}_voice_padded.wav"
            if not padded_wav.exists():
                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", str(raw_audio),
                    "-af", f"apad=whole_dur={sc.actual_duration}",
                    "-t", str(sc.actual_duration),
                    "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
                    str(padded_wav)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            f.write(f"file '{padded_wav.resolve()}'\n")

    full_voiceover = TEMP_DIR / "full_voiceover.wav"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(voice_concat_txt),
        "-c", "copy",
        str(full_voiceover)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Continuous 4-Track BGM Score
    t1 = BGM_DIR / "Main Title (Take 1).wav"
    t2 = BGM_DIR / "High-Stakes Cyber Score.wav"
    t3 = BGM_DIR / "The Mechanism (Take 1).wav"
    t4 = BGM_DIR / "Gritty Industrial Remix with Cinematic String Stabs.wav"

    continuous_bgm = TEMP_DIR / "continuous_bgm.wav"
    cmd_bgm = [
        "ffmpeg", "-y",
        "-i", str(t1), "-i", str(t2), "-i", str(t3), "-i", str(t4),
        "-filter_complex",
        "[0:a][1:a]acrossfade=d=3:c1=tri:c2=tri[a1];"
        "[a1][2:a]acrossfade=d=3:c1=tri:c2=tri[a2];"
        "[a2][3:a]acrossfade=d=3:c1=tri:c2=tri[bgm_full]",
        "-map", "[bgm_full]",
        "-ar", "48000", "-ac", "2",
        str(continuous_bgm)
    ]
    subprocess.run(cmd_bgm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Dynamic Sidechain Auto-Ducking & Mastering
    # BGM drops to -22dB during speech, swells to -12dB during visual transitions and titles
    mastered_audio = TEMP_DIR / "mastered_soundtrack.wav"
    audio_filter = (
        f"[1:a]atrim=0:{total_video_dur},volume=0.32[bgm_trimmed];"
        "[bgm_trimmed][0:a]sidechaincompress=threshold=0.06:ratio=4.5:attack=15:release=350[ducked_bgm];"
        "[ducked_bgm][0:a]amix=inputs=2:duration=first:weights=1.0 1.0[raw_mix];"
        "[raw_mix]highpass=f=75,acompressor=threshold=0.12:ratio=2.8:attack=10:release=60,"
        "loudnorm=I=-14:TP=-1.5:LRA=10,alimiter=limit=0.891[final_master]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(full_voiceover),
        "-i", str(continuous_bgm),
        "-filter_complex", audio_filter,
        "-map", "[final_master]",
        "-ar", "48000", "-ac", "2",
        str(mastered_audio)
    ]
    subprocess.run(cmd_mix, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  [+] Master Audio Created: {mastered_audio.name} ({get_media_duration(mastered_audio):.2f}s)")
    return mastered_audio


# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: VISUAL RENDERING (NETFLIX / CINEMA GRADE 4K)
# ═══════════════════════════════════════════════════════════════════════

def render_cinematic_title_card(scene: CinematicScene) -> Path:
    """Generate a high-contrast cinematic title card on Obsidian slate (#0A0A0F)."""
    out_video = scene.video_file
    if out_video.exists() and out_video.stat().st_size > 5000:
        return out_video

    main_text = scene.title_main.replace(":", "\\:").replace("'", "'\\''")
    sub_text = scene.title_sub.replace(":", "\\:").replace("'", "'\\''")
    d = scene.actual_duration

    fb = r"C\:/Windows/Fonts/segoeuib.ttf"
    fl = r"C\:/Windows/Fonts/segoeuil.ttf"

    drawtext_filter = (
        f"drawtext=fontfile='{fb}':text='{main_text}':"
        f"fontcolor=0xE8E4DF:fontsize=110:"
        f"x=(w-text_w)/2:y=(h-text_h)/2-65,"
        f"drawbox=x=(w-700)/2:y=h/2+25:w=700:h=2:c=0x4A4640:t=fill,"
        f"drawtext=fontfile='{fl}':text='{sub_text}':"
        f"fontcolor=0x8A8680:fontsize=46:"
        f"x=(w-text_w)/2:y=(h/2+75),"
        f"fade=t=in:st=0:d=1.2,fade=t=out:st={d-1.2}:d=1.2"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0A0A0F:s={W}x{H}:d={d}:r={FPS}",
        "-vf", drawtext_filter,
        "-t", str(d),
        "-c:v", SEG_ENCODER, *SEG_OPTS,
        "-an", str(out_video)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_video

def render_cinematic_ken_burns(scene: CinematicScene) -> Path:
    """Render a super-sampled Ken Burns segment with cinema color grade, grain, and letterbox."""
    out_video = scene.video_file
    if out_video.exists() and out_video.stat().st_size > 5000:
        return out_video

    src = resolve_asset_path(scene.source_asset)
    d = scene.actual_duration
    total_frames = int(d * FPS)

    is_chart = (
        scene.source_asset.endswith(".png") or
        "fig" in scene.source_asset.lower() or
        "plate" in scene.source_asset.lower() or
        "takeoff" in scene.source_asset.lower()
    )

    if is_chart:
        # Fit cleanly inside 2.39:1 widescreen letterbox without cropping titles or axes
        # Pad with obsidian slate #0A0A0F, add subtle film grain, letterbox, and fade
        vf = (
            f"scale=w=3600:h=1520:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color=0x0A0A0F,"
            f"{GRAIN},"
            f"{LETTERBOX},"
            f"fade=t=in:st=0:d=0.75,fade=t=out:st={d-0.75}:d=0.75"
        )
    else:
        if scene.zoom_dir == "in":
            z_expr = "min(zoom+0.00025,1.20)"
        elif scene.zoom_dir == "out":
            z_expr = "max(1.20-0.00025*on,1.0)"
        else:
            z_expr = "1.06"

        if scene.pan_dir == "left":
            x_expr = "iw/2-(iw/zoom/2)+on*1.2"
        elif scene.pan_dir == "right":
            x_expr = "iw/2-(iw/zoom/2)-on*1.2"
        else:
            x_expr = "iw/2-(iw/zoom/2)"

        y_expr = "ih/2-(ih/zoom/2)"

        vf = (
            f"scale=5760:-1:flags=lanczos,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={W}x{H}:fps={FPS},"
            f"{COLOR_GRADE},"
            f"{GRAIN},"
            f"{LETTERBOX},"
            f"fade=t=in:st=0:d=0.75,fade=t=out:st={d-0.75}:d=0.75"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(FPS), "-i", str(src),
        "-vf", vf,
        "-t", str(d),
        "-r", str(FPS),
        "-c:v", SEG_ENCODER, *SEG_OPTS,
        "-an", str(out_video)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_video

def render_cinematic_video_clip(scene: CinematicScene) -> Path:
    """Upscale, cinema grade, and letterbox a pre-rendered clean video chapter."""
    out_video = scene.video_file
    if out_video.exists() and out_video.stat().st_size > 5000:
        return out_video

    src = resolve_asset_path(scene.source_asset)
    d = scene.actual_duration

    vf = (
        f"scale={W}:{H}:flags=lanczos,"
        f"unsharp=5:5:0.7:5:5:0,"
        f"{COLOR_GRADE},"
        f"{GRAIN},"
        f"{LETTERBOX},"
        f"fade=t=in:st=0:d=0.75,fade=t=out:st={d-0.75}:d=0.75"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(scene.trim_start),
        "-i", str(src),
        "-t", str(d),
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", SEG_ENCODER, *SEG_OPTS,
        "-an", str(out_video)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_video


# ═══════════════════════════════════════════════════════════════════════
# MAIN BUILD PIPELINE
# ═══════════════════════════════════════════════════════════════════════

async def build_cinematic_documentary():
    print("═" * 76)
    print("  IZHAAN INTELLECT: THE 4D ECONOMIC POWER CINEMATIC MASTER BUILDER")
    print("  Documentary Target: ~9m 10s (Strictly < 10 Minutes)")
    print("═" * 76)

    total_planned_dur = sum(s.actual_duration for s in TIMELINE)
    print(f"Total Planned Duration: {int(total_planned_dur // 60)}m {int(total_planned_dur % 60)}s ({total_planned_dur:.1f}s)")

    # Step 1: Synthesize Voiceover Tracks
    print("\n[Phase 1A] Synthesizing Neural Voiceover Audio...")
    for i, scene in enumerate(TIMELINE, 1):
        print(f"  [{i:02d}/{len(TIMELINE):02d}] {scene.scene_id} ({scene.actual_duration}s)...")
        await generate_narration_audio(scene)

    # Step 2: Render Visual Segments
    print("\n[Phase 2] Rendering 4K Cinematic Visual Segments...")
    rendered_videos = []
    for i, scene in enumerate(TIMELINE, 1):
        print(f"  [{i:02d}/{len(TIMELINE):02d}] Rendering {scene.scene_id} ({scene.scene_type})...")
        if scene.scene_type == "title":
            v = render_cinematic_title_card(scene)
        elif scene.scene_type == "image":
            v = render_cinematic_ken_burns(scene)
        elif scene.scene_type == "video":
            v = render_cinematic_video_clip(scene)
        else:
            raise ValueError(f"Unknown scene type: {scene.scene_type}")
        rendered_videos.append(v)

    # Step 3: Concatenate Video Stream
    print("\n[Phase 3] Concatenating 4K Video Segments...")
    video_concat_list = TEMP_DIR / "video_concat_cinematic.txt"
    with open(video_concat_list, "w", encoding="utf-8") as f:
        for v in rendered_videos:
            f.write(f"file '{v.resolve()}'\n")

    concatenated_video = TEMP_DIR / "all_video_cinematic.mp4"
    cmd_cat_video = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(video_concat_list),
        "-c", "copy",
        "-an",
        str(concatenated_video)
    ]
    subprocess.run(cmd_cat_video, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    actual_video_dur = get_media_duration(concatenated_video)
    print(f"  [+] Concatenated Video Ready: {actual_video_dur:.2f}s")

    # Step 4: Build Master Audio with Auto-Ducking
    mastered_audio = build_master_audio(TIMELINE, actual_video_dur)

    # Step 5: Final Master Mux
    print("\n[Phase 5] Mastering Final 4K Cinematic Output...")
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", str(concatenated_video),
        "-i", str(mastered_audio),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k",
        "-shortest",
        str(FINAL_VIDEO)
    ]
    subprocess.run(cmd_mux, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    final_dur = get_media_duration(FINAL_VIDEO)
    file_size_mb = FINAL_VIDEO.stat().st_size / (1024 * 1024)

    print("\n" + "═" * 76)
    print("  MASTER CINEMATIC VIDEO BUILD COMPLETE")
    print(f"File:       {FINAL_VIDEO.name}")
    print(f"Resolution: {W} x {H} (4K UHD 2.39:1 Anamorphic Cinema)")
    print(f"Duration:   {int(final_dur // 60)}m {int(final_dur % 60)}s ({final_dur:.2f} Seconds)")
    print(f"Size:       {file_size_mb:.2f} MB")
    if final_dur <= 600.0:
        print(f"Status:     PASS (<10 Minutes Limit Confirmed: {final_dur:.1f}s <= 600s)")
    else:
        print(f"Status:     FAIL (Exceeded 10 Minutes Limit: {final_dur:.1f}s > 600s)")
    print("═" * 76)


if __name__ == "__main__":
    import asyncio
    asyncio.run(build_cinematic_documentary())
