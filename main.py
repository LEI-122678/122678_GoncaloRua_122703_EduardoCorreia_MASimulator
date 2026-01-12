

from simulador.MotorDeSimulacao import MotorDeSimulacao

MAX_PASSOS = 100

if __name__ == "__main__":
    # Teste inicial (comente se não for necessário)
    try:
        sim = MotorDeSimulacao.cria("parametros.json")
        agentes = sim.listaAgentes()
        print(f"Agentes na simulação: {len(agentes)}")
        for agente in agentes:
            print(f" - Agente ID: {agente.id}, Política: {type(agente.politica).__name__}")
        sim.executa(MAX_PASSOS)
        print( len(sim.ambiente.historico_paths[agentes[1]]))
    except Exception as e:
        print(f"Aviso: Teste inicial falhou - {e}")

   