# Em agentes/politicas/Politica.py (classe base)
from abc import ABC, abstractmethod
from agentes.Accao import Accao
from agentes.Observacao import Observacao
import random
import numpy as np
class Politica(ABC):
    @abstractmethod
    def decidirAccao(self, observacao: Observacao) -> Accao:
        pass

class PoliticaFixa(Politica):
    
    def __init__(self):
        # Política de fallback caso não hajam sensores
        self.fallback = PoliticaAleatoria()

    def decidirAccao(self, observacao: Observacao) -> Accao:
        # Se o ambiente não forneceu resultados de sensores, usa o fallback
        if not observacao.resultados_sensores:
            return self.fallback.decidirAccao(observacao)

        # Encontra o resultado com a MAIOR recompensa
        # (Lembrando que -5 é maior/melhor que -10)
        melhor_resultado = max(
            observacao.resultados_sensores, 
            key=lambda resul: resul['recompensa_sondada']
        )

        # Devolve a ação base associada a esse melhor sensor
        return melhor_resultado['accao_base']

class PoliticaAleatoria(Politica):
    def __init__(self):
        self.movimentos_possiveis = [
            Accao(1, 0),
            Accao(-1, 0),
            Accao(0, 1),
            Accao(0, -1)
        ]

    def decidirAccao(self, observacao: Observacao) -> Accao:
        # Por agora, a política aleatória ignora a observação
        return random.choice(self.movimentos_possiveis)
    
class PoliticaRedeNeuronal(Politica):
    def __init__(self, rede_neural, ambiente_ref, agente_ref):
        self.net = rede_neural
        self.ambiente = ambiente_ref
        self.agente = agente_ref
        
    def decidirAccao(self, observacao: Observacao) -> Accao:
        # Obter inputs normalizados do ambiente
        inputs = self.ambiente.get_inputs_neurais(self.agente)
        # print(f"Inputs para a rede neural: {inputs}")
        # Ativar a rede
        outputs = self.net.activate(inputs)
        #print(f"Outputs da rede neural: {outputs}")
        # Outputs esperados: [Cima, Baixo, Esquerda, Direita]
        # Escolhe o índice com maior valor (argmax)
        escolha = np.argmax(outputs)
        #print(f"Escolha da ação (índice): {escolha}")
        if escolha == 0: return Accao(0, -1) # Norte
        if escolha == 1: return Accao(0, 1)  # Sul
        if escolha == 2: return Accao(-1, 0) # Oeste
        if escolha == 3: return Accao(1, 0)  # Este
        
        return Accao(0,0)
    

class PoliticaQLearning(Politica):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, q_table=None):
        """
        Args:
            alpha: Probabilidade de aprendizagem.
            gamma: Fator de desconto.
            epsilon: Probabilidade de exploração.
            q_table: Dicionário com a memória (se carregado de ficheiro).
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.acoes_possiveis = [Accao(0, -1), Accao(0, 1),Accao(-1, 0),Accao(1, 0)]
        # Tabela Q: Chave = (x, y), Valor = Dict {(dx, dy): valor}
        self.Q = q_table if q_table is not None else {}
        self.treinando = True # Flag para ativar/desativar aprendizagem

    def decidirAccao(self, observacao) -> Accao:
        if observacao.posicao_atual is None:
            return Accao(0, 0)
        
        estado = (int(observacao.posicao_atual[0]), int(observacao.posicao_atual[1]))
        
        # 2. Inicializar estado na Q-Table se não existir
        if estado not in self.Q:
            self.Q[estado] = { (a.dx, a.dy): 0.0 for a in self.acoes_possiveis }

        # 3. Epsilon-Greedy
        # Se estivermos a treinar, usa epsilon. Se for teste, epsilon = 0 (apenas explora se for muito pequeno)
        taxa_exploracao = self.epsilon if self.treinando else 0.0
        
        if random.random() < taxa_exploracao:
            # Exploração: Ação aleatória
            return random.choice(self.acoes_possiveis)
        else:
            # Exploitation: Melhor ação
            # Encontrar o valor máximo neste estado
            valores = self.Q[estado]
            max_valor = max(valores.values())
            
            # Pegar todas as ações que têm esse valor máximo (para desempatar aleatoriamente)
            melhores_acoes_tuples = [k for k, v in valores.items() if v == max_valor]
            dx, dy = random.choice(melhores_acoes_tuples) 
            return Accao(dx, dy)

    def aprender(self, estado_antigo, accao_tomada, recompensa, estado_novo):
        """
        Método chamado pelo Loop de Treino para atualizar a tabela Q.
        """
        if not self.treinando:
            return

        # Converter para tuplos (chaves do dicionário)
        s = (int(estado_antigo[0]), int(estado_antigo[1]))
        s_prox = (int(estado_novo[0]), int(estado_novo[1]))
        a_key = (accao_tomada.dx, accao_tomada.dy)

        # Garantir que entradas existem
        if s not in self.Q:
            self.Q[s] = { (a.dx, a.dy): 0.0 for a in self.acoes_possiveis }
        if s_prox not in self.Q:
            self.Q[s_prox] = { (a.dx, a.dy): 0.0 for a in self.acoes_possiveis }

        # Equação de Bellman
        q_atual = self.Q[s][a_key]
        max_q_prox = max(self.Q[s_prox].values())
        
        # Atualização
        novo_q = q_atual + self.alpha * (recompensa + self.gamma * max_q_prox - q_atual)
        self.Q[s][a_key] = novo_q