"""Reduz o peso das capas da Biblioteca sem alterar a proporção editorial."""
from pathlib import Path
from PIL import Image


CAPAS_DIR = Path(__file__).resolve().parent.parent / "media" / "biblioteca" / "capas"


def run():
    for source in CAPAS_DIR.glob("*.jpg"):
        with Image.open(source) as image:
            image = image.convert("RGB")
            image.thumbnail((900, 1350), Image.Resampling.LANCZOS)
            image.save(source, "JPEG", quality=84, optimize=True, progressive=True)
            print(f"Optimizada: {source.name} ({image.width}×{image.height})")


if __name__ == "__main__":
    run()
