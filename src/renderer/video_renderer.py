
import shutil
import subprocess
import tempfile

from pathlib import Path

from src.generator.scenes import COLLECTION
from src.renderer.effects import (
    create_intro_card,
    create_outro_card
)
from src.renderer.transitions import build_xfade_filter


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

WIDTH = 1080
HEIGHT = 1920
FPS = 30

INTRO_DURATION = 2.5
SCENE_DURATION = 4.0
OUTRO_DURATION = 2.5

TRANSITION_DURATION = 0.45

BASE_DIR = Path(__file__).resolve().parents[2]

IMAGE_DIR = (
    BASE_DIR
    / "output"
    / "images"
    / COLLECTION["id"]
)

VIDEO_DIR = (
    BASE_DIR
    / "output"
    / "videos"
    / COLLECTION["id"]
)

MUSIC_PATH = (
    BASE_DIR
    / "assets"
    / "music"
    / "background.mp3"
)

OUTPUT_VIDEO = VIDEO_DIR / "cozyverse_winter_night.mp4"


# --------------------------------------------------
# FFMPEG UTILITIES
# --------------------------------------------------

def check_ffmpeg():

    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg not found. Restart your terminal "
            "or reinstall FFmpeg."
        )

    if not shutil.which("ffprobe"):
        raise RuntimeError(
            "FFprobe not found. Check your FFmpeg installation."
        )


def run_command(command: list[str]):

    print("\nRunning FFmpeg...")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print("\nFFmpeg error:")
        print(result.stderr[-5000:])

        raise RuntimeError(
            "Video processing failed."
        )

    return result


# --------------------------------------------------
# CREATE STATIC CARD CLIPS
# --------------------------------------------------

def render_card_clip(
    image_path: Path,
    output_path: Path,
    duration: float
):

    fade_duration = 0.35
    fade_out_start = duration - fade_duration

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", str(FPS),
        "-i", str(image_path),
        "-t", str(duration),
        "-vf",
        (
            f"scale={WIDTH}:{HEIGHT},"
            f"fps={FPS},"
            "format=yuv420p,"
            f"fade=t=in:st=0:d={fade_duration},"
            f"fade=t=out:st={fade_out_start}:d={fade_duration}"
        ),
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        str(output_path)
    ]

    run_command(command)


# --------------------------------------------------
# CREATE SCENE CLIPS
# --------------------------------------------------

def render_scene_clip(
    image_path: Path,
    output_path: Path,
    duration: float
):

    fade_duration = 0.35
    fade_out_start = duration - fade_duration

    filter_complex = (
        # Split original image into foreground/background
        "[0:v]split=2[background][foreground];"

        # Create vertical blurred background
        "[background]"
        f"scale={WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        "boxblur=25:10,"
        "eq=brightness=-0.12:saturation=0.85"
        "[bg];"

        # Preserve original artwork in the foreground
        "[foreground]"
        "scale=980:980:"
        "force_original_aspect_ratio=decrease,"
        "pad=980:980:(ow-iw)/2:(oh-ih)/2:"
        "color=black@0,"
        "format=rgba"
        "[fg];"

        # Composite artwork over blurred background
        "[bg][fg]"
        "overlay=(W-w)/2:(H-h)/2,"
        "format=yuv420p"

        # Add subtle cinematic zoom
        ",zoompan="
        "z='min(1+0.00025*on,1.03)':"
        "x='iw/2-(iw/zoom/2)':"
        "y='ih/2-(ih/zoom/2)':"
        "d=1:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS}"

        # Fade the scene at both ends
        f",fade=t=in:st=0:d={fade_duration}"
        f",fade=t=out:st={fade_out_start}:d={fade_duration}"

        ",setsar=1,format=yuv420p"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", str(FPS),
        "-i", str(image_path),
        "-t", str(duration),
        "-filter_complex", filter_complex,
        "-an",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        str(output_path)
    ]

    run_command(command)


# --------------------------------------------------
# COMBINE ALL CLIPS
# --------------------------------------------------

def combine_clips(
    clip_paths: list[Path],
    durations: list[float],
    output_path: Path
):

    filter_complex, total_duration = build_xfade_filter(
        durations,
        TRANSITION_DURATION
    )

    command = ["ffmpeg", "-y"]

    for clip_path in clip_paths:
        command.extend([
            "-i",
            str(clip_path)
        ])

    music_exists = MUSIC_PATH.exists()

    if music_exists:

        command.extend([
            "-stream_loop", "-1",
            "-i", str(MUSIC_PATH)
        ])

        music_input_index = len(clip_paths)

    command.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]"
    ])

    if music_exists:

        command.extend([
            "-map", f"{music_input_index}:a:0",
            "-af",
            (
                "volume=0.18,"
                f"afade=t=out:st={total_duration - 1.5}:d=1.5"
            ),
        ])

        command.extend([
            "-c:a", "aac",
            "-b:a", "192k"
        ])

    else:

        command.append("-an")

        print(
            "\nNo background music found. "
            "Exporting without audio."
        )

    command.extend([
        "-t", str(total_duration),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-movflags", "+faststart",
        str(output_path)
    ])

    run_command(command)

    print("\nVideo successfully exported!")
    print(f"Duration: {total_duration:.2f} seconds")


# --------------------------------------------------
# MAIN RENDERER
# --------------------------------------------------

def render_reel():

    check_ffmpeg()

    VIDEO_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n" + "=" * 55)
    print("COZYVERSE REEL RENDERER")
    print("=" * 55)

    intro_path = VIDEO_DIR / "intro.png"
    outro_path = VIDEO_DIR / "outro.png"

    # Create opening screen
    create_intro_card(
        output_path=str(intro_path),
        title="Where would you\nspend a magical\nwinter night?",
        subtitle="Four cozy places.\nOne winter night."
    )

    # Create closing screen
    create_outro_card(
        output_path=str(outro_path),
        title="Which place\nwould you choose?",
        subtitle="Tell us your favourite\nin the comments."
    )

    durations = [
        INTRO_DURATION
    ]

    clip_paths = []

    with tempfile.TemporaryDirectory(
        prefix="cozyverse_"
    ) as temporary_directory:

        work_dir = Path(temporary_directory)

        # Render intro
        intro_clip = work_dir / "intro.mp4"

        render_card_clip(
            intro_path,
            intro_clip,
            INTRO_DURATION
        )

        clip_paths.append(intro_clip)

        # Render four scenes
        for scene in COLLECTION["scenes"]:

            number = scene["number"]

            print(
                f"\nRendering scene {number}: "
                f"{scene['name']}"
            )

            image_path = (
                IMAGE_DIR
                / f"scene_{number:02d}_final.png"
            )

            if not image_path.exists():

                raise FileNotFoundError(
                    f"Missing scene image: {image_path}"
                )

            scene_clip = (
                work_dir
                / f"scene_{number:02d}.mp4"
            )

            render_scene_clip(
                image_path,
                scene_clip,
                SCENE_DURATION
            )

            clip_paths.append(scene_clip)
            durations.append(SCENE_DURATION)

        # Render outro
        outro_clip = work_dir / "outro.mp4"

        render_card_clip(
            outro_path,
            outro_clip,
            OUTRO_DURATION
        )

        clip_paths.append(outro_clip)
        durations.append(OUTRO_DURATION)

        # Combine everything with transitions
        combine_clips(
            clip_paths,
            durations,
            OUTPUT_VIDEO
        )

    print("\n" + "=" * 55)
    print("COZYVERSE REEL COMPLETED")
    print("=" * 55)
    print(f"\nOutput: {OUTPUT_VIDEO}")


if __name__ == "__main__":

    render_reel()
