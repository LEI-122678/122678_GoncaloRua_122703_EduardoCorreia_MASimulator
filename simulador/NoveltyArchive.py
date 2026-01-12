import numpy as np

class NoveltyArchive:
    def __init__(self, k_neighbors=15, threshold=10.0, decay_rate=0.05, limit=500):
        self.archive = []  # Lista de coordenadas (x, y) de comportamentos passados
        self.k = k_neighbors
        self.threshold = threshold
        self.decay_rate = decay_rate
        self.limit = limit
        self.max_novelty_seen = 1.0 # Para normalização

    def calcular_novelty(self, pos, populacao_atual_posicoes):
        """
        Calcula a esparsidade (novidade) da posição 'pos' em relação 
        ao arquivo histórico e à população atual.
        """
        # Combina pontos do arquivo com a população atual (menos o próprio agente)
        comparacao = self.archive + [p for p in populacao_atual_posicoes if p != pos]
        
        if not comparacao:
            return 0.0

        # Distância Euclidiana para todos os pontos
        pos_arr = np.array(pos)
        comparacao_arr = np.array(comparacao)
        dists = np.linalg.norm(comparacao_arr - pos_arr, axis=1)
        
        # Ordenar e pegar os k vizinhos mais próximos
        dists.sort()
        k_nearest = dists[:self.k]
        
        # A pontuação é a média das distâncias aos vizinhos
        score = np.mean(k_nearest) if len(k_nearest) > 0 else 0.0
        
        if score > self.max_novelty_seen:
            self.max_novelty_seen = score
            
        return score

    def tentar_adicionar(self, pos, score):
        # Se o arquivo estiver cheio, removemos aleatoriamente ou o menos novo (aqui removemos aleatório para simplificar a diversidade)
        if score > self.threshold:
            if len(self.archive) >= self.limit:
                self.archive.pop(0) # Remove o mais antigo
            self.archive.append(pos)
            return True
        return False

    def decair(self):
        self.threshold *= (1.0 + self.decay_rate)
        # Opcional: Limitar o threshold máximo
        self.threshold = min(self.threshold, 50.0)