import argparse
from pathlib import Path

from src.generator.scenes import COLLECTION
from src.generator.image_generator import generate_image
from src.renderer.pixelate import pixelate_image
from src.renderer.scene_label import add_scene_label


PROJECT_ROOT = Path(__file__).resolve().parents[2]

COLLECTION_NAME = "winter_night_v2"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "images"
    / COLLECTION_NAME
)


def generate_collection(force=False):
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n===================================")
    print("       COZYVERSE GENERATOR")
    print("===================================")
    print(f"Collection: {COLLECTION_NAME}")
    print("Resolution: 864 x 1536")
    print("Aspect ratio: 9:16")
    print("Characters: Recurring travelling couple")
    print("===================================\n")

    for scene in COLLECTION:
        scene_prefix = (
            f"scene_{scene.number:02d}_{scene.slug}"
        )

        raw_path = OUTPUT_DIR / f"{scene_prefix}_raw.png"
        pixel_path = OUTPUT_DIR / f"{scene_prefix}_pixel.png"
        final_path = OUTPUT_DIR / f"{scene_prefix}_final.png"

        print("\n-----------------------------------")
        print(
            f"SCENE {scene.number}: {scene.title}"
        )
        print("-----------------------------------")

        if force or not raw_path.exists():
            generate_image(
                prompt=scene.prompt,
                output_path=raw_path,
                seed=scene.seed,
            )
        else:
            print(f"Using existing raw image: {raw_path}")

        if force or not pixel_path.exists():
            pixelate_image(
                input_path=raw_path,
                output_path=pixel_path,
            )
        else:
            print(f"Using existing pixel image: {pixel_path}")

        if force or not final_path.exists():
            add_scene_label(
                input_path=pixel_path,
                output_path=final_path,
                number=scene.number,
                title=scene.title,
            )
        else:
            print(f"Using existing final image: {final_path}")

    print("\n===================================")
    print("       GENERATION COMPLETE")
    print("===================================")
    print(f"Images saved in:\n{OUTPUT_DIR}")

    print("\nFinal scenes:")

    for scene in COLLECTION:
        scene_prefix = (
            f"scene_{scene.number:02d}_{scene.slug}"
        )

        print(
            OUTPUT_DIR / f"{scene_prefix}_final.png"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate CozyVerse portrait scenes."
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate all images, including existing ones.",
    )

    args = parser.parse_args()

    generate_collection(force=args.force)