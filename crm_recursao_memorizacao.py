from os import path
from functools import lru_cache
import time
import heapq



"""
============================================================
CARING HANDS CRM — SPRINT 4
============================================================
"""


# ================================================================
# UTILITARIOS
# ================================================================

def normalizar(texto):
    """
    minusculo + remove espaco
    (sem acento pra simplificar)
    """
    if not texto:
        return ""
    return texto.lower().strip()


def limpar_telefone(tel):
    """mantem apenas numeros"""
    if not tel:
        return ""

    resultado = ""
    for c in tel:
        if c.isdigit():
            resultado += c
    return resultado


def limpar_cpf(cpf):
    """mantem apenas numeros"""
    if not cpf:
        return ""

    resultado = ""
    for c in cpf:
        if c.isdigit():
            resultado += c
    return resultado


# ================================================================
# ESTRUTURA
# ================================================================

class Lead:

    def __init__(self, nome, telefone, email, cpf):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.cpf = cpf

    def nome_norm(self):
        return normalizar(self.nome)

    def telefone_norm(self):
        return limpar_telefone(self.telefone)

    def email_norm(self):
        if not self.email:
            return ""
        return self.email.lower().strip()

    def cpf_norm(self):
        return limpar_cpf(self.cpf)

    def __repr__(self):
        return "Lead(" + self.nome + ", " + self.cpf + ")"


# ================================================================
# TAREFA 1 — RECURSAO
# ================================================================

def verificar_duplicidade_recursiva(novo, cadastros, i=0, campos=None):

    if campos is None:
        campos = ["cpf", "email", "telefone", "nome"]

    if i >= len(cadastros):
        return 0, None

    atual = cadastros[i]
    match = 0

    # cpf tem prioridade: qualquer coincidência já confirma duplicata
    if "cpf" in campos and novo.cpf_norm():
        if novo.cpf_norm() == atual.cpf_norm():
            return 1, atual

    # outros campos
    if "email" in campos and novo.email_norm():
        if novo.email_norm() == atual.email_norm():
            match += 1

    if "telefone" in campos and novo.telefone_norm():
        if novo.telefone_norm() == atual.telefone_norm():
            match += 1

    if "nome" in campos and novo.nome_norm():
        if novo.nome_norm() == atual.nome_norm():
            match += 1

    if match >= 2:
        return 1, atual

    return verificar_duplicidade_recursiva(novo, cadastros, i+1, campos)


# ================================================================
# TAREFA 2 — CACHE
# ================================================================

cache = {}
hits = 0
misses = 0


def comparar_com_cache(novo, existente, id_novo, id_existente, campos=None):

    # compara dois leads evitando recalcular comparacoes ja realizadas

    global hits, misses

    if campos is None:
        campos = ["cpf", "email", "telefone", "nome"]

    chave = (id_novo, id_existente)

    if chave in cache:
        hits += 1
        return cache[chave]

    misses += 1
    resultado = 0

    if "cpf" in campos and novo.cpf_norm():
        if novo.cpf_norm() == existente.cpf_norm():
            resultado = 1

    if resultado == 0:
        match = 0

        if "email" in campos and novo.email_norm() == existente.email_norm() and novo.email_norm():
            match += 1

        if "telefone" in campos and novo.telefone_norm() == existente.telefone_norm() and novo.telefone_norm():
            match += 1

        if "nome" in campos and novo.nome_norm() == existente.nome_norm() and novo.nome_norm():
            match += 1

        if match >= 2:
            resultado = 1

    cache[chave] = resultado
    return resultado


def verificar_com_cache(novo, id_novo, cadastros, ids, i=0, campos=None):

    if i >= len(cadastros):
        return 0, None

    dup = comparar_com_cache(
        novo,
        cadastros[i],
        id_novo,
        ids[i],
        campos
    )

    if dup == 1:
        return 1, cadastros[i]

    return verificar_com_cache(novo, id_novo, cadastros, ids, i+1, campos)


