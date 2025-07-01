from PIL import Image
import random

from functions.utils.image_adjustments import compactar_conteudo, expandir_conteudo
from functions.utils.image_enhancements import aplicar_sombra, desenhar_texto_inferior

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
ESCALA_NORMAL = 0.65
ESCALA_MINIMA = 0.2
ESCALA_DECRESCENTE = 0.9
ESCALA_AJUSTE = 0.65
MAX_TENTATIVAS = 600

def gerar_imagem_carta(figuras_disponiveis, carta):
    print(f"Imprimindo carta {carta["id"]}...")
    imagem = Image.new("RGBA", (LARGURA_CARTA_PX, ALTURA_CARTA_PX), (255, 255, 255, 0))
    posicoes_ocupadas = []

    # draw = ImageDraw.Draw(imagem)
    # x0, y0, x1, y1 = AREA_UTIL
    # draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=(0, 255, 255, 80))  # Ciano translúcido

    figuras_a_processar = list(carta["figuras"])
    numero_dominante = carta["dominante"]
    if numero_dominante in figuras_a_processar:
        figuras_a_processar.remove(numero_dominante)
        # Insere a figura dominante no início da lista para ser processada primeiro
        figuras_a_processar.insert(0, numero_dominante)
    else:
        print(f"⚠️ Figura dominante {numero_dominante:02d} não encontrada na lista de figuras da carta. Processando todas as figuras normalmente.")


    for numero in figuras_a_processar:
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

            figura_tentativa = imagem_original.rotate(random.randint(0, 90), resample=Image.BICUBIC, expand=True).resize(
                (int(imagem_original.width * escala * ESCALA_AJUSTE),
                 int(imagem_original.height * escala * ESCALA_AJUSTE)),
                Image.LANCZOS
            )

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
                sombra = aplicar_sombra(figura_tentativa)
                imagem.paste(sombra, (x, y), sombra)
                # imagem.paste(figura_tentativa, (x, y), figura_tentativa)
                posicoes_ocupadas.append(nova_bbox)
                sucesso = True
                break

        # Se falhar, compacta o que já foi colocado e faz varredura final
        if not sucesso:
            print(f"Iniciando varredura da figura {numero:02d}")
            # imagem = compactar_conteudo(imagem)
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
                        sombra = aplicar_sombra(figura_tentativa)
                        imagem.paste(sombra, (x, y), sombra)
                        # imagem.paste(figura_tentativa, (x, y), figura_tentativa)
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
    desenhar_texto_inferior(imagem, carta["id"])
    return imagem