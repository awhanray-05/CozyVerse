
import base64
import os
import time
import secrets

from pathlib import Path
from io import BytesIO

import requests

from dotenv import load_dotenv
from PIL import Image


load_dotenv()


ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

MODEL = os.getenv(
    "CLOUDFLARE_MODEL",
    "@cf/black-forest-labs/flux-2-klein-9b",
)

IMAGE_WIDTH = 864
IMAGE_HEIGHT = 1536

API_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/"
    f"{ACCOUNT_ID}/ai/run/{MODEL}"
)


def validate_configuration():

    if not ACCOUNT_ID:
        raise ValueError(
            "CLOUDFLARE_ACCOUNT_ID is missing from .env"
        )

    if not API_TOKEN:
        raise ValueError(
            "CLOUDFLARE_API_TOKEN is missing from .env"
        )


def extract_image_bytes(response):

    content_type = response.headers.get(
        "Content-Type", ""
    ).lower()

    if content_type.startswith("image/"):
        return response.content

    try:
        payload = response.json()

    except ValueError:
        raise RuntimeError(
            "Cloudflare returned an unrecognized response:\n"
            + response.text[:1000]
        )

    if payload.get("success") is False:
        raise RuntimeError(
            f"Cloudflare API error: {payload.get('errors')}"
        )

    result = payload.get("result", payload)

    image_data = (
        result.get("image")
        or result.get("data")
    )

    if isinstance(image_data, str):

        if image_data.startswith("data:image"):
            image_data = image_data.split(",", 1)[1]

        return base64.b64decode(image_data)

    raise RuntimeError(
        "No image data was found in Cloudflare's response."
    )


def validate_generated_image(image_bytes):

    try:
        image = Image.open(BytesIO(image_bytes))
        image.verify()

        image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

    except Exception as exc:
        raise RuntimeError(
            f"Generated response is not a valid image: {exc}"
        )

    width, height = image.size

    actual_ratio = width / height
    expected_ratio = 9 / 16

    if abs(actual_ratio - expected_ratio) > 0.01:
        raise RuntimeError(
            f"Unexpected image dimensions: {width}x{height}. "
            "Expected a 9:16 portrait image."
        )

    return image


def generate_image(
    prompt: str,
    output_path: str | Path,
    seed: int | None = None,
    retries: int = 3,
):

    validate_configuration()

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_path.exists():
        print(f"Image already exists: {output_path}")
        return output_path

    # Generate a different random seed for each image
    # unless the caller explicitly supplies one.
    if seed is None:
        seed = secrets.randbelow(2**31 - 1)

    print(f"Using image seed: {seed}")

    form_data = {
        "prompt": prompt,
        "width": str(IMAGE_WIDTH),
        "height": str(IMAGE_HEIGHT),
        "guidance": "3.5",
        "seed": str(seed),
    }

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }

    last_error = None

    for attempt in range(1, retries + 1):

        try:

            print(
                f"Generating image "
                f"(attempt {attempt}/{retries})..."
            )

            multipart_fields = {
                key: (None, value)
                for key, value in form_data.items()
            }

            response = requests.post(
                API_URL,
                headers=headers,
                files=multipart_fields,
                timeout=300,
            )

            if not response.ok:
                raise RuntimeError(
                    f"Cloudflare HTTP {response.status_code}: "
                    f"{response.text[:1500]}"
                )

            image_bytes = extract_image_bytes(response)

            image = validate_generated_image(image_bytes)

            image.save(
                output_path,
                format="PNG",
                optimize=True,
            )

            print(
                f"Saved: {output_path} "
                f"({image.width}x{image.height})"
            )

            return output_path

        except Exception as exc:

            last_error = exc

            print(f"Generation failed: {exc}")

            if attempt < retries:

                wait_seconds = attempt * 5

                print(
                    f"Retrying in {wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

    raise RuntimeError(
        f"Image generation failed after {retries} attempts: "
        f"{last_error}"
    )
