import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
WIDTH, HEIGHT, FPS = 1080, 1920, 30
TOTAL_SECONDS, TOTAL_FRAMES = 17, 510
SEGMENT_FRAMES, TRANSITION_FRAMES, SEGMENT_STRIDE = 110, 10, 100
TEXT_Y = 790

FONT_PATH = ROOT / "assets" / "fonts" / "Silkscreen-Bold.ttf"


def _font(size=46):
    if not FONT_PATH.is_file():
        raise FileNotFoundError(f"Missing Silkscreen font: {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size)


def _fit_text(draw, text, font=None, max_width=1000):
    """Return a Silkscreen font that fits the label within the frame."""
    if font is None:
        font = _font(46)

    size = font.size
    while size > 24:
        candidate = _font(size)
        bbox = draw.textbbox((0, 0), text, font=candidate)
        if bbox[2] - bbox[0] <= max_width:
            return candidate
        size -= 2

    return _font(24)


def _prepare_image(path, label):
    image = Image.open(path).convert("RGB")

    # Cover-fit the portrait canvas; never use a blurred square background.
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    image = resized.crop((left, top, left + WIDTH, top + HEIGHT)).convert("RGBA")

    draw = ImageDraw.Draw(image, "RGBA")
    font = _fit_text(draw, label, _font())
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    x = (WIDTH - text_width) // 2
    y = TEXT_Y

    # Subtle dark offset for legibility, without a banner or panel.
    draw.text((x + 3, y + 4), label, font=font, fill=(8, 12, 20, 185))
    draw.text((x, y), label, font=font, fill=(255, 241, 211, 255))

    return image.convert("RGB")


def _animate(image, local_frame):
    progress = min(max(local_frame, 0), SEGMENT_FRAMES - 1) / (SEGMENT_FRAMES - 1)
    zoom = 1.0 + 0.012 * progress
    width = round(WIDTH * zoom)
    height = round(HEIGHT * zoom)
    enlarged = image.resize((width, height), Image.Resampling.LANCZOS)
    x = (width - WIDTH) // 2
    y = (height - HEIGHT) // 2
    return enlarged.crop((x, y, x + WIDTH, y + HEIGHT))


def render_reel(image_paths, question, choices, music_path, output_path):
    if len(image_paths) != 5 or len(choices) != 4:
        raise ValueError(
            "Renderer needs one opening image and exactly four choice images."
        )

    if not Path(music_path).is_file():
        raise FileNotFoundError(music_path)

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed or not available on PATH.")

    labels = [question.upper()] + [
        f"{index + 1}. {choice['title'].upper()}"
        for index, choice in enumerate(choices)
    ]
    images = [
        _prepare_image(image_path, label)
        for image_path, label in zip(image_paths, labels)
    ]

    def segment_frame(index, local_frame):
        return _animate(images[index], local_frame)

    def frame_at(frame_number):
        segment = min(frame_number // SEGMENT_STRIDE, 4)
        local = frame_number - segment * SEGMENT_STRIDE

        if segment > 0 and local < TRANSITION_FRAMES:
            previous = segment_frame(segment - 1, SEGMENT_STRIDE + local)
            current = segment_frame(segment, local)
            return Image.blend(
                previous,
                current,
                (local + 1) / (TRANSITION_FRAMES + 1),
            )

        return segment_frame(segment, local)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-r", str(FPS),
        "-i", "-",
        "-stream_loop", "-1",
        "-i", str(music_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", str(TOTAL_SECONDS),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-af", "volume=0.18,afade=t=out:st=16.4:d=0.6",
        "-movflags", "+faststart",
        str(output_path),
    ]

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )

    try:
        for frame_number in range(TOTAL_FRAMES):
            process.stdin.write(frame_at(frame_number).tobytes())
            if (frame_number + 1) % 60 == 0:
                print(
                    f"Rendering video: {frame_number + 1}/{TOTAL_FRAMES} frames"
                )

        process.stdin.close()
        error = process.stderr.read().decode("utf-8", errors="replace")
        return_code = process.wait()

        if return_code:
            raise RuntimeError(f"FFmpeg failed:\n{error[-4000:]}")

    except Exception:
        if process.poll() is None:
            process.kill()
            process.wait()
        raise

    return output_path
