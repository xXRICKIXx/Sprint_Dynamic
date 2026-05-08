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

- [Objetivo](#objetivo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tarefa 1 — Verificacao Recursiva de Duplicidade](#tarefa-1)
- [Tarefa 2 — Memorizacao](#tarefa-2)
- [Tarefa 3 — Otimizacao de Agenda](#tarefa-3)
- [Tarefa 4 — Grafo](#tarefa-4)
- [Tarefa 5 — Dijkstra](#tarefa-5)
- [Como Executar](#como-executar)
- [Exemplos de Saida](#exemplos-de-saida)

---

## Objetivo

Modelar e resolver problemas do CRM do Hospital Sao Rafael usando **recursao** e **memorizacao**:

1. Verificar duplicidade de leads
2. Evitar recalculo de comparacoes repetidas
3. Otimizar encaixe de consultas na agenda
4. Modelar o fluxo do lead com grafos
5. Encontar o melhor caminho e menor custo com dijkstra 
---

## Estrutura do Projeto


crm-recursao/
├── crm_recursao_memorizacao.py
└── README.md


### Estrutura interna do modulo


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

## Tarefa 1

### Verificacao Recursiva de Duplicidade

**Problema:**  
Um lead pode chegar com dados levemente diferentes (nome abreviado, telefone formatado, etc).  
E necessario validar duplicidade de forma flexivel.

**Solucao:**  
Funcao recursiva que percorre a lista de cadastros.

```python
def verificar_duplicidade_recursiva(novo, cadastros, i=0, campos=None):

Logica:

indice >= tamanho -> retorna (0, None)

cpf igual -> retorna (1, lead)

2 campos iguais -> retorna (1, lead)

senao -> chamada recursiva (i + 1)

senao
  -> chamada recursiva (i + 1)

Regras de comparacao:

Campo	Regra
CPF	duplicata direta
Email	+1 ponto
Telefone	+1 ponto
Nome	+1 ponto
Resultado	>= 2 pontos = duplicata

Retorno:

1 = duplicata
0 = nao duplicata

Tarefa 2
Memorizacao (Cache)

Problema:
Comparacoes repetidas entre os mesmos leads.

Solucao:
Uso de dicionario para armazenar resultados.

cache = {}
chave = (id_novo, id_existente)

if chave in cache:
    return cache[chave]

cache[chave] = resultado

Beneficios:

evita recalculo
melhora desempenho

Exemplo:

| Duracao | Consultas no dia (08:00-17:00) |
|---------|-------------------------------|
| 30 min  | 19 consultas                  |
| 45 min  | 10 consultas                  |
| 60 min  | 10 consultas                  |
| 90 min  |  7 consultas                  |


## Tarefa 4

## Modelagem de Fluxo com grafo

**Problema:** No CRM do Hospital São Rafael, o fluxo de leads segue múltiplas etapas até a conversão em cliente. É necessário representar esse processo de forma estruturada para análise e otimização.

**Solução:** Foi utilizado um grafo direcionado, onde:
Nós (vértices) representam etapas do funil
Arestas representam transições entre etapas
Pesos representam valores associados (ex: volume, custo ou tempo)

```python
grafo = {
    'Entrada': {'Visitante': 1000},
    'Visitante': {'Lead': 200},
    'Lead': {'Qualificado': 90, 'Perdidos': 110},
    'Qualificado': {'Cliente': 30},
    'Perdidos': {},
    'Cliente': {}
}
```
**Interpretação: ** Esse grafo modela o funil de leads:
```
Entrada → Visitante → Lead → Qualificado → Cliente
```
Também permite caminhos alternativos (ex: leads perdidos).

**Benefícios:**
Visualização clara do funil
Identificação de gargalos
Base para aplicação de algoritmos (como Dijkstra)


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

TAREFA 5 - Dijkstra

  Menor caminho:
  Entrada → Visitante → Lead → Qualificado → Cliente

  Custo total:
  1320
```

Agenda
Inicio  Fim
08:00   09:00
09:00   10:00
...
Total: 10



