import pickle
from agentes.Accao import Accao
from agentes.Sensor import Sensor
from agentes.Politicas import PoliticaAleatoria, PoliticaFixa, PoliticaQLearning, PoliticaRedeNeuronal
from ambiente.AmbienteFarol import AmbienteFarol
from ambiente.AmbienteBase import AmbienteBase
from ambiente.AmbienteMaze import AmbienteMaze
from agentes.Agente import AgenteBase
from simulador.Visualizador import Visualizador 
import json
import time
import neat
import os

class MotorDeSimulacao:
    def __init__(self, ambiente: AmbienteBase=None, visualizador: Visualizador = None):
        """Novo construtor para ser usado pelo AG."""
        self.ambiente = ambiente
        self.agentes = []
        self.visualizador = visualizador
        self.terminado = False

    def cria(nome_do_ficheiro_parametros: str):
        print(f"A carregar simulação... (ficheiro '{nome_do_ficheiro_parametros}')")
        try:
            with open(nome_do_ficheiro_parametros, "r") as f:
                params = json.load(f)
        except FileNotFoundError:
            print(f"ERRO: Ficheiro '{nome_do_ficheiro_parametros}' não encontrado.")
            return None
        
        simulador = MotorDeSimulacao()
        simulador.agentes = []
        
        # 1. Inicializar Ambiente
        params_ambiente = params.get('ambiente', {})
        tipo_amb = params_ambiente.get('tipo', 'farol')
        
        if tipo_amb == 'farol':
            simulador.ambiente = AmbienteFarol(
                largura=params_ambiente.get('largura', 10),
                altura=params_ambiente.get('altura', 10),
                dificuldade = params_ambiente.get('dificuldade', 1),
            )
        elif tipo_amb == 'maze':
            simulador.ambiente = AmbienteMaze(
                dificuldade = params_ambiente.get('dificuldade', 2),
            )
        else:
            raise ValueError(f"Tipo de ambiente desconhecido: {tipo_amb}")
        
        
        print(f"Ambiente '{tipo_amb}' criado com dificuldade {simulador.ambiente.dificuldade}.")
        # Inicializar Agentes
        for params_agente in params.get('agentes', []):
            id_agente = params_agente.get('id')
            
              # Criar o Agente 
            agente = AgenteBase(id=id_agente)
            # Decidir a Política
            
            params_politica = params_agente.get('politica', {})
            tipo_politica = params_politica.get('tipo', 'aleatoria')
           
            politica_obj = None
            if tipo_politica == 'aleatoria':
                politica_obj = PoliticaAleatoria()
            elif tipo_politica == 'fixa':
                politica_obj = PoliticaFixa()
            elif tipo_politica == 'aprendizagem':
                ficheiro_politica = params_politica.get('ficheiro', 'vencedor.pkl')
                caminho_completo = os.path.join("vencedores", ficheiro_politica)
                 # Carregar configuração NEAT
                local_dir = os.path.dirname(__file__)
                config_path = os.path.join(local_dir,'..', 'config-feedforward.txt')
                config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)
                with open(caminho_completo, 'rb') as f:
                    vencedor = pickle.load(f)
                net = neat.nn.FeedForwardNetwork.create(vencedor, config)
                politica_obj = PoliticaRedeNeuronal(net,simulador.ambiente, agente)
            elif tipo_politica == 'qlearning':
                ficheiro = params_politica.get('ficheiro', 'vencedor_QL.pkl')
                caminho = os.path.join("vencedores", ficheiro)
                # Valores padrão
                q_table = None
                epsilon = 0.0
                
                if not os.path.exists(caminho):
                    caminho = os.path.join("vencedores/vencedor_QL.pkl" )

                print (f"A carregar modelo Q-Learning de '{caminho}'...") 
                with open(caminho, 'rb') as f:
                    dados = pickle.load(f)
                    q_table = dados.get('Q')
                    print(f"Modelo Q-Learning carregado: {len(q_table)} estados.")
                
                # Instancia a política passando a tabela carregada
                politica_obj = PoliticaQLearning(
                    epsilon=epsilon, 
                    q_table=q_table
                )
                # Define como modo de teste (não aprende enquanto executa a simulação final)
                politica_obj.treinando = False 
                
                agente.politica = politica_obj
                print (f"Política Q-Learning atribuída ao agente '{id_agente}'.")

            else:
                print(f"Aviso: Política '{tipo_politica}' desconhecida. A usar Aleatoria.")
                politica_obj = PoliticaAleatoria()
            
            agente.politica = politica_obj

            # Instalar Sensores
            for params_sensor in params_agente.get('sensores', []):
                sensor = Sensor(
                    direcao=params_sensor.get('direcao', [0, 1]),
                    movimentos=params_sensor.get('movimentos', 1)
                )
                agente.instala(sensor)
            
            # Adicionar Agente ao Motor e Ambiente
            simulador.agentes.append(agente)    
            pos_inicial = tuple(params_agente.get('posicao_inicial', [1, 1]))
            simulador.ambiente.adicionar_agente(agente, pos_inicial)
            
        simulador.ambiente.adicionar_obstaculos(simulador.ambiente.dificuldade)
        #  Inicializar Visualizador
        simulador.visualizador = Visualizador(30)
        simulador.terminado = False
        
        print(f"Simulação criada com {len(simulador.agentes)} agentes.")
        return simulador


    def adicionar_agente_programatico(self, agente: AgenteBase, pos_inicial: tuple):
        self.agentes.append(agente)
        self.ambiente.adicionar_agente(agente, pos_inicial)

    def reset(self):
        """Reinicia o motor e o ambiente."""
        self.agentes = []
        self.ambiente.reset() # Chama o novo método reset do ambiente
        self.terminado = False
        
        # Reinicia as políticas dos agentes (para o passo_atual voltar a 0)
        for agente in self.agentes:
            if hasattr(agente.politica, 'reset'):
                agente.politica.reset()

    def listaAgentes(self):
        return self.agentes

    def executa(self, max_passos: int, visualizar: bool = True):
        """Executa a simulação com um máximo de passos e opção de visualização."""
        print("Iniciando simulação..." if visualizar else "", end="" if not visualizar else "\n")
        
        while not self.terminado and self.ambiente.passo_atual < max_passos:
            acoes_a_executar = []
            
            # 1. Ciclo de Observação e Decisão
            for agente in self.agentes:
                obs = self.ambiente.observacaoPara(agente)
                agente.receberObservacao(obs)
                accao = agente.age()
                acoes_a_executar.append((agente, accao))
            
            # 2. Ciclo de Ação
            for agente, accao in acoes_a_executar:
                self.ambiente.agir(accao, agente)
            
            # 3. Atualização do ambiente
            self.ambiente.atualizacao()
            
            # 4. Desenho (só se ativado)
            if self.visualizador and visualizar:
                estado_vis = self.ambiente.get_estado_visualizacao()
                self.visualizador.desenhar(estado_vis)
                time.sleep(0.2) # Mais lento para visualização normal
                if not self.visualizador.janela_aberta():
                    print("Janela fechada pelo utilizador. A terminar simulação.")
                    self.terminado = True
                    break

            # 5. Verificar condição de fim           
            agentes_chegaram = [agente for agente in self.agentes if self.ambiente.agente_no_farol(agente)]
            if all(self.ambiente.agente_no_farol(agente) for agente in self.agentes):
                if visualizar: print("Todos os agentes no objetivo!")
                self.terminado = True
        
        
        agentes_chegaram = [agente for agente in self.agentes if self.ambiente.agente_no_farol(agente)]
        if visualizar:
            print("Simulação terminada.")
            if(agentes_chegaram):
                for agente in agentes_chegaram:
                    print(f"Agente {agente.id} com a {type(agente.politica).__name__} chegou ao objetivo em {len(self.ambiente.historico_paths[agente])} passos!")
            
        
                    

        