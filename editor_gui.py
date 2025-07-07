import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from functions.card_generator import gerar_imagem_carta
from functions.read_card_file import ler_cartas_do_arquivo
from functions.utils.loader import carregar_figuras


class DobbleEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Editor de Cartas Dobble")

        self.figuras = carregar_figuras("figuras")
        self.cartas = ler_cartas_do_arquivo("cartas.txt")
        self.imagem_tk = None  # Referência para manter a imagem visível

        # Layout superior
        self.frame_controle = tk.Frame(master)
        self.frame_controle.pack(pady=10)

        tk.Label(self.frame_controle, text="Número da carta:").pack(side="left", padx=5)
        self.input_numero = tk.Entry(self.frame_controle, width=5)
        self.input_numero.pack(side="left")

        self.btn_gerar = tk.Button(self.frame_controle, text="Gerar carta", command=self.gerar_carta)
        self.btn_gerar.pack(side="left", padx=10)

        # Canvas de visualização
        self.canvas = tk.Canvas(master, width=500, height=700, bg="lightgray")
        self.canvas.pack(padx=10, pady=10)

    def gerar_carta(self):
        numero = self.input_numero.get()
        print(int(numero))

        if int(numero) - 1 > self.cartas.__len__():
            # print(self.cartas)
            messagebox.showerror("Erro", f"A carta {numero} não foi encontrada no arquivo cartas.txt.")
            return

        carta = self.cartas[int(numero) - 1]
        imagem_original = gerar_imagem_carta(self.figuras, carta)

        # Reduz apenas para visualização no canvas (sem perder o original)
        largura_canvas = self.canvas.winfo_width()
        altura_canvas = self.canvas.winfo_height()

        largura_img, altura_img = imagem_original.size

        proporcao_x = largura_canvas / largura_img
        proporcao_y = altura_canvas / altura_img
        proporcao = min(proporcao_x, proporcao_y, 1)  # nunca aumenta

        nova_largura = int(largura_img * proporcao)
        nova_altura = int(altura_img * proporcao)

        imagem_visual = imagem_original.resize((nova_largura, nova_altura), Image.LANCZOS)
        self.imagem_tk = ImageTk.PhotoImage(imagem_visual)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.imagem_tk)

        # Guarda a imagem original para salvar/editar depois
        self.imagem_original = imagem_original
        
        # self.imagem_tk = ImageTk.PhotoImage(imagem_original)
        # self.canvas.delete("all")
        # self.canvas.create_image(0, 0, anchor="nw", image=self.imagem_tk)


if __name__ == "__main__":
    root = tk.Tk()
    app = DobbleEditor(root)
    root.mainloop()
