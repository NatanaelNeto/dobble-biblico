import os
import re
from PIL import Image, ImageDraw
import random

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

# Caminho da pasta com as figuras
PASTA_FIGURAS = "figuras"

# Regex para capturar número e nome da figura no padrão: "01_nome-da-figura.png"
PADRAO_ARQUIVO = re.compile(r"(\d{2})_(.+)\.png")

# Lista para armazenar as figuras encontradas
figuras = []

# Verifica se a pasta existe
if not os.path.isdir(PASTA_FIGURAS):
    print(f"Erro: pasta '{PASTA_FIGURAS}' não encontrada.")
else:
    for arquivo in os.listdir(PASTA_FIGURAS):
        match = PADRAO_ARQUIVO.match(arquivo)
        if match:
            numero = int(match.group(1))
            nome = match.group(2).replace("-", " ").capitalize()
            caminho = os.path.join(PASTA_FIGURAS, arquivo)
            figuras.append({
                "numero": numero,
                "nome": nome,
                "arquivo": arquivo,
                "caminho": caminho
            })

# Função ler_cartas
def ler_cartas_do_arquivo(caminho_arquivo):
    cartas = []
    padrao_figura_dominante = re.compile(r"\((\d{2})\)$")  # Captura o número entre parênteses no final da linha

    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or ":" not in linha:
                continue

            id_carta, conteudo = linha.split(":")
            id_carta = int(id_carta.strip())

            # Extrair figura dominante (número entre parênteses)
            match = padrao_figura_dominante.search(conteudo)
            if not match:
                print(f"Aviso: Carta {id_carta:02d} está sem figura dominante definida corretamente.")
                continue

            figura_dominante = int(match.group(1))

            # Remove os parênteses e separa os demais números
            conteudo_sem_dominante = padrao_figura_dominante.sub("", conteudo).strip()
            numeros_figuras = [int(n.strip()) for n in conteudo_sem_dominante.split(",") if n.strip()]

            if figura_dominante not in numeros_figuras:
                print(f"Erro: Figura dominante {figura_dominante} não está presente na carta {id_carta:02d}.")
                continue

            cartas.append({
                "id": id_carta,
                "figuras": numeros_figuras,
                "dominante": figura_dominante
            })
    
    return cartas


# def gerar_imagem_carta(figuras_disponiveis, carta):
#     imagem = Image.new("RGBA", (LARGURA_CARTA_PX, ALTURA_CARTA_PX), (255, 255, 255, 255))
#     posicoes_ocupadas = []

#     for numero in carta["figuras"]:
#         figura_info = next((f for f in figuras_disponiveis if f["numero"] == numero), None)
#         if not figura_info:
#             print(f"Figura {numero:02d} não encontrada. Pulando...")
#             continue

#         imagem_original = Image.open(figura_info["caminho"]).convert("RGBA")

#         escala = ESCALA_DOMINANTE if numero == carta["dominante"] else ESCALA_NORMAL
#         sucesso = False

#         while escala >= ESCALA_MINIMA and not sucesso:
#             figura = imagem_original.copy()
#             # Redimensiona a figura proporcionalmente
#             nova_largura = int(imagem_original.width * escala)
#             nova_altura = int(imagem_original.height * escala)

#             # Verifica se a figura cabe na área útil, senão reduz a escala
#             while (
#                 nova_largura > (AREA_UTIL[2] - AREA_UTIL[0]) or
#                 nova_altura > (AREA_UTIL[3] - AREA_UTIL[1])
#             ) and escala > ESCALA_MINIMA:
#                 escala *= ESCALA_DECRESCENTE
#                 nova_largura = int(imagem_original.width * escala * ESCALA_AJUSTE)
#                 nova_altura = int(imagem_original.height * escala * ESCALA_AJUSTE)

#             # Se mesmo assim não couber, desiste
#             if escala < ESCALA_MINIMA:
#                 print(f"⚠️ Figura {numero:02d} é grande demais mesmo após reduzir a escala. Pulando.")
#                 continue

#             figura = imagem_original.resize((nova_largura, nova_altura), Image.LANCZOS)


#             angulo = random.randint(0, 90)
#             figura = figura.rotate(angulo, expand=True)

#             alpha = figura.split()[-1]
#             bbox_alpha = alpha.getbbox()

#             if not bbox_alpha:
#                 print(f"Figura {numero:02d} parece estar completamente transparente.")
#                 break

#             for _ in range(400):
#                 max_x = AREA_UTIL[2] - figura.width
#                 max_y = AREA_UTIL[3] - figura.height
#                 min_x = AREA_UTIL[0]
#                 min_y = AREA_UTIL[1]

