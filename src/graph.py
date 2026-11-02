import math
import json

class GrafoMalhaUrbana:
    def __init__(self, filepath=None):
        self.nodes = []
        self.edges = []
        self.V = 0
        self.id_map = {}
        self.rev_id_map = {}
        self.nome_instancia = ""
        self.origem_dados = ""
        
        if filepath:
            self.carregar_json(filepath)

    def carregar_json(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        self.nome_instancia = dados.get("nome_instancia", "Grafo Sem Nome")
        self.origem_dados = dados.get("origem_dados", "")
        self.nodes = dados.get("vertices", [])
        self.edges = dados.get("arestas", [])
        self.V = len(self.nodes)
        
        # Mapeamento de IDs para índices matriciais (0 a V-1)
        self.id_map = {node["id"]: idx for idx, node in enumerate(self.nodes)}
        self.rev_id_map = {idx: node["id"] for idx, node in enumerate(self.nodes)}

    def executar_floyd_warshall(self, vias_bloqueadas=None, fator_trafego=1.0):
        """
        Executa o algoritmo de Floyd-Warshall considerando bloqueios e simulador de tráfego.
        Complexidade de Tempo: O(|V|^3)
        Complexidade de Espaço: O(|V|^2)
        """
        vias_bloqueadas = vias_bloqueadas or []
        D = [[math.inf] * self.V for _ in range(self.V)]
        Next = [[None] * self.V for _ in range(self.V)]

        for i in range(self.V):
            D[i][i] = 0.0

        for aresta in self.edges:
            u_id, v_id = aresta["origem"], aresta["destino"]
            
            # Pula vias bloqueadas na simulação
            if (u_id, v_id) in vias_bloqueadas:
                continue

            if u_id in self.id_map and v_id in self.id_map:
                u_idx = self.id_map[u_id]
                v_idx = self.id_map[v_id]
                
                # Aplica o fator de tráfego/previsão ao tempo base da via
                peso = float(aresta["tempo_min"]) * fator_trafego
                D[u_idx][v_idx] = peso
                Next[u_idx][v_idx] = v_idx

        # Algoritmo de Floyd-Warshall (3 Laços Aninhados)
        for k in range(self.V):
            for i in range(self.V):
                for j in range(self.V):
                    if D[i][k] + D[k][j] < D[i][j]:
                        D[i][j] = D[i][k] + D[k][j]
                        Next[i][j] = Next[i][k]

        return D, Next

    def reconstruir_caminho(self, u_id, v_id, Next):
        """Reconstrói a sequência exata de vértices entre origem e destino."""
        if u_id not in self.id_map or v_id not in self.id_map:
            return []
        
        u_idx = self.id_map[u_id]
        v_idx = self.id_map[v_id]

        if Next[u_idx][v_idx] is None:
            return []

        caminho_indices = [u_idx]
        atual = u_idx
        while atual != v_idx:
            atual = Next[atual][v_idx]
            if atual is None:
                return []
            caminho_indices.append(atual)

        return [self.rev_id_map[idx] for idx in caminho_indices]

    def encontrar_base_mais_proxima(self, destino_id, D):
        """Identifica qual base cadastrada possui o menor tempo de resposta para o ponto do chamado."""
        if destino_id not in self.id_map:
            return None, math.inf
        
        v_idx = self.id_map[destino_id]
        melhor_base_id = None
        menor_tempo = math.inf

        for node in self.nodes:
            if node.get("tipo") == "base":
                u_id = node["id"]
                u_idx = self.id_map[u_id]
                tempo = D[u_idx][v_idx]
                if tempo < menor_tempo:
                    menor_tempo = tempo
                    melhor_base_id = u_id

        return melhor_base_id, menor_tempo
