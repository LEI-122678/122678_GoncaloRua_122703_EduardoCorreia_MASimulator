from agentes.Accao import Accao
from agentes.Politicas import Politica, PoliticaAleatoria
from agentes.Sensor import Sensor
from agentes.Observacao import Observacao

class AgenteBase:
    def __init__(self, id, parametros=None, politica: Politica = PoliticaAleatoria()):
        self.id = id
        self.observacao_atual = None
        self.politica = politica 
        self.sensores = []
        self.estado = 0
        self.colisoes = 0 
        self.agente_no_farol = False
        self.caminho=None

    def reset_fitness(self): 
        # para o NEAT
        self.colisoes = 0

    def registar_colisao(self,accao: Accao):
        self.colisoes += 1 
        return Accao(accao.dy * -1, accao.dx)

            
    def receberObservacao(self, obs):
        self.observacao_atual = obs

    def escolherAccao(self):
        return self.politica.decidirAccao(self.observacao_atual)

    def age(self):
        if self.agente_no_farol:
            return Accao(0,0)  # Fica parado se já chegou ao farol       
        return self.escolherAccao()

    def avaliacaoEstadoAtual(self, recompensa):
       return self.estado + recompensa
    
    def definirRecompensa(self, observacao:Observacao, recompensa):
        return self.avaliacaoEstadoAtual(recompensa)

    def instala(self, sensor:Sensor):
        self.sensores.append(sensor)

    def comunicar(self, mensagem, agente_destino):
        pass
