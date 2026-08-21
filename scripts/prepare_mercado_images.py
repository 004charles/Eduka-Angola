from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path("/home/ubuntu/webdev-static-assets")
TARGET_DIR = ROOT / "static" / "assets" / "images" / "product" / "mercado"

ASSETS = {
    "mercado-laptop-estudante.png": "portatil-estudo.webp",
    "mercado-livros-estudo.png": "livros-estudo.webp",
    "mercado-mochila-estudo.png": "mochila-estudo.webp",
}


def preparar_imagem(origem: Path, destino: Path) -> None:
    with Image.open(origem) as original:
        imagem = original.convert("RGB")
        imagem.thumbnail((860, 860), Image.Resampling.LANCZOS)
        quadro = Image.new("RGB", (900, 900), "#f8faf8")
        posicao = ((900 - imagem.width) // 2, (900 - imagem.height) // 2)
        quadro.paste(imagem, posicao)
        quadro.save(destino, "WEBP", quality=84, method=6)


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    for origem_nome, destino_nome in ASSETS.items():
        origem = SOURCE_DIR / origem_nome
        if not origem.exists():
            raise FileNotFoundError(f"Imagem de origem ausente: {origem}")
        destino = TARGET_DIR / destino_nome
        preparar_imagem(origem, destino)
        print(f"Preparada: {destino.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
