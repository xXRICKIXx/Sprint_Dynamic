"""
============================================================
 CARING HANDS CRM — Sprint 3
 Recursao e Memorizacao no CRM

 Disciplina : Computational Thinking Using Python
 Instituicao: FIAP
 Grupo      : Caring Hands
============================================================

Modulo principal contendo:
  - Tarefa 1: Verificacao recursiva de duplicidade de leads
  - Tarefa 2: Memorizacao para evitar comparacoes repetidas
  - Tarefa 3: Otimizacao de agenda medica com subproblemas
"""

from __future__ import annotations
from functools import lru_cache
from typing import Optional
import unicodedata
import re
import time


# ================================================================
#  UTILITARIOS
# ================================================================

def normalizar(texto: str) -> str:
    """
    Normaliza uma string para comparacao:
    - Remove acentos
    - Converte para letras minusculas
    - Remove espacos extras
    """
    if not texto:
        return ""
    sem_acento = unicodedata.normalize("NFD", texto)
    sem_acento = "".join(c for c in sem_acento
                         if unicodedata.category(c) != "Mn")
    return sem_acento.lower().strip()


def limpar_telefone(tel: str) -> str:
    """Remove tudo que nao seja digito do telefone."""
    return re.sub(r"\D", "", tel or "")


def limpar_cpf(cpf: str) -> str:
    """Remove pontuacao do CPF."""
    return re.sub(r"\D", "", cpf or "")


# ================================================================
#  ESTRUTURA DE DADOS
# ================================================================

class Lead:
    """
    Representa um lead ou cadastro no CRM.

    Atributos
    ----------
    nome     : str — nome completo
    telefone : str — telefone (qualquer formato)
    email    : str — endereco de e-mail
    cpf      : str — CPF (com ou sem pontuacao)
    """

    def __init__(self, nome: str, telefone: str,
                 email: str, cpf: str) -> None:
        self.nome     = nome
        self.telefone = telefone
        self.email    = email
        self.cpf      = cpf

    # Versoes normalizadas para comparacao
    @property
    def nome_norm(self)     -> str: return normalizar(self.nome)
    @property
    def telefone_norm(self) -> str: return limpar_telefone(self.telefone)
    @property
    def email_norm(self)    -> str: return (self.email or "").lower().strip()
    @property
    def cpf_norm(self)      -> str: return limpar_cpf(self.cpf)

    def __repr__(self) -> str:
        return f"Lead(nome={self.nome!r}, cpf={self.cpf!r})"


# ================================================================
#  TAREFA 1 — VERIFICACAO RECURSIVA DE DUPLICIDADE
# ================================================================

def verificar_duplicidade_recursiva(
    novo_lead: Lead,
    cadastros: list[Lead],
    indice: int = 0,
    campos: list[str] | None = None
) -> tuple[bool, Optional[Lead]]:
    """
    Percorre recursivamente a lista de cadastros e verifica se
    o novo_lead ja existe com base nos campos informados.

    Estrategia recursiva
    --------------------
    Caso base  : indice == len(cadastros) → lista percorrida sem match → False
    Caso base  : campo de alta confianca (CPF) coincide → duplicata encontrada
    Caso rec.  : verifica o cadastro atual e avanca para o proximo indice

    Parametros
    ----------
    novo_lead  : Lead a ser verificado
    cadastros  : lista de leads ja cadastrados
    indice     : posicao atual na lista (controle da recursao)
    campos     : lista de campos a comparar.
                 Opcoes: "cpf", "email", "telefone", "nome"
                 Padrao: todos os quatro campos

    Retorno
    -------
    (True, lead_duplicado)  se duplicata encontrada
    (False, None)           se nao ha duplicata
    """
    if campos is None:
        campos = ["cpf", "email", "telefone", "nome"]

    # --- Caso base: percorreu toda a lista sem encontrar duplicata ---
    if indice >= len(cadastros):
        return False, None

    cadastro_atual = cadastros[indice]
    coincidencias  = 0

    # --- Verificacao campo a campo ---
    if "cpf" in campos and novo_lead.cpf_norm:
        if novo_lead.cpf_norm == cadastro_atual.cpf_norm:
            # CPF e identificador unico — uma coincidencia ja confirma duplicata
            return True, cadastro_atual

    if "email" in campos and novo_lead.email_norm:
        if novo_lead.email_norm == cadastro_atual.email_norm:
            coincidencias += 1

    if "telefone" in campos and novo_lead.telefone_norm:
        if novo_lead.telefone_norm == cadastro_atual.telefone_norm:
            coincidencias += 1

    if "nome" in campos and novo_lead.nome_norm:
        if novo_lead.nome_norm == cadastro_atual.nome_norm:
            coincidencias += 1

    # 2 ou mais campos coincidentes (exceto CPF) = duplicata provavel
    if coincidencias >= 2:
        return True, cadastro_atual

    # --- Chamada recursiva: avanca para o proximo cadastro ---
    return verificar_duplicidade_recursiva(
        novo_lead, cadastros, indice + 1, campos
    )


