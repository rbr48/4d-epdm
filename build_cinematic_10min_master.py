#!/usr/bin/env python3
"""
Hollywood/Netflix-Grade 4K Cinematic YouTube Documentary Builder (<10 Minutes)
=============================================================================
Channel: Izhaan Intellect (@IzhaanIntellect)
Title: The 4D Economic Power: Japan vs Bangladesh ($2.8T Convergence)

Production Specs:
- Resolution: 3840 x 2160 (4K UHD), 30 FPS Progressive Full Canvas (16:9)
- Aesthetic: Clean White Editorial Studio (The Economist / Financial Times / Vox Style)
- Background: Pure White Canvas (#FFFFFF) with zero dark borders / zero awkward cropping
- Audio: Google Gemini TTS Female Voice (Aoede) with natural breathing pauses
- Dynamic Audio-First Duration: Audio is NEVER truncated; visual duration >= audio + 0.8s
- Audio Padding: Seamless room-tone extension without hard clamping
- Pacing: High-velocity cuts across 37 synchronized scenes with zero dead voids
- Master Target Duration: ~7:30 to 8:30 (Strictly < 600 Seconds)
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
CARDS_DIR = OUT_DIR / "white_cards"
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

# Encoder options
SEG_ENCODER = "libx264"
SEG_OPTS = ["-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-g", str(FPS * 2)]

@dataclass
class CinematicScene:
    scene_id: str
    scene_type: str           # "image" or "video"
    source_asset: str         # Filename in CARDS_DIR, FIG_DIR, or ASSETS_DIR
    target_duration: float    # Base target duration in seconds
    trim_start: float = 0.0   # For video clips
    narration_text: str = ""
    effective_duration: float = 0.0
    motion_target: tuple = (0.50, 0.50)  # (tx, ty) normalized target to zoom towards
    zoom_max: float = 1.15               # Maximum zoom scale at end of scene

    @property
    def video_file(self) -> Path:
        return SEGMENTS_DIR / f"{self.scene_id}_v4k.mp4"

    @property
    def audio_file(self) -> Path:
        return SEGMENTS_DIR / f"{self.scene_id}_voice_gemini.wav"


# ═══════════════════════════════════════════════════════════════════════
# 37-SCENE HIGH-RETENTION YOUTUBE MASTER TIMELINE (Target: ~7:45 - 8:15)
# ═══════════════════════════════════════════════════════════════════════

TIMELINE: List[CinematicScene] = [
    # ─── ACT 0: PROLOGUE — THE GHOST OF 1945 ─────────────────────────
    CinematicScene(
        scene_id="s01_title_card",
        scene_type="image",
        source_asset="card_00_title.png",
        target_duration=3.5,
        narration_text="",
        motion_target=(0.50, 0.50),
        zoom_max=1.12
    ),
    CinematicScene(
        scene_id="s02_tokyo_ruins",
        scene_type="image",
        source_asset="tokyo_1945_ruins.jpg",
        target_duration=14.0,
        narration_text=(
            "In nineteen forty-five, Tokyo was reduced to two million tons of smoking rubble. "
            "Every major industrial center was destroyed. Western economists predicted Japan would remain permanently impoverished."
        ),
        motion_target=(0.50, 0.45),
        zoom_max=1.18
    ),
    CinematicScene(
        scene_id="s03_shinkansen",
        scene_type="image",
        source_asset="shinkansen_1964.jpg",
        target_duration=15.0,
        narration_text=(
            "Yet just twenty-five years later, Japanese bullet trains were flying past Mount Fuji, "
            "and Japanese corporations were dominating global high-tech electronics, steel, and automotive markets."
        ),
        motion_target=(0.52, 0.55),
        zoom_max=1.20
    ),
    CinematicScene(
        scene_id="s04_zero_resources",
        scene_type="image",
        source_asset="card_04_zero_resources.png",
        target_duration=8.0,
        narration_text=(
            "How did a country with zero natural resources pull off the greatest economic miracle in human history?"
        ),
        motion_target=(0.50, 0.48),
        zoom_max=1.22
    ),
    CinematicScene(
        scene_id="s05_bangladesh_port",
        scene_type="image",
        source_asset="matarbari_deep_port.jpg",
        target_duration=10.0,
        narration_text=(
            "And why is Bangladesh... a booming economy of one hundred and seventy million people... "
            "walking straight into an invisible trap?"
        ),
        motion_target=(0.50, 0.52),
        zoom_max=1.18
    ),

    # ─── ACT I: THE 2026 PRECIPICE — THE TRAPDOOR OPENS ──────────────
    CinematicScene(
        scene_id="s06_act1_card",
        scene_type="image",
        source_asset="card_06_act1.png",
        target_duration=2.5,
        narration_text="",
        motion_target=(0.50, 0.50),
        zoom_max=1.10
    ),
    CinematicScene(
        scene_id="s07_garments_floor",
        scene_type="video",
        source_asset="The_Japanese_Development_Architecture_for_Bangladesh_Clean.mp4",
        target_duration=14.0,
        trim_start=15.0,
        narration_text=(
            "For thirty years, Bangladesh was celebrated as the world's next economic miracle. "
            "It cut extreme poverty in half, built a five-hundred-billion-dollar economy, and dressed the entire world."
        )
    ),
    CinematicScene(
        scene_id="s08_gdp_garments",
        scene_type="image",
        source_asset="card_08_gdp_garments.png",
        target_duration=8.0,
        narration_text=(
            "Over eighty-four percent of all export revenue comes from a single engine: ready-made garments."
        ),
        motion_target=(0.28, 0.50),
        zoom_max=1.28
    ),
    CinematicScene(
        scene_id="s09_ldc_trapdoor",
        scene_type="video",
        source_asset="Forecasting_the_Middle-Income_Trap__Inside_the_4D-EPDM_Architec_Clean.mp4",
        target_duration=12.0,
        trim_start=30.0,
        narration_text=(
            "Then comes 2026. The United Nations Least Developed Country graduation kicks in. "
            "And an invisible economic trapdoor drops wide open."
        )
    ),
    CinematicScene(
        scene_id="s10_tariff_cliff",
        scene_type="image",
        source_asset="card_10_tariff_cliff.png",
        target_duration=11.0,
        narration_text=(
            "Overnight, duty-free access to European markets vanishes, hitting exports with eight to twelve percent tariffs "
            "that obliterate thin factory margins."
        ),
        motion_target=(0.28, 0.52),
        zoom_max=1.28
    ),
    CinematicScene(
        scene_id="s11_banking_stress",
        scene_type="image",
        source_asset="The_Bangladesh_Takeoff_Architecture_page_03.png",
        target_duration=13.0,
        narration_text=(
            "At the exact same moment, the domestic banking sector is paralyzed by non-performing loans, "
            "choking off private investment when factories need to upgrade most."
        ),
        motion_target=(0.40, 0.52),
        zoom_max=1.25
    ),
    CinematicScene(
        scene_id="s12_tax_inertia",
        scene_type="image",
        source_asset="card_12_tax_inertia.png",
        target_duration=10.0,
        narration_text=(
            "And with a tax-to-GDP ratio below eight percent, the sovereign government has virtually no fiscal ammunition "
            "to cushion the blow."
        ),
        motion_target=(0.28, 0.52),
        zoom_max=1.28
    ),

    # ─── ACT II: THE BRUTAL 87% LAW — THE MIDDLE-INCOME CURSE ────────
    CinematicScene(
        scene_id="s13_act2_card",
        scene_type="image",
        source_asset="card_13_act2.png",
        target_duration=2.5,
        narration_text="",
        motion_target=(0.50, 0.50),
        zoom_max=1.10
    ),
    CinematicScene(
        scene_id="s14_88_trapped",
        scene_type="image",
        source_asset="card_14_88_trapped.png",
        target_duration=9.0,
        narration_text=(
            "History has an unforgiving track record. In nineteen sixty, the World Bank tracked one hundred and one middle-income economies."
        ),
        motion_target=(0.32, 0.52),
        zoom_max=1.24
    ),
    CinematicScene(
        scene_id="s15_plate_investment",
        scene_type="image",
        source_asset="plate_01_investment_comparison.png",
        target_duration=12.0,
        narration_text=(
            "By 2008, eighty-eight of those nations were still trapped! Crushed by rising wages, "
            "beaten by cheaper competitors, unable to climb into advanced manufacturing."
        ),
        motion_target=(0.60, 0.52),
        zoom_max=1.26
    ),
    CinematicScene(
        scene_id="s16_complexity_escape",
        scene_type="image",
        source_asset="The_Bangladesh_Takeoff_Architecture_page_05.png",
        target_duration=11.0,
        narration_text=(
            "Only thirteen countries in human history broke free. Every single one of them followed a single rule: "
            "they mastered economic complexity."
        ),
        motion_target=(0.50, 0.45),
        zoom_max=1.25
    ),
    CinematicScene(
        scene_id="s17_fig2_complexity",
        scene_type="image",
        source_asset="fig2_economic_complexity_chasm.png",
        target_duration=14.0,
        narration_text=(
            "Look at the structural reality. Japan achieved a complexity score of plus two point two. "
            "Bangladesh sits at minus zero point eight... a massive structural capability chasm."
        ),
        motion_target=(0.30, 0.62),
        zoom_max=1.30
    ),
    CinematicScene(
        scene_id="s18_cheap_labor_ceiling",
        scene_type="image",
        source_asset="card_18_cheap_labor_ceiling.png",
        target_duration=10.0,
        narration_text=(
            "Cheap labor can lift millions out of extreme poverty. But to escape the middle-income trap, "
            "you need an entirely different engine."
        ),
        motion_target=(0.50, 0.50),
        zoom_max=1.22
    ),

    # ─── ACT III: THE SECRET JAPANESE PLAYBOOK — THE MITI TRIAD ───────
    CinematicScene(
        scene_id="s19_act3_card",
        scene_type="image",
        source_asset="card_19_act3.png",
        target_duration=2.5,
        narration_text="",
        motion_target=(0.50, 0.50),
        zoom_max=1.10
    ),
    CinematicScene(
        scene_id="s20_miti_footage",
        scene_type="video",
        source_asset="The_Japanese_Development_Architecture_for_Bangladesh_Clean.mp4",
        target_duration=12.0,
        trim_start=60.0,
        narration_text=(
            "So how did Japan do it? Neoliberal economists claim it was free markets. "
            "History proves it was the exact opposite: an uncompromising developmental state."
        )
    ),
    CinematicScene(
        scene_id="s21_miti_rule1",
        scene_type="image",
        source_asset="card_21_miti_rule1.png",
        target_duration=17.0,
        narration_text=(
            "Rule number one: Sequenced Industrial Targeting. Japan never tried to build microchips overnight. "
            "They started with basic silk and cotton, used the profits to capitalize heavy steel, and then leapt into automobiles and semiconductors."
        ),
        motion_target=(0.32, 0.52),
        zoom_max=1.26
    ),
    CinematicScene(
        scene_id="s22_miti_rule2",
        scene_type="image",
        source_asset="card_22_miti_rule2.png",
        target_duration=15.0,
        narration_text=(
            "Rule number two: Brutal Export Discipline. Subsidies were never handouts for political favorites. "
            "If a corporation failed to compete in international markets, the government ruthlessly pulled their funding."
        ),
        motion_target=(0.30, 0.52),
        zoom_max=1.26
    ),
    CinematicScene(
        scene_id="s23_miti_rule3",
        scene_type="image",
        source_asset="card_23_miti_rule3.png",
        target_duration=14.0,
        narration_text=(
            "And rule number three: The Postal Savings Engine. Instead of drowning in dollar-denominated foreign debt, "
            "Japan mobilized domestic citizen savings directly into national infrastructure."
        ),
        motion_target=(0.32, 0.52),
        zoom_max=1.26
    ),

    # ─── ACT IV: THE CLOSING DEMOGRAPHIC WINDOW ───────────────────────
    CinematicScene(
        scene_id="s24_act4_card",
        scene_type="image",
        source_asset="card_24_act4.png",
        target_duration=2.5,
        narration_text="",
        motion_target=(0.50, 0.50),
        zoom_max=1.10
    ),
    CinematicScene(
        scene_id="s25_fig1_demographic",
        scene_type="image",
        source_asset="fig1_demographic_dividend.png",
        target_duration=8.0,
        narration_text=(
            "Here is the most dangerous reality for Bangladesh: the clock is ticking faster than anyone realizes."
        ),
        motion_target=(0.32, 0.50),
        zoom_max=1.28
    ),
    CinematicScene(
        scene_id="s26_surplus_labor",
        scene_type="image",
        source_asset="The_Bangladesh_Takeoff_Architecture_page_02.png",
        target_duration=11.0,
        narration_text=(
            "According to United Nations projections, Bangladesh’s demographic dividend peaks around 2038. "
            "After that, the dependency ratio reverses."
        ),
        motion_target=(0.50, 0.48),
        zoom_max=1.25
    ),
    CinematicScene(
        scene_id="s27_demographic_peak",
        scene_type="image",
        source_asset="card_27_demographic_peak.png",
        target_duration=11.0,
        narration_text=(
            "If Bangladesh does not modernize its economy before 2038, it will become an aging society before it becomes a prosperous one!"
        ),
        motion_target=(0.30, 0.52),
        zoom_max=1.28
    ),
    CinematicScene(
        scene_id="s28_fig3_fan_charts",
        scene_type="image",
        source_asset="fig3_bangladesh_2045_fan_charts.png",
        target_duration=17.0,
        narration_text=(
            "Our econometric simulations across five thousand Monte Carlo draws reveal the fork in the road. "
            "In the status quo, growth stalls under four percent. But under the Japanese reform sequence, real growth hits eight percent annually."
        ),
        motion_target=(0.72, 0.48),
        zoom_max=1.28
    ),

    # ─── ACT V: THE $2.8 TRILLION HORIZON — THE ESCAPE VELOCITY ───────
    CinematicScene(
        scene_id="s29_act5_card",
        scene_type="image",
        source_asset="card_29_act5.png",
        target_duration=2.5,
        narration_text="",
        motion_target=(0.50, 0.50),
        zoom_max=1.10
    ),
    CinematicScene(
        scene_id="s30_padma_bridge",
        scene_type="image",
        source_asset="padma_bridge_modern.jpg",
        target_duration=14.0,
        narration_text=(
            "The foundation is already being poured. Mega-infrastructure like the Padma Multipurpose Bridge "
            "has integrated twenty-one isolated districts into the national economy."
        ),
        motion_target=(0.50, 0.52),
        zoom_max=1.20
    ),
    CinematicScene(
        scene_id="s31_matarbari_port",
        scene_type="image",
        source_asset="matarbari_deep_port.jpg",
        target_duration=15.0,
        narration_text=(
            "And right on the Bay of Bengal, the Japanese-backed Matarbari Deep Sea Port will allow "
            "eighteen-meter deep draft mother vessels to dock for the first time in South Asian history!"
        ),
        motion_target=(0.52, 0.48),
        zoom_max=1.22
    ),
    CinematicScene(
        scene_id="s32_matarbari_stats",
        scene_type="image",
        source_asset="card_32_matarbari_stats.png",
        target_duration=15.0,
        narration_text=(
            "This slashes shipping times to Europe and North America by nearly a third, "
            "transforming Bangladesh into the maritime gateway for three billion people across South and Southeast Asia."
        ),
        motion_target=(0.28, 0.52),
        zoom_max=1.28
    ),
    CinematicScene(
        scene_id="s33_fig4_radar",
        scene_type="image",
        source_asset="fig4_capability_radar.png",
        target_duration=16.0,
        narration_text=(
            "By closing the gap in human capital, digital infrastructure, and green power, "
            "Bangladesh can move from stitching cheap t-shirts to precision electronics, software, and light engineering."
        ),
        motion_target=(0.50, 0.48),
        zoom_max=1.26
    ),
    CinematicScene(
        scene_id="s34_fig5_projections",
        scene_type="image",
        source_asset="fig5_macro_monetary_projections.png",
        target_duration=16.0,
        narration_text=(
            "The reward for executing this transition is historic: a three point one trillion dollar nominal economy "
            "by twenty forty-six, generating nearly three hundred billion dollars in annual domestic tax revenue!"
        ),
        motion_target=(0.75, 0.48),
        zoom_max=1.30
    ),
    CinematicScene(
        scene_id="s35_dividend_stats",
        scene_type="image",
        source_asset="card_35_dividend_stats.png",
        target_duration=9.0,
        narration_text=(
            "That is a one point three trillion dollar dividend between success... and catastrophe."
        ),
        motion_target=(0.30, 0.52),
        zoom_max=1.28
    ),
    CinematicScene(
        scene_id="s36_outro",
        scene_type="image",
        source_asset="card_36_outro.png",
        target_duration=12.0,
        narration_text=(
            "In 2026, Bangladesh stands exactly where Japan stood in 1950. The blueprint has already been written. "
            "The only question left... is whether they will execute it."
        ),
        motion_target=(0.50, 0.48),
        zoom_max=1.22
    ),
    CinematicScene(
        scene_id="s37_end_screen",
        scene_type="video",
        source_asset="The_2045_Blueprint__Bangladesh_and_the_4D_Transformation_Clean.mp4",
        target_duration=10.0,
        trim_start=180.0,
        narration_text=(
            "Subscribe to Izhaan Intellect for more deep investigative documentaries on science, economics, and higher dimensions."
        )
    ),
]


# ═══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def resolve_asset_path(filename: str) -> Path:
    p0 = CARDS_DIR / filename
    if p0.exists():
        return p0
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
    print("\n[Phase 1B] Building Master Soundtrack with Dynamic Sidechain Ducking...", flush=True)
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
    # Louder driving BGM (volume=0.62) with 2.2 kHz notch EQ for female vocal clarity,
    # gentle musical ducking (ratio=2.2) and professional broadcast loudness mastering.
    audio_filter = (
        f"[1:a]atrim=0:{total_video_dur},volume=0.62,equalizer=f=2200:width_type=q:w=1.2:g=-4.0[bgm_eq];"
        "[bgm_eq][0:a]sidechaincompress=threshold=0.10:ratio=2.2:attack=25:release=250[ducked_bgm];"
        "[ducked_bgm][0:a]amix=inputs=2:duration=first:weights=1.0 1.0[raw_mix];"
        "[raw_mix]highpass=f=70,acompressor=threshold=0.12:ratio=2.6:attack=10:release=60,"
        "loudnorm=I=-14:TP=-1.0:LRA=11,alimiter=limit=0.891[final_master]"
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
    print(f"  [+] Master Audio Created: {mastered_audio.name} ({get_media_duration(mastered_audio):.2f}s)", flush=True)
    return mastered_audio


# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: VISUAL RENDERING (PURE WHITE STUDIO - ZERO CROPPING)
# ═══════════════════════════════════════════════════════════════════════

def is_valid_video(p: Path) -> bool:
    """Validate that a video segment exists, is non-empty, and has readable duration."""
    if not p.exists() or p.stat().st_size < 10000:
        return False
    try:
        dur = get_media_duration(p)
        return dur > 0.1
    except Exception:
        return False


def render_cinematic_image_scene(scene: CinematicScene, force_rebuild: bool = True) -> Path:
    """
    Render 4K White Studio visual with targeted dynamic camera motion:
    - Pure white studio background (#FFFFFF).
    - Targeted zoompan tracking the subject spoken by the narrator.
    - Smooth subpixel motion across exact speech duration.
    """
    out_video = scene.video_file
    if not force_rebuild and is_valid_video(out_video):
        return out_video

    src = resolve_asset_path(scene.source_asset)
    d = scene.effective_duration
    total_frames = max(1, int(round(d * FPS)))

    tx, ty = scene.motion_target
    z_max = scene.zoom_max

    z_expr = f"1.0+({z_max}-1.0)*on/{total_frames}"
    x_expr = f"max(0,min(iw*(1-1/zoom),iw*({tx}-0.5/zoom)))"
    y_expr = f"max(0,min(ih*(1-1/zoom),ih*({ty}-0.5/zoom)))"

    is_white_card = "card_" in scene.source_asset.lower()
    is_figure_or_chart = (
        scene.source_asset.endswith(".png") and (
            "fig" in scene.source_asset.lower() or
            "plate" in scene.source_asset.lower() or
            "architecture_page" in scene.source_asset.lower() or
            "blueprint_page" in scene.source_asset.lower()
        )
    )

    if is_white_card:
        # Pre-generated 4K cards (3840x2160): smooth targeted zoom onto narrated data card metric
        vf = (
            f"scale={W}:{H}:flags=lanczos,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={W}x{H}:fps={FPS}"
        )
    elif is_figure_or_chart:
        # Scale to fit inside 3840x2160 with pure white canvas (#FFFFFF) padding, then zoom into focal chart quadrant
        vf = (
            f"scale=w=3640:h=2040:force_original_aspect_ratio=decrease:flags=lanczos,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white,"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={W}x{H}:fps={FPS}"
        )
    else:
        # Archival/modern photographs (1376x768 -> 3840x2160)
        vf = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={W}:{H},"
            f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={total_frames}:s={W}x{H}:fps={FPS},"
            f"eq=contrast=1.04:brightness=0.01:saturation=1.02"
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
    """Upscale and grade video clip without letterbox cropping or distortion."""
    out_video = scene.video_file
    if is_valid_video(out_video):
        return out_video

    src = resolve_asset_path(scene.source_asset)
    d = scene.effective_duration

    vf = (
        f"scale={W}:{H}:flags=lanczos,"
        f"unsharp=5:5:0.5:5:5:0,"
        f"eq=contrast=1.03:brightness=0.01:saturation=1.02"
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
    print("  IZHAAN INTELLECT: 4K HIGH-RETENTION YOUTUBE DOCUMENTARY BUILDER", flush=True)
    print("  Documentary Target: ~7:30 to 8:30 (Strictly < 10 Minutes)", flush=True)
    print("  Aesthetic: Clean White Editorial Studio (Pure White Canvas #FFFFFF)", flush=True)
    print("  Narration: Google Gemini Female Neural Voice (Aoede)", flush=True)
    print("═" * 76, flush=True)

    # Step 1: Synthesize Voiceover & Derive Audio-First Durations
    print("\n[Phase 1A] Synthesizing Gemini Female Voiceover Audio...", flush=True)
    for i, scene in enumerate(TIMELINE, 1):
        print(f"  [{i:02d}/{len(TIMELINE):02d}] Processing {scene.scene_id}...", flush=True)
        generate_scene_narration(scene)
        audio_len = get_media_duration(scene.audio_file)
        print(f"       -> Voice: {audio_len:.2f}s | Scene Duration: {scene.effective_duration:.2f}s", flush=True)

    total_effective_dur = sum(s.effective_duration for s in TIMELINE)
    mins = int(total_effective_dur // 60)
    secs = int(total_effective_dur % 60)
    print(f"\nTotal Calculated Runtime: {mins}m {secs}s ({total_effective_dur:.2f}s)", flush=True)
    if total_effective_dur > 600.0:
        print(f"  [!] WARNING: Total duration exceeds 600s: {total_effective_dur:.2f}s!", flush=True)
    else:
        print(f"  [+] Target Check: {total_effective_dur:.2f}s < 600.0s (PASS)", flush=True)

    # Step 2: Render Visual Segments
    print("\n[Phase 2] Rendering 4K Pure White Studio Visual Segments...", flush=True)
    rendered_videos = []
    for i, scene in enumerate(TIMELINE, 1):
        print(f"  [{i:02d}/{len(TIMELINE):02d}] Rendering {scene.scene_id} ({scene.scene_type}, {scene.effective_duration:.2f}s)...", flush=True)
        if scene.scene_type == "image":
            v = render_cinematic_image_scene(scene)
        elif scene.scene_type == "video":
            v = render_cinematic_video_clip(scene)
        else:
            raise ValueError(f"Unknown scene type: {scene.scene_type}")
        rendered_videos.append(v)

    # Step 3: Concatenate Video Stream
    print("\n[Phase 3] Concatenating 4K Video Segments...", flush=True)
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
    print(f"Aesthetic:  Pure White Studio (#FFFFFF Canvas)", flush=True)
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
