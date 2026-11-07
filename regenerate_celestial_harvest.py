
import subprocess
import shutil
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ==================================================
# CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent

COLLECTION_DIR = (
    ROOT / "output" / "daily" / "2026-11-06_celestial_harvest"
)

IMAGE_DIR = COLLECTION_DIR / "images"

MUSIC_DIR = ROOT / "assets" / "music"
FONT_DIR = ROOT / "assets" / "fonts"

OUTPUT_DIR = ROOT / "output" / "videos" / "daily"

OUTPUT_VIDEO = (
    OUTPUT_DIR / "cozyverse_2026-11-06_updated.mp4"
)

WIDTH = 1080
HEIGHT = 1920
FPS = 30

TOTAL_SECONDS = 17
TOTAL_FRAMES = 510

SEGMENT_FRAMES = 110
TRANSITION_FRAMES = 10
SEGMENT_STRIDE = 100

FONT_PATH = FONT_DIR / "Silkscreen-Bold.ttf"

# Intro typography
INTRO_TEXT = [
    "IF YOU COULD TAKE",
    "A WEEKEND AWAY,",
    "WHERE WOULD YOU GO?"
]

INTRO_FONT_SIZE = 49
INTRO_CENTER_Y = 850
INTRO_LINE_SPACING = 16
INTRO_MAX_WIDTH = 850

# Destination typography
OPTIONS = [
    "1. NEBULA ORCHARD",
    "2. AURORA MEADOW",
    "3. ASTRAL OBSERVATORY",
    "4. AURORA CLIFFS",
]

CHOICE_FONT_SIZE = 42
CHOICE_TEXT_Y = 790
CHOICE_LETTER_SPACING = 3

TEXT_COLOR = (255, 241, 211, 255)
SHADOW_COLOR = (8, 12, 20, 210)

# Existing generated images
IMAGE_FILES = [
    "01_intro.png",
    "02_choice_1_Nebula Orchard.png",
    "03_choice_2_Aurora Meadow.png",
    "04_choice_3_Astral Observatory.png",
    "05_choice_4_Aurora Cliffs.png",
]

# Existing embedded intro text region
OLD_TEXT_TOP = 675
OLD_TEXT_BOTTOM = 725


# ==================================================
# VALIDATION
# ==================================================

def validate_files():

    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg is not installed or not in PATH."
        )

    if not FONT_PATH.exists():
        raise FileNotFoundError(
            f"Missing font: {FONT_PATH}"
        )

    if not IMAGE_DIR.exists():
        raise FileNotFoundError(
            f"Image directory not found: {IMAGE_DIR}"
        )

    for filename in IMAGE_FILES:

        path = IMAGE_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing image: {path}"
            )


# ==================================================
# MUSIC
# ==================================================

def get_music(explicit_path=None):

    if explicit_path:

        path = Path(explicit_path)

        if not path.is_absolute():
            path = ROOT / path

        if not path.is_file():
            raise FileNotFoundError(path)

        return path

    preferred = MUSIC_DIR / "background.mp3"

    if preferred.exists():
        return preferred

    supported = {
        ".mp3", ".wav", ".m4a", ".aac", ".ogg"
    }

    tracks = [
        p for p in MUSIC_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in supported
    ]

    if len(tracks) != 1:

        raise RuntimeError(
            "Could not identify the original music track.\n"
            "Use --music to provide its exact path."
        )

    return tracks[0]


# ==================================================
# LOAD IMAGES
# ==================================================

def load_images():

    images = []

    for filename in IMAGE_FILES:

        path = IMAGE_DIR / filename

        image = Image.open(path).convert("RGB")

        if image.size != (WIDTH, HEIGHT):

            raise ValueError(
                f"{filename}: expected 1080x1920, "
                f"got {image.size}"
            )

        images.append(image)

    return images


# ==================================================
# REMOVE OLD INTRO TEXT
# ==================================================

def remove_old_intro_text(image):

    original = np.array(
        image.convert("RGB")
    )

    bgr = cv2.cvtColor(
        original,
        cv2.COLOR_RGB2BGR
    )

    region = bgr[
        OLD_TEXT_TOP:OLD_TEXT_BOTTOM,
        :
    ]

    # Detect bright text pixels.
    mask = cv2.inRange(
        region,
        np.array([150, 150, 150], dtype=np.uint8),
        np.array([255, 255, 255], dtype=np.uint8)
    )

    kernel = np.ones((5, 5), np.uint8)

    mask = cv2.dilate(
        mask,
        kernel,
        iterations=2
    )

    full_mask = np.zeros(
        (HEIGHT, WIDTH),
        dtype=np.uint8
    )

    full_mask[
        OLD_TEXT_TOP:OLD_TEXT_BOTTOM,
        :
    ] = mask

    cleaned = cv2.inpaint(
        bgr,
        full_mask,
        5,
        cv2.INPAINT_TELEA
    )

    cleaned = cv2.cvtColor(
        cleaned,
        cv2.COLOR_BGR2RGB
    )

    return Image.fromarray(cleaned)


# ==================================================
# INTRO TEXT
# ==================================================

def create_new_intro(image):

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        str(FONT_PATH),
        INTRO_FONT_SIZE
    )

    line_heights = []

    for line in INTRO_TEXT:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]

        if line_width > INTRO_MAX_WIDTH:

            raise ValueError(
                f"Intro line exceeds safe width: {line}"
            )

        line_heights.append(line_height)

    total_height = (
        sum(line_heights)
        + INTRO_LINE_SPACING * (len(INTRO_TEXT) - 1)
    )

    current_y = INTRO_CENTER_Y - total_height // 2

    for line, line_height in zip(
        INTRO_TEXT,
        line_heights
    ):

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        line_width = bbox[2] - bbox[0]

        x = (WIDTH - line_width) // 2

        # Text shadow
        draw.text(
            (x + 3, current_y + 4),
            line,
            font=font,
            fill=SHADOW_COLOR
        )

        # Main text
        draw.text(
            (x, current_y),
            line,
            font=font,
            fill=TEXT_COLOR
        )

        current_y += (
            line_height + INTRO_LINE_SPACING
        )

    return image.convert("RGB")