# ================================================================
#  TAREFA 2 — MEMORIZACAO (MEMOIZATION)
# ================================================================

# Cache externo: chave = (id_novo_lead, id_cadastro_existente)
# Valor = resultado da comparacao entre os dois leads
_cache_comparacoes: dict[tuple[int, int], bool] = {}
_cache_hits   = 0
_cache_misses = 0


def comparar_leads_com_cache(
    novo_lead: Lead,
    cadastro: Lead,
    id_novo: int,
    id_cadastro: int,
    campos: list[str] | None = None
) -> bool:
    """
    Compara dois leads e armazena o resultado em cache.
    Em chamadas subsequentes com os mesmos IDs, retorna o
    valor ja calculado sem repetir a comparacao.

    Parametros
    ----------
    novo_lead    : lead sendo verificado
    cadastro     : lead ja cadastrado
    id_novo      : identificador unico do novo lead
    id_cadastro  : identificador unico do cadastro existente
    campos       : campos a comparar (padrao: todos)

    Retorno
    -------
    True se duplicata detectada, False caso contrario
    """
    global _cache_hits, _cache_misses

    if campos is None:
        campos = ["cpf", "email", "telefone", "nome"]

    chave = (id_novo, id_cadastro)

    # --- Retorna resultado ja memorizado ---
    if chave in _cache_comparacoes:
        _cache_hits += 1
        return _cache_comparacoes[chave]

    # --- Calcula e memoriza ---
    _cache_misses += 1
    resultado = False

    if "cpf" in campos and novo_lead.cpf_norm:
        if novo_lead.cpf_norm == cadastro.cpf_norm:
            resultado = True

    if not resultado:
        coincidencias = 0
        if "email" in campos and novo_lead.email_norm == cadastro.email_norm and novo_lead.email_norm:
            coincidencias += 1
        if "telefone" in campos and novo_lead.telefone_norm == cadastro.telefone_norm and novo_lead.telefone_norm:
            coincidencias += 1
        if "nome" in campos and novo_lead.nome_norm == cadastro.nome_norm and novo_lead.nome_norm:
            coincidencias += 1
        resultado = coincidencias >= 2

    _cache_comparacoes[chave] = resultado
    return resultado


def verificar_duplicidade_com_memorizacao(
    novo_lead: Lead,
    id_novo: int,
    cadastros: list[Lead],
    ids_cadastros: list[int],
    indice: int = 0,
    campos: list[str] | None = None
) -> tuple[bool, Optional[Lead]]:
    """
    Versao com memorizacao da verificacao recursiva.
    Cada par (id_novo, id_cadastro) e comparado no maximo uma vez,
    mesmo que a funcao seja chamada multiplas vezes com os mesmos dados.

    Parametros
    ----------
    novo_lead     : lead a verificar
    id_novo       : id unico do novo lead
    cadastros     : lista de leads cadastrados
    ids_cadastros : ids correspondentes a cada cadastro
    indice        : posicao atual na recursao
    campos        : campos para comparacao

    Retorno
    -------
    (True, lead_duplicado) ou (False, None)
    """
    # --- Caso base ---
    if indice >= len(cadastros):
        return False, None

    duplicata = comparar_leads_com_cache(
        novo_lead,
        cadastros[indice],
        id_novo,
        ids_cadastros[indice],
        campos
    )

    if duplicata:
        return True, cadastros[indice]

    # --- Chamada recursiva ---
    return verificar_duplicidade_com_memorizacao(
        novo_lead, id_novo,
        cadastros, ids_cadastros,
        indice + 1, campos
    )


def estatisticas_cache() -> dict:
    """Retorna metricas de desempenho do cache de comparacoes."""
    total = _cache_hits + _cache_misses
    return {
        "total_comparacoes" : total,
        "cache_hits"        : _cache_hits,
        "cache_misses"      : _cache_misses,
        "taxa_acerto"       : f"{(_cache_hits/total*100):.1f}%" if total else "0%",
        "entradas_no_cache" : len(_cache_comparacoes),
    }


