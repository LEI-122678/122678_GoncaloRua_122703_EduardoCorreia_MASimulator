
import math
from agentes.Agente import AgenteBase
from agentes.Accao import Accao
from agentes.Observacao import Observacao

class AmbienteBase():
    def __init__(self, largura=10, altura=10, dificuldade=1):
        self.largura = largura
        self.altura = altura
        self.dificuldade = dificuldade
        self.farol = None
        self.posicoes_agentes = {}
        self.historico_paths = {}
        self.obstaculos = []
        self.ultimas_acoes = {}
        self.passo_atual = 0
    
    def adicionar_agente(self, agente: AgenteBase, pos_inicial: tuple = (1, 1)):
        self.posicoes_agentes[agente] = pos_inicial
        self.historico_paths[agente] = [pos_inicial]

    def adicionar_obstaculos(self, dificuldade: int = 1):
        pass
    
    def _calcular_distancia(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_inputs_neurais(self, agente: AgenteBase):
        """
        Gera um vetor de inputs para a rede neural.
        Inputs (12 neurónios):
        0-3: Sensores de Distância (Norte, Sul, Este, Oeste) - Normalizado [0, 1]
        4-7: Radar do Farol (Quadrantes: Norte, Sul, Este, Oeste) - Binário [0 ou 1]
        8-11: Sensores de Obstáculos (Norte, Sul, Este, Oeste) - Binário [0 ou 1]
        """
        pos = self.posicoes_agentes.get(agente)
        if not pos: return [0]*12
        
        x, y = pos
        
        # 1. Sensores de Parede (Distância normalizada)
        max_dist_x = self.largura
        max_dist_y = self.altura
        
        dist_norte = y / max_dist_y
        dist_sul = (self.altura - 1 - y) / max_dist_y
        dist_oeste = x / max_dist_x
        dist_este = (self.largura - 1 - x) / max_dist_x
        
        s_norte = 1.0 - dist_norte
        s_sul = 1.0 - dist_sul
        s_oeste = 1.0 - dist_oeste
        s_este = 1.0 - dist_este

        # 2. Radar (Pie-slice) - Onde está o farol?
        if self.farol:
            fx, fy = self.farol
            r_norte = 1.0 if fy < y else 0.0
            r_sul = 1.0 if fy > y else 0.0
            r_oeste = 1.0 if fx < x else 0.0
            r_este = 1.0 if fx > x else 0.0
        else:
            r_norte = r_sul = r_oeste = r_este = 0.0

        # 3. Sensores de Obstáculos
        o_norte = o_sul = o_oeste = o_este = 0.0
        
        for sensor in agente.sensores:
            posicoes_sondadas = self.posicoes_sondadas(sensor, pos)
            for px, py in posicoes_sondadas:
                for obstaculo in self.obstaculos:
                    if (obstaculo.dx, obstaculo.dy) == (px, py):
                        if py < y:  # obstáculo a norte
                            o_norte = 1.0
                        elif py > y:  # obstáculo a sul
                            o_sul = 1.0
                        if px < x:  # obstáculo a oeste
                            o_oeste = 1.0
                        elif px > x:  # obstáculo a este
                            o_este = 1.0
                        break
        
        return [s_norte, s_sul, s_oeste, s_este, r_norte, r_sul, r_oeste, r_este, o_norte, o_sul, o_oeste, o_este]
    
    def posicoes_sondadas(self, sensor, pos_atual):
        dx, dy = sensor.direcao_accao.dx, sensor.direcao_accao.dy
        return [(pos_atual[0] + dx * passo, pos_atual[1] + dy * passo) 
                for passo in range(1, sensor.movimentos + 1)]
    
    def agir(self, accao: Accao, agente: AgenteBase):
        pos_atual = self.posicoes_agentes.get(agente)
        if pos_atual is None: return
        if accao is None or (accao.dx == 0 and accao.dy == 0):
            return  # Sem movimento

        # Bloquear movimentos opostos
        ultima = self.ultimas_acoes.get(agente)
        if ultima and (accao.dx == -ultima.dx and accao.dy == -ultima.dy):
            accao = agente.registar_colisao(accao)
        
        x, y = pos_atual
        if x + accao.dx < 0 or x + accao.dx >= self.largura or y + accao.dy < 0 or y + accao.dy >= self.altura:
            # Movimento fora dos limites
            accao = agente.registar_colisao(accao)
        novo_x = max(0, min(self.largura - 1, x + accao.dx))
        novo_y = max(0, min(self.altura - 1, y + accao.dy))

        colidiu = any((o.dx, o.dy) == (novo_x, novo_y) for o in self.obstaculos)

        if colidiu:
            tentativas = 0
            while tentativas < 4:
                accao = agente.registar_colisao(accao)
                novo_x = max(0, min(self.largura - 1, x + accao.dx))
                novo_y = max(0, min(self.altura - 1, y + accao.dy))
                if not any((o.dx, o.dy) == (novo_x, novo_y) for o in self.obstaculos):
                    self._atualizar_posicao(agente, novo_x, novo_y, accao)
                    return
                tentativas += 1
        else:
            self._atualizar_posicao(agente, novo_x, novo_y, accao)
    
    def _atualizar_posicao(self, agente, novo_x, novo_y, accao):
        self.posicoes_agentes[agente] = (novo_x, novo_y)
        self.historico_paths[agente].append((novo_x, novo_y))
        self.ultimas_acoes[agente] = accao
    
    def observacaoPara(self, agente: AgenteBase) -> Observacao:
        pos_atual = self.posicoes_agentes.get(agente)
        if pos_atual is None:
            return Observacao(posicao_atual=None)
        
        resultados_sensores = []
        for sensor in agente.sensores:
            posicoes_sondadas = self.posicoes_sondadas(sensor, pos_atual)
            
            obstaculos_detectados = False
            for pos in posicoes_sondadas:
                for obstaculo in self.obstaculos:
                    if (obstaculo.dx, obstaculo.dy) == pos:
                        obstaculos_detectados = True
                        break
                if obstaculos_detectados:
                    break
            
            if obstaculos_detectados:
                recompensa_sondada = -999
            else:
                pos_final = posicoes_sondadas[-1] 
                recompensa_sondada = -self._calcular_distancia(pos_final, self.farol)
            
            resultados_sensores.append({
                'accao_base': sensor.direcao_accao,
                'recompensa_sondada': recompensa_sondada
            })
        
        return Observacao(posicao_atual=pos_atual, resultados_sensores=resultados_sensores)
    
    def agente_no_farol(self, agente: AgenteBase) -> bool:
        pos = self.posicoes_agentes.get(agente)
        if pos and self.farol and pos == self.farol:
            agente.agente_no_farol = True
            return True
        return False
    
    def dist_to_exit(self, agente: AgenteBase):
        pos = self.posicoes_agentes.get(agente)
        if not pos or not self.farol: return 1000.0
        return self._calcular_distancia(pos, self.farol)
    
    def atualizacao(self):
        self.passo_atual += 1
    
    def recompensaPara(self, agente):
        return 0
    
    def get_estado_visualizacao(self) -> dict:
        return {
            "largura": self.largura,
            "altura": self.altura,
            "farol": self.farol,
            "agentes": list(self.posicoes_agentes.values()),
            "obstaculos": [(o.dx, o.dy) for o in self.obstaculos]
        }
    
    def reset(self):
        self.posicoes_agentes = {}
        self.historico_paths = {}
        self.ultimas_acoes = {}
        self.passo_atual = 0