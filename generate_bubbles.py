import os
import math
import requests

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from xml.sax.saxutils import escape


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "hmzakbss"

TOKEN = os.getenv("GH_TOKEN")

API = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
} if TOKEN else {
    "Accept": "application/vnd.github+json"
}


# Kaç farklı dil gösterilecek?
MAX_LANGUAGES = 14


# GIF ayarları
GIF_WIDTH = 900
GIF_HEIGHT = 520

FPS = 12

# 6 saniyelik animasyon
DURATION_SECONDS = 6

FRAME_COUNT = FPS * DURATION_SECONDS


# ============================================================
# LANGUAGE COLORS
# ============================================================

LANGUAGE_COLORS = {

    "Python": "#3776AB",

    "JavaScript": "#F7DF1E",

    "TypeScript": "#3178C6",

    "C#": "#239120",

    "C++": "#00599C",

    "C": "#A8B9CC",

    "Java": "#B07219",

    "Dart": "#00B4AB",

    "HTML": "#E34F26",

    "CSS": "#1572B6",

    "SQL": "#336791",

    "Shell": "#89E051",

    "Jupyter Notebook": "#DA5B0B",

    "Kotlin": "#A97BFF",

    "Go": "#00ADD8",

    "Rust": "#DEA584",

    "PHP": "#777BB4",

    "Ruby": "#701516",

    "Swift": "#F05138",

    "R": "#198CE7",

    "PLpgSQL": "#64748B",
}


# ============================================================
# FONT
# ============================================================

def get_font(size, bold=False):

    if bold:

        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        ]

    else:

        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        ]

    for path in paths:

        if os.path.exists(path):

            return ImageFont.truetype(
                path,
                size
            )

    return ImageFont.load_default()


# ============================================================
# GITHUB DATA
# ============================================================

def get_language_stats():

    print(
        "Public + private repository'ler taranıyor..."
    )

    languages = {}

    page = 1

    while True:

        repos_url = (
            f"{API}/user/repos"
            f"?per_page=100"
            f"&page={page}"
            f"&affiliation=owner"
            f"&visibility=all"
            f"&sort=updated"
        )

        response = requests.get(
            repos_url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        repos = response.json()

        if not repos:

            break

        print(
            f"\nSayfa {page}: "
            f"{len(repos)} repository bulundu."
        )

        for repo in repos:

            repo_name = repo.get(
                "name",
                "Unknown"
            )

            # Forkları dahil etme
            if repo.get("fork"):

                print(
                    f"  ↳ Fork atlandı: "
                    f"{repo_name}"
                )

                continue

            visibility = (
                "PRIVATE"
                if repo.get("private")
                else "PUBLIC"
            )

            print(
                f"  → Taranıyor: "
                f"{repo_name} "
                f"[{visibility}]"
            )

            languages_url = repo.get(
                "languages_url"
            )

            if not languages_url:

                continue

            language_response = requests.get(
                languages_url,
                headers=HEADERS,
                timeout=30
            )

            if language_response.status_code != 200:

                print(
                    f"    ⚠ Dil bilgisi alınamadı: "
                    f"{repo_name} "
                    f"(HTTP "
                    f"{language_response.status_code})"
                )

                continue

            repo_languages = (
                language_response.json()
            )

            for language, bytes_count in repo_languages.items():

                languages[language] = (
                    languages.get(language, 0)
                    + bytes_count
                )

        page += 1

    print(
        "\n========== LANGUAGE TOTALS =========="
    )

    for language, bytes_count in sorted(
        languages.items(),
        key=lambda item: item[1],
        reverse=True
    ):

        print(
            f"{language:<20} "
            f"{bytes_count:,} bytes"
        )

    print(
        "====================================\n"
    )

    return languages


# ============================================================
# LANGUAGE CALCULATIONS
# ============================================================

def calculate_percentages(languages):

    total = sum(
        languages.values()
    )

    if total == 0:

        return {}

    return {
        language:
        (value / total) * 100

        for language, value
        in languages.items()
    }


def calculate_radii(values):

    max_value = max(values)

    radii = []

    for value in values:

        normalized = math.sqrt(
            value / max_value
        )

        radius = (
            42 +
            normalized * 92
        )

        radii.append(radius)

    return radii


# ============================================================
# COLOR HELPERS
# ============================================================

def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(
            hex_color[i:i + 2],
            16
        )

        for i in (0, 2, 4)
    )


def text_color_for_background(
    hex_color
):

    r, g, b = hex_to_rgb(
        hex_color
    )

    luminance = (
        0.299 * r +
        0.587 * g +
        0.114 * b
    )

    if luminance > 175:

        return "#111827"

    return "#FFFFFF"


# ============================================================
# STATIC SVG
# ============================================================