def stats_cache():
    total = hits + misses
    taxa = "0%" if total == 0 else str(round(hits / total * 100,1)) + "%"
    return {
        "total": total,
        "hits": hits,
        "misses": misses,
        "taxa": taxa,
        "itens": len(cache)
    }


def limpar_cache():
    global hits, misses
    cache.clear()
    hits = 0
    misses = 0


# ================================================================
# TAREFA 3 — AGENDA
# ================================================================

@lru_cache(maxsize=512)
def melhor_agenda(horarios, duracao, i=0):
    "DP com memo para maximizar"

    if i >= len(horarios):
        return [], 0

    atual = horarios[i]

    fim = atual + duracao
    prox = i + 1

    while prox < len(horarios) and horarios[prox] < fim:
        prox += 1

    com_slots, com_total = melhor_agenda(horarios, duracao, prox)
    opcao_a = ([atual] + com_slots, 1 + com_total)

    sem_slots, sem_total = melhor_agenda(horarios, duracao, i+1)
    opcao_b = (sem_slots, sem_total)

    if opcao_a[1] >= opcao_b[1]:
        return opcao_a
    return opcao_b


def minutos_para_hora(m):
    h = m // 60
    mi = m % 60
    return str(h).zfill(2) + ":" + str(mi).zfill(2)


def exibir_agenda(slots, duracao):
    print("\n  Agenda otimizada:")
    print("  Início  Fim")
    print("  " + "-" * 14)
    for s in slots:
        print(" ", minutos_para_hora(s), " ", minutos_para_hora(s + duracao))
    print("  Total de consultas:", len(slots))


# ================================================================
# TAREFA 4 — GRAFO
# ================================================================
# O grafo abaixo representa o funil de conversão do CRM.
# Cada nó é uma etapa do fluxo e cada aresta tem um peso que
# representa o número de leads que transitam entre as etapas.
# Os pesos maiores indicam caminhos com maior volume de leads
# (portanto, maior "custo" de processamento/acompanhamento).
#
# Estrutura:
#   Entrada → Visitante → Lead → Qualificado → Cliente
#                               ↘ Perdidos
#
# Pesos (volume de transições):
#   Entrada    → Visitante  : 1000
#   Visitante  → Lead       :  200
#   Lead       → Qualificado:   90
#   Lead       → Perdidos   :  110
#   Qualificado → Cliente   :   30
# ================================================================

grafo_crm = {
    'Entrada': {'Visitante': 1000},
    'Visitante': {'Lead': 200},
    'Lead': {'Qualificado': 90, 'Perdidos': 110},
    'Qualificado': {'Cliente': 30},
    'Perdidos': {},
    'Cliente': {}
}

# ================================================================
# TAREFA 5 — DIJKSTRA
# ================================================================

