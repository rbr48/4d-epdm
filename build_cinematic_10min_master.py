#!/usr/bin/env python3
"""
Hollywood/Netflix-Grade 4K Cinematic YouTube Documentary Builder (<10 Minutes)
=============================================================================
Channel: Izhaan Intellect
Title: The 4D Economic Power: Japan vs Bangladesh ($2.8T Convergence)

Production Specs:
- Resolution: 3840 x 2160 (4K UHD), 30 FPS Progressive Full Canvas (16:9)
- Color Grade: Studio Cinema Balance + S-Curves + Delicate 35mm Film Grain
- Audio: Google Gemini TTS Female Voice (Aoede) with natural breathing pauses
- Dynamic Audio-First Duration: Audio is NEVER truncated; visual duration >= audio + 0.8s
- Audio Padding: Seamless room-tone extension without hard clamping
- Pacing: Continuous, engaging narration across 32 focused scenes with zero dead voids
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

# Import Gemini Female Neural Voice Engine
from gemini_tts_engine import synthesize_gemini_voice, get_media_duration

# Cinema Filters
COLOR_GRADE = (
    "colorbalance=rs=-0.04:gs=-0.01:bs=0.08:"
    "rm=0.02:gm=-0.01:bm=0.03:"
    "rh=0.06:gh=0.01:bh=-0.02,"
    "curves=m='0/0.03 0.25/0.23 0.5/0.50 0.75/0.78 1/0.97',"
    "eq=saturation=0.95:contrast=1.03:brightness=0.01"
)

GRAIN = "noise=c0s=2:c0f=t+u"

# Encoder options
SEG_ENCODER = "libx264"
SEG_OPTS = ["-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-g", str(FPS * 2)]

@dataclass
class CinematicScene:
    scene_id: str
    scene_type: str           # "title", "image", "video"
    source_asset: str         # Filename in ASSETS_DIR or FIG_DIR
    target_duration: float    # Base target duration in seconds
    trim_start: float = 0.0   # For video clips
    title_main: str = ""
    title_sub: str = ""
    zoom_dir: str = "in"      # "in", "out", "none"
    pan_dir: str = "center"   # "center", "left", "right"
    narration_text: str = ""
    effective_duration: float = 0.0

    @property
    def video_file(self) -> Path:
        return SEGMENTS_DIR / f"{self.scene_id}_v4k.mp4"

    @property
    def audio_file(self) -> Path:
        return SEGMENTS_DIR / f"{self.scene_id}_voice_gemini.wav"


# ═══════════════════════════════════════════════════════════════════════
# 32-SCENE CONTINUOUS CINEMATIC TIMELINE (Target: ~9m 10s Total = 550s)
# ═══════════════════════════════════════════════════════════════════════

TIMELINE: List[CinematicScene] = [
    # ─── PROLOGUE: THE CONVERGENCE PREMISE ────────────────────────────
    CinematicScene(
        scene_id="s00_title_hook",
        scene_type="title",
        source_asset="",
        target_duration=5.0,
        title_main="THE 4D ECONOMIC POWER",
        title_sub="JAPAN · BANGLADESH · THE $2.8 TRILLION CONVERGENCE",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s01_tokyo_ruins",
        scene_type="image",
        source_asset="tokyo_1945_ruins.jpg",
        target_duration=16.0,
        zoom_dir="out", pan_dir="left",
        narration_text=(
            "In nineteen forty-six, Tokyo lay in pulverized ashes. Per capita income was barely one-fifth of the United States. "
            "Conventional economics wrote Japan off as permanently impoverished."
        )
    ),
    CinematicScene(
        scene_id="s02_shinkansen",
        scene_type="image",
        source_asset="shinkansen_1964.jpg",
        target_duration=16.0,
        zoom_dir="in", pan_dir="right",
        narration_text=(
            "Yet within twenty-five years, Japan engineered an industrial catch-up without historical precedent. "
            "It proved that national destiny is not governed by resource endowment, but by structural capability."
        )
    ),
    CinematicScene(
        scene_id="s03_matarbari_intro",
        scene_type="image",
        source_asset="matarbari_deep_port.jpg",
        target_duration=17.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "Today, Bangladesh stands at an identical historical crossroads. As UN LDC graduation approaches in 2026, "
            "it must make a defining choice: slide into the middle-income trap, or execute the Japanese playbook."
        )
    ),

    # ─── ACT I: THE 2026 PRECIPICE & TRIPLE CLIFF ─────────────────────
    CinematicScene(
        scene_id="s04_act1_card",
        scene_type="title",
        source_asset="",
        target_duration=3.5,
        title_main="ACT I",
        title_sub="THE 2026 PRECIPICE & THE TRIPLE CLIFF",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s05_complexity_chasm",
        scene_type="image",
        source_asset="fig2_economic_complexity_chasm.png",
        target_duration=18.0,
        zoom_dir="none", pan_dir="center",
        narration_text=(
            "On headline GDP, Bangladesh appears as a fast-growing frontier market. But inspect structural capabilities, "
            "and Bangladesh scores just 22 points on the Economic Power Index, trapped far behind Vietnam at 54 and Japan at 72. "
            "Over eighty-four percent of export revenue remains locked in basic garments."
        )
    ),
    CinematicScene(
        scene_id="s06a_ldc_cliff",
        scene_type="video",
        source_asset="Forecasting_the_Middle-Income_Trap__Inside_the_4D-EPDM_Architec_Clean.mp4",
        target_duration=20.0,
        trim_start=0.0,
        narration_text=(
            "In 2026, United Nations LDC graduation abruptly terminates duty-free European access, slapping exports with immediate "
            "eight to twelve percent tariffs. This tariff shock threatens the entire garment engine."
        )
    ),
    CinematicScene(
        scene_id="s06b_npl_crisis",
        scene_type="video",
        source_asset="Forecasting_the_Middle-Income_Trap__Inside_the_4D-EPDM_Architec_Clean.mp4",
        target_duration=21.0,
        trim_start=20.0,
        narration_text=(
            "Simultaneously, the banking sector faces systemic stress, with distressed assets and non-performing loans restricting industrial "
            "credit. Private investment stalls just as technological modernization is urgently required."
        )
    ),
    CinematicScene(
        scene_id="s06c_tax_inertia",
        scene_type="video",
        source_asset="Forecasting_the_Middle-Income_Trap__Inside_the_4D-EPDM_Architec_Clean.mp4",
        target_duration=21.0,
        trim_start=41.0,
        narration_text=(
            "Compounded by a tax-to-GDP ratio hovering below eight percent, one of the lowest in the developing world, "
            "the sovereign state faces severe fiscal constraints right as global competition reaches peak intensity."
        )
    ),
    CinematicScene(
        scene_id="s07_plate01_investment",
        scene_type="image",
        source_asset="plate_01_investment_comparison.png",
        target_duration=15.0,
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
        target_duration=15.0,
        zoom_dir="out", pan_dir="right",
        narration_text=(
            "Heavy capital investment alone cannot save an economy if institutional governance, trade openness, "
            "and domestic fiscal mobilization fail to materialize."
        )
    ),

    # ─── ACT II: THE ANATOMY OF A CATCH-UP MIRACLE ────────────────────
    CinematicScene(
        scene_id="s09_act2_card",
        scene_type="title",
        source_asset="",
        target_duration=3.5,
        title_main="ACT II",
        title_sub="THE JAPANESE MIRACLE: POSTWAR RUIN TO INDUSTRIAL SUPERPOWER",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s10a_miti_governance",
        scene_type="video",
        source_asset="The_Japanese_Development_Architecture_for_Bangladesh_Clean.mp4",
        target_duration=25.0,
        trim_start=0.0,
        narration_text=(
            "How did Japan achieve the impossible? Under the Ministry of International Trade and Industry, the state enforced "
            "disciplined export conditions. Subsidies were never handouts; they were strictly tied to foreign export volume and technological milestones."
        )
    ),
    CinematicScene(
        scene_id="s10b_postal_credit",
        scene_type="video",
        source_asset="The_Japanese_Development_Architecture_for_Bangladesh_Clean.mp4",
        target_duration=25.0,
        trim_start=25.0,
        narration_text=(
            "Japan mobilized domestic capital through its national postal savings system, channeling billions in patient, "
            "long-term credit directly into heavy steel, modern shipbuilding, petrochemicals, and deep maritime logistics."
        )
    ),
    CinematicScene(
        scene_id="s10c_keiretsu_scale",
        scene_type="video",
        source_asset="The_Japanese_Development_Architecture_for_Bangladesh_Clean.mp4",
        target_duration=25.0,
        trim_start=50.0,
        narration_text=(
            "The Japanese state created dense industrial ecosystems through the Keiretsu network, shielding domestic infant industries "
            "while demanding cutthroat global competitiveness. It was state-directed market capitalism at its absolute finest."
        )
    ),
    CinematicScene(
        scene_id="s11_takeoff_blueprint",
        scene_type="image",
        source_asset="The_Bangladesh_Takeoff_Architecture_page_01.png",
        target_duration=16.0,
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
        target_duration=16.0,
        zoom_dir="out", pan_dir="left",
        narration_text=(
            "This sequential ladder is the missing architecture for South Asia. Developing nations cannot bypass physical manufacturing "
            "to jump straight into service economies without creating hollow domestic supply chains."
        )
    ),

    # ─── ACT III: THE 9D CAPABILITY MATRIX BEYOND GDP ─────────────────
    CinematicScene(
        scene_id="s13_act3_card",
        scene_type="title",
        source_asset="",
        target_duration=3.5,
        title_main="ACT III",
        title_sub="THE 9D CAPABILITY MATRIX: BEYOND HEADLINE GDP",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s14_radar_matrix",
        scene_type="image",
        source_asset="fig4_capability_radar.png",
        target_duration=19.0,
        zoom_dir="none", pan_dir="center",
        narration_text=(
            "To model this transition, our research team developed the 4D-EPDM framework, tracking nine structural dimensions: "
            "physical capital, human capital, technology depth, institutions, demographic dividend, complexity, maritime gravity, "
            "social cohesion, and domestic fiscal mobilization."
        )
    ),
    CinematicScene(
        scene_id="s15a_science_nonlinear",
        scene_type="video",
        source_asset="4D-EPDM__The_Science_of_Economic_Forecasting_Clean.mp4",
        target_duration=30.0,
        trim_start=0.0,
        narration_text=(
            "Standard macroeconomic models assume smooth factor substitution and perpetual equilibrium. But 4D-EPDM models real-world "
            "economics as a complex dynamical system, incorporating nonlinear feedback loops, structural inertia, and institutional friction."
        )
    ),
    CinematicScene(
        scene_id="s15b_science_friction",
        scene_type="video",
        source_asset="4D-EPDM__The_Science_of_Economic_Forecasting_Clean.mp4",
        target_duration=30.0,
        trim_start=30.0,
        narration_text=(
            "The 4D-EPDM simulation engine exposes critical threshold effects. If technology diffusion or institutional governance falls "
            "below minimum thresholds, capital accumulation alone cannot prevent growth deceleration and structural stagnation."
        )
    ),
    CinematicScene(
        scene_id="s16_demographic_clock",
        scene_type="image",
        source_asset="fig1_demographic_dividend.png",
        target_duration=18.0,
        zoom_dir="none", pan_dir="center",
        narration_text=(
            "And the demographic clock is relentless. Japan became wealthy before its society aged in the 1990s. Bangladesh's golden "
            "demographic window closes around 2038. The nation has twelve years to build high-productivity industry before demographic aging sets in."
        )
    ),

    # ─── ACT IV: 5,000 MONTE CARLO TRAJECTORIES ───────────────────────
    CinematicScene(
        scene_id="s17_act4_card",
        scene_type="title",
        source_asset="",
        target_duration=3.5,
        title_main="ACT IV",
        title_sub="2026 TO 2046: 5,000 MONTE CARLO TRAJECTORIES",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s18_fan_charts",
        scene_type="image",
        source_asset="fig3_bangladesh_2045_fan_charts.png",
        target_duration=19.0,
        zoom_dir="none", pan_dir="center",
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
        target_duration=19.0,
        zoom_dir="none", pan_dir="center",
        narration_text=(
            "The monetary reform dividend is staggering. Integrated reform creates a 4.9 trillion dollar PPP economy by 2046, "
            "generating 320 billion dollars in annual domestic tax revenue. That extra 160 billion dollars every year eliminates dangerous foreign debt dependency."
        )
    ),
    CinematicScene(
        scene_id="s20a_opensource_equations",
        scene_type="video",
        source_asset="The_Open-Source_Economic_Miracle_Clean.mp4",
        target_duration=33.0,
        trim_start=0.0,
        narration_text=(
            "Every single equation, parameter distribution, and econometric backcast in 4D-EPDM is open-source, reproducible, "
            "and pre-registered. No proprietary black boxes; full mathematical transparency allows independent verification across global research institutions."
        )
    ),
    CinematicScene(
        scene_id="s20b_opensource_calibration",
        scene_type="video",
        source_asset="The_Open-Source_Economic_Miracle_Clean.mp4",
        target_duration=34.0,
        trim_start=33.0,
        narration_text=(
            "Across twenty-one historical stress tests spanning from the 1997 Asian Financial Crisis to the 2020 global pandemic, "
            "the model maintained a 0.94 calibration score, giving policymakers rigorous empirical clarity to stress-test national development plans."
        )
    ),

    # ─── ACT V: THE FOUR-PHASE STRATEGIC ROADMAP ──────────────────────
    CinematicScene(
        scene_id="s21_act5_card",
        scene_type="title",
        source_asset="",
        target_duration=3.5,
        title_main="ACT V",
        title_sub="THE FOUR-PHASE STRATEGIC ROADMAP (2026–2046)",
        narration_text=""
    ),
    CinematicScene(
        scene_id="s22_matarbari_deep",
        scene_type="image",
        source_asset="matarbari_deep_port.jpg",
        target_duration=17.0,
        zoom_dir="out", pan_dir="left",
        narration_text=(
            "The escape from the middle-income trap follows four synchronized phases. Phase One: 2026 to 2028, auditing non-performing "
            "loans and digitizing tax collection. Phase Two: 2028 to 2032, commissioning the Matarbari Deep Sea Port to allow direct mother-vessel transshipment, cutting European transit times by half."
        )
    ),
    CinematicScene(
        scene_id="s23a_blueprint_clusters",
        scene_type="video",
        source_asset="The_2045_Blueprint__Bangladesh_and_the_4D_Transformation_Clean.mp4",
        target_duration=32.0,
        trim_start=0.0,
        narration_text=(
            "Phase Three, from 2032 to 2038, scales dedicated export processing zones into high-complexity manufacturing: semiconductor packaging, "
            "consumer electronics, active pharmaceutical ingredients, and precision agro-chemicals, diversifying far beyond basic textiles."
        )
    ),
    CinematicScene(
        scene_id="s23b_blueprint_automation",
        scene_type="video",
        source_asset="The_2045_Blueprint__Bangladesh_and_the_4D_Transformation_Clean.mp4",
        target_duration=33.0,
        trim_start=32.0,
        narration_text=(
            "Phase Four reinvests fiscal revenues into university research, digital infrastructure, and advanced automation, turning youth "
            "demographic momentum into high-value intellectual capital before the demographic dividend window closes."
        )
    ),
    CinematicScene(
        scene_id="s24_padma_modern",
        scene_type="image",
        source_asset="padma_bridge_modern.jpg",
        target_duration=17.0,
        zoom_dir="in", pan_dir="center",
        narration_text=(
            "Japan demonstrated that economic superpower status does not require natural resources. It requires institutional discipline, "
            "relentless technological upgrade, and strategic courage. For Bangladesh, the 2026 to 2046 window is the defining moment."
        )
    ),
    CinematicScene(
        scene_id="s25_end_card",
        scene_type="title",
        source_asset="",
        target_duration=6.0,
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


# ═══════════════════════════════════════════════════════════════════════
# PHASE 1: AUDIO SYNTHESIS & DYNAMIC TIMING DERIVATION
# ═══════════════════════════════════════════════════════════════════════

def generate_scene_narration(scene: CinematicScene) -> Path:
    """Generate Gemini TTS voiceover for scene and calculate effective duration."""
    if not scene.narration_text.strip():
        # Title card or silent scene
        scene.effective_duration = scene.target_duration
        silent_wav = SEGMENTS_DIR / f"{scene.scene_id}_voice_gemini.wav"
        if not silent_wav.exists():
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anullsrc=r=48000:cl=stereo:d={scene.effective_duration}",
                "-c:a", "pcm_s16le",
                str(silent_wav)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return silent_wav

    # Synthesize with Gemini TTS female voice
    audio_path = scene.audio_file
    synthesize_gemini_voice(scene.narration_text, audio_path, voice_name="Aoede")

    # Measure actual spoken length
    audio_dur = get_media_duration(audio_path)

    # Audio-First Rule: Visual duration matches exact speech length + 0.8s breath cushion
    # This guarantees zero truncation AND zero dead gaps!
    scene.effective_duration = round(audio_dur + 0.8, 2)
    return audio_path


def build_master_audio(scenes: List[CinematicScene], total_video_dur: float) -> Path:
    """Concatenate voice tracks with pad, crossfade BGM score, and apply sidechain ducking."""
    print("\n[Phase 1B] Building Master Soundtrack with Dynamic Sidechain Ducking...")
    mastered_audio = TEMP_DIR / "mastered_soundtrack.wav"
    
    # 1. Pad voice tracks to match exact scene visual durations (ZERO -t truncation!)
    voice_concat_txt = TEMP_DIR / "voice_concat.txt"
    with open(voice_concat_txt, "w", encoding="utf-8") as f:
        for sc in scenes:
            raw_audio = sc.audio_file
            padded_wav = SEGMENTS_DIR / f"{sc.scene_id}_voice_padded.wav"
            # apad ensures silent room-tone padding up to sc.effective_duration WITHOUT chopping speech
            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(raw_audio),
                "-af", f"apad=whole_dur={sc.effective_duration}",
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

    # 3. Dynamic Sidechain Auto-Ducking & Broadcast Mastering
    audio_filter = (
        f"[1:a]atrim=0:{total_video_dur},volume=0.30[bgm_trimmed];"
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
# PHASE 2: VISUAL RENDERING (FULL CANVAS 16:9 - ZERO CROPPING)
# ═══════════════════════════════════════════════════════════════════════

def is_valid_video(p: Path) -> bool:
    """Validate that a video segment exists, is non-empty, and has readable moov atom."""
    if not p.exists() or p.stat().st_size < 10000:
        return False
    try:
        dur = get_media_duration(p)
        return dur > 0.1
    except Exception:
        return False

def render_cinematic_title_card(scene: CinematicScene) -> Path:
    """Generate a high-contrast cinematic title card on Obsidian slate (#0A0A0F)."""
    out_video = scene.video_file
    if is_valid_video(out_video):
        return out_video
    d = scene.effective_duration

    main_text = scene.title_main.replace(":", "\\:").replace("'", "'\\''")
    sub_text = scene.title_sub.replace(":", "\\:").replace("'", "'\\''")

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
        f"fade=t=in:st=0:d=1.0,fade=t=out:st={max(0, d-1.0)}:d=1.0"
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
    """Render subtle, elegant Ken Burns drift with zero awkward cropping."""
    out_video = scene.video_file
    if is_valid_video(out_video):
        return out_video
    src = resolve_asset_path(scene.source_asset)
    d = scene.effective_duration
    total_frames = int(d * FPS)

    is_chart = (
        scene.source_asset.endswith(".png") and
        ("fig" in scene.source_asset.lower() or "plate" in scene.source_asset.lower())
    )

    if is_chart:
        # Scale to fit generously inside 3840x2160 with Obsidian slate background
        # Blends 100% invisibly with the dark cinema chart background!
        vf = (
            f"scale=w=3560:h=2000:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color=0x0A0A0F,"
            f"{GRAIN},"
            f"fade=t=in:st=0:d=0.75,fade=t=out:st={max(0, d-0.75)}:d=0.75"
        )
    else:
        # Subtle, wide-angle cinematic drift: max 1.03x zoom to prevent cutting off horizons/towers
        if scene.zoom_dir == "in":
            z_expr = "min(zoom+0.00007,1.03)"
        elif scene.zoom_dir == "out":
            z_expr = "max(1.03-0.00007*on,1.0)"
        else:
            z_expr = "1.01"

        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"

        vf = (
            f"scale=3840:2160:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=3840:2160,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={W}x{H}:fps={FPS},"
            f"{COLOR_GRADE},"
            f"{GRAIN},"
            f"fade=t=in:st=0:d=0.75,fade=t=out:st={max(0, d-0.75)}:d=0.75"
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
    """Upscale and grade pre-rendered clean video chapter without letterbox cropping."""
    out_video = scene.video_file
    if is_valid_video(out_video):
        return out_video
    src = resolve_asset_path(scene.source_asset)
    d = scene.effective_duration

    vf = (
        f"scale={W}:{H}:flags=lanczos,"
        f"unsharp=5:5:0.5:5:5:0,"
        f"{COLOR_GRADE},"
        f"{GRAIN},"
        f"fade=t=in:st=0:d=0.75,fade=t=out:st={max(0, d-0.75)}:d=0.75"
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

def build_cinematic_documentary():
    print("═" * 76, flush=True)
    print("  IZHAAN INTELLECT: 4K CINEMATIC MASTER BUILDER (GEMINI TTS FEMALE)", flush=True)
    print("  Documentary Target: ~9m 10s (Strictly < 10 Minutes)", flush=True)
    print("═" * 76, flush=True)

    # Step 1: Synthesize Voiceover & Derive Audio-First Durations
    print("\n[Phase 1A] Synthesizing Gemini Female Voiceover Audio...", flush=True)
    for i, scene in enumerate(TIMELINE, 1):
        print(f"  [{i:02d}/{len(TIMELINE):02d}] Synthesizing {scene.scene_id}...", flush=True)
        generate_scene_narration(scene)
        print(f"       -> Spoken Audio: {get_media_duration(scene.audio_file):.2f}s | Effective Scene Duration: {scene.effective_duration:.2f}s", flush=True)

    total_effective_dur = sum(s.effective_duration for s in TIMELINE)
    print(f"\nTotal Calculated Duration: {int(total_effective_dur // 60)}m {int(total_effective_dur % 60)}s ({total_effective_dur:.2f}s)", flush=True)
    if total_effective_dur > 600.0:
        print(f"  [!] WARNING: Total duration exceeds 600s: {total_effective_dur:.2f}s!", flush=True)
    else:
        print(f"  [+] Target Check: {total_effective_dur:.2f}s < 600.0s (PASS)", flush=True)

    # Step 2: Render Visual Segments
    print("\n[Phase 2] Rendering 4K Cinematic Visual Segments...", flush=True)
    rendered_videos = []
    for i, scene in enumerate(TIMELINE, 1):
        print(f"  [{i:02d}/{len(TIMELINE):02d}] Rendering {scene.scene_id} ({scene.scene_type}, {scene.effective_duration:.2f}s)...", flush=True)
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
    print(f"  [+] Concatenated Video Ready: {actual_video_dur:.2f}s", flush=True)

    # Step 4: Build Master Audio with Auto-Ducking
    mastered_audio = build_master_audio(TIMELINE, actual_video_dur)

    # Step 5: Final Master Mux
    print("\n[Phase 5] Mastering Final 4K Cinematic Output...", flush=True)
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

    print("\n" + "═" * 76, flush=True)
    print("  MASTER CINEMATIC VIDEO BUILD COMPLETE", flush=True)
    print(f"File:       {FINAL_VIDEO.name}", flush=True)
    print(f"Resolution: {W} x {H} (4K UHD 16:9 Full Canvas)", flush=True)
    print(f"Voiceover:  Gemini Female Neural (Aoede)", flush=True)
    print(f"Duration:   {int(final_dur // 60)}m {int(final_dur % 60)}s ({final_dur:.2f} Seconds)", flush=True)
    print(f"Size:       {file_size_mb:.2f} MB", flush=True)
    if final_dur <= 600.0:
        print(f"Status:     PASS (<10 Minutes Limit Confirmed: {final_dur:.1f}s <= 600s)", flush=True)
    else:
        print(f"Status:     FAIL (Exceeded 10 Minutes Limit: {final_dur:.1f}s > 600s)", flush=True)
    print("═" * 76, flush=True)


if __name__ == "__main__":
    build_cinematic_documentary()
