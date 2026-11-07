from pathlib import Path

from PIL import Image


WORKING_WIDTH = 360
WORKING_HEIGHT = 640

FINAL_WIDTH = 1080
FINAL_HEIGHT = 1920

COLOR_COUNT = 48


def pixelate_image(
    input_path: str | Path,
    output_path: str | Path,
):
    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.open(input_path).convert("RGB")

    # Resize to a true 9:16 working canvas.
    image = image.resize(
        (WORKING_WIDTH, WORKING_HEIGHT),
        Image.Resampling.LANCZOS,
    )

    # Reduce the colour palette.
    image = image.quantize(
        colors=COLOR_COUNT,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )

    image = image.convert("RGB")

    # Enlarge without smoothing to retain pixel-art edges.
    image = image.resize(
        (FINAL_WIDTH, FINAL_HEIGHT),
        Image.Resampling.NEAREST,
    )

    image.save(
        output_path,
        format="PNG",
        optimize=True,
    )

    print(f"Pixel-art image saved: {output_path}")

    return output_path