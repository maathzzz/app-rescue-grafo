import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network
import math
import time
import os
from graph import GrafoMalhaUrbana

st.set_page_config(page_title="RescuEU - Sistema SAMU", layout="wide")

st.title("🚑 RescuEU — Otimização e Roteamento para Emergências (SAMU)")
st.markdown("**Algoritmo de Floyd-Warshall aplicado ao cálculo de caminhos mínimos entre todos os pares de vértices.**")

# Sidebar - Seleção de Instância
st.sidebar.header("⚙️ Configurações do Sistema")
instancia_opcao = st.sidebar.selectbox(
    "Selecione a Instância da Malha Viária:",
    [
        "Instância 1 - Didática (6 Vértices)",
        "Instância 2 - Trechos Desconectados (8 Vértices)",
        "Instância 3 - Malha Viária Real de Bauru-SP (35 Vértices)"
    ]
)

mapeamento_arquivos = {
    "Instância 1 - Didática (6 Vértices)": "data/instancia_1_pequena.json",
    "Instância 2 - Trechos Desconectados (8 Vértices)": "data/instancia_2_desconectada.json",
    "Instância 3 - Malha Viária Real de Bauru-SP (35 Vértices)": "data/instancia_3_urbana_real.json"
}

caminho_json = mapeamento_arquivos[instancia_opcao]
grafo_obj = GrafoMalhaUrbana(caminho_json)

# Simulador de Tráfego / Horário de Pico
st.sidebar.subheader("🚦 Simulação de Condições de Tráfego")
condicao_trafego = st.sidebar.select_slider(
    "Previsão de Fluxo / Horário:",
    options=["Fluidez Normal (Livre)", "Horário de Pico (Trânsito 1.5x)", "Dia de Chuva/Alagamento (2.2x)"],
    value="Fluidez Normal (Livre)"
)

fatores_map = {
    "Fluidez Normal (Livre)": 1.0,
    "Horário de Pico (Trânsito 1.5x)": 1.5,
    "Dia de Chuva/Alagamento (2.2x)": 2.2
}
fator_atual = fatores_map[condicao_trafego]

# Gerenciamento de Vias Bloqueadas na Sessão
if 'bloqueios' not in st.session_state:
    st.session_state.bloqueios = []

# Limpa bloqueios caso troque de instância para evitar inconsistências
if 'ultima_instancia' not in st.session_state or st.session_state.ultima_instancia != instancia_opcao:
    st.session_state.bloqueios = []
    st.session_state.ultima_instancia = instancia_opcao

st.sidebar.subheader("🚧 Simular Interdição de Via")
todas_arestas = [(a["origem"], a["destino"]) for a in grafo_obj.edges]

if todas_arestas:
    aresta_bloquear = st.sidebar.selectbox(
        "Selecione uma via para bloquear:",
        todas_arestas,
        format_func=lambda x: f"Via do Nó {x[0]} -> Nó {x[1]}"
    )
    if st.sidebar.button("Bloquear Via Selecionada"):
        if aresta_bloquear not in st.session_state.bloqueios:
            st.session_state.bloqueios.append(aresta_bloquear)
            st.sidebar.success(f"Via {aresta_bloquear} interditada!")

if st.session_state.bloqueios:
    st.sidebar.write("**Vias Atualmente Interditadas:**")
    for b in st.session_state.bloqueios:
        st.sidebar.text(f"• Nó {b[0]} -> Nó {b[1]}")
    if st.sidebar.button("Limpar Todos os Bloqueios"):
        st.session_state.bloqueios = []
        st.rerun()

# Execução do Algoritmo com Tráfego
inicio_tempo = time.perf_counter()
D, Next = grafo_obj.executar_floyd_warshall(
    vias_bloqueadas=st.session_state.bloqueios,
    fator_trafego=fator_atual
)
tempo_execucao_ms = (time.perf_counter() - inicio_tempo) * 1000

# Painel Principal Dividido em Duas Colunas
col1, col2 = st.columns([1, 2.2])