def limpar_cache() -> None:
    """Limpa o cache de comparacoes e reinicia os contadores."""
    global _cache_hits, _cache_misses
    _cache_comparacoes.clear()
    _cache_hits   = 0
    _cache_misses = 0


# ================================================================
#  TAREFA 3 — OTIMIZACAO DE AGENDA COM SUBPROBLEMAS
# ================================================================

@lru_cache(maxsize=512)
def melhor_encaixe_agenda(
    horarios_disponiveis: tuple[int, ...],
    duracao_consulta: int,
    indice: int = 0
) -> tuple[list[int], int]:
    """
    Calcula recursivamente o melhor encaixe de uma consulta nos
    horarios disponiveis de um medico, evitando recalcular
    os mesmos intervalos via @lru_cache (memorizacao automatica).

    Modelo do problema
    ------------------
    - horarios_disponiveis: tupla de inteiros representando o
      inicio de cada slot disponivel (em minutos desde 00:00).
      Ex: (480, 510, 540) = 08:00, 08:30, 09:00
    - duracao_consulta: duracao em minutos da consulta a encaixar
    - Um slot e valido se nao ha outro slot ocupado no intervalo
      [slot, slot + duracao_consulta)

    Estrategia recursiva
    --------------------
    Caso base : indice >= len(horarios) → nenhum slot restante → []
    Caso rec. : testa encaixar no slot atual
                vs. pular o slot e testar o proximo
                Escolhe a opcao que gera mais consultas no dia

    Retorno
    -------
    (lista_de_slots_escolhidos, total_de_consultas)

    Nota: a funcao usa @lru_cache, portanto os argumentos devem
    ser hashable — por isso horarios_disponiveis e uma tupla.
    """
    # --- Caso base ---
    if indice >= len(horarios_disponiveis):
        return [], 0

    slot_atual = horarios_disponiveis[indice]

    # Encontra o proximo slot apos o fim desta consulta
    fim_consulta = slot_atual + duracao_consulta
    proximo_livre = indice + 1
    while (proximo_livre < len(horarios_disponiveis) and
           horarios_disponiveis[proximo_livre] < fim_consulta):
        proximo_livre += 1

    # --- Opcao A: encaixar no slot atual ---
    slots_com, total_com = melhor_encaixe_agenda(
        horarios_disponiveis, duracao_consulta, proximo_livre
    )
    opcao_encaixar = ([slot_atual] + slots_com, 1 + total_com)

    # --- Opcao B: pular este slot ---
    slots_sem, total_sem = melhor_encaixe_agenda(
        horarios_disponiveis, duracao_consulta, indice + 1
    )
    opcao_pular = (slots_sem, total_sem)

    # --- Escolhe a opcao com mais consultas ---
    if opcao_encaixar[1] >= opcao_pular[1]:
        return opcao_encaixar
    return opcao_pular


def minutos_para_hora(minutos: int) -> str:
    """Converte minutos desde 00:00 para formato HH:MM."""
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def exibir_agenda(slots_escolhidos: list[int],
                  duracao: int,
                  nome_medico: str) -> None:
    """Exibe a agenda otimizada de forma legivel."""
    print(f"\n  Agenda otimizada — {nome_medico} ({duracao} min/consulta)")
    print(f"  {'Slot':<6} {'Inicio':<8} {'Fim':<8}")
    print(f"  {'-'*24}")
    for i, slot in enumerate(slots_escolhidos, 1):
        inicio = minutos_para_hora(slot)
        fim    = minutos_para_hora(slot + duracao)
        print(f"  {i:<6} {inicio:<8} {fim:<8}")
    print(f"  Total: {len(slots_escolhidos)} consultas encaixadas")


# ================================================================
#  ZONA DE TESTES
# ================================================================