#                 # Se a figura ainda estiver grande demais, nem tenta posicionar
#                 if max_x < min_x or max_y < min_y:
#                     escala *= ESCALA_DECRESCENTE
#                     break  # vai sair do loop de tentativas, e a escala será reduzida

#                 x = random.randint(min_x, max_x)
#                 y = random.randint(min_y, max_y)
#                 nova_bbox = (x + bbox_alpha[0], y + bbox_alpha[1], x + bbox_alpha[2], y + bbox_alpha[3])

#                 sobreposicao = any(
#                     not (
#                         nova_bbox[2] < bbox[0] or
#                         nova_bbox[0] > bbox[2] or
#                         nova_bbox[3] < bbox[1] or
#                         nova_bbox[1] > bbox[3]
#                     )
#                     for bbox in posicoes_ocupadas
#                 )

#                 if not sobreposicao:
#                     imagem.paste(figura, (x, y), figura)
#                     posicoes_ocupadas.append(nova_bbox)
#                     sucesso = True
#                     break

#             if not sucesso:
#                 escala *= ESCALA_DECRESCENTE  # Reduz a escala para tentar novamente

#         if not sucesso:
#             print(f"⚠️ Aviso: Não foi possível posicionar a figura {numero:02d} na carta {carta['id']:02d}")

#     return imagem

# ---------------------------------------------------------------------------------------------------------------------

# # Função de reposicionamento
# def compactar_conteudo(imagem: Image) -> Image:
#     bbox = imagem.getbbox()
#     if not bbox:
#         return imagem  # Nada posicionado ainda

#     conteudo = imagem.crop(bbox)
#     nova_imagem = Image.new("RGBA", imagem.size, (255, 255, 255, 255))

#     # Decide se alinha à esquerda/direita e topo/base com base em onde tem mais espaço
#     left_margin = bbox[0] - AREA_UTIL[0]
#     right_margin = AREA_UTIL[2] - bbox[2]
#     top_margin = bbox[1] - AREA_UTIL[1]
#     bottom_margin = AREA_UTIL[3] - bbox[3]

#     novo_x = AREA_UTIL[0] if left_margin >= right_margin else AREA_UTIL[2] - conteudo.width
#     novo_y = AREA_UTIL[1] if top_margin >= bottom_margin else AREA_UTIL[3] - conteudo.height

#     nova_imagem.paste(conteudo, (novo_x, novo_y), conteudo)
#     return nova_imagem


# def obter_bounding_box_opaco(imagem: Image) -> tuple[int, int, int, int] | None:
#     alpha = imagem.split()[-1]
#     return alpha.getbbox()


# # Função de maximização de espaço útil
# def expandir_conteudo(imagem: Image) -> Image:
#     bbox = imagem.getbbox()
#     if not bbox:
#         return imagem

#     conteudo = imagem.crop(bbox)
#     largura_conteudo = conteudo.width
#     altura_conteudo = conteudo.height

#     largura_util = AREA_UTIL[2] - AREA_UTIL[0]
#     altura_util = AREA_UTIL[3] - AREA_UTIL[1]

#     escala_x = largura_util / largura_conteudo
#     escala_y = altura_util / altura_conteudo
#     escala = min(escala_x, escala_y)

#     nova_largura = int(largura_conteudo * escala)
#     nova_altura = int(altura_conteudo * escala)

#     conteudo_redimensionado = conteudo.resize((nova_largura, nova_altura), Image.LANCZOS)

#     nova_imagem = Image.new("RGBA", imagem.size, (255, 255, 255, 255))

#     # Centraliza dentro da área útil
#     offset_x = AREA_UTIL[0] + (largura_util - nova_largura) // 2
#     offset_y = AREA_UTIL[1] + (altura_util - nova_altura) // 2

#     nova_imagem.paste(conteudo_redimensionado, (offset_x, offset_y), conteudo_redimensionado)
#     return nova_imagem


# # Função para criar as cartas propriamente ditas
# def gerar_imagem_carta(figuras_disponiveis, carta):
#     imagem = Image.new("RGBA", (LARGURA_CARTA_PX, ALTURA_CARTA_PX), (255, 255, 255, 255))
#     posicoes_ocupadas = []

#     for numero in carta["figuras"]:
#         figura_info = next((f for f in figuras_disponiveis if f["numero"] == numero), None)
#         if not figura_info:
#             print(f"Figura {numero:02d} não encontrada. Pulando...")
#             continue

#         imagem_original = Image.open(figura_info["caminho"]).convert("RGBA")

