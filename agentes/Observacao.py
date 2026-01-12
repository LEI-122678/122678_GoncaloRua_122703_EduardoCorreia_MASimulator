# Em agentes/Observacao.py
class Observacao:
    def __init__(self, posicao_atual: tuple, resultados_sensores: list = None):
        self.posicao_atual = posicao_atual
        self.resultados_sensores = resultados_sensores if resultados_sensores else []


        
    def __repr__(self):
        return f"Observacao(pos={self.posicao_atual}), sensores={len(self.resultados_sensores)})"