# CozyVerse Dynamic Daily Pipeline

This integration preserves the existing Cloudflare image generator, `BASE_STYLE`,
character reference, pixelation pipeline, Silkscreen font assets and music asset.
The winter collection remains in `src/generator/scenes.py` as a reference; the
new daily pipeline does not use its hardcoded scene list.

## One-time setup

1. Keep your existing `.env` file and Cloudflare credentials.
2. Add these two lines to `.env`:
   `GROQ_API_KEY=your_groq_api_key`
   `GROQ_MODEL=llama-3.3-70b-versatile`
3. Install requirements if needed: `pip install -r requirements.txt`
4. Ensure FFmpeg is installed and available on Windows PATH.

## Run

From the project root:
`python main.py`

The pipeline generates one AI story (theme, question, four distinct choices),
five images using your existing Cloudflare generator and style prompt, pixelates
them with your existing function, and renders a 17-second 1080x1920 Reel at 30 FPS.

## Output

- `output/daily/YYYY-MM-DD_theme/story.json`
- `output/daily/YYYY-MM-DD_theme/raw/` (original generated artwork)
- `output/daily/YYYY-MM-DD_theme/images/` (pixelated 1080x1920 artwork)
- `output/videos/daily/cozyverse_YYYY-MM-DD.mp4`
- `config/story_history.json` (recent story concepts to reduce repetition)
- `config/music_choice.json` (persistent music selection)

The same music file is selected once and persisted. To change it deliberately,
remove `config/music_choice.json` and run again.

If a run fails partway through, existing raw/pixel images are reused on the next run.
The story history is saved only after successful video rendering.

## Notes

The original `generate_collection.py`, `scenes.py`, image generator, pixel-art
style prompt, and pixelation function are retained. The new daily path uses the
same generator and pixelation APIs without rewriting them.