#         escala = ESCALA_DOMINANTE if numero == carta["dominante"] else ESCALA_NORMAL
#         sucesso = False

#         # Reduz a escala até a imagem caber
#         while (
#             imagem_original.width * escala > (AREA_UTIL[2] - AREA_UTIL[0]) or
#             imagem_original.height * escala > (AREA_UTIL[3] - AREA_UTIL[1])
#         ) and escala > ESCALA_MINIMA:
#             escala *= ESCALA_DECRESCENTE

#         if escala < ESCALA_MINIMA:
#             print(f"⚠️ Figura {numero:02d} é grande demais mesmo após reduzir a escala. Pulando.")
#             continue

#         # Redimensiona e gira
#         figura = imagem_original.resize(
#             (int(imagem_original.width * escala * ESCALA_AJUSTE), int(imagem_original.height * escala * ESCALA_AJUSTE)),
#             Image.LANCZOS
#         ).rotate(random.randint(0, 90), expand=True)

#         alpha = figura.split()[-1]
#         bbox_alpha = alpha.getbbox()

#         if not bbox_alpha:
#             print(f"Figura {numero:02d} está completamente transparente.")
#             continue

#         max_x = AREA_UTIL[2] - int(figura.width)
#         max_y = AREA_UTIL[3] - int(figura.height)
#         min_x = AREA_UTIL[0]
#         min_y = AREA_UTIL[1]

#         if max_x < min_x or max_y < min_y:
#             print(f"⚠️ Figura {numero:02d} não cabe fisicamente na carta. Pulando.")
#             continue

#         # Tenta aleatoriamente por algumas vezes
#         tentativas = 0

#         print(f"Tentando posicionar a figura {numero:02d}...")

#         while not sucesso and escala >= ESCALA_MINIMA and tentativas < MAX_TENTATIVAS:
#             tentativas += 1

#             # Redimensiona e rotaciona a cada tentativa
#             figura_tentativa = imagem_original.resize(
#                 (int(imagem_original.width * escala * ESCALA_AJUSTE),
#                 int(imagem_original.height * escala * ESCALA_AJUSTE)),
#                 Image.LANCZOS
#             ).rotate(random.randint(0, 90), expand=True)

#             alpha_tentativa = figura_tentativa.split()[-1]
#             bbox_alpha = alpha_tentativa.getbbox()

#             if not bbox_alpha:
#                 print(f"Figura {numero:02d} está completamente transparente.")
#                 break

#             max_x = AREA_UTIL[2] - figura_tentativa.width
#             max_y = AREA_UTIL[3] - figura_tentativa.height

#             if max_x < min_x or max_y < min_y:
#                 escala *= ESCALA_DECRESCENTE
#                 continue

#             x = random.randint(min_x, max_x)
#             y = random.randint(min_y, max_y)

#             nova_bbox = (
#                 x + bbox_alpha[0],
#                 y + bbox_alpha[1],
#                 x + bbox_alpha[2],
#                 y + bbox_alpha[3]
#             )

#             sobreposicao = any(
#                 not (
#                     nova_bbox[2] < bbox[0] or
#                     nova_bbox[0] > bbox[2] or
#                     nova_bbox[3] < bbox[1] or
#                     nova_bbox[1] > bbox[3]
#                 )
#                 for bbox in posicoes_ocupadas
#             )

#             if not sobreposicao:
#                 print(f"Figura {numero:02d} posicionada com sucesso!")
#                 imagem.paste(figura_tentativa, (x, y), figura_tentativa)
#                 posicoes_ocupadas.append(nova_bbox)
#                 sucesso = True
#                 break

#         # Se esgotar tentativas, faz varredura final com última versão da imagem
#         # Se ainda não conseguiu, faz uma varredura de cima pra baixo, esquerda pra direita

#         imagem = compactar_conteudo(imagem)
#         if not sucesso:
#             passo = 10  # em pixels
#             for y in range(min_y, max_y, passo):
#                 for x in range(min_x, max_x, passo):
#                     nova_bbox = (
#                         x + bbox_alpha[0],
#                         y + bbox_alpha[1],
#                         x + bbox_alpha[2],
#                         y + bbox_alpha[3]
#                     )

#                     sobreposicao = any(
#                         not (
#                             nova_bbox[2] < bbox[0] or
#                             nova_bbox[0] > bbox[2] or
#                             nova_bbox[3] < bbox[1] or
#                             nova_bbox[1] > bbox[3]
#                         )
#                         for bbox in posicoes_ocupadas
#                     )

