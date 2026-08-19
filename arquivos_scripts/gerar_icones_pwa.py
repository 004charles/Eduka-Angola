from pathlib import Path

from PIL import Image

DESTINATION = Path(__file__).resolve().parents[1] / "frontend" / "public" / "icons"
SOURCE = Path(__file__).resolve().parents[1] / "frontend" / "public" / "eduka-mark.png"
SIZES = (72, 96, 128, 144, 152, 192, 384, 512)


def make_icon(size):
    with Image.open(SOURCE) as source:
        return source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)


def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Marca oficial não encontrada: {SOURCE}")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        make_icon(size).save(DESTINATION / f"icon-{size}x{size}.png", "PNG", optimize=True)


if __name__ == "__main__":
    main()
