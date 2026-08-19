from pathlib import Path
from PIL import Image, ImageDraw

DESTINATION = Path(__file__).resolve().parents[1] / "frontend" / "public" / "icons"
SIZES = (72, 96, 128, 144, 152, 192, 384, 512)


def rounded_rectangle(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def make_icon(size):
    image = Image.new("RGBA", (size, size), "#6425e8")
    draw = ImageDraw.Draw(image)
    pad = round(size * 0.105)
    roundness = round(size * 0.22)
    rounded_rectangle(draw, (pad, pad, size - pad, size - pad), roundness, "#7d43ef")

    # Livro aberto com marca de progresso: legível até em 72 px.
    left = round(size * 0.255)
    right = round(size * 0.745)
    top = round(size * 0.29)
    bottom = round(size * 0.73)
    spine = size // 2
    stroke = max(3, round(size * 0.052))
    draw.line((left, top, spine, round(size * 0.41), right, top), fill="white", width=stroke, joint="curve")
    draw.line((left, top, left, bottom, spine, round(size * 0.85), right, bottom, right, top), fill="white", width=stroke, joint="curve")
    draw.line((spine, round(size * 0.41), spine, round(size * 0.85)), fill="white", width=stroke)
    check = [
        (round(size * 0.36), round(size * 0.60)),
        (round(size * 0.45), round(size * 0.69)),
        (round(size * 0.64), round(size * 0.49)),
    ]
    draw.line(check, fill="white", width=stroke, joint="curve")
    return image


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for size in SIZES:
        make_icon(size).save(DESTINATION / f"icon-{size}x{size}.png", "PNG", optimize=True)


if __name__ == "__main__":
    main()
