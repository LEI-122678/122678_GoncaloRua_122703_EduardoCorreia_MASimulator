# MASimulator - Simulador de Sistemas Multi-Agente com Aprendizagem

Este projeto implementa uma infraestrutura de simulação para estudar e comparar paradigmas de Agentes Autónomos (**Q-Learning** vs **Neuroevolução/NEAT**) em ambientes de complexidade variável.

O foco principal é a comparação de performance entre a aprendizagem por reforço clássica e a evolução de redes neuronais assistida por **Novelty Search** (Busca por Novidade) na resolução de labirintos com mínimos locais enganadores.

**Unidade Curricular:** Agentes Autónomos (2025/2026) - ISCTE-IUL

## 👥 Autores
* **Eduardo David Rivas Correia** (nº 122703)
* **Gonçalo Costa Rua** (nº 122678)

## 📂 Estrutura do Projeto

```text
MASimulator/
│
├── agentes/                   # Lógica interna dos agentes
│   ├── Accao.py
│   ├── Agente.py
│   ├── Observacao.py
│   ├── Politicas.py
│   └── Sensor.py
│
├── ambiente/                  # Definição dos mundos e regras
│   ├── AmbienteFarol.py
│   ├── AmbienteMaze.py
│   └── Obstaculos.py
│
├── mazes/                     # Mapas dos labirintos (txt)
│   ├── dificuldade1.txt
│   └── dificuldade2.txt
│   ├── dificuldade3.txt
│   └── dificuldade4.txt
│
├── simulador/                 # Core da simulação
│   ├── MotorDeSimulacao.py
│   ├── NoveltyArchive.py      # Algoritmo de Novelty Search
│   └── Visualizador.py
│
├── vencedores/                # Modelos treinados prontos a testar (.pkl)
│   ├── vencedor_FAROL.pkl
│   ├── vencedor_FAROLQL.pkl
│   ├── vencedor_MAZE[1-4]     # Modelos para os 4 níveis de dificuldade
│   └── vencedor_PAREDES...    # Cenários de teste extra
│
├── config-feedforward.txt     # Configuração do algoritmo NEAT
├── graficos.py                # Gera os gráficos comparativos de performance
├── main.py                    # Motor principal para visualizar a simulação
├── parametros.json            # Configurações globais lidas pelo main.py
├── treino_neat.py             # Script de treino (NEAT)
└── treino_qlearning.py        # Script de treino (Q-Learning)
`````

## 🚀 Como Executar (Modo Visualização)

Para testar os agentes e visualizar a simulação, deve configurar o ficheiro `parametros.json` e executar o `main.py`.

### Passo 1: Configurar o Cenário
Abra o ficheiro `parametros.json` na raiz do projeto e edite os campos conforme o teste desejado. Abaixo estão exemplos de configuração para os cenários mais importantes.

#### A. Testar Política NEAT no Labirinto Mais Difícil (Maze 4)

```json
{
  "ambiente": {
    "tipo": "maze",
    "dificuldade": 4,
    "_comentario": "Não necessário altura e largura pois o maze nao depende disso, mas sim de ficheiros .txt pré-feitos"
  },
  "agentes": [
    {
      "id": 1,
      "posicao_inicial": [1, 1],
      "politica": {
        "tipo": "aprendizagem",
        "ficheiro": "vencedor_MAZE4.pkl"
      },
      "sensores": [
        { "direcao": [1, 0], "movimentos": 1 },
        { "direcao": [-1, 0], "movimentos": 1 },
        { "direcao": [0, 1], "movimentos": 1 },
        { "direcao": [0, -1], "movimentos": 1 }
      ]
    }
  ]
}
`````
#### B. Testar Política Q-Learning no Problema do Farol
```json
{
  "ambiente": {
    "tipo": "farol",
    "largura": 15,
    "altura": 10,
    "dificuldade": 2
  },
  "agentes": [
    {
      "id": 1,
      "posicao_inicial": [1, 1],
      "politica": {
        "tipo": "qlearning",
        "ficheiro": "vencedor_FAROLQL.pkl"
      },
      "sensores": [
        { "direcao": [1, 0], "movimentos": 1 },
        { "direcao": [-1, 0], "movimentos": 1 },
        { "direcao": [0, 1], "movimentos": 1 },
        { "direcao": [0, -1], "movimentos": 1 }
      ]
    }
  ]
}
`````
#### C. Testar Política Fixa no Problema do Faro
```json
{
  "ambiente": {
    "tipo": "farol",
    "largura": 15,
    "altura": 10,
    "dificuldade": 3
  },
  "agentes": [ 
      {
      "id": 3,
      "posicao_inicial": [1, 1],
      "politica": {
        "tipo": "fixa",
        "_comentario": "Não necessário ficheiro pois a política fixa nao necessita disso"
      },
      "sensores": [
        { "direcao": [1, 0], "movimentos": 1 },
        { "direcao": [-1, 0], "movimentos": 1 },
        { "direcao": [0, 1], "movimentos": 1 },
        { "direcao": [0, -1], "movimentos": 1 }
      ]
    }
  ]
}
`````


### Passo 2: Executar
Após guardar as alterações no ficheiro JSON, corra o comando:

```bash
python main.py
`````

## 🧠 Como Treinar (Modo Aprendizagem)

Se desejar treinar novos agentes de raiz em vez de usar os modelos pré-treinados:

### Treino com Q-Learning
Abra o ficheiro treino_qlearning.py, ajuste a variável USAR_MAZE (True ou False), e DIFICULDADE = 1 a 4, conforme o ambiente desejado e execute:

```bash
python treino_qlearning.py
`````

### Treino com NEAT (Redes Neuronais)
Abra o ficheiro treino_neat.py, ajuste a configuração USAR_MAZE e DIFICULDADE e execute:

```bash
python treino_neat.py
`````

O treino irá gerar gráficos de evolução da fitness e guardará o melhor modelo na pasta vencedores/.


