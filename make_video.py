
import argparse
import subprocess
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent

IMAGE_DIR = ROOT / "output" / "images" / "winter_night_v2"
MUSIC_DIR = ROOT / "assets" / "music"
FONT_DIR = ROOT / "assets" / "fonts"

OUTPUT_DIR = ROOT / "output" / "videos" / "winter_night_v2"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
TOTAL_SECONDS = 17
TOTAL_FRAMES = 510

# Five segments, each 110 frames.
# Four transitions overlap by 10 frames each.
SEGMENT_FRAMES = 110
TRANSITION_FRAMES = 10
SEGMENT_STRIDE = 100

TEXT_Y = 790

QUESTION = "WHERE WOULD YOU STAY?"

OPTIONS = [
    "1. CASTLE COURTYARD",
    "2. LIBRARY NOOK",
    "3. RIVERSIDE COTTAGE",
    "4. MOUNTAIN TAVERN",
]

IMAGE_FILES = [
    "intro_pixel.png",
    "scene_01_castle_courtyard_pixel.png",
    "scene_02_library_nook_pixel.png",
    "scene_03_riverside_cottage_pixel.png",
    "scene_04_mountain_tavern_pixel.png",
]


def get_music(explicit_path=None):
    if explicit_path:
        path = Path(explicit_path)

        if not path.is_absolute():
            path = ROOT / path

        if not path.is_file():
            raise FileNotFoundError(path)

        return path

    supported = {
        ".mp3", ".wav", ".m4a", ".aac", ".ogg"
    }

    tracks = [
        p for p in MUSIC_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in supported
    ]

    if len(tracks) != 1:
        raise RuntimeError(
            "Place exactly one music file inside assets/music "
            "or provide --music."
        )

    return tracks[0]


def load_images():
    images = []

    for filename in IMAGE_FILES:
        path = IMAGE_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing image: {path}"
            )

        image = Image.open(path).convert("RGB")

        if image.size != (WIDTH, HEIGHT):
            raise ValueError(
                f"{filename}: expected 1080x1920, "
                f"got {image.size}"
            )

        images.append(image)

    return images


def load_fonts():
    regular = FONT_DIR / "Silkscreen-Regular.ttf"
    bold = FONT_DIR / "Silkscreen-Bold.ttf"

    if not regular.exists():
        raise FileNotFoundError(regular)

    if not bold.exists():
        raise FileNotFoundError(bold)

    return (
        ImageFont.truetype(str(regular), 40),
        ImageFont.truetype(str(bold), 42),
    )


def draw_centered_text(draw, text, font, y):
    spacing = 3

    widths = [
        draw.textlength(char, font=font)
        for char in text
    ]

    total_width = sum(widths) + spacing * (len(text) - 1)
    x = (WIDTH - total_width) / 2

    for char, char_width in zip(text, widths):

        # Subtle shadow, no background box.
        draw.text(
            (round(x) + 3, y + 4),
            char,
            font=font,
            fill=(8, 12, 20, 190),
        )

        draw.text(
            (round(x), y),
            char,
            font=font,
            fill=(255, 241, 211, 255),
        )

        x += char_width + spacing


def add_text(image, segment_index):
    image = image.convert("RGBA")
    draw = ImageDraw.Draw(image, "RGBA")

    regular_font, bold_font = load_fonts()

    if segment_index == 0:
        draw_centered_text(
            draw,
            QUESTION,
            bold_font,
            TEXT_Y,
        )
    else:
        option = OPTIONS[segment_index - 1]

        draw_centered_text(
            draw,
            option,
            bold_font,
            TEXT_Y,
        )

    return image.convert("RGB")


def animate_image(image, frame_index):
    progress = frame_index / (SEGMENT_FRAMES - 1)

    zoom = 1.0 + 0.012 * progress

    new_width = int(WIDTH * zoom)
    new_height = int(HEIGHT * zoom)

    enlarged = image.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2

    return enlarged.crop((
        left,
        top,
        left + WIDTH,
        top + HEIGHT,
    ))


def render_segment(images, index, local_frame):
    frame = animate_image(
        images[index],
        local_frame,
    )

    return add_text(frame, index)


def get_frame(images, global_frame):
    segment = min(
        global_frame // SEGMENT_STRIDE,
        4,
    )

    local_frame = (
        global_frame - segment * SEGMENT_STRIDE
    )

    # Crossfade between the previous and incoming segment.
    if segment > 0 and local_frame < TRANSITION_FRAMES:

        previous = render_segment(
            images,
            segment - 1,
            SEGMENT_STRIDE + local_frame,
        )

        current = render_segment(
            images,
            segment,
            local_frame,
        )

        alpha = (
            (local_frame + 1)
            / (TRANSITION_FRAMES + 1)
        )

        return Image.blend(previous, current, alpha)

    return render_segment(
        images,
        segment,
        local_frame,
    )


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
        str(output),
    ]

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        for frame_number in range(TOTAL_FRAMES):
            frame = get_frame(
                images,
                frame_number,
            )

            process.stdin.write(frame.tobytes())

            if (frame_number + 1) % 30 == 0:
                print(
                    f"Rendering: "
                    f"{frame_number + 1}/{TOTAL_FRAMES}"
                )

        process.stdin.close()

        error = process.stderr.read().decode(
            "utf-8",
            errors="replace",
        )

        result = process.wait()

        if result != 0:
            raise RuntimeError(error[-4000:])

    except Exception:
        if process.poll() is None:
            process.kill()
            process.wait()
        raise


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--music",
        help="Optional background music path",
    )

    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed or on PATH.")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    images = load_images()
    music = get_music(args.music)

    output = (
        OUTPUT_DIR / "cozyverse_winter_night.mp4"
    )

    print("\nCOZYVERSE")
    print("5 visual segments")
    print("17 seconds")
    print("1080 x 1920")
    print("30 FPS")
    print("Large centred Silkscreen typography")
    print(f"Music: {music.name}\n")

    render_video(
        images,
        music,
        output,
    )

    print("\nVIDEO COMPLETE!")
    print(output)


if __name__ == "__main__":
    main()
