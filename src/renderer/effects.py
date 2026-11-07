
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

WIDTH = 1080
HEIGHT = 1920

BACKGROUND_TOP = (14, 23, 43)
BACKGROUND_BOTTOM = (42, 29, 34)

GOLD = (238, 190, 116)
CREAM = (255, 246, 226)
MUTED = (190, 195, 205)

SHADOW = (10, 12, 22)

# Keep text comfortably inside the Reel safe area.
TEXT_MAX_WIDTH = int(WIDTH * 0.78)

BASE_DIR = Path(__file__).resolve().parents[2]
FONT_DIR = BASE_DIR / "assets" / "fonts"

REGULAR_FONT = FONT_DIR / "Silkscreen-Regular.ttf"
BOLD_FONT = FONT_DIR / "Silkscreen-Bold.ttf"


# --------------------------------------------------
# FONT UTILITIES
# --------------------------------------------------

def load_font(size: int, bold: bool = False):

    font_path = BOLD_FONT if bold else REGULAR_FONT

    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)

    raise FileNotFoundError(
        f"Font not found: {font_path}\n"
        "Check assets/fonts and verify the downloaded filenames."
    )


def measure_text(draw, text, font, spacing=18):

    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=font,
        spacing=spacing,
        align="center"
    )

    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# --------------------------------------------------
# AUTOMATIC TEXT WRAPPING
# --------------------------------------------------

def wrap_text(
    draw,
    text: str,
    font,
    max_width: int
):

    """
    Wrap text into balanced lines based on actual
    pixel width rather than character count.

    Existing manual line breaks are preserved.
    """

    final_lines = []

    paragraphs = text.split("\n")

    for paragraph in paragraphs:

        words = paragraph.split()

        if not words:
            final_lines.append("")
            continue

        current_line = ""

        for word in words:

            candidate = (
                f"{current_line} {word}".strip()
            )

            word_width = draw.textbbox(
                (0, 0),
                candidate,
                font=font
            )[2]

            if word_width <= max_width:

                current_line = candidate

            else:

                if current_line:
                    final_lines.append(current_line)

                # Handle unusually long individual words.
                if draw.textbbox(
                    (0, 0),
                    word,
                    font=font
                )[2] > max_width:

                    final_lines.append(word)
                    current_line = ""

                else:
                    current_line = word

        if current_line:
            final_lines.append(current_line)

    return "\n".join(final_lines)


def fit_text(
    draw,
    text: str,
    max_width: int,
    max_font_size: int,
    min_font_size: int,
    bold: bool = True,
    spacing: int = 22
):

    """
    Automatically finds the largest font size
    that fits inside the allowed text width.
    """

    for size in range(
        max_font_size,
        min_font_size - 1,
        -2
    ):

        font = load_font(size, bold)

        wrapped = wrap_text(
            draw,
            text,
            font,
            max_width
        )

        text_width, text_height = measure_text(
            draw,
            wrapped,
            font,
            spacing
        )

        if text_width <= max_width:

            return wrapped, font, text_height

    font = load_font(min_font_size, bold)

    wrapped = wrap_text(
        draw,
        text,
        font,
        max_width
    )

    _, text_height = measure_text(
        draw,
        wrapped,
        font,
        spacing
    )

    return wrapped, font, text_height


# --------------------------------------------------
# BACKGROUND
# --------------------------------------------------

def create_background():

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT)
    )

    draw = ImageDraw.Draw(image)

    for y in range(HEIGHT):

        ratio = y / HEIGHT

        color = tuple(
            int(
                BACKGROUND_TOP[i] * (1 - ratio)
                + BACKGROUND_BOTTOM[i] * ratio
            )
            for i in range(3)
        )

        draw.line(
            (0, y, WIDTH, y),
            fill=color
        )

    return image


def add_snow_details(image):

    draw = ImageDraw.Draw(
        image,
        "RGBA"
    )

    random.seed(42)

    for _ in range(150):

        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)

        radius = random.choice([1, 2, 3, 4])

        draw.ellipse(
            (
                x - radius,
                y - radius,
                x + radius,
                y + radius
            ),
            fill=(
                230,
                239,
                255,
                random.randint(70, 160)
            )
        )


