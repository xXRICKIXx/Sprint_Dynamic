from os import path
from functools import lru_cache
import time
import heapq



"""
============================================================
CARING HANDS CRM — SPRINT 4
VERSAO SIMPLIFICADA
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

    # cpf
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

    global hits, misses

    if campos is None:
        campos = ["cpf", "email", "telefone", "nome"]

    chave = (id_novo, id_existente)

    if chave in cache:
        hits += 1
        return cache[chave]

    misses += 1
    resultado = 0

    # cpf
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

    if total == 0:
        taxa = "0%"
    else:
        taxa = str(round(hits/total*100, 1)) + "%"

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
    print("\nAgenda")
    print("Inicio  Fim")

    for s in slots:
        print(minutos_para_hora(s), minutos_para_hora(s+duracao))

    print("Total:", len(slots))



# ================================================================
# TAREFA 4 — Grafo
# ================================================================

grafo = {
    'Entrada': {'Visitante': 1000},
    'Visitante': {'Lead': 200},
    'Lead': {'Qualificado': 90, 'Perdidos': 110},
    'Qualificado': {'Cliente': 30},
    'Perdidos': {},
    'Cliente': {}
}

# ================================================================
# TAREFA 5 — Dijkstra
# ================================================================

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

cost, path = dijkstra(grafo, 'Entrada', 'Cliente')
print("Menor custo:", cost) 
print("Melhor Caminho:", ", ".join(path)) 

#Por que esse fluxo é mais eficiente?
#Esse fluxo é considerado mais eficiente porque:
#O algoritmo sempre escolhe as transições com menor custo parcial
#A soma total dos pesos (custos) ao longo desse caminho é a menor possível
#Não existe outro caminho alternativo até o nó “Cliente” com custo inferior
#Assim, o Dijkstra garante que esse é o caminho ótimo, ou seja, o mais eficiente dentro das condições modeladas no grafo.

#Conclusão:
#Portanto, o caminho encontrado pelo algoritmo é o mais eficiente 
#porque minimiza o custo total para levar um lead até a conversão em cliente, respeitando a estrutura do grafo definido.

# ================================================================
# TESTES
# ================================================================

def demo1():
    print("\nT1")

    base = [
        Lead("Jose", "1199", "jose@mail.com", "111"),
        Lead("Maria", "1188", "maria@mail.com", "222")
    ]

    novo = Lead("Jose", "0000", "x@mail.com", "111")

    r, d = verificar_duplicidade_recursiva(novo, base)

    print("Duplicata:", r)
    print("Match:", d)


def demo2():
    print("\nT2")

    limpar_cache()

    base = [Lead("P"+str(i), str(i), "p"+str(i), str(i)) for i in range(10)]
    ids = list(range(10))

    novo = Lead("P1", "1", "p1", "1")

    for _ in range(3):
        verificar_com_cache(novo, 100, base, ids)

    print(stats_cache())


def demo3():
    print("\nT3")

    slots = tuple(range(480, 1021, 30))

    melhor_agenda.cache_clear()

    agenda, total = melhor_agenda(slots, 60)

    exibir_agenda(agenda, 60)

# ================================================================
# ================================================================

demo1()
demo2()
demo3()

print("\nFim")