def create_svg(languages):

    if not languages:

        print(
            "SVG oluşturulamadı: "
            "dil verisi yok."
        )

        return

    percentages = (
        calculate_percentages(
            languages
        )
    )

    sorted_languages = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True
    )[:MAX_LANGUAGES]

    values = [
        item[1]
        for item in sorted_languages
    ]

    radii = calculate_radii(
        values
    )

    width = 1150
    height = 700

    positions = [
        (500, 280),
        (730, 235),
        (300, 225),
        (700, 470),
        (380, 465),
        (875, 390),
        (165, 390),
        (535, 535),
        (825, 570),
        (255, 575),
        (1000, 260),
        (85, 245),
        (1030, 535),
        (110, 545),
    ]

    svg = []

    svg.append(
        f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 {width} {height}"
    width="{width}"
    height="{height}">
'''
    )

    svg.append(
        """
<defs>

    <linearGradient
        id="background"
        x1="0"
        y1="0"
        x2="1"
        y2="1">

        <stop
            offset="0%"
            stop-color="#080B12"/>

        <stop
            offset="55%"
            stop-color="#0D111A"/>

        <stop
            offset="100%"
            stop-color="#111827"/>

    </linearGradient>

    <filter
        id="shadow"
        x="-60%"
        y="-60%"
        width="220%"
        height="220%">

        <feDropShadow
            dx="0"
            dy="12"
            stdDeviation="15"
            flood-color="#000000"
            flood-opacity=".42"/>

    </filter>

    <filter
        id="softShadow"
        x="-60%"
        y="-60%"
        width="220%"
        height="220%">

        <feDropShadow
            dx="0"
            dy="7"
            stdDeviation="9"
            flood-color="#000000"
            flood-opacity=".35"/>

    </filter>

</defs>
"""
    )

    svg.append(
        """
<rect
    width="1150"
    height="700"
    rx="30"
    fill="url(#background)"
/>

<rect
    x="1"
    y="1"
    width="1148"
    height="698"
    rx="29"
    fill="none"
    stroke="#FFFFFF"
    stroke-opacity=".08"
/>
"""
    )

    svg.append(
        """
<text
    x="575"
    y="53"
    text-anchor="middle"
    font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    font-size="12"
    font-weight="700"
    letter-spacing="4"
    fill="#94A3B8">

    LANGUAGES I WORK WITH

</text>

<line
    x1="475"
    y1="72"
    x2="675"
    y2="72"
    stroke="#FFFFFF"
    stroke-opacity=".10"
    stroke-linecap="round"
/>
"""
    )

    for index, (
        language,
        percentage
    ) in enumerate(
        sorted_languages
    ):

        x, y = positions[index]

        radius = radii[index]

        color = LANGUAGE_COLORS.get(
            language,
            "#64748B"
        )

        text_color = (
            text_color_for_background(
                color
            )
        )

        shadow = (
            "shadow"
            if radius >= 100
            else "softShadow"
        )

        svg.append(
            f"""
<circle
    cx="{x}"
    cy="{y}"
    r="{radius}"
    fill="{color}"
    opacity=".94"
    filter="url(#{shadow})"
/>
"""
        )

        svg.append(
            f"""
<circle
    cx="{x - radius * .28}"
    cy="{y - radius * .30}"
    r="{radius * .12}"
    fill="#FFFFFF"
    opacity=".10"
/>
"""
        )

        if radius >= 100:

            language_size = 25
            percentage_size = 16

        elif radius >= 75:

            language_size = 18
            percentage_size = 14

        else:

            language_size = 13
            percentage_size = 11

        safe_language = escape(
            language
        )

        svg.append(
            f"""
<text
    x="{x}"
    y="{y - 5}"
    text-anchor="middle"
    font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    font-size="{language_size}"
    font-weight="700"
    fill="{text_color}">

    {safe_language}

</text>
"""
        )

        svg.append(
            f"""
<text
    x="{x}"
    y="{y + percentage_size + 5}"
    text-anchor="middle"
    font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    font-size="{percentage_size}"
    font-weight="500"
    fill="{text_color}"
    opacity=".82">

    {percentage:.1f}%

</text>
"""
        )

    svg.append(
        """
<text
    x="575"
    y="650"
    text-anchor="middle"
    font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    font-size="11"
    font-weight="500"
    fill="#64748B">

    Based on public + private non-forked repositories

</text>
"""
    )

    svg.append(
        "</svg>"
    )

    with open(
        "languages_bubble.svg",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(svg)
        )

    print(
        "languages_bubble.svg oluşturuldu."
    )


# ============================================================
# ANIMATED GIF
# ============================================================

def create_background():

    image = Image.new(
        "RGBA",
        (
            GIF_WIDTH,
            GIF_HEIGHT
        ),
        (8, 11, 18, 255)
    )

    draw = ImageDraw.Draw(
        image
    )

    # Ortadaki hafif mavi glow
    for radius in range(
        300,
        0,
        -8
    ):

        alpha = int(
            20 *
            (1 - radius / 300)
        )

        draw.ellipse(
            (
                GIF_WIDTH / 2 - radius,
                GIF_HEIGHT / 2 - radius,
                GIF_WIDTH / 2 + radius,
                GIF_HEIGHT / 2 + radius
            ),
            fill=(
                50,
                90,
                150,
                alpha
            )
        )

    return image


def draw_centered_text(
    draw,
    position,
    text,
    font,
    fill
):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    draw.text(
        (
            position[0] -
            text_width / 2,

            position[1] -
            text_height / 2
        ),
        text,
        font=font,
        fill=fill
    )


def draw_glowing_bubble(
    image,
    x,
    y,
    radius,
    color
):

    rgb = hex_to_rgb(
        color
    )

    # Glow layer
    glow_layer = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(
        glow_layer
    )

    glow_radius = (
        radius * 1.35
    )

    glow_draw.ellipse(
        (
            x - glow_radius,
            y - glow_radius,
            x + glow_radius,
            y + glow_radius
        ),
        fill=(
            rgb[0],
            rgb[1],
            rgb[2],
            35
        )
    )

    glow_layer = (
        glow_layer.filter(
            ImageFilter.GaussianBlur(
                16
            )
        )
    )

    image.alpha_composite(
        glow_layer
    )

    draw = ImageDraw.Draw(
        image
    )

    # Shadow
    shadow_offset = 8

    draw.ellipse(
        (
            x - radius + 3,
            y - radius + shadow_offset,
            x + radius + 3,
            y + radius + shadow_offset
        ),
        fill=(
            0,
            0,
            0,
            65
        )
    )

    # Bubble
    draw.ellipse(
        (
            x - radius,
            y - radius,
            x + radius,
            y + radius
        ),
        fill=(
            rgb[0],
            rgb[1],
            rgb[2],
            245
        ),
        outline=(
            255,
            255,
            255,
            45
        ),
        width=2
    )

    # Highlight
    highlight_radius = max(
        5,
        radius * .12
    )

    draw.ellipse(
        (
            x - radius * .45,
            y - radius * .50,
            x - radius * .20,
            y - radius * .25
        ),
        fill=(
            255,
            255,
            255,
            30
        )
    )


def create_animated_gif(
    languages
):

    if not languages:

        print(
            "GIF oluşturulamadı: "
            "dil verisi yok."
        )

        return

    percentages = (
        calculate_percentages(
            languages
        )
    )

    sorted_languages = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True
    )[:MAX_LANGUAGES]

    values = [
        item[1]
        for item in sorted_languages
    ]

    radii = calculate_radii(
        values
    )

    # GIF için ekran pozisyonları
    positions = [
        (450, 265),
        (650, 205),
        (260, 200),
        (650, 375),
        (295, 385),
        (765, 290),
        (135, 315),
        (490, 410),
        (820, 420),
        (205, 465),
        (760, 115),
        (130, 125),
        (830, 175),
        (80, 420),
    ]

    fonts = {
        "large": get_font(
            18,
            bold=True
        ),

        "medium": get_font(
            13,
            bold=True
        ),

        "small": get_font(
            10,
            bold=True
        ),

        "percentage": get_font(
            10,
            bold=False
        ),

        "title": get_font(
            12,
            bold=True
        ),

        "footer": get_font(
            9,
            bold=False
        ),
    }

    frames = []

    # ========================================================
    # FRAME LOOP
    # ========================================================

    for frame_number in range(
        FRAME_COUNT
    ):

        progress = (
            frame_number /
            FRAME_COUNT
        )

        image = (
            create_background()
        )

        draw = ImageDraw.Draw(
            image
        )

        # ====================================================
        # STARS / PARTICLES
        # ====================================================

        for star in range(45):

            star_x = (
                star * 137 + 23
            ) % GIF_WIDTH

            star_y = (
                star * 83 + 31
            ) % GIF_HEIGHT

            twinkle = (
                math.sin(
                    progress *
                    math.tau *
                    1.4 +
                    star
                ) + 1
            ) / 2

            alpha = int(
                45 +
                80 * twinkle
            )

            draw.ellipse(
                (
                    star_x,
                    star_y,
                    star_x + 2,
                    star_y + 2
                ),
                fill=(
                    180,
                    205,
                    235,
                    alpha
                )
            )

        # ====================================================
        # HEADER
        # ====================================================

        draw_centered_text(
            draw,
            (
                GIF_WIDTH / 2,
                36
            ),
            "LANGUAGES I WORK WITH",
            fonts["title"],
            (
                148,
                163,
                184
            )
        )

        draw.line(
            (
                340,
                56,
                560,
                56
            ),
            fill=(
                51,
                65,
                85
            ),
            width=1
        )

        # ====================================================
        # ORBIT CENTER
        # ====================================================

        center_x = 450
        center_y = 265

        # Ana yörünge
        draw.ellipse(
            (
                center_x - 235,
                center_y - 145,
                center_x + 235,
                center_y + 145
            ),
            outline=(
                100,
                130,
                170,
                45
            ),
            width=1
        )

        # İç yörünge
        draw.ellipse(
            (
                center_x - 175,
                center_y - 110,
                center_x + 175,
                center_y + 110
            ),
            outline=(
                100,
                130,
                170,
                32
            ),
            width=1
        )

        # ====================================================
        # ORBITING LANGUAGES
        # ====================================================

        orbit_languages = (
            sorted_languages[1:]
        )

        for index, (
            language,
            percentage
        ) in enumerate(
            orbit_languages
        ):

            if index >= len(
                positions
            ) - 1:

                break

            color = (
                LANGUAGE_COLORS.get(
                    language,
                    "#64748B"
                )
            )

            # Dış ve iç yörüngeler
            if index < 3:

                orbit_x = 235
                orbit_y = 145

            else:

                orbit_x = 175
                orbit_y = 110

            # Her bubble farklı fazda
            angle = (
                math.tau *
                index /
                max(
                    1,
                    len(
                        orbit_languages
                    )
                )
            )

            rotation_speed = (
                0.18
                if index % 2 == 0
                else -0.18
            )

            angle += (
                progress *
                math.tau *
                rotation_speed
            )

            x = (
                center_x +
                math.cos(angle) *
                orbit_x
            )

            y = (
                center_y +
                math.sin(angle) *
                orbit_y
            )

            radius = radii[
                index + 1
            ]

            # Hafif pulse
            pulse = (
                1 +
                0.025 *
                math.sin(
                    progress *
                    math.tau +
                    index
                )
            )

            radius *= pulse

            draw_glowing_bubble(
                image,
                x,
                y,
                radius,
                color
            )

            foreground = (
                "#111827"
                if color == "#F7DF1E"
                else "#FFFFFF"
            )

            if radius >= 90:

                language_font = (
                    fonts["large"]
                )

            elif radius >= 65:

                language_font = (
                    fonts["medium"]
                )

            else:

                language_font = (
                    fonts["small"]
                )

            draw = ImageDraw.Draw(
                image
            )

            draw_centered_text(
                draw,
                (
                    x,
                    y - 5
                ),
                language,
                language_font,
                foreground
            )

            draw_centered_text(
                draw,
                (
                    x,
                    y + 14
                ),
                f"{percentage:.1f}%",
                fonts["percentage"],
                foreground
            )

        # ====================================================
        # CENTER BUBBLE
        # ====================================================

        center_language = (
            sorted_languages[0]
        )

        center_name = (
            center_language[0]
        )

        center_percentage = (
            center_language[1]
        )

        center_color = (
            LANGUAGE_COLORS.get(
                center_name,
                "#64748B"
            )
        )

        center_radius = (
            radii[0]
        )

        # Merkez pulse
        center_pulse = (
            1 +
            0.035 *
            math.sin(
                progress *
                math.tau
            )
        )

        center_radius *= (
            center_pulse
        )

        draw_glowing_bubble(
            image,
            center_x,
            center_y,
            center_radius,
            center_color
        )

        draw = ImageDraw.Draw(
            image
        )

        draw_centered_text(
            draw,
            (
                center_x,
                center_y - 8
            ),
            center_name,
            fonts["large"],
            "#FFFFFF"
        )

        draw_centered_text(
            draw,
            (
                center_x,
                center_y + 19
            ),
            f"{center_percentage:.1f}%",
            fonts["medium"],
            "#FFFFFF"
        )

        # ====================================================
        # FOOTER
        # ====================================================

        draw_centered_text(
            draw,
            (
                GIF_WIDTH / 2,
                GIF_HEIGHT - 22
            ),
            "Based on public + private non-forked repositories",
            fonts["footer"],
            (
                100,
                116,
                139
            )
        )

        frames.append(
            image.convert("RGB")
        )

    # ========================================================
    # SAVE GIF
    # ========================================================

    output = (
        "languages_bubble.gif"
    )

    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=int(
            1000 / FPS
        ),
        loop=0,
        optimize=True
    )

    print(
        f"{output} başarıyla oluşturuldu!"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    languages = (
        get_language_stats()
    )

    # Statik SVG'yi de üret
    create_svg(
        languages
    )

    # Animasyonlu GIF üret
    create_animated_gif(
        languages
    )
