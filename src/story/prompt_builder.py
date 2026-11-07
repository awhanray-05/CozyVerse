
from src.prompts.pixel_art_style import (
    BASE_STYLE,
    CHARACTER_REFERENCE,
)


PIXEL_ART_QUALITY = """
PIXEL ART QUALITY:
- Premium handcrafted 16-bit RPG pixel art.
- Clearly visible square pixel clusters.
- Deliberate pixel placement and crisp edges.
- Rich environmental detail without excessive visual noise.
- Beautiful pixel-art lighting and atmospheric depth.
- Strong foreground, middle-ground and background separation.
- Native vertical 9:16 portrait artwork.
- Full-bleed environment, edge to edge.
- No photorealism, 3D, vector art or smooth digital painting.
- No words, letters, numbers, captions, signage, UI or watermarks.
"""


ENVIRONMENT_PRIORITY = """
ENVIRONMENT PRIORITY:
- The environment is the main subject, not the couple.
- At least 80 percent of the composition should communicate the location.
- The couple should be relatively small, approximately 8-12 percent
  of the image height.
- Do not create a large character portrait.
- Do not automatically put the couple in the centre.
- Do not automatically make them stand side by side.
- The location must remain recognizable even without the couple.
- Use the exact physical environment described in the scene.
- Do not replace missing environmental details with generic buildings,
  village streets or cobblestone pathways.
"""


OPENING_DIRECTION = """
OPENING IMAGE:
Create a wide establishing view of the theme-world.

Show a large, memorable landscape with a distinctive landmark.
The environment should dominate the image.

The recurring couple should appear small, preferably from behind
or at a three-quarter angle, exploring the world.

This image must establish the overall theme.
It must not simply reproduce one of the four destinations.
"""


def _format_list(items):
    if not items:
        return "- No additional restrictions."

    return "\n".join(
        f"- {item}" for item in items
    )


def _choice_direction(choice):
    title = choice.get("title", "Fantasy destination")

    description = choice.get("description", "")

    scene_type = choice.get(
        "scene_type",
        "Distinct fantasy environment"
    )

    composition = choice.get("composition", "")

    camera = choice.get("camera", "")

    palette = choice.get("dominant_palette", "")

    couple_action = choice.get("couple_action", "")

    must_show = choice.get("must_show", [])

    avoid = choice.get("avoid", [])

    return f"""
DESTINATION NAME:
{title}

==================================================
1. ENVIRONMENT — MOST IMPORTANT
==================================================

{description}

This exact environment must be the dominant subject.
Do not replace it with a generic fantasy village.

==================================================
2. ENVIRONMENT CATEGORY
==================================================

{scene_type}

==================================================
3. SPATIAL COMPOSITION
==================================================

{composition}

Follow this layout carefully.

The foreground, middle-ground and background should
visually communicate the described location.

==================================================
4. CAMERA AND VIEWPOINT
==================================================

{camera}

Follow this camera instruction rather than using
a default front-facing character composition.

==================================================
5. DOMINANT COLOUR PALETTE
==================================================

{palette}

Use this palette for the environment.

Do not automatically reuse the same navy-blue,
icy-blue and amber village palette.

==================================================
6. COUPLE ACTIVITY
==================================================

{couple_action}

The couple must be small and naturally integrated
into the location.

Preserve their signature clothing and appearance.

==================================================
7. REQUIRED ENVIRONMENTAL FEATURES
==================================================

{_format_list(must_show)}

These features must be clearly visible.

==================================================
8. FORBIDDEN ELEMENTS
==================================================

{_format_list(avoid)}

==================================================
9. FINAL VISUAL REQUIREMENT
==================================================

Create a distinctive pixel-art game environment.

The environment must dominate the artwork.

Do not create:
- A generic medieval village street.
- Two rows of symmetrical timber houses.
- A central cobblestone pathway.
- A large standing couple in the foreground.
- Unrequested snow or winter scenery.
- Generic buildings as filler.

Only include these elements if the destination
description explicitly requires them.
"""


def build_prompt(description, opening=False, choice=None):

    if opening:

        if isinstance(description, dict):
            environment = description.get(
                "environment",
                description.get("description", "")
            )

            camera = description.get(
                "camera",
                "Wide establishing landscape view."
            )

            couple_action = description.get(
                "couple_action",
                "The couple explores the landscape."
            )

        else:
            environment = description
            camera = "Wide establishing landscape view."
            couple_action = (
                "The couple explores the landscape, "
                "seen small from behind."
            )

        scene = f"""
{OPENING_DIRECTION}

THEME ENVIRONMENT:
{environment}

CAMERA:
{camera}

COUPLE ACTIVITY:
{couple_action}
"""

    elif choice is not None:

        scene = _choice_direction(choice)

    else:

        scene = f"""
DESTINATION ENVIRONMENT:
{description}

{CHARACTER_REFERENCE}

The environment must dominate the artwork.
The couple must remain small and naturally integrated.
"""

    # Important: The environment-specific prompt is placed BEFORE
    # the shared visual style so that the scene remains the focus.
    return "\n\n".join([
        scene,
        ENVIRONMENT_PRIORITY,
        CHARACTER_REFERENCE,
        BASE_STYLE,
        PIXEL_ART_QUALITY,
    ]).strip()
