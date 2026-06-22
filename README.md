# VMTranslator

> **Disciplina:** Elementos de Sistemas de Computação (Nand to Tetris)
> **Instituição:** UFMA — Universidade Federal do Maranhão
> **Campus:** São Luís — M | Centro de Ciências Exatas e Tecnologia (CCET)
> **Curso:** Ciência e Tecnologia

---

## Autores

| Nome | Matrícula | GitHub |
|---|---|---|
| Pedro Victor Rocha Gonçalves | 2022029920 | [@pedrovi35](https://github.com/pedrovi35) |
| Sara Ferreira de Souza | 2022029911 | [@SaraFerreira42](https://github.com/SaraFerreira42) |

---

## Sobre o Projeto

Tradutor VM → Assembly Hack, implementado em **Python 3.10+** como parte da **Parte 1** do projeto VMTranslator do curso *Nand to Tetris*.

O tradutor converte arquivos `.vm` (bytecode da máquina virtual de dois níveis do livro *The Elements of Computing Systems*) em instruções `.asm` válidas para a CPU Hack.

---

## Estrutura do Projeto

```
vmtranslator/
├── parser/
│   ├── __init__.py
│   └── parser.py          # Tokenização, filtro de comentários, classificação de comandos
├── codewriter/
│   ├── __init__.py
│   └── code_writer.py     # Geração de Assembly Hack para todos os segmentos e operações
├── tests/
│   ├── test_parser.py     # Testes unitários do Parser (27 casos)
│   └── test_code_writer.py # Testes unitários do CodeWriter (24 casos)
├── StackArithmetic/
│   └── SimpleAdd/SimpleAdd.vm
├── MemoryAccess/
│   └── BasicTest/BasicTest.vm
├── vmtranslator.py        # Ponto de entrada — orquestrador
├── conftest.py            # Configuração do pytest
├── requirements.txt
└── README.md
```

---

## Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- (Opcional) instalar dependências de teste:

```bash
pip install -r requirements.txt
```

### Traduzir um arquivo `.vm`

```bash
python vmtranslator.py <caminho/para/Arquivo.vm>
```

O arquivo `.asm` gerado é salvo no **mesmo diretório** do arquivo de entrada.

---

## Exemplos de Uso

```bash
# Teste 1 — operação aritmética simples
python vmtranslator.py StackArithmetic/SimpleAdd/SimpleAdd.vm
# Saída: StackArithmetic/SimpleAdd/SimpleAdd.asm

# Teste 2 — acesso a segmentos de memória
python vmtranslator.py MemoryAccess/BasicTest/BasicTest.vm
# Saída: MemoryAccess/BasicTest/BasicTest.asm
```

---

## Executar os Testes Unitários

```bash
pytest tests/ -v
```

Resultado esperado: **51 testes passando**.

---

## Segmentos de Memória Suportados

| Segmento | Descrição | Mapeamento |
|---|---|---|
| `constant` | Valor literal (sem leitura de RAM) | Direto na instrução |
| `local` | Variáveis locais da função | `LCL` → RAM[1] |
| `argument` | Argumentos da função | `ARG` → RAM[2] |
| `this` | Base para objetos/arrays | `THIS` → RAM[3] |
| `that` | Base para estruturas dinâmicas | `THAT` → RAM[4] |
| `temp` | Registradores temporários | RAM[5] – RAM[12] |
| `pointer` | Acesso direto a `this`/`that` | RAM[3] ou RAM[4] |
| `static` | Variáveis estáticas do módulo | Símbolo `Módulo.índice` |

---

## Operações Suportadas

| Categoria | Comandos |
|---|---|
| Aritmética | `add`, `sub`, `neg` |
| Lógica bitwise | `and`, `or`, `not` |
| Comparação | `eq`, `gt`, `lt` |
| Memória | `push` / `pop` (todos os segmentos acima) |

---

## Decisões de Implementação

- **Labels de comparação** (`eq`, `gt`, `lt`) usam um contador interno (`VM_TRUE_0`, `VM_END_0`, …) para garantir unicidade quando o mesmo arquivo contém múltiplas comparações.
- **Segmentos com ponteiro** (`local`, `argument`, `this`, `that`) calculam o endereço final em `R13` antes do pop, evitando corrupção do SP durante a escrita.
- **`temp`** usa endereço absoluto fixo (`5 + índice`) sem necessidade de `R13`.
- **`static`** gera o símbolo Assembly `NomeDoMódulo.índice`, resolvido pelo assembler Hack.
