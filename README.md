## RescuEU — Sistema de Otimização e Roteamento para Emergências (SAMU Bauru-SP)

**Disciplina:** Teoria dos Grafos  
**Tema:** Caminhos Mínimos (Algoritmok: Floyd-Warshall)  
**Curso:** Ciência da Computação  

---

## Identificação dos Integrantes

| Nome Completo | Matrícula / R.A. | Função no Projeto |

| [Matheus de Amorim Favero] | [23111800] | Estruturação de Repositório e Automação |

| [Kaue Kanagusko Ruiz] | [23110392] | Modelagem de Dados JSON (Bauru-SP) |

| [Gerson de Oliveira Lopes Junior] | [23110278] | Algoritmo Core e Estrutura de Grafos |

| [Lucas Antonio Pires de Souza] | [23111386] | Interface Gráfica Streamlit e Renderização PyVis |

| [Lucas Souza dos Santos] | [23111950] | Simulador de Tráfego e Documentação Técnica |

---

## Descrição do Problema e Relevância

O tempo de resposta do Atendimento Móvel de Urgência (SAMU) é determinante em casos de emergência médica. Em uma rede urbana como a de **Bauru-SP**, a escolha da base ideal para o despacho de ambulâncias e a definição imediata da rota até o local do chamado — e posteriormente ao hospital com leito disponível — exige o cálculo completo das distâncias mínimas entre todos os pontos da cidade ($APSP - All\text{-}Pairs\ Shortest\ Path$).

O sistema **RescuEU** utiliza o algoritmo de **Floyd-Warshall** para pré-calcular e atualizar a matriz global de tempos de deslocamento entre intersecções, bases operacionais e unidades hospitalares.

---

## Modelagem do Grafo

O problema foi modelado como um **grafo direcionado e ponderado** $G = (V, A, w)$:

* **Vértices ($V$):** Representam os pontos de interesse na cidade de Bauru-SP:
  * **Bases SAMU:** Central (Av. Duque de Caxias), Geisel/Redentor, Vila Falcão e Mary Dota.
  * **Hospitais / UPAs:** PSC, Hospital de Base, Hospital Estadual, Hospital das Clínicas, Unimed, Maternidade Santa Isabel e UPAs Bela Vista, Ipiranga, Geisel, Mary Dota e Redentor.
  * **Intersecções Viárias:** Cruzamentos estratégicos e acessos a rodovias (Rod. Marechal Rondon SP-300, Rod. Bauru-Jaú SP-225, Av. Nações Unidas, Av. Getúlio Vargas).
* **Arestas ($A$):** Segmentos de vias públicas com sentido direcionado (respeitando vias de mão única).
* **Pesos ($w$):** Tempo estimado de deslocamento em minutos ($t = \frac{d}{v}$), ajustado dinamicamente por fatores de tráfego e condições climáticas.

---

## Fundamentação do Algoritmo (Floyd-Warshall)

O algoritmo de **Floyd-Warshall** resolve o problema dos caminhos mínimos entre todos os pares de vértices em complexidade de tempo $O(\vert{}V\vert{}^3)$ e espaço $O(\vert{}V\vert{}^2)$.

$$\text{Equação de Recorrência: } D^{(k)}[i][j] = \min \left( D^{(k-1)}[i][j], D^{(k-1)}[i][k] + D^{(k-1)}[k][j] \right)$$

O sistema mantém duas matrizes principais:
1. **Matriz de Distâncias ($D$):** Armazena o tempo mínimo acumulado em minutos entre cada par de nós.
2. **Matriz de Sucessores ($\text{Next}$):** Utilizada na reconstrução exata da sequência de vértices do caminho percorrido.

---

## Estrutura do Repositório

```text
rescueu_project/
├── data/
│   ├── instancia_1_pequena.json          # Caso Didático (6 Vértices)
│   ├── instancia_2_desconectada.json      # Caso Fronteira com Nós Isolados (8 Vértices)
│   └── instancia_3_urbana_real.json       # Malha Viária Real de Bauru-SP (35 Vértices)
├── src/
│   ├── graph.py                           # Módulo do Grafo e Floyd-Warshall
│   └── app.py                             # Interface Streamlit e Renderização PyVis
├── .gitignore                             # Arquivos ignorados pelo Git
├── README.md                              # Documentação completa
├── requirements.txt                       # Dependências Python
└── run.bat                                # Executável automatizado Windows
