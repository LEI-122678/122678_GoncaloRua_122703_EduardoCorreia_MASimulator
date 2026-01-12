
from agentes.Accao import Accao

class Sensor:
    def __init__(self, direcao: list, movimentos: int):
        # A 'direcao' é a ação base que este sensor representa
        self.direcao_accao = Accao(direcao[0], direcao[1])
        # 'movimentos' é a "distância" que o sensor sonda
        self.movimentos = movimentos

    
    def __repr__(self):
        return f"Sensor(direcao={self.direcao_accao}, movimentos={self.movimentos})"