# Caring Hands CRM — Recursao e Memorizacao

**Disciplina:** Dynamic Programming
**Instituicao:** FIAP  
**Sprint:** 3  
**Grupo:** Caring Hands — Hospital Sao Rafael (HSR)
**Alunos:** Henrique Celso rm559687, Lucas Cortizo rm 559734

---

## Sumario

- [Objetivo](#objetivo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tarefa 1 — Verificacao Recursiva de Duplicidade](#tarefa-1)
- [Tarefa 2 — Memorizacao](#tarefa-2)
- [Tarefa 3 — Otimizacao de Agenda](#tarefa-3)
- [Como Executar](#como-executar)
- [Exemplos de Saida](#exemplos-de-saida)

---

## Objetivo

Modelar e resolver dois problemas recorrentes no CRM do Hospital Sao Rafael usando **recursao** e **memorizacao**:

1. Verificar se um novo lead ja existe no banco de dados (duplicidade)
2. Otimizar o encaixe de consultas na agenda de um medico

O modulo e integrado ao backend Java (API Spring Boot) como camada de analise e pre-processamento de dados antes da persistencia no Oracle.

---

## Estrutura do Projeto

```
crm-recursao/
├── crm_recursao_memorizacao.py   # Modulo principal com as 3 tarefas
└── README.md                     # Esta documentacao
```

### Estrutura interna do modulo

```
crm_recursao_memorizacao.py
│
├── UTILITARIOS
│   ├── normalizar(texto)          # Remove acentos, lowercase, strip
│   ├── limpar_telefone(tel)       # Retorna apenas digitos
│   └── limpar_cpf(cpf)            # Retorna apenas digitos
│
├── ESTRUTURA DE DADOS
│   └── class Lead                 # nome, telefone, email, cpf
│                                  # + propriedades normalizadas
│
├── TAREFA 1 — RECURSAO
│   └── verificar_duplicidade_recursiva(...)
│
├── TAREFA 2 — MEMORIZACAO
│   ├── comparar_leads_com_cache(...)
│   ├── verificar_duplicidade_com_memorizacao(...)
│   ├── estatisticas_cache()
│   └── limpar_cache()
│
├── TAREFA 3 — AGENDA
│   ├── melhor_encaixe_agenda(...)   # @lru_cache
│   ├── minutos_para_hora(minutos)
│   └── exibir_agenda(...)
│
└── ZONA DE TESTES
    ├── demo_tarefa1()
    ├── demo_tarefa2()
    └── demo_tarefa3()
```

---

## Tarefa 1

### Verificacao Recursiva de Duplicidade

**Problema:** Quando um novo lead chega ao CRM, ele pode ja estar cadastrado com dados ligeiramente diferentes (nome abreviado, telefone formatado diferente, CPF sem mascara). E necessario verificar duplicidade de forma flexivel.

**Solucao:** Funcao recursiva que percorre a lista de cadastros e compara os campos informados.

```python
def verificar_duplicidade_recursiva(
    novo_lead: Lead,
    cadastros: list[Lead],
    indice: int = 0,
    campos: list[str] | None = None
) -> tuple[bool, Optional[Lead]]:
```

**Logica da recursao:**

```
verificar(lead, lista, indice=0)
│
├── Caso base: indice >= len(lista)
│     └── Retorna (False, None)  — lista percorrida sem match
│
├── CPF coincide?
│     └── Retorna (True, cadastro)  — CPF e identificador unico
│
├── 2+ campos coincidem (email, telefone, nome)?
│     └── Retorna (True, cadastro)  — duplicata provavel
│
└── Chamada recursiva: verificar(lead, lista, indice + 1)
```

**Campos de comparacao:**

| Campo     | Peso       | Logica                                      |
|-----------|------------|---------------------------------------------|
| CPF       | Definitivo | 1 coincidencia = duplicata confirmada        |
| E-mail    | Alto       | Conta como 1 ponto                          |
| Telefone  | Alto       | Conta como 1 ponto                          |
| Nome      | Medio      | Normalizado (sem acentos, lowercase)         |
| Limiar    | —          | CPF: 1 ponto; demais: >= 2 pontos = duplicata|

**Exemplo de uso:**

```python
cadastros = [
    Lead("Jose Antonio da Silva", "11988880001", "jose@email.com", "10010010011"),
    Lead("Maria Aparecida",       "11988880002", "maria@email.com","20020020022"),
]

novo = Lead("Jose A. Silva", "11900000000", "outro@email.com", "10010010011")
encontrado, duplicata = verificar_duplicidade_recursiva(novo, cadastros)
# encontrado = True (CPF identico)
# duplicata  = Lead("Jose Antonio da Silva", ...)
```

---

## Tarefa 2

### Memorizacao para Evitar Comparacoes Repetidas

**Problema:** Em sistemas de alto volume, o mesmo par (novo_lead, cadastro_existente) pode ser comparado multiplas vezes — por exemplo, ao reprocessar lotes ou revalidar leads durante integracao com a API Java. Sem cache, cada comparacao refaz todo o trabalho.

**Solucao:** Cache em dicionario indexado por `(id_novo_lead, id_cadastro)`. A primeira comparacao e calculada e armazenada; chamadas subsequentes com os mesmos IDs retornam o resultado instantaneamente.

```python
_cache_comparacoes: dict[tuple[int, int], bool] = {}

def comparar_leads_com_cache(
    novo_lead, cadastro,
    id_novo, id_cadastro,
    campos=None
) -> bool:
    chave = (id_novo, id_cadastro)

    if chave in _cache_comparacoes:   # HIT: retorna sem recalcular
        return _cache_comparacoes[chave]

    resultado = _calcular_comparacao(novo_lead, cadastro, campos)
    _cache_comparacoes[chave] = resultado  # armazena
    return resultado
```

**Impacto observado:**

```
Lead ID 201 verificado 1a vez  -> cache MISS  (calcula e armazena)
Lead ID 201 verificado 2a vez  -> cache HIT   (retorna imediatamente)
Lead ID 202 verificado 1a vez  -> cache MISS
Lead ID 202 verificado 2a vez  -> cache HIT

Tempo 1a chamada: ~0.28 ms
Tempo 2a chamada: ~0.001 ms  (280x mais rapido)
```

**Estatisticas disponiveis:**

```python
stats = estatisticas_cache()
# {
#   "total_comparacoes": 22,
#   "cache_hits":         3,
#   "cache_misses":      19,
#   "taxa_acerto":    "13.6%",
#   "entradas_no_cache": 19
# }
```

> A taxa de acerto cresce proporcionalmente ao volume de leads repetidos no lote. Em producao com reprocessamentos frequentes, pode ultrapassar 60%.

---

## Tarefa 3

### Otimizacao de Agenda com Subproblemas

**Problema:** Dado um conjunto de slots horarios disponiveis para um medico, encontrar o maior numero de consultas que podem ser encaixadas no dia, respeitando a duracao de cada consulta e sem sobreposicao de horarios.

**Modelo:** Cada slot disponivel e um inteiro representando minutos desde 00:00.
- `480` = 08:00, `510` = 08:30, `540` = 09:00 ...

**Solucao:** Programacao dinamica via recursao + `@lru_cache`.

```python
@lru_cache(maxsize=512)
def melhor_encaixe_agenda(
    horarios_disponiveis: tuple[int, ...],
    duracao_consulta: int,
    indice: int = 0
) -> tuple[list[int], int]:
```

**Arvore de decisao recursiva:**

```
encaixar(slots, duracao, indice)
│
├── Caso base: indice >= len(slots)
│     └── Retorna ([], 0)
│
├── Opcao A — ENCAIXAR no slot[indice]:
│   ├── fim = slot[indice] + duracao
│   ├── proximo_livre = primeiro slot >= fim
│   └── resultado = [slot[indice]] + encaixar(slots, dur, proximo_livre)
│
├── Opcao B — PULAR o slot[indice]:
│   └── resultado = encaixar(slots, dur, indice + 1)
│
└── Retorna a opcao com MAIS consultas
```

**@lru_cache — memorizacao automatica:**

Como os argumentos sao imutaveis (tupla de inteiros + inteiros), o Python
armazena automaticamente cada chamada. Subproblemas identicos nao sao
recalculados, tornando a solucao eficiente mesmo para agendas longas.

```
Cache info apos execucao:
  hits    : 20    (subproblemas reutilizados)
  misses  : 20    (subproblemas calculados 1 vez)
  currsize: 20
```

**Resultados por duracao:**

| Duracao | Consultas no dia (08:00-17:00) |
|---------|-------------------------------|
| 30 min  | 19 consultas                  |
| 45 min  | 10 consultas                  |
| 60 min  | 10 consultas                  |
| 90 min  |  7 consultas                  |

---

## Como Executar

### Pre-requisitos

- Python 3.10 ou superior (usa `list[str]` como type hint)
- Sem dependencias externas — usa apenas bibliotecas da stdlib

### Executar o modulo completo

```bash
python3 crm_recursao_memorizacao.py
```

### Importar funcoes individualmente

```python
from crm_recursao_memorizacao import (
    Lead,
    verificar_duplicidade_recursiva,
    verificar_duplicidade_com_memorizacao,
    melhor_encaixe_agenda,
    minutos_para_hora,
    limpar_cache,
    estatisticas_cache,
)

# Verificar duplicidade
cadastros = [Lead("Nome", "telefone", "email@x.com", "12345678901")]
novo = Lead("Nome", "telefone", "email@x.com", "12345678901")
dup, lead = verificar_duplicidade_recursiva(novo, cadastros)

# Otimizar agenda
slots = tuple(range(480, 1021, 30))
agenda, total = melhor_encaixe_agenda(slots, duracao_consulta=60)
```

---

## Exemplos de Saida

```
TAREFA 1 — Verificacao Recursiva de Duplicidade

[Caso 1] Lead com CPF ja cadastrado:
  Novo lead   : Lead(nome='Jose A. Silva', cpf='10010010011')
  Duplicata?  : True
  Coincide com: Lead(nome='Jose Antonio da Silva', cpf='10010010011')

[Caso 4] Lead genuinamente novo:
  Novo lead   : Lead(nome='Carla Fernanda Braga', cpf='77711122233')
  Duplicata?  : False

TAREFA 3 — Otimizacao de Agenda

  Agenda otimizada — Dr. Carlos Eduardo Souza (60 min/consulta)
  Slot   Inicio   Fim
  ------------------------
  1      08:00    09:00
  2      09:00    10:00
  ...
  10     17:00    18:00
  Total: 10 consultas encaixadas

  Tempo 1a chamada : 0.0104 ms
  Tempo 2a chamada : 0.0005 ms   <- cache ativo
```

---

## Integrantes

| Nome | RM |
|---|---|
| [Nome do Integrante 1] | [RM] |
| [Nome do Integrante 2] | [RM] |
| [Nome do Integrante 3] | [RM] |
| [Nome do Integrante 4] | [RM] |
| [Nome do Integrante 5] | [RM] |
