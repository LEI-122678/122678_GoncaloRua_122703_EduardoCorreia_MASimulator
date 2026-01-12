import random

class Obstaculo:
    def __init__(self, dx: int, dy: int):
        self.dx = dx
        self.dy = dy
    
    def __repr__(self):
        return f"Obstáculo(dx={self.dx}, dy={self.dy})"
    
    def colocar(self, dif, ambiente) -> bool:
        prob = min(0.05 * dif, 0.9)
        return random.random() < prob and self.inserir(ambiente)
    
    def inserir(self, ambiente) -> bool:
        pos = (self.dx, self.dy)
        
        def vizinhos(coord):
            x, y = coord
            return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
        for agente_pos in ambiente.posicoes_agentes.values():
            if pos == agente_pos or pos in vizinhos(agente_pos):
                return False
        
        if ambiente.farol and (pos == ambiente.farol or pos in vizinhos(ambiente.farol)):
            return False
        
        return True