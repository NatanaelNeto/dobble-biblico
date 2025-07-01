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

def aplicar_sombra(figura: Image, offset=(4, 4), blur_radius=6, cor_sombra=(0, 0, 0, 100)) -> Image:
    # Cria imagem do tamanho da figura + offset (para acomodar sombra)
    largura = figura.width + abs(offset[0]) + blur_radius * 2
    altura = figura.height + abs(offset[1]) + blur_radius * 2
    base = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))

    # Cria a sombra a partir do canal alpha da figura
    sombra = Image.new("RGBA", figura.size, cor_sombra)
    alpha = figura.split()[-1]
    sombra.putalpha(alpha)

    # Posição da sombra (deslocada + padding do blur)
    pos_sombra = (blur_radius + offset[0], blur_radius + offset[1])
    base.paste(sombra, pos_sombra, sombra)

    # Aplica blur para suavizar a sombra
    base = base.filter(ImageFilter.GaussianBlur(blur_radius))

    # Posição da figura (colada acima da sombra, centralizada)
    pos_figura = (blur_radius, blur_radius)
    base.paste(figura, pos_figura, figura)

    return base


def desenhar_texto_inferior(imagem: Image.Image, numero_carta: int, titulo: str = "Tá Ali!"):
    draw = ImageDraw.Draw(imagem)
    
    try:
        fonte = ImageFont.truetype("fonts/oldenburg.ttf", 24)
    except:
        fonte = ImageFont.load_default()

    texto_esquerda = f"{numero_carta:02d}"
    texto_direita = titulo

    margem = 10

    # Inferior esquerdo
    draw.text((AREA_UTIL[0] + margem, AREA_UTIL[3] - 30), texto_esquerda, fill="#222428", font=fonte)

    # Inferior direito
    bbox = fonte.getbbox(texto_direita)
    largura_texto = bbox[2] - bbox[0]
    draw.text((AREA_UTIL[2] - largura_texto - margem, AREA_UTIL[3] - 30), texto_direita, fill="#222428", font=fonte)
