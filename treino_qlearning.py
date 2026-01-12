from agentes.Agente import AgenteBase
from agentes.Politicas import PoliticaQLearning
from agentes.Sensor import Sensor # Importante se o ambiente depender da criação de sensores
from simulador.MotorDeSimulacao import MotorDeSimulacao
from ambiente.AmbienteMaze import AmbienteMaze
from ambiente.AmbienteFarol import AmbienteFarol

import matplotlib.pyplot as plt
import pickle
import os
import math
import time
# Configurações
MAX_PASSOS = 60
EPISODIOS = 1000
DIFICULDADE = 1
USAR_MAZE = True

def run_training():
    print("=== INICIANDO TREINO Q-LEARNING (MODO NATIVO) ===")
    
    # 1. Setup do Ambiente e Motor
    sim = MotorDeSimulacao()
    if USAR_MAZE:
        sim.ambiente = AmbienteMaze(dificuldade=DIFICULDADE)
    else:
        sim.ambiente = AmbienteFarol(largura=15, altura=10, dificuldade=DIFICULDADE)
    
    sim.ambiente.adicionar_obstaculos()

    # 2. Criar Agente e Política
    # Criamos a política UMA vez para manter a memória (Q-Table)
    politica_ql = PoliticaQLearning(alpha=0.1,gamma=0.9,epsilon=1.0) # Começa totalmente aleatório
        
    start_time = time.time()
    historico_recompensas = []

    for ep in range(EPISODIOS):
        # Reset para novo episódio
        sim.reset() 
        
        # Criar/Reiniciar agente
        agente = AgenteBase(id=f"treino_{ep}")
        agente.politica = politica_ql
        
        # Adicionar sensores 
        # o Agente precisa deles se quiseres usar a classe Sensor no futuro ou para compatibilidade)
        direcoes = [[0, -1], [0, 1], [-1, 0], [1, 0]]
        for d in direcoes:
            agente.instala(Sensor(direcao=d, movimentos=1))
        
        # Adicionar ao motor (posição fixa ou aleatória)
        pos_inicial = (1, 1)
        sim.adicionar_agente_programatico(agente, pos_inicial)
        
        total_recompensa = 0
        passos = 0
        done = False
        
        # === LOOP DO EPISÓDIO ===
        while passos < MAX_PASSOS and not done:
            
            # A. Observação e Decisão (Feito pelo Agente internamente!)
            obs_anterior = sim.ambiente.observacaoPara(agente)
            pos_anterior = obs_anterior.posicao_atual
            
            # O agente decide usando decidirAccao() da PoliticaQLearning
            agente.receberObservacao(obs_anterior)
            accao = agente.age() 
            
            # B. Executar Ação no Ambiente
            sim.ambiente.agir(accao, agente)
            
            # C. Nova Observação e Cálculo de Recompensa
            obs_nova = sim.ambiente.observacaoPara(agente)
            pos_nova = obs_nova.posicao_atual
            
            # Lógica de Recompensa (Customizada para o Treino)
            recompensa = -0.1 # Penalização por passo -> diminuir a penalização quando está a treinar no maze
            colisoes = agente.colisoes
            recompensa += -0.01 * colisoes # Penalização por colisões
            # Verificar Distância
            if sim.ambiente.farol:
                dist_ant = math.dist(pos_anterior, sim.ambiente.farol)
                dist_nov = math.dist(pos_nova, sim.ambiente.farol)
                
                # Shaping reward: recompensa se aproximar
                if dist_nov < dist_ant:
                    recompensa += 0.1 # se for maior que o de passos ele fica a dar voltas
            
            # Verificar Fim
            if sim.ambiente.agente_no_farol(agente):
                recompensa = 100.0
                done = True
            
            # Se a posição não mudou e a ação não era nula
            if pos_anterior == pos_nova and (accao.dx != 0 or accao.dy != 0):
                recompensa = -1
            
            # D. APRENDIZAGEM (Backpropagation do Q-Learning)
            politica_ql.aprender(pos_anterior, accao, recompensa, pos_nova)
            
            total_recompensa += recompensa
            passos += 1

        # Fim do Episódio - Decaimento do Epsilon
        historico_recompensas.append(total_recompensa)
        politica_ql.epsilon = max(0.01, politica_ql.epsilon * 0.995)

        if (ep+1) % 100 == 0:
            media = sum(historico_recompensas[-100:]) / 100
            print(f"Ep {ep+1}/{EPISODIOS} | Rec: {media:.2f} | Epsilon: {politica_ql.epsilon:.3f}")

        sim.ambiente.reset()

    # Mostrar gráfico de recompensas
    plt.figure(figsize=(10, 5))
    x = range(len(historico_recompensas))
    # Pegar apenas num ponto a cada 10
    plt.plot(x[::10], historico_recompensas[::10])
    plt.title("Recompensa por Episódio (Q-Learning)")
    plt.xlabel("Episódio")
    plt.ylabel("Recompensa Total")
    plt.grid(True)
    plt.show()

    # Salvar
    salvar_modelo(politica_ql, "vencedores/vencedor_QL.pkl")
    print(f"Treino concluído em {time.time() - start_time:.2f}s")


def salvar_modelo(politica, caminho):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    dados = {
        'Q': politica.Q,
        'epsilon': politica.epsilon,
        'alpha': politica.alpha,
        'gamma': politica.gamma
    }
    with open(caminho, 'wb') as f:
        pickle.dump(dados, f)
    print(f"Modelo salvo em {caminho}")

if __name__ == "__main__":
    run_training()