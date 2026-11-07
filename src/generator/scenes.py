
from dataclasses import dataclass


@dataclass
class Scene:
    number: int
    slug: str
    title: str
    description: str
    prompt: str
    seed: int


CHARACTERS = """
Include the same small recurring fantasy travelling couple:
a young man with dark brown hair, teal cloak and brown scarf;
a young woman with chestnut hair, burgundy cloak and cream scarf.
They wear simple travelling boots and carry small leather bags.

Use charming, refined 16-bit RPG pixel-art character design.
Small expressive faces, understated features, beautiful silhouettes.
They should occupy only 12-18 percent of the image height.
They are part of the world, not posing for a portrait.
"""


COMMON = """
Vertical 9:16 composition, full-screen environment.
High-quality handcrafted 16-bit pixel art.
Crisp pixel clusters, beautiful lighting and rich depth.
Sophisticated game-art direction, atmospheric colour palette.
The environment must occupy at least 80 percent of the visual attention.

No text, no numbers, no labels, no UI, no watermark.
No anime, no photorealism, no 3D rendering.
"""


COLLECTION = [

    Scene(
        number=1,
        slug="castle_courtyard",
        title="Castle Courtyard",
        description="A grand fantasy castle courtyard.",

        prompt=f"""
Create a GRAND MEDIEVAL CASTLE COURTYARD.

IMPORTANT: This is NOT a village street.

COMPOSITION:
A wide, open stone courtyard dominates the foreground.
A magnificent enormous castle dominates the background.
Show tall castle towers, battlements, a grand arched entrance,
a central ornamental fountain and a broad stone staircase.

Snow-covered evergreen trees frame the courtyard.
Golden lights glow from the castle windows.
A deep blue twilight sky is visible above the towers.

The travelling couple stands very small beside the fountain,
admiring the castle architecture.

The image should feel like an establishing shot
from a beautiful fantasy RPG game.

ENVIRONMENT MUST BE THE MAIN SUBJECT.

{CHARACTERS}
{COMMON}
""",
        seed=6101,
    ),

    Scene(
        number=2,
        slug="library_nook",
        title="Library Nook",
        description="A warm indoor fantasy library.",

        prompt=f"""
Create a BEAUTIFUL INDOOR FANTASY LIBRARY.

CRITICAL: THE ENTIRE SCENE MUST BE INSIDE A BUILDING.
DO NOT CREATE A STREET, VILLAGE, CASTLE COURTYARD OR OUTDOOR SCENE.

COMPOSITION:
The viewer is standing inside a magnificent old library.
Towering wooden bookshelves cover the walls.
A spiral staircase leads to an upper gallery.
A huge fireplace glows on one side.
A large arched window shows a snowy forest outside.

In the foreground there is a plush reading sofa,
a wooden coffee table, open books and candle lanterns.
A small orange cat sleeps beside the fireplace.

The travelling couple sits together on the sofa,
reading a book.

The room architecture and bookshelves dominate the image.
Warm amber lighting, deep walnut wood, soft shadows.
A peaceful, intimate fantasy-game interior.

This must unmistakably look like a library interior.

{CHARACTERS}
{COMMON}
""",
        seed=6102,
    ),

    Scene(
        number=3,
        slug="riverside_cottage",
        title="Riverside Cottage",
        description="A secluded cottage beside a flowing river.",

        prompt=f"""
Create A SECLUDED RIVERSIDE COTTAGE LANDSCAPE.

CRITICAL: SHOW A LARGE, CLEARLY VISIBLE RIVER.
DO NOT CREATE A VILLAGE STREET OR ROWS OF MEDIEVAL HOUSES.

COMPOSITION:
A peaceful turquoise river flows diagonally
across the foreground and middle of the image.
A little wooden footbridge crosses the river.

On the riverbank stands ONE charming isolated wooden cottage.
It has a glowing window, a sloping roof,
a chimney releasing smoke and a small garden.

Surround the cottage with tall pine trees,
soft hills, a few distant mountains and forest vegetation.
The water reflects the warm lights of the cottage.

The travelling couple sits together on the wooden bridge,
looking at the flowing water.

The river, cottage and surrounding natural landscape
must dominate the composition.

Peaceful evening colours, teal water, forest greens,
warm golden windows and a dreamy twilight sky.

This is a natural landscape, not a medieval town.

{CHARACTERS}
{COMMON}
""",
        seed=6103,
    ),

    Scene(
        number=4,
        slug="mountain_tavern",
        title="Mountain Tavern",
        description="A rustic tavern interior overlooking mountains.",

        prompt=f"""
Create A COZY INDOOR MOUNTAIN TAVERN.

CRITICAL: THE VIEWER MUST BE INSIDE THE TAVERN.
DO NOT CREATE A VILLAGE STREET OR OUTDOOR BUILDING EXTERIOR.

COMPOSITION:
A beautifully detailed rustic tavern interior.
Large wooden ceiling beams and stone walls.
A long wooden bar with mugs and bottles.
A large glowing stone fireplace.
Wooden dining tables, stools and warm hanging lanterns.

A huge panoramic window occupies the back wall.
Through the window, show spectacular snow-covered mountains,
pine forests and a deep blue evening sky.

The travelling couple sits at a small wooden table
near the panoramic window, holding warm drinks.

The tavern interior fills most of the image.
The mountains are visible only through the window.

Warm amber firelight contrasts with the cool blue mountains.
A welcoming, magical fantasy RPG atmosphere.

This must unmistakably look like an indoor tavern.

{CHARACTERS}
{COMMON}
""",
        seed=6104,
    ),
]
