from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Tamanho da carta em pixels (300 DPI)
LARGURA_CARTA_PX = int(2.5 * 300)
ALTURA_CARTA_PX = int(3.5 * 300)
MARGEM_PX = 30  # 0.5 cm convertido para polegadas, depois para pixels

# Tamanho da área útil (sem margens)
AREA_UTIL = (
    MARGEM_PX,
    MARGEM_PX,
    LARGURA_CARTA_PX - MARGEM_PX,
    ALTURA_CARTA_PX - MARGEM_PX
)

# Tamanho relativo da figura dominante e das demais
ESCALA_DOMINANTE = 1.0
ESCALA_NORMAL = 0.6
ESCALA_MINIMA = 0.2
ESCALA_DECRESCENTE = 0.9
ESCALA_AJUSTE = 0.6
MAX_TENTATIVAS = 600

def aplicar_sombra(figura: Image, deslocamento=(5, 5), raio_blur=5, opacidade=20):
    sombra = Image.new("RGBA", figura.size, (0, 0, 0, 0))
    sombra_figura = figura.copy()

    # Torna preta com opacidade controlada
    sombra_data = []
    for pixel in sombra_figura.getdata():
        r, g, b, a = pixel
        sombra_data.append((0, 0, 0, int(opacidade * (a / 255))))  # proporcional à opacidade original
    sombra_figura.putdata(sombra_data)

    sombra.paste(sombra_figura, (0, 0), sombra_figura)
    sombra = sombra.filter(ImageFilter.GaussianBlur(radius=raio_blur))

    # Cria imagem com sombra deslocada
    imagem_sombra = Image.new("RGBA", (figura.width + deslocamento[0], figura.height + deslocamento[1]), (0, 0, 0, 0))
    imagem_sombra.paste(sombra, deslocamento, sombra)

    return imagem_sombra


def desenhar_texto_inferior(imagem: Image.Image, numero_carta: int, titulo: str = "Tá Ali!"):
    draw = ImageDraw.Draw(imagem)
    
    try:
        fonte = ImageFont.truetype("fonts/josefin.ttf", 20)
    except:
        fonte = ImageFont.load_default()

    texto_esquerda = f"{numero_carta:02d}"
    texto_direita = titulo

    margem = 10

    # Inferior esquerdo
    draw.text((AREA_UTIL[0] + margem, AREA_UTIL[3] - 30), texto_esquerda, fill="#333639", font=fonte)

    # Inferior direito
    largura_texto, _ = draw.textsize(texto_direita, font=fonte)
    draw.text((AREA_UTIL[2] - largura_texto - margem, AREA_UTIL[3] - 30), texto_direita, fill="#333639", font=fonte)
