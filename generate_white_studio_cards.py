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

def draw_studio_base(draw: ImageDraw.ImageDraw, badge_text: str, badge_color=ROYAL_BLUE):
    # Outer margin border
    draw.rectangle([(80, 80), (W - 80, H - 80)], outline=BORDER, width=4)
    draw.rectangle([(100, 100), (W - 100, H - 100)], outline=(243, 244, 246), width=2)
    
    # Header badge
    badge_font = get_font(38, bold=True)
    bbox = draw.textbbox((0, 0), badge_text.upper(), font=badge_font)
    text_w = bbox[2] - bbox[0]
    draw.rounded_rectangle([(140, 130), (140 + text_w + 50, 195)], radius=12, fill=badge_color)
    draw.text((165, 142), badge_text.upper(), fill=WHITE, font=badge_font)
    
    # Channel watermark top right
    wm_font = get_font(36, bold=True)
    draw.text((W - 560, 142), "IZHAAN INTELLECT", fill=NAVY_CHARCOAL, font=wm_font)
    draw.rectangle([(W - 170, 142), (W - 140, 182)], fill=CRIMSON)

def make_act_card(out_name: str, act_num: str, act_title: str, subtitle: str, color=ROYAL_BLUE):
    im = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_studio_base(draw, f"DOCUMENTARY CHAPTER // {act_num}", color)
    
    # Big Act numeral
    f_act = get_font(84, bold=True)
    draw.text((240, 680), act_num, fill=color, font=f_act)
    draw.line([(240, 790), (600, 790)], fill=color, width=8)
    
    # Act Title
    f_title = get_font(130, bold=True)
    draw.text((240, 840), act_title, fill=NAVY_CHARCOAL, font=f_title)
    
    # Subtitle
    f_sub = get_font(56, bold=False)
    draw.text((240, 1060), subtitle, fill=MUTED_GREY, font=f_sub)
    
    p = CARDS_DIR / f"{out_name}.png"
    im.save(p, quality=95)
    print(f"Saved: {p.name}")

def make_kinetic_metric_card(out_name: str, badge: str, main_title: str, big_stat1: str, label1: str, big_stat2: str = "", label2: str = "", note: str = "", accent=CRIMSON):
    im = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_studio_base(draw, badge, accent)
    
    # Main Question / Headline
    f_head = get_font(90, bold=True)
    draw.text((200, 480), main_title, fill=NAVY_CHARCOAL, font=f_head)
    
    # Big stat box 1
    draw.rounded_rectangle([(200, 720), (1800, 1450)], radius=24, fill=WHITE, outline=BORDER, width=4)
    draw.rectangle([(200, 720), (220, 1450)], fill=accent)
    
    f_stat = get_font(150, bold=True)
    f_lbl = get_font(52, bold=True)
    draw.text((270, 850), big_stat1, fill=accent, font=f_stat)
    draw.text((270, 1140), label1, fill=NAVY_CHARCOAL, font=f_lbl)
    
    # Big stat box 2 (if present)
    if big_stat2:
        draw.rounded_rectangle([(1950, 720), (W - 200, 1450)], radius=24, fill=WHITE, outline=BORDER, width=4)
        draw.rectangle([(1950, 720), (1970, 1450)], fill=ROYAL_BLUE)
        draw.text((2020, 850), big_stat2, fill=ROYAL_BLUE, font=f_stat)
        draw.text((2020, 1140), label2, fill=NAVY_CHARCOAL, font=f_lbl)
        
    if note:
        f_note = get_font(46, bold=False)
        draw.text((200, 1620), note, fill=MUTED_GREY, font=f_note)
        
    p = CARDS_DIR / f"{out_name}.png"
    im.save(p, quality=95)
    print(f"Saved: {p.name}")

def make_rule_card(out_name: str, rule_num: str, rule_title: str, formula: str, explanation: str, color=EMERALD):
    im = Image.new("RGB", (W, H), BG_LIGHT)
    draw = ImageDraw.Draw(im)
    draw_studio_base(draw, "THE JAPANESE DEVELOPMENTAL PLAYBOOK", color)
    
    f_rnum = get_font(72, bold=True)
    draw.text((220, 480), rule_num, fill=color, font=f_rnum)
    
    f_rtitle = get_font(110, bold=True)
    draw.text((220, 580), rule_title, fill=NAVY_CHARCOAL, font=f_rtitle)
    
    # Formula Box
    draw.rounded_rectangle([(220, 800), (W - 220, 1100)], radius=20, fill=WHITE, outline=BORDER, width=4)
    f_form = get_font(68, bold=True)
    draw.text((280, 900), formula, fill=color, font=f_form)
    
    # Explanation
    f_exp = get_font(54, bold=False)
    draw.text((220, 1260), explanation, fill=MUTED_GREY, font=f_exp)
    
    p = CARDS_DIR / f"{out_name}.png"
    im.save(p, quality=95)
    print(f"Saved: {p.name}")