#                     if not sobreposicao:
#                         imagem.paste(figura, (x, y), figura)
#                         posicoes_ocupadas.append(nova_bbox)
#                         sucesso = True
#                         break
#                 if sucesso:
#                     break

#         if not sucesso:
#             print(f"❌ Figura {numero:02d} não pôde ser posicionada mesmo com varredura.")

#     imagem = expandir_conteudo(imagem)
#     draw = ImageDraw.Draw(imagem)
#     x0, y0, x1, y1 = AREA_UTIL
#     draw.rectangle([x0, y0, x1 - 1, y1 - 1], outline="magenta", width=1)
#     return imagem

# ---------------------------------------------------------------------------------------------------------------------

# Função auxiliar: considera apenas a parte opaca (visível)
def obter_bounding_box_opaco(imagem: Image):
    alpha = imagem.split()[-1]
    # Torna tudo com alpha <= 10 totalmente transparente para evitar falsos limites
    threshold = 10
    alpha = alpha.point(lambda p: 255 if p > threshold else 0)
    return alpha.getbbox()

# Função de reposicionamento: move o conteúdo para a borda mais próxima
# def compactar_conteudo(imagem: Image) -> Image:
#     bbox = obter_bounding_box_opaco(imagem)
#     if not bbox:
#         return imagem

#     conteudo = imagem.crop(bbox)
#     nova_imagem = Image.new("RGBA", imagem.size, (255, 255, 255, 255))

#     left_margin = bbox[0] - AREA_UTIL[0]
#     right_margin = AREA_UTIL[2] - bbox[2]
#     top_margin = bbox[1] - AREA_UTIL[1]
#     bottom_margin = AREA_UTIL[3] - bbox[3]

#     novo_x = AREA_UTIL[0] if left_margin >= right_margin else AREA_UTIL[2] - conteudo.width
#     novo_y = AREA_UTIL[1] if top_margin >= bottom_margin else AREA_UTIL[3] - conteudo.height

#     nova_imagem.paste(conteudo, (novo_x, novo_y), conteudo)
#     return nova_imagem

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

# # Função de expansão: redimensiona o conteúdo até preencher a área útil
# def expandir_conteudo(imagem: Image) -> Image:
#     bbox = obter_bounding_box_opaco(imagem)
#     if not bbox:
#         return imagem

#     conteudo = imagem.crop(bbox)
#     largura_conteudo = conteudo.width
#     altura_conteudo = conteudo.height

#     largura_util = AREA_UTIL[2] - AREA_UTIL[0]
#     altura_util = AREA_UTIL[3] - AREA_UTIL[1]

#     # Calcula a maior escala possível sem ultrapassar os limites
#     escala_x = largura_util / largura_conteudo
#     escala_y = altura_util / altura_conteudo
#     escala = min(escala_x, escala_y)

#     nova_largura = int(largura_conteudo * escala)
#     nova_altura = int(altura_conteudo * escala)

#     conteudo_redimensionado = conteudo.resize((nova_largura, nova_altura), Image.LANCZOS)

#     nova_imagem = Image.new("RGBA", imagem.size, (255, 255, 255, 255))

#     # Alinhamento: canto superior esquerdo da área útil
#     offset_x = AREA_UTIL[0]
#     offset_y = AREA_UTIL[1]

#     nova_imagem.paste(conteudo_redimensionado, (offset_x, offset_y), conteudo_redimensionado)
#     return nova_imagem

# Função de expansão: redimensiona o conteúdo até preencher a área útil e o centraliza
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


