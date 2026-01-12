from ambiente.AmbienteBase import AmbienteBase
from ambiente.Obstaculos import Obstaculo
from agentes.Agente import AgenteBase

class AmbienteFarol(AmbienteBase):
    def __init__(self, largura=15, altura=10, dificuldade=1):
        super().__init__(largura, altura, dificuldade)
        # Posição do farol
        self.farol = (largura-2, altura-2)
    
    def adicionar_obstaculos(self, dificuldade: int = None):
        dif = dificuldade or self.dificuldade
        for i in range(self.altura):
            for j in range(self.largura):
                obst = Obstaculo(j, i)
                if obst.colocar(dif, self):
                    self.obstaculos.append(obst)