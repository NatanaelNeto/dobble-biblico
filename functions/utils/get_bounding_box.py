from PIL import Image

# Função auxiliar: considera apenas a parte opaca (visível)
def obter_bounding_box_opaco(imagem: Image):
    alpha = imagem.split()[-1]
    # Torna tudo com alpha <= 10 totalmente transparente para evitar falsos limites
    threshold = 10
    alpha = alpha.point(lambda p: 255 if p > threshold else 0)
    return alpha.getbbox()