# Geração da carta
def gerar_imagem_carta(figuras_disponiveis, carta):
    imagem = Image.new("RGBA", (LARGURA_CARTA_PX, ALTURA_CARTA_PX), (255, 255, 255, 0))
    posicoes_ocupadas = []

    # draw = ImageDraw.Draw(imagem)
    # x0, y0, x1, y1 = AREA_UTIL
    # draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(0, 255, 255, 80))  # Ciano translúcido

    for numero in carta["figuras"]:
        figura_info = next((f for f in figuras_disponiveis if f["numero"] == numero), None)
        if not figura_info:
            print(f"Figura {numero:02d} não encontrada. Pulando...")
            continue

        imagem_original = Image.open(figura_info["caminho"]).convert("RGBA")

        escala = ESCALA_DOMINANTE if numero == carta["dominante"] else ESCALA_NORMAL
        sucesso = False

        while (
            imagem_original.width * escala > (AREA_UTIL[2] - AREA_UTIL[0]) or
            imagem_original.height * escala > (AREA_UTIL[3] - AREA_UTIL[1])
        ) and escala > ESCALA_MINIMA:
            escala *= ESCALA_DECRESCENTE

        if escala < ESCALA_MINIMA:
            print(f"⚠️ Figura {numero:02d} é grande demais mesmo após reduzir a escala. Pulando.")
            continue

        tentativas = 0
        print(f"Tentando posicionar a figura {numero:02d}...")

        while not sucesso and escala >= ESCALA_MINIMA and tentativas < MAX_TENTATIVAS:
            tentativas += 1

            figura_tentativa = imagem_original.resize(
                (int(imagem_original.width * escala * ESCALA_AJUSTE),
                 int(imagem_original.height * escala * ESCALA_AJUSTE)),
                Image.LANCZOS
            ).rotate(random.randint(0, 90), expand=True)

            alpha_tentativa = figura_tentativa.split()[-1]
            bbox_alpha = alpha_tentativa.getbbox()

            if not bbox_alpha:
                print(f"Figura {numero:02d} está completamente transparente.")
                break

            max_x = AREA_UTIL[2] - figura_tentativa.width
            max_y = AREA_UTIL[3] - figura_tentativa.height
            min_x = AREA_UTIL[0]
            min_y = AREA_UTIL[1]

            if max_x < min_x or max_y < min_y:
                escala *= ESCALA_DECRESCENTE
                continue

            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)

            nova_bbox = (
                x + bbox_alpha[0],
                y + bbox_alpha[1],
                x + bbox_alpha[2],
                y + bbox_alpha[3]
            )

            sobreposicao = any(
                not (
                    nova_bbox[2] < bbox[0] or
                    nova_bbox[0] > bbox[2] or
                    nova_bbox[3] < bbox[1] or
                    nova_bbox[1] > bbox[3]
                )
                for bbox in posicoes_ocupadas
            )

            if not sobreposicao:
                imagem.paste(figura_tentativa, (x, y), figura_tentativa)
                posicoes_ocupadas.append(nova_bbox)
                sucesso = True
                break

        # Se falhar, compacta o que já foi colocado e faz varredura final
        if not sucesso:
            print(f"Iniciando varredura da figura {numero:02d}")
            imagem = compactar_conteudo(imagem)
            passo = 10  # px
            for y in range(AREA_UTIL[1], AREA_UTIL[3], passo):
                for x in range(AREA_UTIL[0], AREA_UTIL[2], passo):
                    nova_bbox = (
                        x + bbox_alpha[0],
                        y + bbox_alpha[1],
                        x + bbox_alpha[2],
                        y + bbox_alpha[3]
                    )
                    sobreposicao = any(
                        not (
                            nova_bbox[2] < bbox[0] or
                            nova_bbox[0] > bbox[2] or
                            nova_bbox[3] < bbox[1] or
                            nova_bbox[1] > bbox[3]
                        )
                        for bbox in posicoes_ocupadas
                    )
                    if not sobreposicao:
                        imagem.paste(figura_tentativa, (x, y), figura_tentativa)
                        posicoes_ocupadas.append(nova_bbox)
                        sucesso = True
                        break
                if sucesso:
                    break

        if not sucesso:
            print(f"❌ Figura {numero:02d} não pôde ser posicionada mesmo com varredura.")

    # Finalização: compactar e expandir
    # imagem.show()
    # imagem.save("pre1.png")
    imagem = compactar_conteudo(imagem)
    # imagem.show()
    # imagem.save("pre2.png")
    imagem = expandir_conteudo(imagem)

    # Desenho do limite (debug visual)
    # draw = ImageDraw.Draw(imagem)
    # x0, y0, x1, y1 = AREA_UTIL
    # draw.rectangle([x0, y0, x1 - 1, y1 - 1], outline="magenta", width=1)

    return imagem


# Exibe os resultados
print(f"{len(figuras)} figuras encontradas:")
for figura in figuras:
    print(f"{figura['numero']:02d} - {figura['nome']} ({figura['arquivo']})")

# Exibe as cartas lidas
caminho_txt = "cartas.txt"
cartas = ler_cartas_do_arquivo(caminho_txt)

print("\nCartas lidas do arquivo:")
for carta in cartas:
    print(f"Carta {carta['id']:02d}: Figuras = {carta['figuras']} | Dominante = {carta['dominante']:02d}")

carta_teste = next((c for c in cartas if c["id"] == 1), None)
if carta_teste:
    imagem_carta = gerar_imagem_carta(figuras, carta_teste)
    imagem_carta.show()  # Abre a imagem em um visualizador
    imagem_carta.save("carta_01.png")  # Salva como teste