def main():
    print("Generating 4K White Studio Graphic Cards...")
    
    # Title & Prologue
    make_act_card("card_00_title", "SPECIAL INVESTIGATION", "THE 4D ECONOMIC POWER", "Japan · Bangladesh · The $2.8 Trillion Convergence", ROYAL_BLUE)
    make_kinetic_metric_card("card_04_zero_resources", "HISTORICAL ANOMALY", "HOW DID JAPAN CONQUER GLOBAL MARKETS?", "0%", "NATURAL RESOURCES", "100%", "STRUCTURAL CAPABILITY", "Postwar Japan possessed zero oil, iron ore, or bauxite — yet built the world's 2nd largest GDP.", ROYAL_BLUE)
    
    # Act I
    make_act_card("card_06_act1", "ACT I", "THE 2026 PRECIPICE", "LDC Graduation & The Death of Cheap Labor Preferences", CRIMSON)
    make_kinetic_metric_card("card_08_gdp_garments", "STRUCTURAL CONCENTRATION", "THE SINGLE-ENGINE VULNERABILITY", "$505B", "TOTAL NOMINAL GDP (2026)", "84%", "EXPORT REVENUE IN GARMENTS", "A $500B sovereign economy relying entirely on cotton textiles to survive.", CRIMSON)
    make_kinetic_metric_card("card_10_tariff_cliff", "POLICY PRECIPICE", "UN LDC GRADUATION: THE IMMEDIATE HIT", "+8% to +12%", "IMMEDIATE TARIFF INCREASE", "0.0%", "DUTY-FREE PREFERENCES REMAINING", "European Everything-But-Arms duty-free access expires automatically upon graduation.", CRIMSON)
    make_kinetic_metric_card("card_12_tax_inertia", "SOVEREIGN BUFFER COLLAPSE", "FISCAL REVENUE IMMOBILITY", "7.6%", "TAX-TO-GDP RATIO", "< 8.0%", "DEVELOPING WORLD AVERAGE", "The state lacks sovereign tax capital to buffer industrial modernization or credit shocks.", CRIMSON)
    
    # Act II
    make_act_card("card_13_act2", "ACT II", "THE 87% FAILURE RATE", "Why 88 Out of 101 Middle-Income Nations Got Trapped", AMBER)
    make_kinetic_metric_card("card_14_88_trapped", "WORLD BANK 1960-2008 COHORT", "THE MIDDLE-INCOME TRAP IS THE STATISTICAL NORM", "88", "NATIONS FAILED & GOT TRAPPED", "13", "NATIONS ESCAPED TO HIGH-INCOME", "Out of 101 middle-income economies in 1960, only 13 reached high-income status.", AMBER)
    make_kinetic_metric_card("card_18_cheap_labor_ceiling", "STRUCTURAL DIAGNOSIS", "THE PER CAPITA GLASS CEILING", "$2,000", "CHEAP LABOR CEILING (GARMENTS)", "$12,000+", "HIGH-INCOME COMPLEXITY THRESHOLD", "Cheap wages can lift people to low-middle income. After that, rising wages crush factor margins.", AMBER)
    
    # Act III
    make_act_card("card_19_act3", "ACT III", "THE JAPANESE PLAYBOOK", "The 3 Uncompromising Rules of Postwar MITI", EMERALD)
    make_rule_card("card_21_miti_rule1", "RULE 01", "SEQUENCED INDUSTRIAL TARGETING", "TEXTILES (1950s) -> STEEL (1960s) -> AUTOS (1970s) -> CHIPS (1980s)", "Never leap blindly into high-tech. Use basic exports to capitalize heavy steel and ships first.", EMERALD)
    make_rule_card("card_22_miti_rule2", "RULE 02", "BRUTAL EXPORT DISCIPLINE", "CREDIT ALLOCATION = GLOBAL EXPORT PERFORMANCE", "Subsidies were never political handouts. Fail in global markets, and state credit was cut off.", EMERALD)
    make_rule_card("card_23_miti_rule3", "RULE 03", "DOMESTIC CAPITAL FUNNEL", "POSTAL SAVINGS SYSTEM -> INFRASTRUCTURE & INDUSTRY", "Citizen savings mobilized directly into sovereign industrial banks without accumulating foreign dollar debt.", EMERALD)
    
    # Act IV
    make_act_card("card_24_act4", "ACT IV", "THE CLOSING WINDOW", "Demographic Countdown: The Race Against 2038", CRIMSON)
    make_kinetic_metric_card("card_27_demographic_peak", "DEMOGRAPHIC INFLECTION", "THE UNFORGIVING CLOCK", "2038", "DEMOGRAPHIC DIVIDEND ENDS", "12 YRS", "REMAINING WINDOW TO REFORM", "Bangladesh must reach escape velocity before the dependency ratio rises. Get rich before getting old.", CRIMSON)
    
    # Act V
    make_act_card("card_29_act5", "ACT V", "THE $2.8 TRILLION BLUEPRINT", "Matarbari, Structural Complexity & The 2046 Horizon", ROYAL_BLUE)
    make_kinetic_metric_card("card_32_matarbari_stats", "MARITIME LOGISTICS REVOLUTION", "MATARBARI DEEP SEA PORT", "18.5m", "DRAFT (MOTHER VESSEL CAPACITY)", "-30%", "SHIPPING TIME TO EU / US", "Deep draft container vessels can dock directly, bypassing feeder ports in Singapore and Colombo.", ROYAL_BLUE)
    make_kinetic_metric_card("card_35_dividend_stats", "20-YEAR MACROECONOMIC DIVIDEND", "THE 2026-2046 REFORM PAYOFF", "+$1.34T", "NOMINAL GDP REFORM DIVIDEND", "+$298B/yr", "ANNUAL DOMESTIC TAX BASE (2046)", "The difference between executing the Japanese playbook ($3.16T) versus middle-income inertia ($1.82T).", ROYAL_BLUE)
    
    # Outro
    make_act_card("card_36_outro", "THE VERDICT", "THE BLUEPRINT IS WRITTEN", "Subscribe to Izhaan Intellect for Deep Investigative Documentaries", ROYAL_BLUE)
    
    print("\nAll White Studio Graphic Cards generated successfully in outputs/white_cards/!")

if __name__ == "__main__":
    main()
