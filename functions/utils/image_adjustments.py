from PIL import Image
import random

from functions.utils.get_bounding_box import obter_bounding_box_opaco

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

def compactar_conteudo(imagem: Image) -> Image:
    bbox = obter_bounding_box_opaco(imagem)
    if not bbox:
        return imagem

    conteudo = imagem.crop(bbox)
    nova_imagem = Image.new("RGBA", imagem.size, (255, 255, 255, 0)) # Fundo branco transparente

    # Calcular as distâncias do conteúdo atual para os limites da AREA_UTIL
    # As coordenadas de bbox são relativas à imagem original.
    # Precisamos considerar a posição de bbox em relação à AREA_UTIL.
    
    # Coordenadas do conteúdo dentro da imagem total (relativas a 0,0 da imagem)
    conteudo_x0, conteudo_y0, conteudo_x1, conteudo_y1 = bbox

    # Distâncias do conteúdo para os limites da AREA_UTIL
    dist_left = conteudo_x0 - AREA_UTIL[0]
    dist_right = AREA_UTIL[2] - conteudo_x1
    dist_top = conteudo_y0 - AREA_UTIL[1]
    dist_bottom = AREA_UTIL[3] - conteudo_y1

    # Determinar a nova posição (novo_x, novo_y) para alinhar à borda mais próxima
    # Horizontal
    if dist_left <= dist_right: # Conteúdo está mais próximo ou equidistante da borda esquerda
        novo_x = AREA_UTIL[0]
    else: # Conteúdo está mais próximo da borda direita
        novo_x = AREA_UTIL[2] - conteudo.width

    # Vertical
    if dist_top <= dist_bottom: # Conteúdo está mais próximo ou equidistante da borda superior
        novo_y = AREA_UTIL[1]
    else: # Conteúdo está mais próximo da borda inferior
        novo_y = AREA_UTIL[3] - conteudo.height
    
    nova_imagem.paste(conteudo, (novo_x, novo_y), conteudo)
    return nova_imagem


def expandir_conteudo(imagem: Image) -> Image:
    bbox = obter_bounding_box_opaco(imagem)
    if not bbox:
        return imagem

    conteudo = imagem.crop(bbox)
    largura_conteudo = conteudo.width
    altura_conteudo = conteudo.height

    largura_util = AREA_UTIL[2] - AREA_UTIL[0]
    altura_util = AREA_UTIL[3] - AREA_UTIL[1]

    # Calcula a maior escala possível sem ultrapassar os limites
    escala_x = largura_util / largura_conteudo
    escala_y = altura_util / altura_conteudo
    escala = min(escala_x, escala_y)

    nova_largura = int(largura_conteudo * escala)
    nova_altura = int(altura_conteudo * escala)

    conteudo_redimensionado = conteudo.resize((nova_largura, nova_altura), Image.LANCZOS)


    # Alinhamento: centralizar o conteúdo redimensionado dentro da área útil
    # Calcula o espaço restante horizontalmente e divide por 2 para centralizar
    offset_x = AREA_UTIL[0] + (largura_util - nova_largura) // 2
    # Calcula o espaço restante verticalmente e divide por 2 para centralizar
    offset_y = AREA_UTIL[1] + (altura_util - nova_altura) // 2

    nova_imagem = Image.new("RGBA", imagem.size, (255, 255, 255, 255)) # Fundo branco transparente
    nova_imagem.paste(conteudo_redimensionado, (offset_x, offset_y), conteudo_redimensionado)
    return nova_imagem