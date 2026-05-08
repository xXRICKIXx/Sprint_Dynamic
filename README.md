# Caring Hands CRM — Recursao e Memorizacao

**Disciplina:** Dynamic Programing

**Sprint:** 4

**Grupo:** Caring Hands — Hospital Sao Rafael 

| Nome | RM |
|---|---|
| [Henrique Celso] | [559687] |
| [Lucas Cortizo] | [559734] |
| [Gabriela Queiroga] | [560035] |
| [Maria Eduarda Ferrés] | [560418] |

---

## Sumario

- [Visão Geral](#objetivo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Executar](#como-executar)
- [Tarefas Implementadas](#tarefas-implementadas)
  - [Tarefa 1 — Verificação de Duplicidade (Recursão)](#tarefa-1--verificação-de-duplicidade-recursão)
  - [Tarefa 2 — Cache de Comparações](#tarefa-2--cache-de-comparações)
  - [Tarefa 3 — Otimização de Agenda (Memoização)](#tarefa-3--otimização-de-agenda-memoização)
  - [Tarefa 4 — Grafo do Fluxo CRM](#tarefa-4--grafo-do-fluxo-crm)
  - [Tarefa 5 — Dijkstra: Menor Caminho no Funil](#tarefa-5--dijkstra-menor-caminho-no-funil)
- [Saída Esperada](#saída-esperada)
- [Decisões Técnicas](#decisões-técnicas)

---

## Objetivo

Modelar e resolver problemas do CRM do Hospital Sao Rafael usando **recursao** e **memorizacao**:

1. Verificar duplicidade de leads
2. Evitar recalculo de comparacoes repetidas
3. Otimizar encaixe de consultas na agenda
4. Modelar o fluxo do lead com grafos
5. Encontar o melhor caminho e menor custo com dijkstra 
---

## Como Executar

**Pré-requisito:** Python 3.8 ou superior. Nenhuma dependência externa é necessária.

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/caring-hands-crm.git
cd caring-hands-crm

# Execute diretamente
python caring_hands_crm_sprint4.py
```

---

## Estrutura do Projeto

```
crm_recursao_memorizacao.py
│
├── UTILITARIOS
│   ├── normalizar(texto)
│   ├── limpar_telefone(tel)
│   └── limpar_cpf(cpf)
│
├── ESTRUTURA DE DADOS
│   └── class Lead
│
├── TAREFA 1 — RECURSAO
│   └── verificar_duplicidade_recursiva(...)
│
├── TAREFA 2 — CACHE
│   ├── comparar_com_cache(...)
│   ├── verificar_com_cache(...)
│   ├── stats_cache()
│   └── limpar_cache()
│
├── TAREFA 3 — AGENDA
│   ├── melhor_agenda(...)
│   ├── minutos_para_hora(...)
│   └── exibir_agenda(...)
│
├── TAREFA 4 — GRAFO
│   └── grafo
│
├── TAREFA 5 — DIJKSTRA
│   └── dijkstra(grafo, start, end)
│
└── ZONA DE TESTES
    ├── demo_tarefa1()
    ├── demo_tarefa2()
    └── demo_tarefa3()
```

---

## Tarefas Implementadas

### Tarefa 1 — Verificação de Duplicidade (Recursão)

**Função:** `verificar_duplicidade_recursiva(novo, cadastros, i, campos)`

Verifica recursivamente se um novo lead já existe na base de dados, usando dois critérios:

- **CPF igual** → duplicata imediata (prioridade máxima)
- **2 ou mais campos coincidentes** (nome, e-mail, telefone) → duplicata confirmada

```python
base = [
    Lead("Jose",  "1199", "jose@mail.com",  "111"),
    Lead("Maria", "1188", "maria@mail.com", "222"),
]

novo = Lead("Jose Outro", "0000", "x@mail.com", "111")
resultado, duplicata = verificar_duplicidade_recursiva(novo, base)
# resultado = 1, duplicata = Lead(Jose, 111)
```

**Fluxo da recursão:**

```
verificar(novo, cadastros, i=0)
  ├── compara com cadastros[0]  → match? → retorna
  └── não match → verificar(novo, cadastros, i=1)
                    ├── compara com cadastros[1] → match? → retorna
                    └── não match → verificar(novo, cadastros, i=2)
                                      └── i >= len → retorna (0, None)
```

---

### Tarefa 2 — Cache de Comparações

**Funções:** `comparar_com_cache()`, `verificar_com_cache()`, `stats_cache()`

Evita recalcular comparações entre pares de leads já processados anteriormente, usando um dicionário de cache indexado por `(id_novo, id_existente)`.

```python
limpar_cache()

base = [Lead("P5", "5", "p5@mail.com", "5"), ...]
novo = Lead("P5", "5", "p5@mail.com", "5")

# 1ª execução: todas as comparações são misses
verificar_com_cache(novo, 100, base, ids)

# 2ª execução: comparações já cacheadas viram hits
verificar_com_cache(novo, 100, base, ids)

print(stats_cache())
# {'total': 12, 'hits': 6, 'misses': 6, 'taxa': '50.0%', 'itens': 6}
```

**Evolução da taxa de hit com chamadas repetidas:**

| Rodada | Hits | Misses | Taxa |
|--------|------|--------|------|
| 1ª     | 0    | 6      | 0%   |
| 2ª     | 6    | 6      | 50%  |
| 3ª     | 12   | 6      | 66.7%|

---


## Tarefa 5

**Algoritmo Dijkstra**

**Problema:** Dado o grafo de leads, é necessário encontrar o caminho mais eficiente da entrada até a conversão em cliente.

**Solução:** Foi implementado o algoritmo de Dijkstra para encontrar o menor caminho (menor custo acumulado) entre dois nós.
```python
def dijkstra(grafo, start, end):
    dist = {node: float('inf') for node in grafo}
    dist[start] = 0

    pq = [(0, start, [start])]

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node == end:
            return cost, path

        if cost > dist[node]:
            continue

        for neighbor, weight in grafo[node].items():
            new_cost = cost + weight
            new_path = path + [neighbor]

            if new_cost < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor, new_path))

    return float('inf'), []
```
**Interpretação do Resultado:** Após executar o algoritmo:
```
Menor caminho:
Entrada → Visitante → Lead → Qualificado → Cliente

Custo total:
1320
```
**Explicação:** O algoritmo percorre o grafo acumulando os pesos das arestas e seleciona o caminho com menor custo total.
Por que esse fluxo é mais eficiente?
É o único caminho que leva até “Cliente”
Possui o menor custo acumulado possível
O algoritmo garante que não existe caminho melhor

**Conclusão:**
A modelagem com grafos e o uso do Dijkstra permitiram:

Representar o funil de leads de forma estruturada
Aplicar conceitos de algoritmos clássicos
Analisar caminhos de conversão

Essas técnicas complementam as tarefas anteriores de recursão e memorização, trazendo uma abordagem mais analítica e orientada a otimização dentro do CRM.

---

Metricas:

{
  "total": 20,
  "hits": 5,
  "misses": 15,
  "taxa": "25%",
  "itens": 15
}
Tarefa 3
Otimizacao de Agenda

Problema:
Maximizar numero de consultas sem conflito de horario.

Entrada:

lista de horarios (em minutos)
duracao da consulta

Solucao:
Recursao + lru_cache

@lru_cache(maxsize=512)
def melhor_agenda(horarios, duracao, i=0):

Logica:

1. encaixar horario atual
2. pular horario
3. escolher melhor resultado

Exemplo:

Duracao	Total
30 min	19
60 min	10
90 min	7
Como Executar
Requisitos
Python 3.x
Nenhuma biblioteca externa
Execucao
python crm_recursao_memorizacao.py
Exemplos de Saida
T1

Duplicata: 1
Match: Lead(Jose, 111)

T2

{'total': 30, 'hits': 10, 'misses': 20, 'taxa': '33%', 'itens': 20}

  Tempo 1a chamada : 0.0104 ms
  Tempo 2a chamada : 0.0005 ms   <- cache ativo

### Tarefa 3 — Otimização de Agenda (Memoização)

**Função:** `melhor_agenda(horarios, duracao, i)` — decorada com `@lru_cache`

Usa programação dinâmica para encontrar o maior número de consultas que podem ser agendadas sem sobreposição de horários.

```python
slots = tuple(range(480, 1021, 30))  # 08:00 às 17:00, a cada 30 min
agenda, total = melhor_agenda(slots, 60)

# Saída:
# 08:00 → 09:00
# 09:00 → 10:00
# ...
# 16:00 → 17:00
# Total: 10 consultas
```

> A função avalia recursivamente duas opções a cada horário — incluir ou pular — e armazena os subproblemas resolvidos via `lru_cache`, evitando recomputações.

---

### Tarefa 4 — Grafo do Fluxo CRM

O funil de conversão é modelado como um **grafo direcionado e ponderado**, onde:

- **Nós** representam etapas do funil
- **Arestas** representam transições entre etapas
- **Pesos** representam o volume de leads em cada transição

```
Entrada (1000)
   │
   ▼
Visitante (200)
   │
   ▼
  Lead
  ├──(90)──▶ Qualificado
  │               │
  │              (30)
  │               ▼
  │            Cliente  ← destino
  │
  └──(110)──▶ Perdidos
```

```python
grafo_crm = {
    'Entrada':    {'Visitante':   1000},
    'Visitante':  {'Lead':         200},
    'Lead':       {'Qualificado':   90, 'Perdidos': 110},
    'Qualificado':{'Cliente':        30},
    'Perdidos':   {},
    'Cliente':    {}
}
```

---

### Tarefa 5 — Dijkstra: Menor Caminho no Funil

**Função:** `dijkstra(grafo, start, end)`

Encontra o caminho de menor custo total entre dois nós do grafo usando uma **fila de prioridade (heap mínimo)**.

```python
custo, caminho = dijkstra(grafo_crm, 'Entrada', 'Cliente')

# Saída:
# Caminho: Entrada → Visitante → Lead → Qualificado → Cliente
# Custo total: 1320
```

**Detalhamento do caminho encontrado:**

| Transição | Peso |
|---|---|
| Entrada → Visitante | 1000 |
| Visitante → Lead | 200 |
| Lead → Qualificado | 90 |
| Qualificado → Cliente | 30 |
| **Total** | **1320** |

**Por que esse caminho é o mais eficiente?**

1. **É o único caminho viável:** o grafo possui estrutura linear com um único desvio (`Lead → Perdidos`), que não alcança o nó `Cliente`.

2. **O ramo alternativo é descartado:** `Lead → Perdidos` tem peso 110, mas o nó `Perdidos` não possui saída para `Cliente`, sendo eliminado pelo algoritmo.

3. **Garantia de optimalidade:** o Dijkstra usa um heap mínimo que sempre expande o caminho de menor custo acumulado primeiro. Quando o nó destino é alcançado, o custo encontrado é matematicamente o menor possível para a estrutura do grafo.

> **Conclusão:** o caminho `Entrada → Visitante → Lead → Qualificado → Cliente`, com custo total de **1320**, é o único caminho viável e, portanto, o mais eficiente para converter um lead em cliente dentro do funil modelado.

---

## Saída Esperada

```
==================================================
TAREFA 1 — Verificação de Duplicidade (Recursão)
==================================================

  Novo lead:  Lead(Jose Outro, 111)
  Duplicata?: Sim
  Conflito:   Lead(Jose, 111)

  Novo lead:  Lead(Jose, 999)
  Duplicata?: Sim
  Conflito:   Lead(Jose, 111)

  Novo lead:  Lead(Carlos, 333)
  Duplicata?: Não
  Conflito:   None

==================================================
TAREFA 2 — Cache de Comparações
==================================================

  Executando 3 buscas pelo mesmo lead...
  Rodada 1: hits=0, misses=6, taxa=0.0%
  Rodada 2: hits=6, misses=6, taxa=50.0%
  Rodada 3: hits=12, misses=6, taxa=66.7%

==================================================
TAREFA 3 — Otimização de Agenda (Memoização)
==================================================

  Agenda otimizada:
  Início  Fim
  08:00   09:00
  ...
  16:00   17:00
  Total de consultas: 10

==================================================
TAREFA 5 — Dijkstra: Menor Caminho
==================================================

  Menor caminho encontrado:
  Entrada → Visitante → Lead → Qualificado → Cliente

  Custo total: 1320
```

---

## Decisões Técnicas

| Escolha | Justificativa |
|---|---|
| Recursão na deduplicação | Estrutura natural para percorrer listas de tamanho variável; facilita rastreamento da lógica de comparação |
| Cache manual com dicionário | Controle explícito de hits/misses para auditoria e métricas de desempenho |
| `@lru_cache` na agenda | Memoização automática do Python para subproblemas da programação dinâmica |
| Grafo como dicionário de adjacência | Representação simples, legível e compatível com o algoritmo de Dijkstra |
| Heap mínimo no Dijkstra | Garante complexidade O((V + E) log V), ideal para grafos esparsos como o funil CRM |
| Python puro (sem dependências) | Portabilidade máxima; todos os módulos usados (`heapq`, `functools`) são da biblioteca padrão |

---