# ==================================================
# DESTINATION LABELS
# ==================================================

def add_choice_label(image, segment_index):

    # Intro does not receive a destination label.
    if segment_index == 0:
        return image

    image = image.convert("RGBA")

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(
        str(FONT_PATH),
        CHOICE_FONT_SIZE
    )

    text = OPTIONS[segment_index - 1]

    # Measure each character for pixel-letter spacing.
    widths = [
        draw.textlength(char, font=font)
        for char in text
    ]

    total_width = (
        sum(widths)
        + CHOICE_LETTER_SPACING * (len(text) - 1)
    )

    # Centre the entire label.
    x = (WIDTH - total_width) / 2

    for char, char_width in zip(text, widths):

        # Subtle shadow
        draw.text(
            (round(x) + 3, CHOICE_TEXT_Y + 4),
            char,
            font=font,
            fill=SHADOW_COLOR
        )

        # Cream pixel typography
        draw.text(
            (round(x), CHOICE_TEXT_Y),
            char,
            font=font,
            fill=TEXT_COLOR
        )

        x += char_width + CHOICE_LETTER_SPACING

    return image.convert("RGB")


# ==================================================
# IMAGE ANIMATION
# ==================================================

def animate_image(image, frame_index):

    progress = frame_index / (SEGMENT_FRAMES - 1)

    zoom = 1.0 + 0.012 * progress

    new_width = int(WIDTH * zoom)
    new_height = int(HEIGHT * zoom)

    enlarged = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )

    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2

    return enlarged.crop((
        left,
        top,
        left + WIDTH,
        top + HEIGHT
    ))


# ==================================================
# FRAME RENDERING
# ==================================================

def render_segment(images, index, local_frame):

    frame = animate_image(
        images[index],
        local_frame
    )

    # Apply destination label to each choice image.
    frame = add_choice_label(
        frame,
        index
    )

    return frame


def get_frame(images, global_frame):

    segment = min(
        global_frame // SEGMENT_STRIDE,
        4
    )

    local_frame = (
        global_frame - segment * SEGMENT_STRIDE
    )

    # Crossfade between previous and incoming segment.
    if segment > 0 and local_frame < TRANSITION_FRAMES:

        previous = render_segment(
            images,
            segment - 1,
            SEGMENT_STRIDE + local_frame
        )

        current = render_segment(
            images,
            segment,
            local_frame
        )

        alpha = (
            (local_frame + 1)
            / (TRANSITION_FRAMES + 1)
        )

        return Image.blend(
            previous,
            current,
            alpha
        )

    return render_segment(
        images,
        segment,
        local_frame
    )


# ==================================================
# VIDEO RENDERING
# ==================================================

def render_video(images, music, output):

    command = [
        "ffmpeg",
        "-y",

        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS),
        "-i", "-",

        "-stream_loop", "-1",
        "-i", str(music),

        "-map", "0:v:0",
        "-map", "1:a:0",

        "-t", str(TOTAL_SECONDS),

        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "192k",

        "-af", "afade=t=out:st=16.4:d=0.6",

        "-movflags", "+faststart",
        str(output)
    ]

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )

    try:

        for frame_number in range(TOTAL_FRAMES):

            frame = get_frame(
                images,
                frame_number
            )

            process.stdin.write(
                frame.tobytes()
            )

            if (frame_number + 1) % 30 == 0:

                print(
                    f"Rendering: "
                    f"{frame_number + 1}/{TOTAL_FRAMES}"
                )

        process.stdin.close()

        error = process.stderr.read().decode(
            "utf-8",
            errors="replace"
        )

        result = process.wait()

        if result != 0:
            raise RuntimeError(error[-4000:])

    except Exception:

        if process.poll() is None:
            process.kill()
            process.wait()

        raise


# ==================================================
# MAIN
# ==================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--music",
        help="Exact original background music path"
    )

    args = parser.parse_args()

    validate_files()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n" + "=" * 55)
    print("COZYVERSE - CELESTIAL HARVEST REGENERATION")
    print("=" * 55)

    print("\nLoading existing images...")

    images = load_images()

    print("Removing original intro text...")

    clean_intro = remove_old_intro_text(
        images[0]
    )

    print("Generating new intro typography...")

    new_intro = create_new_intro(
        clean_intro
    )

    preview_path = (
        OUTPUT_DIR / "cozyverse_new_intro_preview.png"
    )

    new_intro.save(preview_path)

    images[0] = new_intro

    print(f"Intro preview saved: {preview_path}")

    print("\nDestination labels:")

    for option in OPTIONS:
        print(f"  {option}")

    music = get_music(args.music)

    print(f"\nMusic: {music.name}")
    print(f"Output: {OUTPUT_VIDEO}")

    print("\nStarting video rendering...")

    render_video(
        images,
        music,
        OUTPUT_VIDEO
    )

    print("\n" + "=" * 55)
    print("VIDEO REGENERATION COMPLETE")
    print("=" * 55)

    print(f"\nIntro preview: {preview_path}")
    print(f"Updated video: {OUTPUT_VIDEO}")


if __name__ == "__main__":
    main()
