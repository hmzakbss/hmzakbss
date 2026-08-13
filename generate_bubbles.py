import os
import math
import requests
from xml.sax.saxutils import escape

USERNAME = "hmzakbss"
TOKEN = os.getenv("GH_TOKEN")

API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
} if TOKEN else {
    "Accept": "application/vnd.github+json"
}

MAX_LANGUAGES = 14

# GitHub Linguist renklerine yakın resmi dil renkleri
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
}

# Bubble yerleşimi
POSITIONS = [
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


def get_language_stats():
    print("Repository'ler taranıyor...")

    repos_url = (
        f"{API}/users/{USERNAME}/repos"
        "?per_page=100&type=owner&sort=updated"
    )

    response = requests.get(
        repos_url,
        headers=HEADERS,
        timeout=30
    )
    response.raise_for_status()

    repos = response.json()

    languages = {}

    for repo in repos:
        if repo.get("fork"):
            continue

        languages_url = repo.get("languages_url")

        if not languages_url:
            continue

        response = requests.get(
            languages_url,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code != 200:
            continue

        repo_languages = response.json()

        for language, byte_count in repo_languages.items():
            languages[language] = (
                languages.get(language, 0) + byte_count
            )

    return languages


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def text_color_for_background(hex_color):
    r, g, b = hex_to_rgb(hex_color)

    luminance = (
        0.299 * r +
        0.587 * g +
        0.114 * b
    )

    return "#111827" if luminance > 175 else "#FFFFFF"


def calculate_percentages(languages):
    total = sum(languages.values())

    if total == 0:
        return {}

    return {
        language: (value / total) * 100
        for language, value in languages.items()
    }


def calculate_radii(values):
    """
    Bubble alanlarını yüzdeye göre ölçekler.
    Çok küçük dillerin tamamen kaybolmasını engeller.
    """

    max_value = max(values)

    radii = []

    for value in values:
        normalized = math.sqrt(value / max_value)

        radius = 45 + normalized * 95

        radii.append(radius)

    return radii


def create_svg(languages):
    if not languages:
        print("Dil verisi bulunamadı.")
        return

    percentages = calculate_percentages(languages)

    sorted_languages = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True
    )[:MAX_LANGUAGES]

    labels = [item[0] for item in sorted_languages]
    values = [item[1] for item in sorted_languages]

    radii = calculate_radii(values)

    width = 1150
    height = 700

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )

    # Arka plan
    svg.append("""
    <defs>

        <linearGradient id="background"
                        x1="0"
                        y1="0"
                        x2="1"
                        y2="1">

            <stop offset="0%" stop-color="#0B1220"/>
            <stop offset="100%" stop-color="#111827"/>

        </linearGradient>

        <filter id="shadow"
                x="-50%"
                y="-50%"
                width="200%"
                height="200%">

            <feDropShadow
                dx="0"
                dy="12"
                stdDeviation="12"
                flood-color="#000000"
                flood-opacity="0.30"/>

        </filter>

        <filter id="softShadow"
                x="-50%"
                y="-50%"
                width="200%"
                height="200%">

            <feDropShadow
                dx="0"
                dy="6"
                stdDeviation="7"
                flood-color="#000000"
                flood-opacity="0.25"/>

        </filter>

    </defs>
    """)

    svg.append("""
    <rect
        x="0"
        y="0"
        width="1150"
        height="700"
        rx="28"
        fill="url(#background)"
    />
    """)

    # Üst başlık
    svg.append("""
    <text
        x="575"
        y="58"
        text-anchor="middle"
        font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
        font-size="18"
        font-weight="700"
        letter-spacing="4"
        fill="#94A3B8">
        LANGUAGES I WORK WITH
    </text>
    """)

    # İnce ayraç
    svg.append("""
    <line
        x1="430"
        y1="82"
        x2="720"
        y2="82"
        stroke="#334155"
        stroke-width="2"
        stroke-linecap="round"
    />
    """)

    for index, (language, percentage) in enumerate(sorted_languages):

        x, y = POSITIONS[index]
        radius = radii[index]

        color = LANGUAGE_COLORS.get(
            language,
            "#64748B"
        )

        text_color = text_color_for_background(color)

        # Büyük bubble
        shadow = "shadow" if radius > 100 else "softShadow"

        svg.append(
            f"""
            <circle
                cx="{x}"
                cy="{y}"
                r="{radius}"
                fill="{color}"
                opacity="0.96"
                filter="url(#{shadow})"
            />
            """
        )

        # İç highlight
        svg.append(
            f"""
            <circle
                cx="{x - radius * 0.28}"
                cy="{y - radius * 0.28}"
                r="{radius * 0.14}"
                fill="#FFFFFF"
                opacity="0.10"
            />
            """
        )

        # Büyük bubble için font
        if radius >= 100:
            language_size = 24
            percentage_size = 17

        elif radius >= 75:
            language_size = 18
            percentage_size = 14

        else:
            language_size = 14
            percentage_size = 12

        safe_language = escape(language)

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
                y="{y + percentage_size + 4}"
                text-anchor="middle"
                font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
                font-size="{percentage_size}"
                font-weight="500"
                fill="{text_color}"
                opacity="0.85">
                {percentage:.1f}%
            </text>
            """
        )

    # Alt bilgi
    svg.append("""
    <text
        x="575"
        y="670"
        text-anchor="middle"
        font-family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
        font-size="12"
        font-weight="500"
        fill="#64748B">
        Based on non-forked public repositories
    </text>
    """)

    svg.append("</svg>")

    with open(
        "languages_bubble.svg",
        "w",
        encoding="utf-8"
    ) as file:

        file.write("\n".join(svg))

    print("languages_bubble.svg başarıyla oluşturuldu!")


if __name__ == "__main__":
    languages = get_language_stats()
    create_svg(languages)
