import os
from ambiente.AmbienteBase import AmbienteBase
from ambiente.Obstaculos import Obstaculo

class AmbienteMaze(AmbienteBase):
    def __init__(self, dificuldade=1):
        self.maze_matrix = self.ler_maze(str(dificuldade))
        self.largura = len(self.maze_matrix[0])
        self.altura = len(self.maze_matrix) 
        super().__init__(self.largura, self.altura, dificuldade)
        self.construir_maze()
    
    def ler_maze(self, dificuldade):
        matriz = []
        caminho_completo=os.path.join("mazes", f"dificuldade{dificuldade}.txt")
        with open(caminho_completo, "r") as f:
            for linha in f:
                linha = linha.strip()
                if linha:
                    matriz.append(linha.split(","))
        return matriz
    
    def construir_maze(self):
        for y in range(self.altura):
            for x in range(self.largura):
                if self.maze_matrix[y][x] == "X":
                    self.obstaculos.append(Obstaculo(x, y))
                elif self.maze_matrix[y][x] == "1":
                    self.farol = (x, y)
    