def dijkstra(grafo, start, end):
    """
    Encontra o menor caminho entre dois nós em um grafo ponderado.

    Parâmetros:
        grafo  : dicionário de adjacência {nó: {vizinho: peso}}
        start  : nó de origem
        end    : nó de destino

    Retorna:
        (custo_total, caminho) — menor custo e lista de nós do percurso.
        Se não houver caminho, retorna (inf, []).

    Complexidade: O((V + E) log V)
    """
    # Inicializa todas as distâncias como infinito
    dist = {node: float('inf') for node in grafo}
    dist[start] = 0

    # Fila de prioridade: (custo_acumulado, nó_atual, caminho_percorrido)
    pq = [(0, start, [start])]

    while pq:
        cost, node, path = heapq.heappop(pq)

        # Chegamos ao destino
        if node == end:
            return cost, path

        # Ignora entradas desatualizadas na fila
        if cost > dist[node]:
            continue

        for neighbor, weight in grafo[node].items():
            new_cost = cost + weight
            if new_cost < dist.get(neighbor, float('inf')):
                dist[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    return float('inf'), []

# ================================================================
# TAREFA 6 — COMPARAÇÃO DE CAMINHOS
# ================================================================
 
def todos_os_caminhos(grafo, start, end, caminho=None):
    """
    Encontra todos os caminhos possíveis entre dois nós usando DFS.
 
    Parâmetros:
        grafo   : dicionário de adjacência {nó: {vizinho: peso}}
        start   : nó de origem
        end     : nó de destino
        caminho : caminho acumulado na recursão (uso interno)
 
    Retorna:
        Lista de tuplas (custo_total, caminho) para cada rota encontrada.
    """
    if caminho is None:
        caminho = [start]
 
    if start == end:
        custo = 0
        for i in range(len(caminho) - 1):
            custo += grafo[caminho[i]][caminho[i + 1]]
        return [(custo, list(caminho))]
 
    resultados = []
    for vizinho in grafo[start]:
        if vizinho not in caminho:  # evita ciclos
            resultados += todos_os_caminhos(grafo, vizinho, end, caminho + [vizinho])
 
    return resultados
 
 
def comparar_caminhos(grafo, start, end):
    """
    Lista todos os caminhos entre start e end, ordenados pelo custo,
    destacando o caminho mínimo encontrado pelo Dijkstra.
    """
    caminhos = todos_os_caminhos(grafo, start, end)
 
    if not caminhos:
        print(f"\n  Nenhum caminho encontrado entre '{start}' e '{end}'.")
        return
 
    caminhos.sort(key=lambda x: x[0])
    melhor_custo = caminhos[0][0]
 
    print(f"\n  Todos os caminhos de '{start}' até '{end}':\n")
    print(f"  {'#':<4} {'Caminho':<50} {'Custo':>6}  ")
    print("  " + "-" * 65)
 
    for i, (custo, caminho) in enumerate(caminhos, 1):
        rota = " → ".join(caminho)
        destaque = "  ◀ MENOR CAMINHO" if custo == melhor_custo else ""
        print(f"  {i:<4} {rota:<50} {custo:>6}{destaque}")
 
    print("  " + "-" * 65)
    print(f"\n  Total de caminhos encontrados: {len(caminhos)}")


# ================================================================
# TESTES
# ================================================================
def demo1():
    print("\n" + "=" * 50)
    print("TAREFA 1 — Verificação de Duplicidade (Recursão)")
    print("=" * 50)

    base = [
        Lead("Jose",  "1199", "jose@mail.com",  "111"),
        Lead("Maria", "1188", "maria@mail.com", "222")
    ]

    # CPF igual → duplicata imediata
    novo_cpf = Lead("Jose Outro", "0000", "x@mail.com", "111")
    r, d = verificar_duplicidade_recursiva(novo_cpf, base)
    print(f"\n  Novo lead:  {novo_cpf}")
    print(f"  Duplicata?: {'Sim' if r else 'Não'}")
    print(f"  Conflito:   {d}")

    # 2 campos coincidentes → duplicata
    novo_multi = Lead("Jose", "1199", "outro@mail.com", "999")
    r2, d2 = verificar_duplicidade_recursiva(novo_multi, base)
    print(f"\n  Novo lead:  {novo_multi}")
    print(f"  Duplicata?: {'Sim' if r2 else 'Não'}")
    print(f"  Conflito:   {d2}")

    # Nenhum campo coincidente → sem duplicata
    novo_ok = Lead("Carlos", "9999", "carlos@mail.com", "333")
    r3, d3 = verificar_duplicidade_recursiva(novo_ok, base)
    print(f"\n  Novo lead:  {novo_ok}")
    print(f"  Duplicata?: {'Sim' if r3 else 'Não'}")
    print(f"  Conflito:   {d3}")


def demo2():
    print("\n" + "=" * 50)
    print("TAREFA 2 — Cache de Comparações")
    print("=" * 50)

    limpar_cache()

    base = [Lead("P" + str(i), str(i), "p" + str(i) + "@mail.com", str(i)) for i in range(10)]
    ids = list(range(10))

    novo = Lead("P5", "5", "p5@mail.com", "5")

    print("\n  Executando 3 buscas pelo mesmo lead...")
    for rodada in range(1, 4):
        verificar_com_cache(novo, 100, base, ids)
        s = stats_cache()
        print(f"  Rodada {rodada}: hits={s['hits']}, misses={s['misses']}, taxa={s['taxa']}")

    print(f"\n  Resultado final do cache: {stats_cache()}")


def demo3():
    print("\n" + "=" * 50)
    print("TAREFA 3 — Otimização de Agenda (Memoização)")
    print("=" * 50)

    slots = tuple(range(480, 1021, 30))  # 08:00 às 17:00, a cada 30 min
    melhor_agenda.cache_clear()
    agenda, total = melhor_agenda(slots, 60)
    exibir_agenda(agenda, 60)


def demo_grafo_dijkstra():
    print("\n" + "=" * 50)
    print("TAREFA 4 — Grafo do Fluxo CRM")
    print("=" * 50)

    print("""
  Estrutura do funil de conversão:

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
    """)

    print("  Nós do grafo:", list(grafo_crm.keys()))
    print("\n  Arestas e pesos:")
    for origem, destinos in grafo_crm.items():
        for destino, peso in destinos.items():
            print(f"    {origem:15} → {destino:15} (peso: {peso})")

    print("\n" + "=" * 50)
    print("TAREFA 5 — Dijkstra: Menor Caminho")
    print("=" * 50)

    origem = 'Entrada'
    destino = 'Cliente'

    custo, caminho = dijkstra(grafo_crm, origem, destino)

    print(f"\n  De: '{origem}'  →  Até: '{destino}'")
    print(f"\n  Menor caminho encontrado:")
    print("  " + " → ".join(caminho))
    print(f"\n  Custo total: {custo}")

    print("""
  ─────────────────────────────────────────────────
  INTERPRETAÇÃO DO RESULTADO
  ─────────────────────────────────────────────────

  O algoritmo de Dijkstra percorreu o grafo e encontrou
  o caminho de menor custo total entre 'Entrada' e 'Cliente':

      Entrada → Visitante → Lead → Qualificado → Cliente

  Custo de cada aresta nesse trajeto:
    • Entrada    → Visitante  :   1000
    • Visitante  → Lead       :    200
    • Lead       → Qualificado:     90
    • Qualificado → Cliente   :     30
                              ─────────
                       Total  :   1320

  Por que esse caminho é o mais eficiente?

  1. É o único caminho que conecta 'Entrada' até 'Cliente',
     pois o grafo possui estrutura linear com um único
     desvio possível (Lead → Perdidos), que não chega ao
     destino.

  2. O ramo alternativo Lead → Perdidos tem peso 110 e
     não leva ao nó 'Cliente', sendo descartado pelo
     Dijkstra por não atingir o destino.

  3. O algoritmo garante a optimalidade: ao usar uma fila
     de prioridade (heap mínimo), sempre expande o caminho
     de menor custo acumulado primeiro, assegurando que,
     ao atingir o destino, o custo encontrado seja o mínimo
     possível dentro da estrutura do grafo.

  Conclusão:
  O caminho Entrada → Visitante → Lead → Qualificado →
  Cliente, com custo total de 1320, é o único caminho
  viável e, portanto, o mais eficiente para converter um
  lead em cliente dentro do funil modelado.
  ─────────────────────────────────────────────────
    """)

    print("=" * 50)
    print("TAREFA 6 — Comparação de Todos os Caminhos")
    print("=" * 50)
    comparar_caminhos(grafo_crm, origem, destino)


# ================================================================
# EXECUÇÃO
# ================================================================


if __name__ == "__main__":
    demo1()
    demo2()
    demo3()
    demo_grafo_dijkstra()
    print("\nFim")
