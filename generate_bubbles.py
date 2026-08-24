import os
import math
import requests

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from xml.sax.saxutils import escape


# ============================================================
# CONFIG
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


# ============================================================
# LANGUAGE SETTINGS
# ============================================================

MAX_LANGUAGES = 10


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
    "PowerShell": "#012456",
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
# HIGH RESOLUTION GIF
# ============================================================

# 2x retina resolution
WIDTH = 1800
HEIGHT = 1040

# README'de 900px gösterilecek
DISPLAY_WIDTH = 900

FPS = 8

DURATION_SECONDS = 6

FRAME_COUNT = FPS * DURATION_SECONDS


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
# GITHUB API
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

            # Forkları atla
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

            for language, bytes_count in (
                repo_languages.items()
            ):

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
            f"{language:<20}"
            f"{bytes_count:,} bytes"
        )

    print(
        "====================================\n"
    )

    return languages


# ============================================================
# CALCULATIONS
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

    if not values:

        return []

    max_value = max(values)

    radii = []

    for value in values:

        normalized = math.sqrt(
            value / max_value
        )

        # Daha kontrollü bubble boyutları
        radius = (
            82 +
            normalized * 105
        )

        radii.append(radius)

    return radii


# ============================================================
# COLORS
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
    ]

    svg = []

    svg.append(
        f"""
<svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 {width} {height}"
    width="{width}"
    height="{height}">

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
    x="-40%"
    y="-40%"
    width="180%"
    height="180%">

    <feDropShadow
        dx="0"
        dy="8"
        stdDeviation="9"
        flood-color="#000000"
        flood-opacity=".35"/>

</filter>

</defs>

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

<text
    x="575"
    y="53"
    text-anchor="middle"
    font-family="Inter, Arial, sans-serif"
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

        foreground = (
            text_color_for_background(
                color
            )
        )

        svg.append(
            f"""
<circle
    cx="{x}"
    cy="{y}"
    r="{radius}"
    fill="{color}"
    filter="url(#shadow)"
/>
"""
        )

        if radius >= 160:

            language_size = 23
            percentage_size = 15

        elif radius >= 120:

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
    font-family="Inter, Arial, sans-serif"
    font-size="{language_size}"
    font-weight="700"
    fill="{foreground}">

{safe_language}

</text>

<text
    x="{x}"
    y="{y + percentage_size + 5}"
    text-anchor="middle"
    font-family="Inter, Arial, sans-serif"
    font-size="{percentage_size}"
    fill="{foreground}"
    opacity=".85">

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
    font-family="Inter, Arial, sans-serif"
    font-size="11"
    fill="#64748B">

Based on public + private non-forked repositories

</text>

</svg>
"""
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
# BACKGROUND
# ============================================================

def create_background():

    image = Image.new(
        "RGBA",
        (
            WIDTH,
            HEIGHT
        ),
        (
            7,
            10,
            17,
            255
        )
    )

    draw = ImageDraw.Draw(
        image
    )

    # Çok daha kontrollü merkez glow
    for radius in range(
        360,
        30,
        -15
    ):

        strength = (
            1 -
            radius / 360
        )

        alpha = int(
            7 * strength
        )

        draw.ellipse(
            (
                WIDTH / 2 - radius,
                HEIGHT / 2 - radius,
                WIDTH / 2 + radius,
                HEIGHT / 2 + radius
            ),
            fill=(
                35,
                75,
                125,
                alpha
            )
        )

    return image


# ============================================================
# TEXT
# ============================================================

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

    width = (
        bbox[2] -
        bbox[0]
    )

    height = (
        bbox[3] -
        bbox[1]
    )

    draw.text(
        (
            position[0] -
            width / 2,

            position[1] -
            height / 2
        ),
        text,
        font=font,
        fill=fill
    )


# ============================================================
# BUBBLE
# ============================================================

def draw_bubble(
    image,
    x,
    y,
    radius,
    color
):

    rgb = hex_to_rgb(
        color
    )

    # -----------------------------------------
    # Very subtle glow
    # -----------------------------------------

    glow = Image.new(
        "RGBA",
        image.size,
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(
        glow
    )

    glow_radius = (
        radius * 1.10
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
            22
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            10
        )
    )

    image.alpha_composite(
        glow
    )

    draw = ImageDraw.Draw(
        image
    )

    # -----------------------------------------
    # Shadow
    # -----------------------------------------

    draw.ellipse(
        (
            x - radius + 4,
            y - radius + 10,
            x + radius + 4,
            y + radius + 10
        ),
        fill=(
            0,
            0,
            0,
            70
        )
    )

    # -----------------------------------------
    # Bubble
    # -----------------------------------------

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
            250
        ),
        outline=(
            255,
            255,
            255,
            60
        ),
        width=3
    )

    # -----------------------------------------
    # Small highlight
    # -----------------------------------------

    highlight = (
        radius * .12
    )

    draw.ellipse(
        (
            x - radius * .42,
            y - radius * .48,
            x - radius * .42 + highlight,
            y - radius * .48 + highlight
        ),
        fill=(
            255,
            255,
            255,
            30
        )
    )


# ============================================================
# ANIMATED GIF
# ============================================================

