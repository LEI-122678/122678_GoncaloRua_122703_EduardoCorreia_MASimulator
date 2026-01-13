# MASimulator - Simulador de Sistemas Multi-Agente

Este projeto consiste numa infraestrutura modular de simulação desenvolvida no âmbito da disciplina de **Agentes Autónomos**. O simulador permite a comparação entre diferentes paradigmas de controlo de agentes, especificamente **Aprendizagem por Reforço Tabular (Q-Learning)** e **Neuroevolução (NEAT com Novelty Search)**.

## 👥 Autores
* **Eduardo David Rivas Correia** (nº 122703)
* **Gonçalo Costa Rua** (nº 122678)

## 📋 Descrição do Projeto
O MASimulator implementa dois cenários principais de teste:
1.  **Problema do Farol:** Um ambiente contínuo e aberto onde o agente deve localizar um alvo.
2.  **Problema do Labirinto (Maze):** Um ambiente complexo com obstáculos e "becos sem saída", ideal para testar a capacidade de superação de mínimos locais através de *Novelty Search*.

### Agentes Implementados
* **Agente Fixo:** Comportamento pré-programado (Baseline).
* **Q-Learning:** Aprendizagem por reforço.
* **NEAT (NeuroEvolution of Augmenting Topologies):** Redes neuronais evolutivas, combinadas com uma métrica de Novidade (Novelty Search) para melhor exploração.

## ⚙️ Como executar o Projeto

