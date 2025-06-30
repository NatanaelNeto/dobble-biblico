import re
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
