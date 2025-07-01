import os
import re

from functions.card_generator import gerar_imagem_carta
from functions.read_card_file import ler_cartas_do_arquivo

# Caminho da pasta com as figuras
PASTA_FIGURAS = "figuras"
PASTA_SAIDA = "out"

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

# carta_teste = next((c for c in cartas if c["id"] == 1), None)
# if carta_teste:
#     imagem_carta = gerar_imagem_carta(figuras, carta_teste)
#     imagem_carta.show()  # Abre a imagem em um visualizador
#     imagem_carta.save("carta_01.png")  # Salva como teste

def print_cartas(lista):
    for item in lista:
        carta = next((c for c in cartas if c["id"] == item), None)
        if carta:
            imagem_carta = gerar_imagem_carta(figuras, carta)
            imagem_carta.save(f"out/carta_{carta["id"]:02d}.png")

print_cartas([23,24])