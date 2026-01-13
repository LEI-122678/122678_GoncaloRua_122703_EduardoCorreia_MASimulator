# Em main.py - VERSÃO COM GRÁFICOS DE BARRAS
import pickle
from agentes.Agente import AgenteBase
from agentes.Politicas import PoliticaFixa, PoliticaQLearning, PoliticaRedeNeuronal
from agentes.Sensor import Sensor
from ambiente.AmbienteFarol import AmbienteFarol
from ambiente.AmbienteMaze import AmbienteMaze
from simulador.MotorDeSimulacao import MotorDeSimulacao
from collections import defaultdict
import matplotlib.pyplot as plt
import os
import numpy as np
import neat 

# Configurações globais
NUM_SIMULACOES = 10
NUM_EPISODIOS = 30
MAX_PASSOS = 100
cores = ["blue", "red", "green", "orange", "purple", "pink"]

if __name__ == "__main__":
    # Teste inicial (comente se não for necessário)
    ambientes = {
        "FAROL": {"dificuldades": range(1, 6), "num_sim": 2},
        "MAZE": {"dificuldades": range(1, 5), "num_sim": 1}
    }

    resultados = defaultdict(lambda: defaultdict(list))

    for ambiente, info in ambientes.items():
        for dificuldade in info["dificuldades"]:
            for sim_num in range(info["num_sim"]):
                print(f"Simulação {sim_num+1} - Ambiente {ambiente} Dificuldade {dificuldade}.")

                # Criar ambiente
                if ambiente == "FAROL":
                    sim = MotorDeSimulacao()
                    sim.ambiente = AmbienteFarol(largura=15, altura=10, dificuldade=dificuldade)
                else:
                    sim = MotorDeSimulacao()
                    sim.ambiente = AmbienteMaze(dificuldade=dificuldade)

                sim.agentes = []
                
                # Criar agentes
                lista_agentes = [] 

                # Política fixa
                agente_fixa = AgenteBase(id="fixa")
                agente_fixa.politica = PoliticaFixa()
                lista_agentes.append(agente_fixa)

                # QLearning
                try:
                    if ambiente == "FAROL":
                        caminho_q = f"vencedores/vencedor_FAROLQL.pkl"
                    else:
                        caminho_q = f"vencedores/vencedor_MAZE{dificuldade}QL.pkl"
                    
                    with open(caminho_q, "rb") as f:
                        dados = pickle.load(f)
                        q_table = dados.get("Q")
                    
                    agente_q = AgenteBase(id=f"qlearning{dificuldade}")
                    agente_q.politica = PoliticaQLearning(epsilon=0.0, q_table=q_table)
                    agente_q.politica.treinando = False
                    lista_agentes.append(agente_q)
                except FileNotFoundError:
                    print(f"Aviso: Arquivo Q-table não encontrado: {caminho_q}")

                # Aprendizagem (NEAT)
                try:
                    if ambiente == "FAROL":
                        caminho_n = f"vencedores/vencedor_FAROL.pkl"
                    else:
                        caminho_n = f"vencedores/vencedor_MAZE{dificuldade}.pkl"
            
                    with open(caminho_n, "rb") as f:
                        vencedor = pickle.load(f)

                   

                     # Carregar configuração NEAT
                    
                    local_dir = os.path.dirname(__file__)
                    config_path = os.path.join(local_dir, "config-feedforward.txt")
                    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                        config_path)
                    net = neat.nn.FeedForwardNetwork.create(vencedor, config)
                    agente_n = AgenteBase(id=f"aprendizagem{dificuldade}")
                    agente_n.politica = PoliticaRedeNeuronal(net, sim.ambiente, agente_n)
                    lista_agentes.append(agente_n)
                  
                except FileNotFoundError:
                    print(f"Aviso: Arquivo NEAT não encontrado: {caminho_n}")

                # Adicionar agentes ao ambiente
                for agente in lista_agentes:
                    direcoes_sensores = [ [0, -1], [0, 1], [-1, 0], [1, 0] ]
                    for dir in direcoes_sensores:
                        sensor = Sensor(direcao=dir, movimentos=1)
                        agente.instala(sensor)
                    
                    sim.agentes.append(agente)
                    # Posição inicial pode precisar de ajuste
                    sim.ambiente.adicionar_agente(agente, (1, 1))

                passos_por_episodio = defaultdict(list)

                # Executar episódios
                for episodio in range(NUM_EPISODIOS):
                    # Verifique o nome exato do parâmetro
                    if ambiente=="MAZE" and dificuldade==3:
                        sim.executa(MAX_PASSOS, visualizar=True)
                    else:
                        sim.executa(MAX_PASSOS, visualizar=False)
                    for agente in sim.listaAgentes():
                        politica_nome = type(agente.politica).__name__   
                        passos = len(sim.ambiente.historico_paths[agente])
                        passos_por_episodio[politica_nome].append(passos)
                    

                # Guardar resultados
                for politica, passos in passos_por_episodio.items():
                    resultados[f"{ambiente}{dificuldade}"][politica].append(passos)

    # === GRÁFICOS DE BARRAS ===
    for ambiente_dif, politicas in resultados.items():
        if not politicas: 
            print(f"Não há dados para {ambiente_dif}")
            continue
        
        plt.figure(figsize=(12, 6))
        
        # Calcular médias para cada política
        nomes_politicas = []
        medias_passos = []
        erros_passos = []
        
        for i, (politica, dados_simulacoes) in enumerate(politicas.items()):
            # dados_simulacoes é uma lista de listas: [[ep1_sim1, ep2_sim1, ...], [ep1_sim2, ...], ...
            # Achatar os dados: todos os episódios de todas as simulações
            todos_passos = []
            for sim_passos in dados_simulacoes:
               
                todos_passos.extend(sim_passos)
            
            # Calcular média e desvio padrão
            media = np.mean(todos_passos)
            erro = np.std(todos_passos)
            
            nomes_politicas.append(politica)
            medias_passos.append(media)
            erros_passos.append(erro)
        
        # Criar barras
        barras = plt.bar(nomes_politicas, medias_passos, yerr=erros_passos,
                        capsize=3, error_kw={'elinewidth': 0.6,'ecolor': 'gray','capthick': 0.6},
                        color=cores[:len(nomes_politicas)],alpha=0.7,edgecolor='black', linewidth=0.5)        
        # Adicionar valores nas barras
        for barra, valor in zip(barras, medias_passos):
            plt.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 2,f'{valor:.1f}',ha='center',va='bottom',fontsize=10)
        
        plt.xlabel('Política')
        plt.ylabel('Número Médio de Passos')
        plt.title(f'Comparação de Políticas - {ambiente_dif}')
       
        
       
        
        plt.show()
        

       