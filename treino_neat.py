from ambiente.AmbienteMaze import AmbienteMaze
from ambiente.AmbienteFarol import AmbienteFarol
from agentes.Sensor import Sensor
from agentes.Agente import AgenteBase
from agentes.Politicas import PoliticaRedeNeuronal
from simulador.MotorDeSimulacao import MotorDeSimulacao
from simulador.NoveltyArchive import NoveltyArchive

import matplotlib.pyplot as plt
import os
import random
import neat
import pickle

# Configurações Globais
MAX_PASSOS = 70
GERACOES = 150
DIFICULDADE = 2

# Inicializa o Arquivo de Novelty (Global para persistir entre gerações)
arquivo_novelty = NoveltyArchive(threshold=5.0, decay_rate=0.02)
USAR_MAZE = True  # Alternar entre Maze e Farol

def eval_genomes(genomes, config):
    # Função de avaliação chamada pelo NEAT a cada geração.
    sim = MotorDeSimulacao()
    # Cria o ambiente manualmente (sem JSON)
    if USAR_MAZE:
        sim.ambiente = AmbienteMaze(DIFICULDADE)
        print(f"Usando Ambiente Maze com largura {sim.ambiente.largura}")
    else:
        sim.ambiente = AmbienteFarol(largura=15, altura=10)
    sim.agentes = []
    
    # Criar redes neurais e agentes para cada genoma
    agentes_e_genomas = []
    
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        
        # 1. Criar a rede neural (Fenótipo)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        
        # 2. Criar o agente com a Política Neural
        agente = AgenteBase(id=genome_id)
        agente.reset_fitness()
        # Injetar dependências na política
        agente.politica = PoliticaRedeNeuronal(net, sim.ambiente, agente)
         # INSTALAR SENSORES na visualização também
        
        direcoes_sensores = [
            [0, -1], [0, 1], [-1, 0], [1, 0]
        ]
        for dir in direcoes_sensores:
            sensor = Sensor(direcao=dir, movimentos=1)
            agente.instala(sensor)
        x = random.randint(0, 15)
        y = random.randint(0, 10)
        sim.adicionar_agente_programatico(agente, pos_inicial=(1, 1))
        
        agentes_e_genomas.append((agente, genome))

    # --- Executar Simulação ---
    # Executar sem visualização para ser rápido
    sim.ambiente.adicionar_obstaculos(dificuldade=2)    
    sim.executa(max_passos=MAX_PASSOS, visualizar=False)

    # a= 90.0, b= 50.0, c= 40.0 funciona +- com dificuldade = 2 para farol
    # a= 70.0, b= 100.0, c= 20.0 funciona bem com maze dificuldade 3 PRIORIZAR NOVELTY

    a = 60.0 
    b = 120.0
    c = 20.0
    
    posicoes_finais = [sim.ambiente.posicoes_agentes[ag] for ag, _ in agentes_e_genomas]
    
    for agente, genome in agentes_e_genomas:
        pos_final = sim.ambiente.posicoes_agentes[agente]
        
        dist = sim.ambiente.dist_to_exit(agente)
        # Evitar divisão por zero
        score_objetivo = 1.0 / (dist + 0.1) 
        if sim.ambiente.agente_no_farol(agente):
            score_objetivo += 2.0 # Bónus extra por chegar

        # 2. Componente Novelty
        score_novelty = arquivo_novelty.calcular_novelty(pos_final, posicoes_finais)
        
        # Adicionar ao arquivo se for relevante
        arquivo_novelty.tentar_adicionar(pos_final, score_novelty)

        num_colisoes = agente.colisoes
        score_penalizacao = c * num_colisoes

        # 3. Fitness Combinado
        # Fórmula: Fitness = a * (1/Distancia) + b * Novelty - c * Colisões
        fitness_final = (a * score_objetivo) + (b * score_novelty) - score_penalizacao
        genome.fitness = max(0,fitness_final)  # Garantir fitness não negativo


    # Aplicar Decaimento do Arquivo (Fim da geração)
    arquivo_novelty.decair()
    print(f"Arquivo Novelty: {len(arquivo_novelty.archive)} itens. Threshold atual: {arquivo_novelty.threshold:.2f}")


def run(config_file):
    # Carregar configuração
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Criar população
    p = neat.Population(config)

    # Reporters (Stats no terminal)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # --- RODAR A EVOLUÇÃO ---
    # Chama eval_genomes por X gerações
    vencedor = p.run(eval_genomes, GERACOES)
    
    caminho_arquivo = os.path.join('vencedores', 'vencedor.pkl')
    with open(caminho_arquivo, 'wb') as f:
        pickle.dump(vencedor, f)
        
   

    # Extrair dados do reporter do NEAT
    media_fitness = stats.get_fitness_mean()
    melhor_fitness = [c.fitness for c in stats.most_fit_genomes]
    geracoes = range(len(media_fitness))

    # Mostrar gráfico de fitness
    plt.figure(figsize=(10, 5))
    # Plota a média
    plt.plot(geracoes, media_fitness, label="Média Fitness")
    # Plota o melhor (opcional, mas recomendado para ver se houve evolução real)
    plt.plot(geracoes, melhor_fitness, label="Melhor Fitness")

    plt.title("Evolução do Fitness por Geração (NEAT)")
    plt.xlabel("Geração")
    plt.ylabel("Fitness")
    plt.legend() # Mostra a legenda (Média vs Melhor)
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)