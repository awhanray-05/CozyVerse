import json
from datetime import date
from pathlib import Path

from src.generator.image_generator import generate_image
from src.renderer.pixelate import pixelate_image
from src.renderer.dynamic_video_renderer import render_reel
from src.story.story_generator import generate_story, save_story_history
from src.story.prompt_builder import build_prompt
from src.story.music_manager import get_daily_music

ROOT = Path(__file__).resolve().parent


def main():
    print("\n" + "=" * 58)
    print("COZYVERSE — DAILY REEL GENERATOR")
    print("=" * 58)

    story = generate_story()
    today = date.today().isoformat()
    slug = "".join(
        ch.lower() if ch.isalnum() else "_"
        for ch in story["theme"]
    ).strip("_")

    run_dir = ROOT / "output" / "daily" / f"{today}_{slug}"
    raw_dir = run_dir / "raw"
    pixel_dir = run_dir / "images"
    raw_dir.mkdir(parents=True, exist_ok=True)
    pixel_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nToday's theme: {story['theme']}")
    print(f"Question: {story['question']}")

    # Pass the complete structured choice to the prompt builder so that
    # scene type, camera, composition, palette and couple action are used.
    scenes = [
        ("intro", story["intro_environment"], True, None)
    ]
    scenes.extend(
        (
            f"choice_{index}_{choice['title']}",
            choice["description"],
            False,
            choice,
        )
        for index, choice in enumerate(story["choices"], start=1)
    )

    image_paths = []

    for index, (name, description, opening, choice) in enumerate(scenes, start=1):
        raw_path = raw_dir / f"{index:02d}_{name}.png"
        pixel_path = pixel_dir / f"{index:02d}_{name}.png"

        if not pixel_path.exists():
            if not raw_path.exists():
                prompt = build_prompt(
                    description,
                    opening=opening,
                    choice=choice,
                )
                print(f"\nGenerating image {index}/5: {name}")
                generate_image(prompt, raw_path, seed=None)
            else:
                print(f"\nUsing existing raw image: {raw_path}")

            pixelate_image(raw_path, pixel_path)
        else:
            print(f"\nUsing existing pixel-art image: {pixel_path}")

        image_paths.append(pixel_path)

    story_file = run_dir / "story.json"
    story_file.write_text(
        json.dumps(story, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    music = get_daily_music()
    output = ROOT / "output" / "videos" / "daily" / f"cozyverse_{today}.mp4"

    print(f"\nUsing persistent music: {music.name}")
    render_reel(
        image_paths,
        story["question"],
        story["choices"],
        music,
        output,
    )

    save_story_history(story)

    print("\n" + "=" * 58)
    print("COZYVERSE REEL COMPLETE")
    print(f"Video: {output}")
    print("=" * 58)


if __name__ == "__main__":
    main()