def create_animated_gif(
    languages
):

    if not languages:

        print(
            "GIF oluşturulamadı."
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

    # -----------------------------------------
    # Orbit configuration
    # -----------------------------------------

    center_x = WIDTH // 2
    center_y = 530

    OUTER_RX = 470
    OUTER_RY = 290

    INNER_RX = 350
    INNER_RY = 220

    # -----------------------------------------
    # Fonts - 2x retina
    # -----------------------------------------

    fonts = {

        "title":
            get_font(
                24,
                bold=True
            ),

        "large":
            get_font(
                36,
                bold=True
            ),

        "medium":
            get_font(
                26,
                bold=True
            ),

        "small":
            get_font(
                21,
                bold=True
            ),

        "percentage":
            get_font(
                20,
                bold=False
            ),

        "footer":
            get_font(
                18,
                bold=False
            ),
    }

    frames = []

    # ========================================================
    # ANIMATION
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
        # PARTICLES
        # ====================================================

        for particle in range(
            55
        ):

            x = (
                particle * 137 +
                41
            ) % WIDTH

            y = (
                particle * 83 +
                37
            ) % HEIGHT

            twinkle = (
                math.sin(
                    progress *
                    math.tau *
                    1.2 +
                    particle
                ) + 1
            ) / 2

            alpha = int(
                35 +
                55 * twinkle
            )

            draw.ellipse(
                (
                    x,
                    y,
                    x + 3,
                    y + 3
                ),
                fill=(
                    190,
                    210,
                    235,
                    alpha
                )
            )

        # ====================================================
        # TITLE
        # ====================================================

        draw_centered_text(
            draw,
            (
                WIDTH / 2,
                70
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
                670,
                110,
                1130,
                110
            ),
            fill=(
                51,
                65,
                85,
                255
            ),
            width=2
        )

        # ====================================================
        # ORBITS
        # ====================================================

        draw.ellipse(
            (
                center_x - OUTER_RX,
                center_y - OUTER_RY,
                center_x + OUTER_RX,
                center_y + OUTER_RY
            ),
            outline=(
                100,
                130,
                170,
                55
            ),
            width=2
        )

        draw.ellipse(
            (
                center_x - INNER_RX,
                center_y - INNER_RY,
                center_x + INNER_RX,
                center_y + INNER_RY
            ),
            outline=(
                100,
                130,
                170,
                38
            ),
            width=2
        )

        # ====================================================
        # ORBITING LANGUAGES
        # ====================================================

        orbit_languages = (
            sorted_languages[1:]
        )

        count = len(
            orbit_languages
        )

        for index, (
            language,
            percentage
        ) in enumerate(
            orbit_languages
        ):

            if index >= len(
                radii
            ) - 1:

                break

            color = LANGUAGE_COLORS.get(
                language,
                "#64748B"
            )

            # First 3 languages
            # outer orbit
            if index < 3:

                orbit_x = OUTER_RX
                orbit_y = OUTER_RY

            else:

                orbit_x = INNER_RX
                orbit_y = INNER_RY

            # Evenly distribute
            base_angle = (
                math.tau *
                index /
                max(
                    count,
                    1
                )
            )

            # Slow orbital motion
            speed = (
                0.035
                if index % 2 == 0
                else -0.035
            )

            angle = (
                base_angle +
                progress *
                math.tau *
                speed
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

            radius = (
                radii[index + 1]
            )

            # Very subtle pulse
            pulse = (
                1 +
                0.018 *
                math.sin(
                    progress *
                    math.tau +
                    index
                )
            )

            radius *= pulse

            draw_bubble(
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

            draw = ImageDraw.Draw(
                image
            )

            if radius >= 150:

                language_font = (
                    fonts["large"]
                )

            elif radius >= 110:

                language_font = (
                    fonts["medium"]
                )

            else:

                language_font = (
                    fonts["small"]
                )

            draw_centered_text(
                draw,
                (
                    x,
                    y - 8
                ),
                language,
                language_font,
                foreground
            )

            draw_centered_text(
                draw,
                (
                    x,
                    y + 35
                ),
                f"{percentage:.1f}%",
                fonts["percentage"],
                foreground
            )

        # ====================================================
        # CENTER BUBBLE
        # ====================================================

        center_name = (
            sorted_languages[0][0]
        )

        center_percentage = (
            sorted_languages[0][1]
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

        # Small pulse
        center_radius *= (
            1 +
            0.015 *
            math.sin(
                progress *
                math.tau
            )
        )

        draw_bubble(
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
                center_y - 12
            ),
            center_name,
            fonts["large"],
            "#FFFFFF"
        )

        draw_centered_text(
            draw,
            (
                center_x,
                center_y + 45
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
                WIDTH / 2,
                HEIGHT - 42
            ),
            "Based on public + private non-forked repositories",
            fonts["footer"],
            (
                100,
                116,
                139
            )
        )

        # ====================================================
        # STORE FRAME
        # ====================================================

        frames.append(
            image.convert(
                "RGB"
            )
        )

    # ========================================================
    # GIF PALETTE
    # ========================================================

    print(
        "GIF frame'leri optimize ediliyor..."
    )

    optimized_frames = []

    for frame in frames:

        palette_frame = (
            frame.quantize(
                colors=256,
                method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.FLOYDSTEINBERG
            )
        )

        optimized_frames.append(
            palette_frame
        )

    # ========================================================
    # SAVE
    # ========================================================

    output = (
        "languages_bubble.gif"
    )

    optimized_frames[0].save(
        output,
        save_all=True,
        append_images=optimized_frames[1:],
        duration=int(
            1000 / FPS
        ),
        loop=0,
        optimize=True,
        disposal=2
    )

    file_size = (
        os.path.getsize(
            output
        ) / (1024 * 1024)
    )

    print(
        f"\n{output} oluşturuldu."
    )

    print(
        f"GIF boyutu: "
        f"{file_size:.2f} MB"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    languages = (
        get_language_stats()
    )

    create_svg(
        languages
    )

    create_animated_gif(
        languages
    )
