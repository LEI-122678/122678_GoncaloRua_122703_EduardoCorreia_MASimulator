# Em simulador/Visualizador.py
import tkinter as tk

class Visualizador:
    def __init__(self, tamanho_celula=25):
        self.tamanho = tamanho_celula
        self.janela = tk.Tk()
        self.janela.title("Simulador Multi-Agente")
        self.canvas = None

    def desenhar(self, estado: dict):
        # estado = { "largura": 10, "altura": 10, "farol": (5,5), "agentes": [(0,0), (1,1)] }
        try:
            # Verifica se a janela ainda existe
            if not self.janela.winfo_exists():
                return

            largura_px = estado["largura"] * self.tamanho
            altura_px = estado["altura"] * self.tamanho

            if self.canvas is None:
                self.canvas = tk.Canvas(self.janela, width=largura_px, height=altura_px)
                self.canvas.pack()

            self.canvas.delete("all")

            # Desenhar grelha
            for x in range(estado["largura"]):
                for y in range(estado["altura"]):
                    self.canvas.create_rectangle(x * self.tamanho, y * self.tamanho, (x+1) * self.tamanho, (y+1) * self.tamanho, fill="white", outline="lightgray")
            
            # Desenhar obstaculos
            for (ax, ay) in estado["obstaculos"]:
                self.canvas.create_rectangle(ax * self.tamanho, ay * self.tamanho, (ax+1) * self.tamanho, (ay+1) * self.tamanho, fill="black", outline="gray")

            # Desenhar farol
            fx, fy = estado["farol"]
            self.canvas.create_oval(fx * self.tamanho + 5, fy * self.tamanho + 5, (fx+1) * self.tamanho - 5, (fy+1) * self.tamanho - 5, fill="yellow")

            cores = ["blue", "red", "green", "orange", "purple", "pink"]

            # Desenhar agentes
            for i, (ax, ay) in enumerate(estado["agentes"]):
                cor = cores[i % len(cores)]  # roda a lista se houver mais agentes que cores
                self.canvas.create_oval(
                    ax * self.tamanho + 5, ay * self.tamanho + 5,
                    (ax+1) * self.tamanho - 5, (ay+1) * self.tamanho - 5,
                    fill=cor
        )
            self.canvas.update()
        except tk.TclError:
            return

    def janela_aberta(self):
            try:
                return self.janela.winfo_exists()
            except tk.TclError:
                return False