def separador(titulo: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


def demo_tarefa1() -> None:
    """Demonstracao da verificacao recursiva de duplicidade."""
    separador("TAREFA 1 — Verificacao Recursiva de Duplicidade")

    # Base de dados existente no CRM
    cadastros = [
        Lead("Jose Antonio da Silva",  "11988880001", "jose.antonio@email.com",  "10010010011"),
        Lead("Maria Aparecida Rodrigues","11988880002","maria.aparecida@email.com","20020020022"),
        Lead("Roberto Carlos Mendes",  "11988880003", "roberto.mendes@email.com", "30030030033"),
        Lead("Luiza Helena Carvalho",  "11988880004", "luiza.carvalho@email.com", "40040040044"),
        Lead("Antonio Ferreira Neto",  "11988880005", "antonio.neto@email.com",   "50050050055"),
    ]

    # --- Caso 1: lead com CPF identico (duplicata certa) ---
    print("\n[Caso 1] Lead com CPF ja cadastrado:")
    lead_cpf = Lead("Jose A. Silva", "11900000000", "outro@email.com", "10010010011")
    encontrado, duplicata = verificar_duplicidade_recursiva(lead_cpf, cadastros)
    print(f"  Novo lead  : {lead_cpf}")
    print(f"  Duplicata? : {encontrado}")
    if duplicata:
        print(f"  Coincide com: {duplicata}")

    # --- Caso 2: lead com email + telefone iguais ---
    print("\n[Caso 2] Lead com e-mail e telefone iguais (2 campos):")
    lead_et = Lead("Maria A. Rodrigues", "11988880002",
                   "maria.aparecida@email.com", "99999999999")
    encontrado, duplicata = verificar_duplicidade_recursiva(lead_et, cadastros)
    print(f"  Novo lead  : {lead_et}")
    print(f"  Duplicata? : {encontrado}")
    if duplicata:
        print(f"  Coincide com: {duplicata}")

    # --- Caso 3: lead com nome e email iguais ---
    print("\n[Caso 3] Lead com nome e e-mail iguais (2 campos):")
    lead_ne = Lead("Roberto Carlos Mendes", "11977777777",
                   "roberto.mendes@email.com", "88888888888")
    encontrado, duplicata = verificar_duplicidade_recursiva(lead_ne, cadastros)
    print(f"  Novo lead  : {lead_ne}")
    print(f"  Duplicata? : {encontrado}")
    if duplicata:
        print(f"  Coincide com: {duplicata}")

    # --- Caso 4: lead genuinamente novo ---
    print("\n[Caso 4] Lead genuinamente novo (nenhum campo coincide):")
    lead_novo = Lead("Carla Fernanda Braga", "11966660001",
                     "carla.braga@email.com", "77711122233")
    encontrado, duplicata = verificar_duplicidade_recursiva(lead_novo, cadastros)
    print(f"  Novo lead  : {lead_novo}")
    print(f"  Duplicata? : {encontrado}")

    # --- Caso 5: verificacao apenas por CPF e email ---
    print("\n[Caso 5] Verificacao apenas pelos campos CPF e email:")
    lead_par = Lead("Luiza H. Carvalho", "11000000000",
                    "luiza.carvalho@email.com", "99988877766")
    encontrado, duplicata = verificar_duplicidade_recursiva(
        lead_par, cadastros, campos=["cpf", "email"]
    )
    print(f"  Novo lead  : {lead_par}")
    print(f"  Duplicata? : {encontrado}")
    if duplicata:
        print(f"  Coincide com: {duplicata}")


def demo_tarefa2() -> None:
    """Demonstracao da memorizacao e seu impacto de desempenho."""
    separador("TAREFA 2 — Memorizacao (Memoization)")

    limpar_cache()

    cadastros = [
        Lead("Jose Antonio da Silva",   "11988880001", "jose@email.com",  "10010010011"),
        Lead("Maria Aparecida",         "11988880002", "maria@email.com", "20020020022"),
        Lead("Roberto Carlos",          "11988880003", "rob@email.com",   "30030030033"),
        Lead("Luiza Helena",            "11988880004", "lui@email.com",   "40040040044"),
        Lead("Antonio Ferreira",        "11988880005", "ant@email.com",   "50050050055"),
        Lead("Conceicao Barbosa",       "11988880006", "con@email.com",   "60060060066"),
        Lead("Paulo Henrique Teixeira", "11988880007", "pau@email.com",   "70070070077"),
        Lead("Tereza Cristina Gomes",   "11988880008", "ter@email.com",   "80080080088"),
    ]
    ids_cadastros = list(range(100, 100 + len(cadastros)))

    novos_leads = [
        (Lead("Jose A. Silva",    "11988880001", "outro@email.com",  "10010010011"), 201),
        (Lead("Maria Aparecida",  "11988880002", "maria@email.com",  "99999999999"), 202),
        (Lead("Paciente Novo A",  "11900000001", "novo_a@email.com", "11122233344"), 203),
        (Lead("Paciente Novo B",  "11900000002", "novo_b@email.com", "55566677788"), 204),
        # Repetir os primeiros dois leads — o cache deve evitar recomputacao
        (Lead("Jose A. Silva",    "11988880001", "outro@email.com",  "10010010011"), 201),
        (Lead("Maria Aparecida",  "11988880002", "maria@email.com",  "99999999999"), 202),
    ]

    print("\n  Processando lote de leads com memorizacao...\n")
    t0 = time.perf_counter()

    for lead, id_novo in novos_leads:
        encontrado, duplicata = verificar_duplicidade_com_memorizacao(
            lead, id_novo, cadastros, ids_cadastros
        )
        status = f"DUPLICATA de {duplicata}" if encontrado else "LEAD NOVO"
        print(f"  Lead ID {id_novo} ({lead.nome[:22]:<22}) -> {status}")

    t1 = time.perf_counter()
    print(f"\n  Tempo total: {(t1-t0)*1000:.2f} ms")

    stats = estatisticas_cache()
    print("\n  Estatisticas do Cache:")
    for k, v in stats.items():
        print(f"    {k:<25}: {v}")

    print("\n  Explicacao:")
    print("  Os leads de ID 201 e 202 foram verificados duas vezes.")
    print("  Na segunda verificacao, o cache retornou o resultado")
    print("  imediatamente sem recalcular as comparacoes.")


def demo_tarefa3() -> None:
    """Demonstracao da otimizacao de agenda com subproblemas."""
    separador("TAREFA 3 — Otimizacao de Agenda com Subproblemas")

    # Slots disponiveis: minutos desde 00:00
    # 08:00=480, 08:30=510, 09:00=540, 09:30=570... ate 17:00=1020
    slots_dia = tuple(range(480, 1021, 30))  # a cada 30 min das 08:00 ate 17:00

    print("\n  Slots disponiveis no dia:")
    print("  " + "  ".join(minutos_para_hora(s) for s in slots_dia))

    # --- Cenario 1: consultas de 60 minutos ---
    print("\n\n[Cenario 1] Consultas de 60 minutos")
    melhor_encaixe_agenda.cache_clear()
    slots60, total60 = melhor_encaixe_agenda(slots_dia, 60)
    exibir_agenda(slots60, 60, "Dr. Carlos Eduardo Souza")

    # --- Cenario 2: consultas de 45 minutos ---
    print("\n[Cenario 2] Consultas de 45 minutos")
    melhor_encaixe_agenda.cache_clear()
    slots45, total45 = melhor_encaixe_agenda(slots_dia, 45)
    exibir_agenda(slots45, 45, "Dra. Ana Paula Ferreira")

    # --- Cenario 3: consultas de 90 minutos ---
    print("\n[Cenario 3] Consultas de 90 minutos")
    melhor_encaixe_agenda.cache_clear()
    slots90, total90 = melhor_encaixe_agenda(slots_dia, 90)
    exibir_agenda(slots90, 90, "Dra. Mariana Santos Pereira")

    # --- Demonstracao do cache do lru_cache ---
    print("\n  Demonstracao do cache (lru_cache) na Tarefa 3:")
    melhor_encaixe_agenda.cache_clear()

    print("  Primeira chamada (sem cache)...")
    t0 = time.perf_counter()
    melhor_encaixe_agenda(slots_dia, 60)
    t1 = time.perf_counter()
    print(f"  Tempo 1a chamada : {(t1-t0)*1000:.4f} ms")

    print("  Segunda chamada  (com cache — mesmos argumentos)...")
    t0 = time.perf_counter()
    melhor_encaixe_agenda(slots_dia, 60)
    t1 = time.perf_counter()
    print(f"  Tempo 2a chamada : {(t1-t0)*1000:.4f} ms")

    info = melhor_encaixe_agenda.cache_info()
    print(f"\n  Cache info (lru_cache):")
    print(f"    hits   : {info.hits}")
    print(f"    misses : {info.misses}")
    print(f"    maxsize: {info.maxsize}")
    print(f"    currsize: {info.currsize}")


# ================================================================
#  PONTO DE ENTRADA
# ================================================================

if __name__ == "__main__":
    print("============================================================")
    print(" CARING HANDS CRM — Recursao e Memorizacao")
    print(" Hospital Sao Rafael (HSR) — Sprint 3 — FIAP")
    print("============================================================")

    demo_tarefa1()
    demo_tarefa2()
    demo_tarefa3()

    print("\n" + "="*60)
    print("  Execucao concluida com sucesso.")
    print("="*60)