# --------------------------------------------------
# TEXT DRAWING
# --------------------------------------------------

def draw_centered_text(
    draw,
    position,
    text,
    font,
    fill,
    spacing=20,
    shadow=True
):

    x, y = position

    if shadow:

        draw.multiline_text(
            (x + 3, y + 4),
            text,
            font=font,
            fill=SHADOW,
            anchor="mm",
            align="center",
            spacing=spacing
        )

    draw.multiline_text(
        position,
        text,
        font=font,
        fill=fill,
        anchor="mm",
        align="center",
        spacing=spacing
    )


def draw_adaptive_title(
    draw,
    text: str,
    center_y: int,
    max_font_size: int = 76,
    min_font_size: int = 42
):

    wrapped, font, text_height = fit_text(
        draw=draw,
        text=text,
        max_width=TEXT_MAX_WIDTH,
        max_font_size=max_font_size,
        min_font_size=min_font_size,
        bold=True,
        spacing=24
    )

    draw_centered_text(
        draw,
        (WIDTH // 2, center_y),
        wrapped,
        font,
        CREAM,
        spacing=24
    )

    print(
        f"Title rendered at {font.size}px "
        f"across {len(wrapped.splitlines())} lines."
    )

    return text_height


# --------------------------------------------------
# INTRO CARD
# --------------------------------------------------

def create_intro_card(
    output_path: str,
    title: str,
    subtitle: str
):

    image = create_background()
    add_snow_details(image)

    draw = ImageDraw.Draw(image)

    small_font = load_font(19, bold=True)
    subtitle_font = load_font(27)

    # Brand heading
    draw_centered_text(
        draw,
        (WIDTH // 2, 620),
        "A LITTLE WINTER MAGIC",
        small_font,
        GOLD
    )

    draw.line(
        (330, 690, 750, 690),
        fill=GOLD,
        width=3
    )

    # Main question: large and automatically wrapped.
    draw_adaptive_title(
        draw,
        title,
        center_y=900,
        max_font_size=76,
        min_font_size=42
    )

    # Subtitle
    wrapped_subtitle = wrap_text(
        draw,
        subtitle,
        subtitle_font,
        int(WIDTH * 0.72)
    )

    draw_centered_text(
        draw,
        (WIDTH // 2, 1190),
        wrapped_subtitle,
        subtitle_font,
        MUTED,
        spacing=24
    )

    # Bottom label
    draw_centered_text(
        draw,
        (WIDTH // 2, 1690),
        "CHOOSE YOUR PLACE",
        small_font,
        GOLD
    )

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(output)

    print(
        f"Pixel-font intro created: {output}"
    )

    return str(output)


# --------------------------------------------------
# OUTRO CARD
# --------------------------------------------------

def create_outro_card(
    output_path: str,
    title: str,
    subtitle: str
):

    image = create_background()
    add_snow_details(image)

    draw = ImageDraw.Draw(image)

    small_font = load_font(19, bold=True)
    subtitle_font = load_font(27)

    # Heading
    draw_centered_text(
        draw,
        (WIDTH // 2, 650),
        "YOUR WINTER ESCAPE",
        small_font,
        GOLD
    )

    # Main question
    draw_adaptive_title(
        draw,
        title,
        center_y=920,
        max_font_size=76,
        min_font_size=42
    )

    # Subtitle
    wrapped_subtitle = wrap_text(
        draw,
        subtitle,
        subtitle_font,
        int(WIDTH * 0.72)
    )

    draw_centered_text(
        draw,
        (WIDTH // 2, 1190),
        wrapped_subtitle,
        subtitle_font,
        MUTED,
        spacing=24
    )

    # Comment prompt
    draw_centered_text(
        draw,
        (WIDTH // 2, 1530),
        "COMMENT YOUR CHOICE BELOW",
        small_font,
        GOLD
    )

    draw_centered_text(
        draw,
        (WIDTH // 2, 1690),
        "COZYVERSE",
        small_font,
        CREAM
    )

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(output)

    print(
        f"Pixel-font outro created: {output}"
    )

    return str(output)
