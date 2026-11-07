
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
HISTORY_PATH = ROOT / "config" / "story_history.json"


def _recent_history():
    if not HISTORY_PATH.exists():
        return []

    try:
        value = json.loads(
            HISTORY_PATH.read_text(encoding="utf-8")
        )
        return value[-20:] if isinstance(value, list) else []

    except (json.JSONDecodeError, OSError):
        return []


def _extract_json(text):
    """Extract a complete JSON object from the model response."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Groq returned an empty message.")

    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        result = json.loads(cleaned)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")

    if start < 0:
        raise ValueError("No JSON object found.")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(cleaned)):

        char = cleaned[index]

        if in_string:

            if escaped:
                escaped = False

            elif char == "\\":
                escaped = True

            elif char == '"':
                in_string = False

        else:

            if char == '"':
                in_string = True

            elif char == "{":
                depth += 1

            elif char == "}":
                depth -= 1

                if depth == 0:
                    candidate = cleaned[start:index + 1]
                    result = json.loads(candidate)

                    if isinstance(result, dict):
                        return result

    raise ValueError(
        "Groq returned incomplete JSON. "
        "The response may have been truncated."
    )


def _validate_story(data):

    if not isinstance(data, dict):
        raise ValueError("Story must be a JSON object.")

    choices = data.get("choices")

    if not isinstance(choices, list) or len(choices) != 4:
        raise ValueError(
            "Exactly four choices are required."
        )

    required_fields = [
        "title",
        "description",
        "scene_type",
        "composition",
        "camera",
        "dominant_palette",
        "couple_action",
        "must_show"
    ]

    for index, choice in enumerate(choices, start=1):

        if not isinstance(choice, dict):
            raise ValueError(
                f"Choice {index} must be an object."
            )

        missing = [
            field
            for field in required_fields
            if not choice.get(field)
        ]

        if missing:
            raise ValueError(
                f"Choice {index} missing fields: {missing}"
            )

        if not isinstance(choice["must_show"], list):
            raise ValueError(
                f"Choice {index}: must_show must be a list."
            )

        if not isinstance(choice.get("avoid", []), list):
            choice["avoid"] = []

    if not data.get("theme"):
        raise ValueError("Missing theme.")

    if not data.get("question"):
        raise ValueError("Missing question.")

    if not data.get("intro_environment"):
        raise ValueError("Missing intro_environment.")

    scene_types = [
        str(c["scene_type"]).strip().casefold()
        for c in choices
    ]

    compositions = [
        str(c["composition"]).strip().casefold()
        for c in choices
    ]

    if len(set(scene_types)) != 4:
        raise ValueError(
            "The four choices must have distinct scene types."
        )

    if len(set(compositions)) != 4:
        raise ValueError(
            "The four choices must have distinct compositions."
        )

    return data


def generate_story():

    load_dotenv(ROOT / ".env")

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing from .env."
        )

    model = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )

    recent = _recent_history()

    example = {
        "theme": "Daily fantasy theme",
        "question": "Engaging opening question",
        "intro_environment": "Wide establishing landscape",
        "intro_camera": "Wide landscape camera",
        "intro_couple_action": "Couple exploring the world",
        "choices": [
            {
                "title": "Location title",
                "description": "Detailed physical environment",
                "scene_type": "Unique environment category",
                "composition": "Distinct spatial arrangement",
                "camera": "Camera angle and distance",
                "dominant_palette": "Distinct environment palette",
                "couple_action": "Natural couple activity",
                "must_show": [
                    "Feature one",
                    "Feature two",
                    "Feature three"
                ],
                "avoid": [
                    "Unwanted visual element"
                ]
            }
        ]
    }

    system_message = """
You are the creative director of CozyVerse,
a premium handcrafted 16-bit fantasy RPG world.

Create original, visually diverse fantasy environments.

Return valid JSON only.
Never use Markdown fences.
Never add explanatory text.
Complete the entire JSON response.
"""

    user_message = f"""
Create a completely new daily CozyVerse concept.

Return one valid JSON object matching this structure:

{json.dumps(example, ensure_ascii=False)}

IMPORTANT:
The choices array must contain EXACTLY FOUR complete objects.

RECENT STORIES:
{json.dumps(recent, ensure_ascii=False)}

STORY REQUIREMENTS:

- One original daily theme.
- One engaging question.
- Four distinct places to stay.
- Four physically different environments.
- Short, attractive location titles.

VISUAL DIVERSITY:

Each choice must have a different:

- scene_type
- composition
- camera
- dominant_palette

Use different environment categories.

Examples:
- Open lake
- Dense forest
- Treehouse
- Underground cavern
- Coastal cliff
- Floating island
- Flower meadow
- Observatory
- Waterfall
- Greenhouse
- Desert oasis
- Mountain sanctuary

Do not choose four variations of the same environment.

ENVIRONMENT FIRST:

The environment must occupy at least 80 percent
of each image.

The recurring couple should be small,
approximately 8-12 percent of image height.

Do not automatically place them in the centre.

Vary their pose and activity according to the scene.

The environment must remain recognizable
even without the couple.

OPENING IMAGE:

Create a wide establishing view of the overall theme.

Do not copy any of the four destinations.

Show the couple small, exploring the world.

AVOID GENERIC REPETITION:

Do not automatically generate:
- Snow-covered villages
- Medieval timber houses
- Cobblestone streets
- Symmetrical buildings
- Central standing couples
- Identical blue-and-amber palettes

Only use these when the actual theme requires them.

JSON RULES:

- Use double quotes.
- No trailing commas.
- Use arrays for must_show and avoid.
- Exactly four choice objects.
- Complete every string and object.
- Return nothing outside the JSON.
"""

    print(f"\nGenerating story using Groq model: {model}")

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",

        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },

        json={
            "model": model,
            "temperature": 0.8,
            "top_p": 0.9,

            # Give the model sufficient room to finish
            # all four detailed scene descriptions.
            "max_completion_tokens": 8192,

            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },

        timeout=120
    )

    if not response.ok:
        raise RuntimeError(
            f"Groq API error {response.status_code}: "
            f"{response.text[:1500]}"
        )

    try:
        result = response.json()

        message = result["choices"][0]["message"]["content"]

        finish_reason = result["choices"][0].get(
            "finish_reason"
        )

    except (KeyError, IndexError, TypeError) as exc:

        raise RuntimeError(
            f"Unexpected Groq response: {response.text[:1000]}"
        ) from exc

    # Detect token-limit truncation before attempting JSON parsing.
    if finish_reason == "length":
        raise RuntimeError(
            "Groq stopped because the completion-token limit "
            "was reached. Increase max_completion_tokens."
        )

    try:
        story = _extract_json(message)

    except (ValueError, json.JSONDecodeError) as exc:

        raise RuntimeError(
            "Groq returned incomplete or invalid JSON.\n"
            f"Finish reason: {finish_reason}\n"
            f"Parse error: {exc}\n"
            f"Response excerpt: {str(message)[:1200]}"
        ) from exc

    return _validate_story(story)


def save_story_history(story):

    HISTORY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    history = _recent_history()

    history.append({
        "theme": story["theme"],
        "question": story["question"],
        "locations": [
            choice["title"]
            for choice in story["choices"]
        ]
    })

    HISTORY_PATH.write_text(
        json.dumps(
            history[-30:],
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )
