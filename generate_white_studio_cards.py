#!/usr/bin/env python3
"""
Generate 4K White Studio Editorial Title & Kinetic Cards for Izhaan Intellect
===========================================================================
Produces broadcast-grade, high-contrast 4K graphic cards (3840x2160)
for "The 4D Economic Power: Japan vs Bangladesh" documentary.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CARDS_DIR = ROOT / "outputs" / "white_cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

W, H = 3840, 2160

# Palette
WHITE = (255, 255, 255)
BG_LIGHT = (250, 250, 252)
BORDER = (229, 231, 235)
NAVY_CHARCOAL = (17, 24, 39)
MUTED_GREY = (107, 114, 128)
ROYAL_BLUE = (13, 110, 253)
CRIMSON = (220, 38, 38)
EMERALD = (22, 163, 74)
AMBER = (217, 119, 6)

def get_font(size: int, bold: bool = True):
    font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()

def draw_studio_base(draw: ImageDraw.ImageDraw, badge_text: str, badge_color=ROYAL_BLUE, act_idx: int = 1):
    # Outer margin border
    draw.rectangle([(60, 60), (W - 60, H - 60)], outline=BORDER, width=3)
    draw.rectangle([(80, 80), (W - 80, H - 80)], outline=(243, 244, 246), width=2)
    
    # Technical Corner Crosshairs (+)
    cross_color = (180, 185, 195)
    for cx, cy in [(100, 100), (W - 100, 100), (100, H - 100), (W - 100, H - 100)]:
        draw.line([(cx - 20, cy), (cx + 20, cy)], fill=cross_color, width=3)
        draw.line([(cx, cy - 20), (cx, cy + 20)], fill=cross_color, width=3)
    
    # Header badge (pill)
    badge_font = get_font(36, bold=True)
    bbox = draw.textbbox((0, 0), badge_text.upper(), font=badge_font)
    text_w = bbox[2] - bbox[0]
    draw.rounded_rectangle([(140, 125), (140 + text_w + 50, 190)], radius=12, fill=badge_color)
    draw.text((165, 137), badge_text.upper(), fill=WHITE, font=badge_font)
    
    # Metadata Tag next to badge
    meta_font = get_font(28, bold=False)
    draw.text((140 + text_w + 80, 145), "ANALYSIS // 4D-EPDM CONVERGENCE MODEL", fill=MUTED_GREY, font=meta_font)
    
    # Channel watermark top right
    wm_font = get_font(36, bold=True)
    draw.text((W - 620, 137), "IZHAAN INTELLECT", fill=NAVY_CHARCOAL, font=wm_font)
    draw.rectangle([(W - 200, 137), (W - 170, 177)], fill=CRIMSON)
    
    # Bottom institutional citation footer
    cite_font = get_font(28, bold=False)
    draw.line([(100, H - 140), (W - 100, H - 140)], fill=(235, 238, 242), width=2)
    draw.text((140, H - 115), "EMPIRICAL SOURCES: MIT HARVARD CID / WORLD BANK WDI / JICA MARITIME STUDY 2026", fill=MUTED_GREY, font=cite_font)
    
    # Act Progress Indicator Dots (1-5)
    dot_font = get_font(26, bold=True)
    draw.text((W - 600, H - 116), "PROGRESS", fill=MUTED_GREY, font=dot_font)
    for dot_i in range(1, 6):
        dx = W - 430 + (dot_i - 1) * 60
        dy = H - 105
        is_active = (dot_i == act_idx)
        dot_fill = badge_color if is_active else (215, 220, 228)
        radius = 12 if is_active else 8
        draw.ellipse([(dx - radius, dy - radius), (dx + radius, dy + radius)], fill=dot_fill)

def make_act_card(out_name: str, act_num: str, act_title: str, subtitle: str, color=ROYAL_BLUE, act_idx: int = 1):
    im = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_studio_base(draw, f"DOCUMENTARY CHAPTER // {act_num}", color, act_idx=act_idx)
    
    # Big Act numeral with decorative bracket
    f_act = get_font(90, bold=True)
    draw.text((240, 620), f"[ {act_num} ]", fill=color, font=f_act)
    draw.line([(240, 750), (750, 750)], fill=color, width=10)
    
    # Act Title
    f_title = get_font(136, bold=True)
    draw.text((240, 810), act_title, fill=NAVY_CHARCOAL, font=f_title)
    
    # Subtitle
    f_sub = get_font(56, bold=False)
    draw.text((240, 1050), subtitle, fill=MUTED_GREY, font=f_sub)
    
    # Decorative technical grid lines
    grid_col = (235, 238, 245)
    for gy in [420, 520, 1250, 1350]:
        draw.line([(240, gy), (W - 240, gy)], fill=grid_col, width=2)
    
    p = CARDS_DIR / f"{out_name}.png"
    im.save(p, quality=95)
    print(f"Saved: {p.name}")

def make_kinetic_metric_card(
    out_name: str,
    badge: str,
    main_title: str,
    big_stat1: str,
    label1: str,
    big_stat2: str = "",
    label2: str = "",
    note: str = "",
    accent=CRIMSON,
    tag1: str = "KEY METRIC",
    tag2: str = "BENCHMARK",
    act_idx: int = 1
):
    im = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_studio_base(draw, badge, accent, act_idx=act_idx)
    
    # Headline
    f_head = get_font(86, bold=True)
    draw.text((200, 430), main_title, fill=NAVY_CHARCOAL, font=f_head)
    
    f_stat = get_font(154, bold=True)
    f_lbl = get_font(48, bold=True)
    f_tag = get_font(30, bold=True)
    
    # Card 1: Drop Shadow + White Card Box
    # Shadow offset (14, 18)
    draw.rounded_rectangle([(214, 698), (1814, 1428)], radius=28, fill=(232, 236, 242))
    # Card surface
    draw.rounded_rectangle([(200, 680), (1800, 1410)], radius=28, fill=WHITE, outline=BORDER, width=4)
    # Accent color pillar
    draw.rectangle([(200, 680), (224, 1410)], fill=accent)
    
    # Tag badge inside Card 1
    tbbox1 = draw.textbbox((0, 0), tag1, font=f_tag)
    tw1 = tbbox1[2] - tbbox1[0]
    draw.rounded_rectangle([(270, 730), (270 + tw1 + 36, 782)], radius=8, fill=(245, 247, 250), outline=(220, 224, 232), width=2)
    draw.text((288, 742), tag1, fill=accent, font=f_tag)
    
    # Stat 1 & Label 1
    draw.text((270, 830), big_stat1, fill=accent, font=f_stat)
    draw.text((270, 1120), label1, fill=NAVY_CHARCOAL, font=f_lbl)
    
    # Card 2 (if present)
    if big_stat2:
        # Shadow
        draw.rounded_rectangle([(1964, 698), (W - 186, 1428)], radius=28, fill=(232, 236, 242))
        # Surface
        draw.rounded_rectangle([(1950, 680), (W - 200, 1410)], radius=28, fill=WHITE, outline=BORDER, width=4)
        # Accent pillar
        draw.rectangle([(1950, 680), (1974, 1410)], fill=ROYAL_BLUE)
        
        # Tag badge inside Card 2
        tbbox2 = draw.textbbox((0, 0), tag2, font=f_tag)
        tw2 = tbbox2[2] - tbbox2[0]
        draw.rounded_rectangle([(2020, 730), (2020 + tw2 + 36, 782)], radius=8, fill=(245, 247, 250), outline=(220, 224, 232), width=2)
        draw.text((2038, 742), tag2, fill=ROYAL_BLUE, font=f_tag)
        
        # Stat 2 & Label 2
        draw.text((2020, 830), big_stat2, fill=ROYAL_BLUE, font=f_stat)
        draw.text((2020, 1120), label2, fill=NAVY_CHARCOAL, font=f_lbl)
        
    if note:
        f_note = get_font(44, bold=False)
        draw.text((200, 1550), note, fill=MUTED_GREY, font=f_note)
        
    p = CARDS_DIR / f"{out_name}.png"
    im.save(p, quality=95)
    print(f"Saved: {p.name}")

def make_rule_card(out_name: str, rule_num: str, rule_title: str, formula: str, explanation: str, color=EMERALD, act_idx: int = 3):
    im = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_studio_base(draw, "THE JAPANESE DEVELOPMENTAL PLAYBOOK", color, act_idx=act_idx)
    
    f_rnum = get_font(72, bold=True)
    draw.text((220, 440), f"[ {rule_num} ]", fill=color, font=f_rnum)
    
    f_rtitle = get_font(114, bold=True)
    draw.text((220, 550), rule_title, fill=NAVY_CHARCOAL, font=f_rtitle)
    
    # Formula Box Shadow & Surface
    draw.rounded_rectangle([(234, 768), (W - 206, 1088)], radius=24, fill=(232, 236, 242))
    draw.rounded_rectangle([(220, 750), (W - 220, 1070)], radius=24, fill=WHITE, outline=BORDER, width=4)
    draw.rectangle([(220, 750), (244, 1070)], fill=color)
    
    f_form = get_font(68, bold=True)
    draw.text((280, 860), formula, fill=color, font=f_form)
    
    # Explanation
    f_exp = get_font(52, bold=False)
    draw.text((220, 1220), explanation, fill=MUTED_GREY, font=f_exp)
    
    p = CARDS_DIR / f"{out_name}.png"
    im.save(p, quality=95)
    print(f"Saved: {p.name}")

def main():
    print("Generating 4K White Studio Graphic Cards with Motion Accents...")
    
    # Title & Prologue
    make_act_card("card_00_title", "SPECIAL INVESTIGATION", "THE 4D ECONOMIC POWER", "Japan · Bangladesh · The $2.8 Trillion Convergence", ROYAL_BLUE, act_idx=1)
    make_kinetic_metric_card("card_04_zero_resources", "HISTORICAL ANOMALY", "HOW DID JAPAN CONQUER GLOBAL MARKETS?", "0%", "NATURAL RESOURCES", "100%", "STRUCTURAL CAPABILITY", "Postwar Japan possessed zero oil, iron ore, or bauxite — yet built the world's 2nd largest GDP.", ROYAL_BLUE, tag1="NATURAL ENDOWMENT", tag2="MITI ARCHITECTURE", act_idx=1)
    
    # Act I
    make_act_card("card_06_act1", "ACT I", "THE 2026 PRECIPICE", "LDC Graduation & The Death of Cheap Labor Preferences", CRIMSON, act_idx=1)
    make_kinetic_metric_card("card_08_gdp_garments", "STRUCTURAL CONCENTRATION", "THE SINGLE-ENGINE VULNERABILITY", "$505B", "TOTAL NOMINAL GDP (2026)", "84%", "EXPORT REVENUE IN GARMENTS", "A $500B sovereign economy relying entirely on cotton textiles to survive.", CRIMSON, tag1="SOVEREIGN OUTPUT", tag2="EXPORT CONCENTRATION", act_idx=1)
    make_kinetic_metric_card("card_10_tariff_cliff", "POLICY PRECIPICE", "UN LDC GRADUATION: THE IMMEDIATE HIT", "+8% to +12%", "IMMEDIATE TARIFF INCREASE", "0.0%", "DUTY-FREE PREFERENCES REMAINING", "European Everything-But-Arms duty-free access expires automatically upon graduation.", CRIMSON, tag1="TARIFF SHOCK", tag2="DUTY-FREE EXPIRATION", act_idx=1)
    make_kinetic_metric_card("card_12_tax_inertia", "SOVEREIGN BUFFER COLLAPSE", "FISCAL REVENUE IMMOBILITY", "7.6%", "TAX-TO-GDP RATIO", "< 8.0%", "DEVELOPING WORLD AVERAGE", "The state lacks sovereign tax capital to buffer industrial modernization or credit shocks.", CRIMSON, tag1="DOMESTIC REVENUE", tag2="GLOBAL THRESHOLD", act_idx=1)
    
    # Act II
    make_act_card("card_13_act2", "ACT II", "THE 87% FAILURE RATE", "Why 88 Out of 101 Middle-Income Nations Got Trapped", AMBER, act_idx=2)
    make_kinetic_metric_card("card_14_88_trapped", "WORLD BANK 1960-2008 COHORT", "THE MIDDLE-INCOME TRAP IS THE STATISTICAL NORM", "88", "NATIONS FAILED & GOT TRAPPED", "13", "NATIONS ESCAPED TO HIGH-INCOME", "Out of 101 middle-income economies in 1960, only 13 reached high-income status.", AMBER, tag1="TRAPPED COHORT (87%)", tag2="ESCAPE COHORT (13%)", act_idx=2)
    make_kinetic_metric_card("card_18_cheap_labor_ceiling", "STRUCTURAL DIAGNOSIS", "THE PER CAPITA GLASS CEILING", "$2,000", "CHEAP LABOR CEILING (GARMENTS)", "$12,000+", "HIGH-INCOME COMPLEXITY THRESHOLD", "Cheap wages can lift people to low-middle income. After that, rising wages crush factor margins.", AMBER, tag1="LOW-TECH CEILING", tag2="COMPLEXITY FRONTIER", act_idx=2)
    
    # Act III
    make_act_card("card_19_act3", "ACT III", "THE JAPANESE PLAYBOOK", "The 3 Uncompromising Rules of Postwar MITI", EMERALD, act_idx=3)
    make_rule_card("card_21_miti_rule1", "RULE 01", "SEQUENCED INDUSTRIAL TARGETING", "TEXTILES (1950s) -> STEEL (1960s) -> AUTOS (1970s) -> CHIPS (1980s)", "Never leap blindly into high-tech. Use basic exports to capitalize heavy steel and ships first.", EMERALD, act_idx=3)
    make_rule_card("card_22_miti_rule2", "RULE 02", "BRUTAL EXPORT DISCIPLINE", "CREDIT ALLOCATION = GLOBAL EXPORT PERFORMANCE", "Subsidies were never political handouts. Fail in global markets, and state credit was cut off.", EMERALD, act_idx=3)
    make_rule_card("card_23_miti_rule3", "RULE 03", "DOMESTIC CAPITAL FUNNEL", "POSTAL SAVINGS SYSTEM -> INFRASTRUCTURE & INDUSTRY", "Citizen savings mobilized directly into sovereign industrial banks without accumulating foreign dollar debt.", EMERALD, act_idx=3)
    
    # Act IV
    make_act_card("card_24_act4", "ACT IV", "THE CLOSING WINDOW", "Demographic Countdown: The Race Against 2038", CRIMSON, act_idx=4)
    make_kinetic_metric_card("card_27_demographic_peak", "DEMOGRAPHIC INFLECTION", "THE UNFORGIVING CLOCK", "2038", "DEMOGRAPHIC DIVIDEND ENDS", "12 YRS", "REMAINING WINDOW TO REFORM", "Bangladesh must reach escape velocity before the dependency ratio rises. Get rich before getting old.", CRIMSON, tag1="INFLECTION YEAR", tag2="ACTION WINDOW", act_idx=4)
    
    # Act V
    make_act_card("card_29_act5", "ACT V", "THE $2.8 TRILLION BLUEPRINT", "Matarbari, Structural Complexity & The 2046 Horizon", ROYAL_BLUE, act_idx=5)
    make_kinetic_metric_card("card_32_matarbari_stats", "MARITIME LOGISTICS REVOLUTION", "MATARBARI DEEP SEA PORT", "18.5m", "DRAFT (MOTHER VESSEL CAPACITY)", "-30%", "SHIPPING TIME TO EU / US", "Deep draft container vessels can dock directly, bypassing feeder ports in Singapore and Colombo.", ROYAL_BLUE, tag1="CHANNEL DEPTH", tag2="TRANSIT REDUCTION", act_idx=5)
    make_kinetic_metric_card("card_35_dividend_stats", "20-YEAR MACROECONOMIC DIVIDEND", "THE 2026-2046 REFORM PAYOFF", "+$1.34T", "NOMINAL GDP REFORM DIVIDEND", "+$298B/yr", "ANNUAL DOMESTIC TAX BASE (2046)", "The difference between executing the Japanese playbook ($3.16T) versus middle-income inertia ($1.82T).", ROYAL_BLUE, tag1="GDP GAP BY 2046", tag2="ANNUAL TAX BASE", act_idx=5)
    
    # Outro
    make_act_card("card_36_outro", "THE VERDICT", "THE BLUEPRINT IS WRITTEN", "Subscribe to Izhaan Intellect for Deep Investigative Documentaries", ROYAL_BLUE, act_idx=5)
    
    print("\nAll White Studio Graphic Cards generated successfully in outputs/white_cards/!")

if __name__ == "__main__":
    main()

