# Sliding Puzzle - Genetic Algorithm Solver

Um solver para Sliding Puzzles que utiliza **Algoritmo Genético** para encontrar sequências de movimentos que resolvem o puzzle.

## Tecnologias

- **Python 3.10+** — Linguagem principal
- **NumPy** — Operações matriciais e cálculos
- **Pygame** — Interface gráfica interativa

## Fluxo do Algoritmo Genético

### Estrutura Geral

```
┌─────────────────────────────────────┐
│  População Inicial Aleatória        │
│  (cromossomos = sequências de moves)│
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  LOOP POR GERAÇÃO (até max_gen)     │
├─────────────────────────────────────┤
│ 1.  Calcular Fitness (cada indivíduo)
│    └─ Simula o jogo com a sequência
│    └─ Se resolver: fitness alto
│    └─ Se não: conta peças corretas
│
│ 2.  Seleção por Torneio
│    └─ Escolhe 2 pais competindo
│
│ 3.  Cruzamento (Crossover)
│    └─ Combina genes dos pais
│
│ 4.  Mutação
│    └─ Muta ~5% dos genes aleatoriamente
│
│ 5.  Elitismo
│    └─ Preserva melhor da geração
│
│ 6.  Nova Geração
└─────────────────────────────────────┘
       ↓
┌─────────────────────────────────────┐
│  Melhor Solução Encontrada          │
│  (cromossomo com maior fitness)      │
└─────────────────────────────────────┘
```

### Detalhes Técnicos

| Componente | Descrição |
|---|---|
| **Cromossomo** | Lista de movimentos [up, down, left, right] |
| **Fitness** | Se resolvido: `10000 + (movimentos_economizados)`. Se não: `número_peças_corretas` |
| **Seleção** | Torneio com 3 indivíduos |
| **Cruzamento** | Ponto único (single-point crossover) |
| **Mutação** | 5% de chance por gene |
| **Elitismo** | Mantém o melhor indivíduo entre gerações |

### Hiperparâmetros (em `main.py`)

```python
tamanho_populacao = 100          # Indivíduos por geração
tamanho_cromossomo = 100         # Movimentos máximos permitidos
taxa_mutacao = 0.05              # 5% de chance de mutação
max_geracoes = 100               # Limite de evoluções
```

## Estrutura do Projeto

```
├── main.py                 # Script principal (AG terminal)
├── gui.py                  # Interface gráfica (Pygame)
├── genetic_algorithm.py    # Implementação do AG
├── game_logic.py          # Lógica do Sliding Puzzle
├── requirements.txt        # Dependências
└── pyproject.toml         # Configuração Poetry
```

## Como Usar

```bash
# Terminal
python main.py

# GUI
python -m gui
```

## Saída do Algoritmo

O algoritmo retorna:
- Sequência de movimentos para resolver o puzzle
- Número total de movimentos utilizados
- Evolução do fitness ao longo das gerações
