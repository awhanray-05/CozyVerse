from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_DIR = Path("assets/fonts")

REGULAR_FONT = FONT_DIR / "Silkscreen-Regular.ttf"
BOLD_FONT = FONT_DIR / "Silkscreen-Bold.ttf"


def load_font(path, size):
    if path.exists():
        return ImageFont.truetype(str(path), size)

    return ImageFont.load_default()


def add_scene_label(
    input_path: str | Path,
    output_path: str | Path,
    number: int,
    title: str,
):
    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.open(input_path).convert("RGBA")

    draw = ImageDraw.Draw(image, "RGBA")

    number_font = load_font(BOLD_FONT, 30)
    title_font = load_font(REGULAR_FONT, 20)

    margin_x = 48
    margin_y = 100

    number_text = f"0{number}"
    title_text = title.upper()

    number_box = draw.textbbox(
        (0, 0),
        number_text,
        font=number_font,
    )

    title_box = draw.textbbox(
        (0, 0),
        title_text,
        font=title_font,
    )

    number_width = number_box[2] - number_box[0]
    title_width = title_box[2] - title_box[0]

    content_width = max(
        number_width,
        title_width,
    )

    panel_width = content_width + 56
    panel_height = 100

    x1 = margin_x
    y1 = margin_y
    x2 = x1 + panel_width
    y2 = y1 + panel_height

    # Dark translucent pixel-game panel.
    draw.rectangle(
        (x1, y1, x2, y2),
        fill=(13, 19, 28, 205),
        outline=(224, 181, 111, 255),
        width=3,
    )

    # Small decorative pixel corner details.
    corner = 10

    draw.rectangle(
        (x1, y1, x1 + corner, y1 + corner),
        fill=(245, 204, 135, 255),
    )

    draw.rectangle(
        (x2 - corner, y2 - corner, x2, y2),
        fill=(245, 204, 135, 255),
    )

    draw.text(
        (x1 + 20, y1 + 10),
        number_text,
        font=number_font,
        fill=(255, 211, 135, 255),
    )

    draw.text(
        (x1 + 20, y1 + 57),
        title_text,
        font=title_font,
        fill=(255, 245, 220, 255),
    )

    image.convert("RGB").save(
        output_path,
        format="PNG",
        optimize=True,
    )

    print(f"Scene label added: {output_path}")

    return output_path