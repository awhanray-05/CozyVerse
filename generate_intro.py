
from pathlib import Path

from src.generator.image_generator import generate_image
from src.renderer.pixelate import pixelate_image


ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = (
    ROOT / "output" / "images" / "winter_night_v2"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

prompt = """
A beautiful handcrafted 16-bit pixel art fantasy RPG scene.

A young travelling couple stands together on a peaceful
hilltop overlooking a vast magical fantasy world.

The young man has dark brown hair, a deep teal travelling
cloak and a warm brown scarf.

The young woman has chestnut hair, a burgundy travelling
cloak and a cream knitted scarf.

They are standing side by side, seen mostly from behind
and slightly from the side, looking curiously across
the beautiful world in front of them.

Their body language communicates curiosity, excitement
and wonder about where their journey might take them.

In the distant landscape, show several different
fantasy environments naturally belonging to one world:
a magnificent castle on a hill, a peaceful river winding
through a forest, a warm cottage, and a distant tavern
with glowing windows.

This must be ONE coherent panoramic fantasy landscape,
not a collage or separate panels.

Beautiful twilight sky, soft glowing stars,
warm golden lights in the distance, gentle mist,
dreamy atmospheric depth.

The couple should be charming, elegant and relatively
small compared with the landscape.

Authentic handcrafted 16-bit pixel art.
Beautiful pixel clusters, sophisticated game art,
rich but restrained colours.

Vertical 9:16 portrait composition.
Full-screen edge-to-edge artwork.

No text, no letters, no numbers, no logos,
no banners, no labels, no UI.
"""

raw = OUTPUT_DIR / "intro_raw.png"
final = OUTPUT_DIR / "intro_pixel.png"

generate_image(
    prompt=prompt,
    output_path=raw,
    seed=7100,
)

pixelate_image(
    input_path=raw,
    output_path=final,
)

print(f"Opening image ready: {final}")
