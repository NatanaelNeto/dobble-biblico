import os
import re


PADRAO_ARQUIVO = re.compile(r"(\d{2})_(.+)\.png")

def carregar_figuras(pasta_figuras):
    figuras = []

    for arquivo in os.listdir(pasta_figuras):
        match = PADRAO_ARQUIVO.match(arquivo)
        if match:
            numero = int(match.group(1))
            nome = match.group(2).replace("-", " ").capitalize()
            caminho = os.path.join(pasta_figuras, arquivo)
            figuras.append({
                "numero": numero,
                "nome": nome,
                "arquivo": arquivo,
                "caminho": caminho
            })

    return figuras
