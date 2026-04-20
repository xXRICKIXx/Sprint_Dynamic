# Caring Hands CRM — Recursao e Memorizacao

**Disciplina:** Dynamic Programming  
**Instituicao:** FIAP  
**Sprint:** 3  
**Grupo:** Caring Hands — Hospital Sao Rafael (HSR)

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

Modelar e resolver problemas do CRM do Hospital Sao Rafael usando **recursao** e **memorizacao**:

1. Verificar duplicidade de leads
2. Evitar recalculo de comparacoes repetidas
3. Otimizar encaixe de consultas na agenda

Implementacao simplificada:
- sem uso de `bool` (utiliza 0 e 1)
- sem `Optional`
- sem bibliotecas externas (`re`, `unicodedata`)

---

## Estrutura do Projeto


crm-recursao/
├── crm_recursao_memorizacao.py
└── README.md


### Estrutura interna do modulo


crm_recursao_memorizacao.py
│
├── UTILITARIOS
│ ├── normalizar(texto)
│ ├── limpar_telefone(tel)
│ └── limpar_cpf(cpf)
│
├── ESTRUTURA DE DADOS
│ └── class Lead
│
├── TAREFA 1 — RECURSAO
│ └── verificar_duplicidade_recursiva(...)
│
├── TAREFA 2 — CACHE
│ ├── comparar_com_cache(...)
│ ├── verificar_com_cache(...)
│ ├── stats_cache()
│ └── limpar_cache()
│
├── TAREFA 3 — AGENDA
│ ├── melhor_agenda(...)
│ ├── minutos_para_hora(...)
│ └── exibir_agenda(...)
│
└── TESTES
├── demo1()
├── demo2()
└── demo3()


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

1a execucao -> MISS (calcula)
2a execucao -> HIT (usa cache)

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

T3

Agenda
Inicio  Fim
08:00   09:00
09:00   10:00
...
Total: 10


Integrantes
Nome	RM
Henrique Celso	559687
Lucas Cortizo	559734