with col1:
    st.subheader("📍 Registrar Chamado de Emergência")
    
    opcoes_nos = {n["id"]: f"ID {n['id']} - {n['rotulo']}" for n in grafo_obj.nodes}
    destino_id = st.selectbox("Selecione o local da ocorrência (Destino):", list(opcoes_nos.keys()), format_func=lambda x: opcoes_nos[x])

    base_id, tempo_minimo = grafo_obj.encontrar_base_mais_proxima(destino_id, D)

    if base_id is not None and not math.isinf(tempo_minimo):
        caminho_nos = grafo_obj.reconstruir_caminho(base_id, destino_id, Next)
        st.success("✅ **Base Ideal Identificada!**")
        st.metric(label="Base Alocada", value=f"Nó {base_id}")
        st.metric(
            label="Tempo Estimado de Chegada",
            value=f"{tempo_minimo:.1f} min",
            delta=f"+{(tempo_minimo - tempo_minimo/fator_atual):.1f} min pelo tráfego" if fator_atual > 1.0 else None,
            delta_color="inverse"
        )
        st.write("**Rota Recomendada (Sequência de Vértices):**")
        st.info(" ➔ ".join([f"Nó {n}" for n in caminho_nos]))
    else:
        caminho_nos = []
        st.error("⚠️ **Inalcançável:** Não existe nenhuma base com rota disponível para este ponto!")

    st.caption(f"⚡ Tempo de processamento da matriz (Floyd-Warshall): **{tempo_execucao_ms:.3f} ms**")
    if grafo_obj.origem_dados:
        st.caption(f"ℹ️ **Fonte dos Dados:** {grafo_obj.origem_dados}")

with col2:
    st.subheader("🗺️ Visualização Interativa do Grafo (Com Zoom & Pan)")
    st.caption("🔍 **Dica:** Use o Scroll do mouse para dar Zoom e clique/arraste para mover o mapa.")

    # Moldura visual ao redor do mapa de grafos
    with st.container(border=True):
        # 1. Montagem do Grafo Base em NetworkX para calcular coordenadas estáticas
        G_full = nx.DiGraph()
        for n in grafo_obj.nodes:
            G_full.add_node(n["id"])
        for a in grafo_obj.edges:
            G_full.add_edge(a["origem"], a["destino"])

        # Cálculo de Posições Estáticas
        try:
            pos_dict = nx.kamada_kawai_layout(G_full)
        except Exception:
            pos_dict = nx.spring_layout(G_full, seed=42)

        # 2. Criação da Rede Interativa PyVis
        net = Network(height="580px", width="100%", directed=True, notebook=False)
        net.toggle_physics(False)

        net.set_options("""
        var options = {
          "nodes": {
            "shape": "circle",
            "size": 24,
            "font": {
              "color": "#ffffff",
              "size": 15,
              "bold": true,
              "face": "arial"
            },
            "borderWidth": 2
          },
          "edges": {
            "font": {
              "size": 11,
              "align": "middle"
            },
            "color": { "inherit": false },
            "smooth": { "type": "continuous", "roundness": 0.15 }
          },
          "physics": {
            "enabled": false
          },
          "interaction": {
            "hover": true,
            "zoomView": true,
            "dragView": true,
            "dragNodes": true
          }
        }
        """)

        # Vias componentes da rota calculada
        edges_caminho = set(zip(caminho_nos[:-1], caminho_nos[1:])) if len(caminho_nos) > 1 else set()

        # Adicionar Nós com Posições Fixas e Rótulos Numéricos Internos
        for n in grafo_obj.nodes:
            n_id = n["id"]
            tipo = n.get("tipo", "intersecao")
            rotulo_tooltip = f"Nó {n_id}: {n['rotulo']}"
            
            x_pos = float(pos_dict[n_id][0] * 1200)
            y_pos = float(pos_dict[n_id][1] * 1200)

            # Definição de Cores por Tipo
            if tipo == "base":
                cor = "#2ecc71"  # Verde
            elif tipo == "hospital":
                cor = "#e74c3c"  # Vermelho
            else:
                cor = "#3498db"  # Azul

            net.add_node(
                n_id,
                label=str(n_id),
                title=rotulo_tooltip,
                color=cor,
                x=x_pos,
                y=y_pos,
                shape="circle"
            )

        # Adicionar Arestas (Omitindo completamente vias bloqueadas)
        for a in grafo_obj.edges:
            u, v = a["origem"], a["destino"]
            
            if (u, v) in st.session_state.bloqueios:
                continue

            tempo_calculado = a['tempo_min'] * fator_atual
            peso_label = f"{tempo_calculado:.1f} min"
            is_rota = (u, v) in edges_caminho

            if is_rota:
                net.add_edge(u, v, label=peso_label, color="#f1c40f", width=4, arrowStrikethrough=False)
            else:
                net.add_edge(u, v, label=peso_label, color="#bdc3c7", width=1.5, arrowStrikethrough=False)

        # Renderizar no Streamlit
        html_file = "temp_graph.html"
        net.save_graph(html_file)

        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        components.html(html_content, height=600)

        if os.path.exists(html_file):
            os.remove(html_file)

# Exibição Transparente da Matriz D
with st.expander("📊 Visualizar Matriz de Distâncias Mínimas D (Floyd-Warshall)"):
    st.write("Linhas representam Vértices de Origem e Colunas Vértices de Destino (Valores em Minutos Reais com Tráfego):")
    st.dataframe(D)